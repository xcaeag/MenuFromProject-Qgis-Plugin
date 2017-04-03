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
import os
from qgis.core import (QgsMessageLog, QgsApplication, QgsProject)

from qgis.PyQt.QtCore import (QTranslator, QFile, QFileInfo, QSettings,
                              QCoreApplication, QIODevice, Qt, QUuid)
from qgis.PyQt.QtGui import (QFont)
from qgis.PyQt.QtWidgets import (QMenu, QAction, QApplication)

from qgis.PyQt import QtXml
import webbrowser

from .menu_conf_dlg import menu_conf_dlg

# Initialize Qt resources from file resources.py
from . import resources


def getFirstChildByTagNameValue(elt, tagName, key, value):
    nodes = elt.elementsByTagName(tagName)
    for node in (nodes.at(i) for i in range(nodes.size())):
        idNode = node.namedItem(key)
        if idNode and value == idNode.firstChild().toText().data():
            # layer founds
            return node

    return None


class menu_from_project:

    def __init__(self, iface):
        self.path = QFileInfo(os.path.realpath(__file__)).path()
        self.iface = iface
        self.toolBar = None

        # new multi projects var
        self.projects = []
        self.menubarActions = []
        self.canvas = self.iface.mapCanvas()
        self.optionTooltip = (False)
        self.optionCreateGroup = (False)
        self.optionLoadAll = (False)
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

    def store(self):
        s = QSettings()
        s.remove("menu_from_project/projectFilePath")

        s.setValue("menu_from_project/optionTooltip", self.optionTooltip)
        s.setValue("menu_from_project/optionCreateGroup",
                   self.optionCreateGroup)
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
            self.optionCreateGroup = s.value(
                "menu_from_project/optionCreateGroup", False, type=bool)
            self.optionLoadAll = s.value("menu_from_project/optionLoadAll",
                                         False, type=bool)

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

    def getMaplayerDomFromQgs(self, fileName, layerId):
        doc = QtXml.QDomDocument()
        xml = QFile(fileName)
        if (xml.open(QIODevice.ReadOnly | QIODevice.Text)):
            doc.setContent(xml)

        maplayers = doc.elementsByTagName("maplayer")
        for ml in (maplayers.item(i) for i in range(maplayers.size())):
            idelt = ml.namedItem("id")
            if idelt and layerId == idelt.firstChild().toText().data():
                return ml

        return None

    def addMenuLayerItem(self, ml, id, action, embeded):
        # embedded layers ?
        embeddedFile = ""
        if (embeded == "1"):
            try:
                embeddedFile = ml.toElement().attribute("project", "")
                # read embedded project
                if not self.absolute and (embeddedFile.find(".") == 0):
                    embeddedFile = self.projectpath + "/" + embeddedFile

                ml = self.getMaplayerDomFromQgs(embeddedFile, id)
            except:
                pass

        if ml is not None:
            try:
                title = ml.namedItem("title").firstChild().toText().data()
                abstract = ml.namedItem("abstract") \
                    .firstChild().toText().data()

                action.setStatusTip(title)
                if (abstract != "") and (title == ""):
                    action.setToolTip("<p>%s</p>" % ("<br/>".join(
                        abstract.split("\n"))))
                else:
                    if (abstract != "" or title != ""):
                        action.setToolTip(
                            "<b>%s</b><br/>%s" % (title,
                                                  "<br/>".join(
                                                      abstract.split("\n"))))
                    else:
                        action.setToolTip("")
            except:
                pass
        else:
            QgsMessageLog.logMessage(
                "Menu from layer: " + id +
                " not found in project " + embeddedFile, 'Extensions')

        return embeddedFile

    def addMenuItem(self, filename, node, menu, domdoc):
        yaLayer = False
        initialFilename = filename
        if node is None:
            return yaLayer

        element = node.toElement()

        # if legendlayer tag
        if node.nodeName() == "legendlayer":
            try:
                legendlayerfileElt = element.firstChild().firstChildElement(
                    "legendlayerfile")
                layerId = legendlayerfileElt.attribute("layerid")
                action = QAction(element.attribute("name"),
                                 self.iface.mainWindow())
                if (self.optionTooltip == (True)):
                    try:
                        maplayers = domdoc.elementsByTagName("maplayer")
                        for ml in (maplayers.item(i) for i in
                                   range(maplayers.size())):
                            idelt = ml.namedItem("id")
                            id = ""

                            if (idelt is not None):
                                id = idelt.firstChild().toText().data()

                            embeded = ml.toElement().attribute("embedded",
                                                               "0")
                            if (embeded == "1"):
                                id = ml.toElement().attribute("id", "")

                            if (id == layerId):
                                embed = self.addMenuLayerItem(ml, id,
                                                              action, embeded)
                                if embed:
                                    filename = embed

                                break
                    except:
                        pass

                menu.addAction(action)
                yaLayer = True
                # helper = lambda _filename,_who,_menu: (lambda: self.do_aeag_menu(_filename, _who, _menu))
                action.triggered.connect(lambda checked,
                                         f=filename,
                                         lid=layerId,
                                         m=menu: self.do_aeag_menu(f, lid, m))
            except:
                pass

            nextNode = node.nextSibling()
            if (nextNode is not None):
                # ! recursion
                self.addMenuItem(initialFilename, nextNode, menu, domdoc)
        # / if element.tagName() == "legendlayer":

        # if legendgroup tag
        if node.nodeName() == "legendgroup":
            name = element.attribute("name")
            if name == "-":
                menu.addSeparator()
                nextNode = node.nextSibling()
                if (nextNode is not None):
                    # ! recursion
                    self.addMenuItem(initialFilename, nextNode, menu, domdoc)

            elif name.startswith("-"):
                action = QAction(name[1:], self.iface.mainWindow())
                font = QFont()
                font.setBold(True)
                action.setFont(font)
                menu.addAction(action)

                nextNode = node.nextSibling()
                if (nextNode is not None):
                    # ! recursion
                    self.addMenuItem(initialFilename, nextNode, menu, domdoc)

            else:
                # sub-menu
                sousmenu = menu.addMenu('&'+element.attribute("name"))
                sousmenu.menuAction().setToolTip("")
                sousmenu.setToolTipsVisible(self.optionTooltip)

                childNode = node.firstChild()

                #  ! recursion
                r = self.addMenuItem(initialFilename, childNode,
                                     sousmenu, domdoc)

                if r and self.optionLoadAll and (len(sousmenu.actions()) > 1):
                    action = QAction(QApplication.translate(
                        "menu_from_project", "&Load all", None),
                        self.iface.mainWindow())
                    font = QFont()
                    font.setBold(True)
                    action.setFont(font)
                    sousmenu.addAction(action)
                    # helper = lambda _filename,_who,_menu: (lambda: self.do_aeag_menu(_filename, _who, _menu))
                    action.triggered.connect(
                        lambda checked,
                        f=None,
                        w=None,
                        m=sousmenu: self.do_aeag_menu(f, w, m))

                nextNode = node.nextSibling()
                if (nextNode is not None):
                    # ! recursion
                    self.addMenuItem(initialFilename, nextNode, menu, domdoc)
        # / if element.tagName() == "legendgroup":

        return yaLayer

    def addMenu(self, name, filename, domdoc):
        # main project menu
        menuBar = self.iface.editMenu().parentWidget()
        projectMenu = QMenu('&'+name, menuBar)

        projectMenu.setToolTipsVisible(self.optionTooltip)

        projectAction = menuBar.addMenu(projectMenu)
        self.menubarActions.append(projectAction)

        self.absolute = self.isAbsolute(domdoc)
        self.projectpath = QFileInfo(os.path.realpath(filename)).path()

        # build menu on legend schema
        legends = domdoc.elementsByTagName("legend")
        if (legends.length() > 0):
            node = legends.item(0)
            if node:
                node = node.firstChild()
                self.addMenuItem(filename, node, projectMenu, domdoc)

    def initMenus(self):
        menuBar = self.iface.editMenu().parentWidget()
        for action in self.menubarActions:
            menuBar.removeAction(action)
            del(action)

        self.menubarActions = []

        QgsApplication.setOverrideCursor(Qt.WaitCursor)
        for project in self.projects:
            QgsMessageLog.logMessage(
                'Menu from layer: Loading ' +
                project["file"] + ' in menu ' +
                project["name"] + '...', 'Extensions')
            try:
                doc = QtXml.QDomDocument()
                xml = QFile(project["file"])
                if (xml.open(QIODevice.ReadOnly | QIODevice.Text)):
                    doc.setContent(xml)

                self.addMenu(project["name"], project["file"], doc)
            except Exception as e:
                QgsMessageLog.logMessage(
                    'Menu from layer: Invalid {}'.format(project["file"]),
                    'Extensions')
                for m in e.args:
                    QgsMessageLog.logMessage(format(e), 'Extensions')

                pass

        QgsApplication.restoreOverrideCursor()

    def initGui(self):
        self.act_aeag_menu_config = QAction(
            QApplication.translate(
                "menu_from_project",
                "Projects configuration", None)+"...", self.iface.mainWindow())
        self.iface.addPluginToMenu(
            QApplication.translate(
                "menu_from_project",
                "&Layers menu from project", None), self.act_aeag_menu_config)
        # Add actions to the toolbar
        self.act_aeag_menu_config.triggered.connect(self.do_aeag_menu_config)

        self.act_aeag_menu_help = QAction(QApplication.translate(
            "menu_from_project", "Help", None)+"...", self.iface.mainWindow())
        self.iface.addPluginToMenu(QApplication.translate(
            "menu_from_project",
            "&Layers menu from project", None), self.act_aeag_menu_help)
        self.act_aeag_menu_help.triggered.connect(self.do_help)

        # build menu
        self.initMenus()

    def unload(self):
        menuBar = self.iface.editMenu().parentWidget()
        for action in self.menubarActions:
            menuBar.removeAction(action)

        self.iface.removePluginMenu(
            QApplication.translate(
                "menu_from_project",
                "&Layers menu from project", None), self.act_aeag_menu_config)
        self.iface.removePluginMenu(
            QApplication.translate(
                "menu_from_project",
                "&Layers menu from project", None), self.act_aeag_menu_help)
        self.act_aeag_menu_config.triggered.disconnect(
            self.do_aeag_menu_config)
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
    def do_aeag_menu(self, fileName, who, menu=None):
        self.canvas.freeze(True)
        self.canvas.setRenderFlag(False)
        group = None
        theLayer = None
        groupName = None
        QgsApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            if type(menu.parentWidget()) == QMenu and self.optionCreateGroup:
                groupName = menu.title().replace("&", "")

                group = QgsProject.instance().layerTreeRoot().findGroup(
                    groupName)

                if group is None:
                    group = QgsProject.instance().layerTreeRoot().addGroup(
                        groupName)

            # load all layers
            if fileName is None and who is None and self.optionLoadAll:
                for action in reversed(menu.actions()):
                    if action.text() != QApplication.translate(
                            "menu_from_project",
                            "&Load all",
                            None):
                        action.trigger()
            else:
                # read QGis project
                doc = QtXml.QDomDocument()
                xml = QFile(fileName)
                if (xml.open(QIODevice.ReadOnly | QIODevice.Text)):
                    doc.setContent(xml)

                # is project in relative path ?
                absolute = self.isAbsolute(doc)

                node = getFirstChildByTagNameValue(doc.documentElement(),
                                                   "maplayer", "id", who)
                if node:
                    idNode = node.namedItem("id")
                    # give it a new id (for multiple import)
                    try:
                        import re
                        newLayerId = "L%s" % re.sub(
                            "[{}-]",
                            "",
                            QUuid.createUuid().toString())
                        idNode.firstChild().toText().setData(newLayerId)
                    except:
                        pass

                    # if relative path, adapt datasource
                    if not absolute:
                        try:
                            datasourceNode = node.namedItem("datasource")
                            ds = datasourceNode.firstChild().toText().data()
                            providerNode = node.namedItem("provider")
                            provider = providerNode.firstChild() \
                                .toText().data()

                            if provider == "ogr" and (ds.find(".") == 0):
                                projectpath = QFileInfo(
                                    os.path.realpath(fileName)).path()
                                newlayerpath = projectpath + "/" + ds
                                datasourceNode.firstChild() \
                                    .toText().setData(newlayerpath)
                        except:
                            pass

                    # read modified layer node
                    QgsProject.instance().readLayer(node)

                    if self.optionCreateGroup:
                        theLayer = QgsProject.instance().mapLayer(newLayerId)
                        if group is not None and theLayer is not None:
                            group.addLayer(theLayer)

        except:
            QgsMessageLog.logMessage(
                'Menu from layer: Invalid ' +
                (fileName if fileName is not None else ""),
                'Extensions')
            pass

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
            pass
