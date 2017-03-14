# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_atlashelp.ui'
#
# Created: Tue Jan 24 23:32:27 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from qgis.PyQt.QtCore import (QMetaObject, Qt)
#from qgis.PyQt.QtGui import *
#from PyQt5 import QtCore
from PyQt5 import QtWidgets
#from PyQt5.QtWebKitWidgets import QWebView


class Ui_browser(object):
    def setupUi(self, featureInfo):
        featureInfo.setObjectName("Help")
        featureInfo.resize(800, 650)
        self.verticalLayout = QtWidgets.QVBoxLayout(featureInfo)
        self.verticalLayout.setObjectName("verticalLayout")
        self.helpContent = QtWidgets.QLabel("TODO") #QWebView(featureInfo)
        self.helpContent.setObjectName("featureInfoContent")
        self.verticalLayout.addWidget(self.helpContent)
        self.buttonBox = QtWidgets.QDialogButtonBox(featureInfo)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(featureInfo)
        QMetaObject.connectSlotsByName(featureInfo)

    def retranslateUi(self, w):
        w.setWindowTitle("Help")

