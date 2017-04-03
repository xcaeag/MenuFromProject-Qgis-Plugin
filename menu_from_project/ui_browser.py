# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import (QMetaObject, Qt)
from PyQt5 import QtWidgets


class Ui_browser(object):
    def setupUi(self, featureInfo):
        featureInfo.setObjectName("Help")
        featureInfo.resize(800, 650)
        self.verticalLayout = QtWidgets.QVBoxLayout(featureInfo)
        self.verticalLayout.setObjectName("verticalLayout")
        self.helpContent = QtWidgets.QWebView(featureInfo)
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
