"""
/***************************************************************************
Name            : menu_from_project plugin
Description          : Build layers shortcut menu based on QGIS project
Date                 :  10/11/2011
copyright            : (C) 2011 by Agence de l'Eau Adour Garonne
email                : xavier.culos@eau-adour-garonne.fr
***************************************************************************/

/***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************/

"""

# Standard library
import logging
import os
import re
from pathlib import Path

# PyQGIS
from qgis.core import (
    QgsApplication,
    QgsMessageLog,
    QgsProject,
    QgsRasterLayer,
    QgsReadWriteContext,
    QgsSettings,
    QgsVectorLayer,
    QgsVectorTileLayer,
    QgsRelation,
)
from qgis.PyQt.QtCore import QCoreApplication, QFileInfo, Qt, QTranslator, QUuid
from qgis.PyQt.QtGui import QFont, QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QWidget
from qgis.utils import plugins

# project
from .__about__ import DIR_PLUGIN_ROOT, __title__, __title_clean__
from .logic.qgs_manager import (
    get_project_title,
    is_absolute,
    read_from_database,
    read_from_file,
    read_from_http,
)
from .logic.tools import guess_type_from_uri, icon_per_geometry_type
from .ui.menu_conf_dlg import MenuConfDialog  # noqa: F4 I001

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
cache_folder = Path.home() / f".cache/QGIS/{__title_clean__}"
cache_folder.mkdir(exist_ok=True, parents=True)

# ############################################################################
# ########## Functions #############
# ##################################

from qgis.PyQt.QtCore import QLocale, QUrl, QDir
from qgis.PyQt.QtGui import QDesktopServices

"""
    En attendant un correctif
"""


def showPluginHelp(packageName: str = None, filename: str = "index", section: str = ""):
    try:
        source = ""
        if packageName is None:
            import inspect

            source = inspect.currentframe().f_back.f_code.co_filename
        else:
            import sys

            source = sys.modules[packageName].__file__
    except:
        return
    path = os.path.dirname(source)
    locale = str(QLocale().name())
    helpfile = os.path.join(path, filename + "-" + locale + ".html")
    if not os.path.exists(helpfile):
        helpfile = os.path.join(path, filename + "-" + locale.split("_")[0] + ".html")
    if not os.path.exists(helpfile):
        helpfile = os.path.join(path, filename + "-en.html")
    if not os.path.exists(helpfile):
        helpfile = os.path.join(path, filename + "-en_US.html")
    if not os.path.exists(helpfile):
        helpfile = os.path.join(path, filename + ".html")
    if os.path.exists(helpfile):
        url = "file://" + QDir.fromNativeSeparators(helpfile)
        if section != "":
            url = url + "#" + section
        QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))


def getFirstChildByTagNameValue(elt, tagName, key, value):
    nodes = elt.elementsByTagName(tagName)
    for node in (nodes.at(i) for i in range(nodes.size())):
        nd = node.namedItem(key)
        if nd and value == nd.firstChild().toText().data():
            # layer founds
            return node

    return None


def getFirstChildByAttrValue(elt, tagName, key, value):
    nodes = elt.elementsByTagName(tagName)
    for node in (nodes.at(i) for i in range(nodes.size())):
        if (
            node.toElement().hasAttribute(key)
            and node.toElement().attribute(key) == value
        ):
            # layer founds
            return node

    return None


def getMapLayersDict(domdoc):
    r = {}
    nodes = domdoc.documentElement().elementsByTagName("maplayer")
    for node in (nodes.at(i) for i in range(nodes.size())):
        nd = node.namedItem("id")
        if nd:
            r[nd.firstChild().toText().data()] = node

    return r


def project_trusted(doc):
    """Return if the project is trusted.

    :param doc: The QGIS project as XML document. Default to None.
    :type doc: QDomDocument

    :return: True of False.
    :rtype: bool
    """
    tags = doc.elementsByTagName("qgis")
    if tags.count():
        node = tags.at(0)
        trust_node = node.namedItem("trust")
        return trust_node.toElement().attribute("active") == "1"

    return False


# ############################################################################
# ########## Classes ###############
# ##################################


