# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name            : menu_from_project plugin
Description          : Build layers shortcut menu based on QGis project
Date                 :  10/11/2011
copyright            : (C) 2011 by AEAG
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

# Import the PyQt and QGIS libraries
import zipfile
import os
from qgis.core import (QgsMessageLog, QgsApplication, QgsProject,
    QgsVectorLayer, QgsRasterLayer, QgsReadWriteContext)

from qgis.PyQt.QtCore import (QTranslator, QFile, QFileInfo, QSettings,
                              QCoreApplication, QIODevice, Qt, QUuid,
                              QTemporaryFile, QTemporaryDir, QDir)
from qgis.PyQt.QtGui import (QFont)
from qgis.PyQt.QtWidgets import (QWidget, QMenu, QAction)

from qgis.PyQt import QtXml
import webbrowser

from .menu_conf_dlg import menu_conf_dlg


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
        if node.toElement().hasAttribute(key) and \
                node.toElement().attribute(key) == value:
            # layer founds
            return node

    return None


def getMapLayerDomFromQgs(fileName, layerId):
    doc = QtXml.QDomDocument()
    xml = QFile(fileName)
    if xml.open(QIODevice.ReadOnly | QIODevice.Text):
        doc.setContent(xml)

    return getFirstChildByTagNameValue(doc.documentElement(), "maplayer", "id", layerId)


def getMapLayersDict(domdoc):
    r = {}
    nodes = domdoc.documentElement().elementsByTagName("maplayer")
    for node in (nodes.at(i) for i in range(nodes.size())):
        nd = node.namedItem("id")
        if nd:
            r[nd.firstChild().toText().data()] = node

    return r


