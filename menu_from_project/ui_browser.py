# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_atlashelp.ui'
#
# Created: Tue Jan 24 23:32:27 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from PyQt5 import QtCore
from PyQt5 import QtWidgets
#from PyQt5.QtWebKitWidgets import QWebView

_fromUtf8 = lambda s: str(s)
_toUtf8 = lambda s: str(s)


class Ui_browser(object):
    def setupUi(self, featureInfo):
        featureInfo.setObjectName(_fromUtf8("Help"))
        featureInfo.resize(800, 650)
        self.verticalLayout = QtWidgets.QVBoxLayout(featureInfo)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.helpContent = QtWidgets.QLabel("TODO") #QWebView(featureInfo)
        self.helpContent.setObjectName(_fromUtf8("featureInfoContent"))
        self.verticalLayout.addWidget(self.helpContent)
        self.buttonBox = QtWidgets.QDialogButtonBox(featureInfo)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(featureInfo)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), featureInfo.accept)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), featureInfo.reject)
        QtCore.QMetaObject.connectSlotsByName(featureInfo)

    def retranslateUi(self, w):
        w.setWindowTitle("Help")