class MenuFromProject:
    SOURCE_MD_OGC = "ogc"
    SOURCE_MD_LAYER = "layer"

    def on_initializationCompleted(self):
        # build menu
        self.initMenus()

    def __init__(self, iface):
        self.path = QFileInfo(os.path.realpath(__file__)).path()
        self.iface = iface
        self.toolBar = None
        self.project_registry = QgsApplication.projectStorageRegistry()

        # new multi projects var
        self.projects = []
        self.docs = dict()
        self.menubarActions = []
        self.layerMenubarActions = []
        self.canvas = self.iface.mapCanvas()
        self.optionTooltip = False
        self.optionCreateGroup = False
        self.optionLoadAll = False
        self.optionOpenLinks = False
        self.optionSourceMD = MenuFromProject.SOURCE_MD_OGC
        self.mapLayerIds = {}
        self.read()
        settings = QgsSettings()

        if settings.value("menu_from_project/is_setup_visible") is None:
            # This setting does not exist. We add it by default.
            settings.setValue("menu_from_project/is_setup_visible", True)

        # If we want to hide the dialog setup to users.
        self.is_setup_visible = settings.value(
            "menu_from_project/is_setup_visible", True, bool
        )

        self.action_project_configuration = None
        self.action_menu_help = None

        # default lang
        locale = settings.value("locale/userLocale")
        self.myLocale = locale[0:2]
        # dictionary
        localePath = self.path + "/i18n/" + self.myLocale + ".qm"
        # translator
        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)
            QCoreApplication.installTranslator(self.translator)

    @staticmethod
    def tr(message):
        return QCoreApplication.translate("MenuFromProject", message)

    @staticmethod
    def log(message, application=__title__, indent=0):
        indent_chars = " .. " * indent
        QgsMessageLog.logMessage(
            f"{indent_chars}{message}", application, notifyUser=True
        )

    def store(self):
        """Store the configuration in the QSettings."""
        s = QgsSettings()

        s.beginGroup("menu_from_project")
        try:
            s.setValue("optionTooltip", self.optionTooltip)
            s.setValue("optionCreateGroup", self.optionCreateGroup)
            s.setValue("optionLoadAll", self.optionLoadAll)
            s.setValue("optionOpenLinks", self.OpenLinks)
            s.setValue("optionSourceMD", self.optionSourceMD)

            s.beginWriteArray("projects", len(self.projects))
            try:
                for i, project in enumerate(self.projects):
                    s.setArrayIndex(i)
                    s.setValue("file", project["file"])
                    s.setValue("name", project["name"])
                    s.setValue("location", project["location"])
                    s.setValue(
                        "type_storage",
                        project.get(
                            "type_storage", guess_type_from_uri(project.get("file"))
                        ),
                    )
            finally:
                s.endArray()
        finally:
            s.endGroup()

    def read(self):
        """Read the configuration from QSettings."""
        s = QgsSettings()
        try:
            s.beginGroup("menu_from_project")
            try:
                self.optionTooltip = s.value("optionTooltip", True, type=bool)
                self.optionCreateGroup = s.value("optionCreateGroup", False, type=bool)
                self.optionLoadAll = s.value("optionLoadAll", False, type=bool)
                self.optionOpenLinks = s.value("optionOpenLinks", True, type=bool)
                self.optionSourceMD = s.value(
                    "optionSourceMD", MenuFromProject.SOURCE_MD_OGC, type=str
                )

                size = s.beginReadArray("projects")
                try:
                    for i in range(size):
                        s.setArrayIndex(i)
                        file = s.value("file", "")
                        name = s.value("name", "")
                        location = s.value("location", "new")
                        type_storage = s.value(
                            "type_storage", guess_type_from_uri(file)
                        )
                        if file != "":
                            self.projects.append(
                                {
                                    "file": file,
                                    "name": name,
                                    "location": location,
                                    "type_storage": type_storage,
                                }
                            )
                finally:
                    s.endArray()

            finally:
                s.endGroup()

        except Exception:
            pass

    def addToolTip(self, ml, action):
        """Search and add a tooltip to a given action according to a maplayer.

        :param ml: The maplayer as XML definition.
        :type ml: documentElement

        :param action: The action.
        :type action: QAction
        """
        if ml is not None:
            try:
                abstract, title = "", ""
                md = ml.namedItem("resourceMetadata")
                mdLayerTitle = md.namedItem("title").firstChild().toText().data()
                mdLayerAbstract = md.namedItem("abstract").firstChild().toText().data()
                ogcTitle = ml.namedItem("title").firstChild().toText().data()
                ogcAbstract = ml.namedItem("abstract").firstChild().toText().data()

                if self.optionSourceMD == MenuFromProject.SOURCE_MD_OGC:
                    abstract = ogcAbstract or mdLayerAbstract
                    title = ogcTitle or mdLayerTitle
                else:
                    abstract = mdLayerAbstract or ogcAbstract
                    title = mdLayerTitle or ogcTitle

                if (abstract != "") and (title == ""):
                    action.setToolTip(
                        "<p>{}</p>".format("<br/>".join(abstract.split("\n")))
                    )
                else:
                    if abstract != "" or title != "":
                        action.setToolTip(
                            "<b>{}</b><br/>{}".format(
                                title, "<br/>".join(abstract.split("\n"))
                            )
                        )
                    else:
                        action.setToolTip("")

            except Exception as e:
                for m in e.args:
                    self.log(m)

    def addMenuItem(self, uri, filename, node, menu, absolute, mapLayersDict):
        """Add menu to an item."""
        yaLayer = False
        if node is None or node.nodeName() == "":
            return yaLayer

        element = node.toElement()

        # if legendlayer tag
        if node.nodeName() == "layer-tree-layer":
            try:
                name = element.attribute("name")
                layerId = element.attribute("id")
                visible = element.attribute("checked", "") == "Qt::Checked"
                expanded = element.attribute("expanded", "0") == "1"
                action = QAction(name, self.iface.mainWindow())
                embedNd = getFirstChildByAttrValue(
                    element, "property", "key", "embedded"
                )

                # is layer embedded ?
                if embedNd and embedNd.toElement().attribute("value") == "1":
                    # layer is embeded
                    efilename = None
                    eFileNd = getFirstChildByAttrValue(
                        element, "property", "key", "embedded_project"
                    )

                    if eFileNd:
                        # get project file name
                        embeddedFile = eFileNd.toElement().attribute("value")
                        if not absolute and (embeddedFile.find(".") == 0):
                            efilename = QFileInfo(filename).path() + "/" + embeddedFile

                        # if ok
                        if efilename:
                            # add menu item
                            action.triggered.connect(
                                lambda checked, uri=uri, f=efilename, lid=layerId, m=menu, v=visible, x=expanded: self.loadLayer(
                                    uri, f, lid, m, v, x
                                )
                            )

                            menu.addAction(action)
                            yaLayer = True

                            if self.optionTooltip:
                                # search embeded maplayer (for title, abstract)
                                mapLayer = self.getMapLayerDomFromQgs(
                                    efilename, layerId
                                )
                                if mapLayer is not None:
                                    self.addToolTip(mapLayer, action)
                    else:
                        self.log(
                            "Menu from layer: {} not found in project {}".format(
                                layerId, efilename
                            )
                        )

                # layer is not embedded
                else:
                    efilename = filename

                    if self.optionTooltip:
                        self.addToolTip(mapLayersDict[layerId], action)

                    action.triggered.connect(
                        lambda checked, uri=uri, f=filename, lid=layerId, m=menu, v=visible, x=expanded: self.loadLayer(
                            uri, f, lid, m, v, x
                        )
                    )

                    menu.addAction(action)
                    yaLayer = True

                # Add geometry type icon
                try:
                    map_layer = self.getMapLayerDomFromQgs(
                        efilename, layerId
                    ).toElement()
                    geometry_type = map_layer.attribute("geometry")
                    if geometry_type == "":
                        # A TMS has not a geometry attribute.
                        # Let's read the "type"
                        geometry_type = map_layer.attribute("type")

                    action.setIcon(icon_per_geometry_type(geometry_type))
                except Exception:
                    pass

            except Exception as e:
                for m in e.args:
                    self.log(m)

        # / if element.tagName() == "layer-tree-layer":

        # if legendgroup tag
        if node.nodeName() == "layer-tree-group":
            name = element.attribute("name")
            propertiesNode = node.firstChild()
            embedNd = getFirstChildByAttrValue(
                propertiesNode.toElement(), "property", "key", "embedded"
            )

            # is group embedded ?
            if embedNd and embedNd.toElement().attribute("value") == "1":
                # group is embeded
                efilename = None
                eFileNd = getFirstChildByAttrValue(
                    element, "property", "key", "embedded_project"
                )

                if eFileNd:
                    # get project file name
                    embeddedFile = eFileNd.toElement().attribute("value")
                    if not absolute and (embeddedFile.find(".") == 0):
                        efilename = QFileInfo(filename).path() + "/" + embeddedFile

                    # if ok
                    if efilename:
                        # add menu group
                        doc, _ = self.getQgsDoc(efilename)

                        groupNode = getFirstChildByAttrValue(
                            doc.documentElement(), "layer-tree-group", "name", name
                        )

                        # and do recursion
                        r = self.addMenuItem(
                            efilename,
                            efilename,
                            groupNode,
                            menu,
                            absolute,
                            getMapLayersDict(doc),
                        )

                        yaLayer = yaLayer or r

                else:
                    self.log(
                        "Menu from layer: {} not found in project {}".format(
                            layerId, efilename
                        )
                    )

            # group is not embedded
            else:
                if name == "-":
                    menu.addSeparator()

                elif name.startswith("-"):
                    action = QAction(name[1:], self.iface.mainWindow())
                    font = QFont()
                    font.setBold(True)
                    action.setFont(font)
                    menu.addAction(action)

                else:
                    # sub-menu
                    sousmenu = menu.addMenu("&" + element.attribute("name"))
                    sousmenu.menuAction().setToolTip("")
                    sousmenu.setToolTipsVisible(self.optionTooltip)

                    childNode = node.firstChild()

                    #  ! recursion
                    r = self.addMenuItem(
                        uri, filename, childNode, sousmenu, absolute, mapLayersDict
                    )

                    if r and self.optionLoadAll and (len(sousmenu.actions()) > 1):
                        action = QAction(self.tr("Load all"), self.iface.mainWindow())
                        font = QFont()
                        font.setBold(True)
                        action.setFont(font)
                        sousmenu.addAction(action)
                        action.triggered.connect(
                            lambda checked, f=None, w=None, m=sousmenu: self.loadLayer(
                                uri, f, w, m
                            )
                        )

        # / if element.tagName() == "legendgroup":

        nextNode = node.nextSibling()
        if nextNode is not None:
            # ! recursion
            r = self.addMenuItem(uri, filename, nextNode, menu, absolute, mapLayersDict)
            yaLayer = yaLayer or r

        return yaLayer

    def addMenu(self, name, uri, filepath, domdoc, location, previous=None):
        """Add menu to the QGIS interface.

        :param name: The name of the parent menu. It might be an empty string.
        :type name: basestring

        :param filepath: The filepath of the project.
        :type filepath: basestring

        :param domdoc: The QGIS project as XML document.
        :type domdoc: QDomDocument

        :param location: The menu location (new menu, or added in "layer - add layer" sub-menu).
        :type location: string

        :param previous: The previous added menu (for merging eventually)
        :type previous: QMenu
        """
        if not name:
            name = get_project_title(domdoc)

            if not name:
                try:
                    name = filepath.split("/")[-1]
                    name = name.split(".")[0]
                except IndexError:
                    name = ""

        # main project menu
        if location == "merge":
            projectMenu = previous
            projectMenu.addSeparator()
        else:
            if location == "layer":
                menuBar = self.iface.addLayerMenu()
            if location == "new":
                menuBar = self.iface.editMenu().parentWidget()

            projectMenu = QMenu("&" + name, menuBar)
            projectMenu.setToolTipsVisible(self.optionTooltip)
            projectAction = menuBar.addMenu(projectMenu)

            if location == "layer":
                self.layerMenubarActions.append(projectAction)
            if location == "new":
                self.menubarActions.append(projectAction)

        mapLayersDict = getMapLayersDict(domdoc)

        # build menu on legend schema
        legends = domdoc.elementsByTagName("layer-tree-group")
        if legends.length() > 0:
            node = legends.item(0)
            if node:
                node = node.firstChild()
                self.addMenuItem(
                    uri, filepath, node, projectMenu, is_absolute(domdoc), mapLayersDict
                )

        return projectMenu

    def getQgsDoc(self, uri):
        """Return the XML document and the path from an URI.

        The URI can be a filepath or stored in database.

        :param uri: The URI to fetch.
        :type uri: basestring

        :return: Tuple with XML document and the filepath.
        :rtype: (QDomDocument, basestring)
        """
        # determine storage type: file, database or http
        qgs_storage_type = guess_type_from_uri(uri)

        # check if docs is already here
        if uri in self.docs:
            return self.docs[uri], uri

        if qgs_storage_type == "file":
            doc, project_path = read_from_file(uri)
        elif qgs_storage_type == "database":
            doc, project_path = read_from_database(uri, self.project_registry)
        elif qgs_storage_type == "http":
            doc, project_path = read_from_http(uri, cache_folder)
        else:
            self.log(f"Unrecognized project type: {uri}")

        # store doc into the plugin registry
        self.docs[project_path] = doc

        return doc, project_path

    def getMapLayerDomFromQgs(self, fileName, layerId):
        """Return the maplayer node in a project filepath given a maplayer ID.

        :param fileName: The project filepath on the filesystem.
        :type fileName: basestring

        :param layerId: The layer ID to look for in the project.
        :type layerId: basestring

        :return: The XML node of the layer.
        :rtype: QDomNode
        """
        doc, _ = self.getQgsDoc(fileName)
        return getFirstChildByTagNameValue(
            doc.documentElement(), "maplayer", "id", layerId
        )

    def initMenus(self):
        menuBar = self.iface.editMenu().parentWidget()
        for action in self.menubarActions:
            menuBar.removeAction(action)
            del action

        self.menubarActions = []

        menuBar = self.iface.addLayerMenu()
        for action in self.layerMenubarActions:
            menuBar.removeAction(action)
            del action

        self.layerMenubarActions = []

        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        previous = None
        for project in self.projects:
            try:
                project["valid"] = True
                uri = project["file"]
                doc, path = self.getQgsDoc(uri)
                previous = self.addMenu(
                    project["name"], uri, path, doc, project["location"], previous
                )
            except Exception as e:
                project["valid"] = False
                self.log("Menu from layer: Invalid {}".format(uri))
                for m in e.args:
                    self.log(m)

        QgsApplication.restoreOverrideCursor()

    def initGui(self):
        if self.is_setup_visible:
            # menu item - Main
            self.action_project_configuration = QAction(
                QIcon(str(DIR_PLUGIN_ROOT / "resources/menu_from_project.png")),
                self.tr("Projects configuration"),
                self.iface.mainWindow(),
            )

            self.iface.addPluginToMenu(
                "&" + __title__, self.action_project_configuration
            )
            # Add actions to the toolbar
            self.action_project_configuration.triggered.connect(
                self.open_projects_config
            )

            # menu item - Documentation
            self.action_menu_help = QAction(
                QIcon(QgsApplication.iconPath("mActionHelpContents.svg")),
                self.tr("Help"),
                self.iface.mainWindow(),
            )

            self.iface.addPluginToMenu("&" + __title__, self.action_menu_help)
            self.action_menu_help.triggered.connect(
                lambda: showPluginHelp(filename="doc/index")
            )

        self.iface.initializationCompleted.connect(self.on_initializationCompleted)

    def unload(self):
        menuBar = self.iface.editMenu().parentWidget()
        for action in self.menubarActions:
            menuBar.removeAction(action)
            del action

        menuBar = self.iface.addLayerMenu()
        for action in self.layerMenubarActions:
            menuBar.removeAction(action)
            del action

        self.menubarActions = []
        self.layerMenubarActions = []

        if self.is_setup_visible:
            self.iface.removePluginMenu(
                "&" + __title__, self.action_project_configuration
            )
            self.iface.removePluginMenu("&" + __title__, self.action_menu_help)
            self.action_project_configuration.triggered.disconnect(
                self.open_projects_config
            )

        self.iface.initializationCompleted.disconnect(self.on_initializationCompleted)

        self.store()

    def open_projects_config(self):
        dlg = MenuConfDialog(self.iface.mainWindow(), self)
        dlg.setModal(True)

        dlg.show()
        result = dlg.exec_()
        del dlg

        if result != 0:
            # clear web projects cache
            try:
                read_from_http.cache_clear()
                read_from_file.cache_clear()
            except Exception:
                pass

            # build menus
            self.initMenus()

    def addLayer(
        self,
        uri,
        doc,
        layerId,
        group=None,
        visible=False,
        expanded=False,
        parentsLoop: dict = {},
        loop=0,
    ):
        theLayer = None

        # is project in relative path ?
        absolute = is_absolute(doc)
        trusted = project_trusted(doc)

        node = getFirstChildByTagNameValue(
            doc.documentElement(), "maplayer", "id", layerId
        )
        node = node.cloneNode()
        if node:
            idNode = node.namedItem("id")
            layerType = node.toElement().attribute("type", "vector")
            # give it a new id (for multiple import)
            newLayerId = "L%s" % re.sub("[{}-]", "", QUuid.createUuid().toString())
            self.mapLayerIds[newLayerId] = layerId

            try:
                idNode.firstChild().toText().setData(newLayerId)
            except Exception:
                pass

            # if relative path, adapt datasource
            if not absolute:
                try:
                    datasourceNode = node.namedItem("datasource")
                    ds = datasourceNode.firstChild().toText().data()
                    providerNode = node.namedItem("provider")
                    provider = providerNode.firstChild().toText().data()

                    if provider in ["ogr", "gdal"] and (ds.find(".") == 0):
                        projectpath = QFileInfo(uri).path()
                        newlayerpath = projectpath + "/" + ds
                        datasourceNode.firstChild().toText().setData(newlayerpath)
                except Exception:
                    pass

            # is relations exists ?
            relationsToBuild = []
            if self.optionOpenLinks:
                relationsToBuild = self.buildRelations(
                    uri, doc, layerId, newLayerId, group, parentsLoop, loop
                )

            # read modified layer node
            newLayer = None
            if self.optionCreateGroup and group is not None:
                if layerType == "raster":
                    theLayer = QgsRasterLayer()
                elif layerType == "vector-tile":
                    theLayer = QgsVectorTileLayer()
                else:
                    theLayer = QgsVectorLayer()
                    theLayer.setReadExtentFromXml(trusted)

                theLayer.readLayerXml(node.toElement(), QgsReadWriteContext())

                # Special process if the plugin "DB Style Manager" is installed
                flag = "use_db_style_manager_in_custom_menu" in os.environ
                if flag and "db-style-manager" in plugins:
                    try:
                        plugins["db-style-manager"].load_style_from_database(theLayer)
                    except Exception:
                        self.log(
                            "DB-Style-Manager failed to load the style.", indent=loop
                        )

                # needed
                newLayer = QgsProject.instance().addMapLayer(theLayer, False)
                if newLayer is not None:
                    # add to group
                    treeNode = group.insertLayer(0, newLayer)
                    treeNode.setExpanded(expanded)
                    treeNode.setItemVisibilityChecked(visible)
            else:
                # create layer
                ok = QgsProject.instance().readLayer(node)
                if ok:
                    newLayer = QgsProject.instance().mapLayer(newLayerId)

            return newLayer, relationsToBuild

        else:
            self.log("{} not found".format(layerId), indent=loop)

        return None, None

    def getRelations(self, doc):
        """
        Charger la définition des relations (niveau projet), pour les rétablir éventuellement après chargement des couches

        <relations>
            <relation strength="Association" referencedLayer="layerid" id="refid" name="fk_region" referencingLayer="layerid">
                <fieldRef referencedField="insee_region" referencingField="insee_region"/>
            </relation>
        </relations>
        """
        relations = []
        try:
            nodes = doc.elementsByTagName("relations")
            relsNode = nodes.at(0)

            relNodes = relsNode.toElement().elementsByTagName("relation")
            for relNode in (relNodes.at(i) for i in range(relNodes.size())):
                fieldNodes = relNode.toElement().elementsByTagName("fieldRef")
                fieldNode = fieldNodes.at(0)

                if fieldNode:
                    relation = {}
                    for attr in [
                        "strength",
                        "referencedLayer",
                        "id",
                        "name",
                        "referencingLayer",
                    ]:
                        relation[attr] = relNode.toElement().attribute(attr)

                    for attr in [
                        "referencedField",
                        "referencingField",
                    ]:
                        relation[attr] = fieldNode.toElement().attribute(attr)

                    if relation["referencedLayer"] != "":
                        relations.append(relation)
        except Exception as e:
            for m in e.args:
                self.log(m)

        return relations

    def getRelationsForLayer(self, relations, source=None, target=None):
        """Retourne le dico de la relation selon si 'source'=referencedLayer ou 'target'=referencingLayer"""

        r = []
        try:
            for relation in relations:
                if source is not None and source == relation["referencedLayer"]:
                    r.append(relation)

                if target is not None and target == relation["referencingLayer"]:
                    r.append(relation)
        except Exception as e:
            for m in e.args:
                self.log(m)

        return r

    def fixForm(self, doc, newLayerId: str, oldRelationId, newRelationId):
        """rebuilds the form when relations are defined in it

        Principle: reading the source XML document, updating identifiers, updating editFormConfig
        """
        theLayer = QgsProject.instance().mapLayer(newLayerId)
        oldLayerId = self.mapLayerIds[newLayerId]

        layerNode = getFirstChildByTagNameValue(
            doc.documentElement(), "maplayer", "id", oldLayerId
        )

        nodes = layerNode.toElement().elementsByTagName("attributeEditorForm")
        if nodes.count() == 0:
            return
        aefNode = nodes.at(0)

        nodes = aefNode.toElement().elementsByTagName("attributeEditorRelation")
        for nodeIdx in range(nodes.length()):
            aerNode = nodes.at(nodeIdx)
            rid = aerNode.toElement().attribute("relation")
            if rid == oldRelationId:
                aerNode.toElement().setAttribute("relation", newRelationId)

                nodes = aefNode.toElement().elementsByTagName("widgets")
                widgets = nodes.at(0)
                widgets.toElement().setAttribute("name", newRelationId)

                editFormConfig = theLayer.editFormConfig()
                rootContainer = editFormConfig.invisibleRootContainer()
                rootContainer.clear()
                editFormConfig.clearTabs()
                editFormConfig.readXml(layerNode, QgsReadWriteContext())
                theLayer.setEditFormConfig(editFormConfig)

    def buildProjectRelation(self, doc, relDict):
        try:
            """builds one relation, add it to the project"""
            REL_STRENGTH = {
                "Association": QgsRelation.Association,
                "Composition": QgsRelation.Composition,
            }
            relMan = QgsProject.instance().relationManager()

            rel = QgsRelation()
            rel.addFieldPair(relDict["referencingField"], relDict["referencedField"])
            oldRelationId = relDict["id"]
            newRelationId = "R%s" % re.sub("[{}-]", "", QUuid.createUuid().toString())
            rel.setId(newRelationId)
            rel.setName(relDict["name"])
            rel.setReferencedLayer(relDict["referencedLayer"])
            rel.setReferencingLayer(relDict["referencingLayer"])
            rel.setStrength(REL_STRENGTH[relDict["strength"]])
            rel.updateRelationStatus()

            if rel.isValid():
                relMan.addRelation(rel)

                # Adapter le formulaire de la couche referencedLayer
                try:
                    self.fixForm(
                        doc, relDict["referencedLayer"], oldRelationId, newRelationId
                    )
                except Exception:
                    self.log(
                        "Form not fixed for layer {}".format(relDict["referencedLayer"])
                    )

            else:
                self.log(
                    "Invalid relation {} : {}".format(rel.id(), rel.validationError())
                )
        except Exception as e:
            for m in e.args:
                self.log(m)

    def buildRelations(
        self, uri, doc, oldLayerId, newLayerId, group, parentsLoop, loop
    ):
        """identify the relations to be created (later, after source layer creation)

        Based on those of the source project, adapted to the new identifiers of the layers
        """
        relationsToBuild, targetRelations = [], []

        relations = self.getRelations(doc)
        relsTarget = self.getRelationsForLayer(relations, source=oldLayerId)
        # relsSource = self.getRelationsForLayer(relations, target=oldLayerId)

        if len(relsTarget) > 0:
            for relDict in relsTarget:
                if relDict["referencingLayer"] in parentsLoop:
                    self.log(
                        "{} déjà référencée".format(relDict["referencingLayer"]),
                        indent=loop,
                    )

                    # La couche cible a déjà été ajoutée (boucle infinie)
                    # on se contente de référencer celle-ci
                    relDict["referencedLayer"] = newLayerId
                    relDict["referencingLayer"] = parentsLoop[
                        relDict["referencingLayer"]
                    ]
                    relationsToBuild.append(relDict)
                else:
                    # la couche cible n'a pas été ajoutée
                    parentsLoop.update({oldLayerId: newLayerId})

                    targetLayer, targetRelations = self.addLayer(
                        uri,
                        doc,
                        relDict["referencingLayer"],
                        group,
                        False,
                        False,
                        parentsLoop,
                        loop + 1,
                    )
                    if targetLayer is not None:
                        relDict["referencedLayer"] = newLayerId
                        relDict["referencingLayer"] = targetLayer.id()
                        relationsToBuild.append(relDict)

        return targetRelations + relationsToBuild

    def loadLayer(self, uri, fileName, layerId, menu=None, visible=None, expanded=None):
        """Load the chosen layer(s)

        :param uri: The layer URI (file path or PG URI)
        :type uri: basestring

        :param layerId: The layer ID to look for in the project.
        :type layerId: basestring

        """
        self.canvas.freeze(True)
        self.canvas.setRenderFlag(False)
        group = None
        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        self.mapLayerIds = {}

        try:
            if (
                isinstance(menu.parentWidget(), (QMenu, QWidget))
                and self.optionCreateGroup
            ):
                groupName = menu.title().replace("&", "")
                group = QgsProject.instance().layerTreeRoot().findGroup(groupName)
                if group is None:
                    group = (
                        QgsProject.instance().layerTreeRoot().insertGroup(0, groupName)
                    )

            # load all layers
            if fileName is None and layerId is None and self.optionLoadAll:
                for action in menu.actions()[::-1]:
                    if (
                        action.text() != self.tr("Load all")
                        and action.text() != "Load all"
                    ):
                        action.trigger()
            else:
                doc, _ = self.getQgsDoc(fileName)

                # Loading layer
                layer, relationsToBuild = self.addLayer(
                    uri, doc, layerId, group, visible, expanded, {}, 0
                )
                for relDict in relationsToBuild:
                    self.buildProjectRelation(doc, relDict)

                # is joined layers exists ?
                if self.optionOpenLinks and layer and type(layer) == QgsVectorLayer:
                    for j in layer.vectorJoins():
                        try:
                            joinLayer, joinRelations = self.addLayer(
                                uri, doc, j.joinLayerId(), group
                            )
                            for relDict in joinRelations:
                                self.buildProjectRelation(doc, relDict)

                            if joinLayer:
                                j.setJoinLayerId(joinLayer.id())
                                j.setJoinLayer(joinLayer)
                                layer.addJoin(j)
                        except Exception as e:
                            self.log(
                                "Joined layer {} not added.".format(j.joinLayerId())
                            )
                            pass

        except Exception as e:
            # fixme fileName is not defined
            # self.log(
            #     'Menu from layer: Invalid ' + (fileName if fileName is not None else ""))
            for m in e.args:
                self.log(m)

        finally:
            self.canvas.freeze(False)
            self.canvas.setRenderFlag(True)
            self.canvas.refresh()
            QgsApplication.restoreOverrideCursor()