class menu_from_project:

    def __init__(self, iface):
        self.path = QFileInfo(os.path.realpath(__file__)).path()
        self.iface = iface
        self.toolBar = None
        self.project_registry = QgsApplication.projectStorageRegistry()

        # new multi projects var
        self.projects = []
        self.menubarActions = []
        self.canvas = self.iface.mapCanvas()
        self.optionTooltip = False
        self.optionCreateGroup = False
        self.optionLoadAll = False
        self.read()
        # default lang
        locale = QSettings().value("locale/userLocale")
        self.myLocale = locale[0:2]
        # dictionnary
        localePath = self.path+"/i18n/menu_from_project_" + self.myLocale + \
            ".qm"
        # translator
        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)
            QCoreApplication.installTranslator(self.translator)

    def tr(self, message):
        return QCoreApplication.translate('menu_from_project', message)

    def store(self):
        s = QSettings()
        s.remove("menu_from_project/projectFilePath")

        s.setValue("menu_from_project/optionTooltip", self.optionTooltip)
        s.setValue("menu_from_project/optionCreateGroup", self.optionCreateGroup)
        s.setValue("menu_from_project/optionLoadAll", self.optionLoadAll)

        s.beginWriteArray("menu_from_project/projects")
        for i, project in enumerate(self.projects):
            s.setArrayIndex(i)
            s.setValue("file", project["file"])
            s.setValue("name", project["name"])

        s.endArray()

    def read(self):
        s = QSettings()
        try:
            # old single project conf
            filePath = s.value("menu_from_project/projectFilePath", "")

            if filePath:
                title = filePath.split('/')[-1]
                title = title.split('.')[0]
                self.projects.append({"file": filePath, "name": title})
                self.store()
            else:
                # patch : lecture ancienne conf
                size = s.beginReadArray("projects")
                for i in range(size):
                    s.setArrayIndex(i)
                    file = ((s.value("file").toString()))
                    name = ((s.value("name").toString()))
                    if file:
                        self.projects.append({"file": file, "name": name})
                s.endArray()

                size = s.beginReadArray("menu_from_project/projects")
                for i in range(size):
                    s.setArrayIndex(i)
                    file = s.value("file", "")
                    name = s.value("name", "")
                    if file != "":
                        self.projects.append({"file": file, "name": name})

                s.endArray()

            self.optionTooltip = s.value("menu_from_project/optionTooltip",
                                         True, type=bool)

            # create group option only since 1.9
            self.optionCreateGroup = s.value("menu_from_project/optionCreateGroup",
                                             False, type=bool)
            self.optionLoadAll = s.value("menu_from_project/optionLoadAll", False, type=bool)

        except:
            pass

    def isAbsolute(self, doc):
        absolute = False
        try:
            props = doc.elementsByTagName("properties")
            if props.count() == 1:
                node = props.at(0)
                pathNode = node.namedItem("Paths")
                absNode = pathNode.namedItem("Absolute")
                absolute = ("true" == absNode.firstChild().toText().data())
        except:
            pass

        return absolute

    def addToolTip(self, ml, action):
        if ml is not None:
            try:
                title = ml.namedItem("title").firstChild().toText().data()
                abstract = ml.namedItem("abstract").firstChild().toText().data()

                action.setStatusTip(title)
                if (abstract != "") and (title == ""):
                    action.setToolTip("<p>%s</p>" % ("<br/>".join(abstract.split("\n"))))
                else:
                    if abstract != "" or title != "":
                        action.setToolTip(
                            "<b>%s</b><br/>%s" % (title, "<br/>".join(abstract.split("\n"))))
                    else:
                        action.setToolTip("")
            except:
                pass

    def addMenuItem(self, filename, node, menu, domdoc, mapLayersDict):
        yaLayer = False
        initialFilename = filename
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
                embedNd = getFirstChildByAttrValue(element, "property", "key", "embedded")

                # is layer embedded ?
                if embedNd and embedNd.toElement().attribute("value") == "1":
                    # layer is embeded
                    efilename = None
                    eFileNd = getFirstChildByAttrValue(element, "property", "key",
                                                       "embedded_project")

                    # get project file name
                    embeddedFile = eFileNd.toElement().attribute("value")
                    if not self.absolute and (embeddedFile.find(".") == 0):
                        efilename = self.projectpath + "/" + embeddedFile

                    # if ok
                    if efilename:
                        # add menu item
                        action.triggered.connect(
                            lambda checked,
                            f=efilename,
                            lid=layerId,
                            m=menu,
                            v=visible,
                            x=expanded:self.do_aeag_menu(f, lid, m, v, x))

                        menu.addAction(action)
                        yaLayer = True

                        if self.optionTooltip:
                            # search embeded maplayer (for title, abstract)
                            mapLayer = getMapLayerDomFromQgs(efilename,
                                                             layerId)
                            if mapLayer is not None:
                                self.addToolTip(mapLayer, action)
                            else:
                                QgsMessageLog.logMessage(
                                    "Menu from layer: " + layerId +
                                    " not found in project " + efilename,
                                    'Extensions')

                # layer is not embedded
                else:
                    if self.optionTooltip:
                        self.addToolTip(mapLayersDict[layerId], action)

                    action.triggered.connect(
                        lambda checked,
                        f=filename,
                        lid=layerId,
                        m=menu,
                        v=visible,
                        x=expanded: self.do_aeag_menu(f, lid, m, v, x))

                    menu.addAction(action)
                    yaLayer = True
            except Exception as e:
                for m in e.args:
                    QgsMessageLog.logMessage(m, 'Extensions')

        # / if element.tagName() == "layer-tree-layer":

        # if legendgroup tag
        if node.nodeName() == "layer-tree-group":
            name = element.attribute("name")
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
                sousmenu = menu.addMenu('&'+element.attribute("name"))
                sousmenu.menuAction().setToolTip("")
                sousmenu.setToolTipsVisible(self.optionTooltip)

                childNode = node.firstChild()

                #  ! recursion
                r = self.addMenuItem(initialFilename, childNode, sousmenu, domdoc, mapLayersDict)

                if r and self.optionLoadAll and (len(sousmenu.actions()) > 1):
                    action = QAction(self.tr("Load all"), self.iface.mainWindow())
                    font = QFont()
                    font.setBold(True)
                    action.setFont(font)
                    sousmenu.addAction(action)
                    action.triggered.connect(
                        lambda checked,
                        f=None,
                        w=None,
                        m=sousmenu: self.do_aeag_menu(f, w, m))

        # / if element.tagName() == "legendgroup":

        nextNode = node.nextSibling()
        if nextNode is not None:
            # ! recursion
            r = self.addMenuItem(initialFilename, nextNode, menu, domdoc, mapLayersDict)
            yaLayer = yaLayer or r

        return yaLayer

    def addMenu(self, name, filename, domdoc):
        # main project menu
        menuBar = self.iface.addLayerMenu()
        projectMenu = QMenu('&'+name, menuBar)

        projectMenu.setToolTipsVisible(self.optionTooltip)

        projectAction = menuBar.addMenu(projectMenu)
        self.menubarActions.append(projectAction)

        self.absolute = self.isAbsolute(domdoc)
        self.projectpath = QFileInfo(os.path.realpath(filename)).path()

        mapLayersDict = getMapLayersDict(domdoc)

        # build menu on legend schema
        legends = domdoc.elementsByTagName("layer-tree-group")
        if legends.length() > 0:
            node = legends.item(0)
            if node:
                node = node.firstChild()
                self.addMenuItem(filename, node, projectMenu, domdoc, mapLayersDict)

    def getQgsDoc(self, uri):
        #QgsMessageLog.logMessage(uri, 'Extensions')

        doc = QtXml.QDomDocument()
        file = QFile(uri)
        # file on disk
        if file.exists() and file.open(QIODevice.ReadOnly | QIODevice.Text):
            doc.setContent(file)
            project_path = uri
        else:
            # uri PG
            project_storage = self.project_registry.projectStorageFromUri(uri)

            temporary_zip = QTemporaryFile()
            temporary_zip.open()
            zip_project = temporary_zip.fileName()

            project_storage.readProject(uri, temporary_zip, QgsReadWriteContext())

            temporary_unzip = QTemporaryDir()
            with zipfile.ZipFile(zip_project, "r") as zip_ref:
                zip_ref.extractall(temporary_unzip.path())

            project_filename = QDir(temporary_unzip.path()).entryList(['*.qgs'])[0]
            project_path = os.path.join(temporary_unzip.path(), project_filename)
            xml = QFile(project_path)
            if xml.open(QIODevice.ReadOnly | QIODevice.Text):
                doc.setContent(xml)

        return (doc, project_path)

    def initMenus(self):
        menuBar = self.iface.addLayerMenu()
        for action in self.menubarActions:
            menuBar.removeAction(action)
            del action

        self.menubarActions = []

        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        for project in self.projects:
            try:
                uri = project["file"]
                doc, path = self.getQgsDoc(uri)
                self.addMenu(project["name"], path, doc)
            except Exception as e:
                QgsMessageLog.logMessage(
                    'Menu from layer: Invalid {}'.format(uri), 'Extensions')
                for m in e.args:
                    QgsMessageLog.logMessage(m, 'Extensions')

        QgsApplication.restoreOverrideCursor()

    def initGui(self):
        self.act_aeag_menu_config = QAction(
            self.tr("Projects configuration")+"...", self.iface.mainWindow())

        self.iface.addPluginToMenu(
            self.tr("&Layers menu from project"), self.act_aeag_menu_config)
        # Add actions to the toolbar
        self.act_aeag_menu_config.triggered.connect(self.do_aeag_menu_config)

        self.act_aeag_menu_help = QAction(self.tr("Help") + "...", self.iface.mainWindow())
        self.iface.addPluginToMenu(self.tr("&Layers menu from project"), self.act_aeag_menu_help)
        self.act_aeag_menu_help.triggered.connect(self.do_help)

        # build menu
        self.initMenus()

    def unload(self):
        menuBar = self.iface.addLayerMenu()
        for action in self.menubarActions:
            menuBar.removeAction(action)

        self.iface.removePluginMenu(self.tr("&Layers menu from project"),
                                    self.act_aeag_menu_config)
        self.iface.removePluginMenu(self.tr("&Layers menu from project"),
                                    self.act_aeag_menu_help)
        self.act_aeag_menu_config.triggered.disconnect(self.do_aeag_menu_config)
        self.act_aeag_menu_help.triggered.disconnect(self.do_help)

        self.store()

    def do_aeag_menu_config(self):
        dlg = menu_conf_dlg(self.iface.mainWindow(), self)
        dlg.setModal(True)

        dlg.show()
        result = dlg.exec_()
        del dlg

        if result != 0:
            self.initMenus()

    # run method that performs all the real work
    def do_aeag_menu(self, uri, who, menu=None, visible=None, expanded=None):
        self.canvas.freeze(True)
        self.canvas.setRenderFlag(False)
        group = None
        theLayer = None
        groupName = None
        QgsApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            if (type(menu.parentWidget()) == QMenu or type(menu.parentWidget()) == QWidget) and self.optionCreateGroup:
                groupName = menu.title().replace("&", "")
                group = QgsProject.instance().layerTreeRoot().findGroup(groupName)
                if group is None:
                    group = QgsProject.instance().layerTreeRoot().addGroup(groupName)

            # load all layers
            if uri is None and who is None and self.optionLoadAll:
                for action in menu.actions():
                    if ((action.text() != self.tr("&Load all")) and (action.text() != "Load all")):
                        action.trigger()
            else:
                # read QGis project
                doc, path = self.getQgsDoc(uri)

                # is project in relative path ?
                absolute = self.isAbsolute(doc)

                node = getFirstChildByTagNameValue(doc.documentElement(), "maplayer", "id", who)
                if node:
                    idNode = node.namedItem("id")
                    layerType = node.toElement().attribute("type", "vector")
                    # give it a new id (for multiple import)
                    import re
                    newLayerId = "L%s" % re.sub("[{}-]", "", QUuid.createUuid().toString())
                    try:
                        idNode.firstChild().toText().setData(newLayerId)
                    except:
                        pass

                    # if relative path, adapt datasource
                    if not absolute:
                        try:
                            datasourceNode = node.namedItem("datasource")
                            ds = datasourceNode.firstChild().toText().data()
                            providerNode = node.namedItem("provider")
                            provider = providerNode.firstChild().toText().data()

                            if provider == "ogr" and (ds.find(".") == 0):
                                projectpath = QFileInfo(os.path.realpath(fileName)).path()
                                newlayerpath = projectpath + "/" + ds
                                datasourceNode.firstChild().toText().setData(newlayerpath)
                        except:
                            pass


                    # read modified layer node
                    if self.optionCreateGroup and group is not None:
                        """# sol 1 bug : layer incomplete
                        # because of API strange behaviour, we clone the layer... 
                        theLayer = QgsProject.instance().mapLayer(newLayerId)
                        cloneLayer = theLayer.clone()
                        # removing the first
                        QgsProject.instance().removeMapLayer(newLayerId)
                        # adding the clone...
                        treeNode = group.addLayer(cloneLayer)
                        treeNode.setExpanded(expanded)
                        treeNode.setItemVisibilityChecked(visible)"""

                        # solution 2, ok !
                        if layerType == "raster":
                            theLayer = QgsRasterLayer()
                        else:
                            theLayer = QgsVectorLayer()

                        theLayer.readLayerXml(node.toElement(), QgsReadWriteContext())
                        # needed
                        QgsProject.instance().addMapLayer(theLayer, False)
                        # add to group
                        treeNode = group.addLayer(theLayer)
                        treeNode.setExpanded(expanded)
                        treeNode.setItemVisibilityChecked(visible)
                    else:
                        # create layer
                        QgsProject.instance().readLayer(node)

        except Exception as e:
            QgsMessageLog.logMessage(
                'Menu from layer: Invalid ' + (fileName if fileName is not None else ""),
                'Extensions')
            for m in e.args:
                QgsMessageLog.logMessage(m, 'Extensions')

        self.canvas.freeze(False)
        self.canvas.setRenderFlag(True)
        self.canvas.refresh()
        QgsApplication.restoreOverrideCursor()

    def do_help(self):
        try:
            if os.path.isfile(self.path+"/help_"+self.myLocale+".html"):
                webbrowser.open(self.path+"/help_"+self.myLocale+".html")
            else:
                webbrowser.open(self.path+"/help.html")

        except Exception as e:
            for m in e.args:
                QgsMessageLog.logMessage(m, 'Extensions')
