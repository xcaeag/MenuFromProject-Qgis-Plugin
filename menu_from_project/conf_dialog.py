# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'W:\projets\QGis plugins\menu_from_project\conf_dialog.ui'
#
# Created: Tue Feb 19 16:47:11 2013
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

_fromUtf8 = lambda s: (s.decode("utf-8").encode("latin-1")) if s else s
_toUtf8 = lambda s: s.decode("latin-1").encode("utf-8") if s else s

class Ui_ConfDialog(object):
    def setupUi(self, ConfDialog):
        ConfDialog.setObjectName(_fromUtf8("ConfDialog"))
        ConfDialog.setWindowModality(QtCore.Qt.WindowModal)
        ConfDialog.resize(640, 224)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ConfDialog.sizePolicy().hasHeightForWidth())
        ConfDialog.setSizePolicy(sizePolicy)
        ConfDialog.setMinimumSize(QtCore.QSize(540, 150))
        ConfDialog.setSizeGripEnabled(True)
        self.verticalLayout_2 = QtGui.QVBoxLayout(ConfDialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tableWidget = QtGui.QTableWidget(ConfDialog)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setTextElideMode(QtCore.Qt.ElideNone)
        self.tableWidget.setRowCount(2)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(2)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.verticalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setDefaultSectionSize(17)
        self.verticalLayout_2.addWidget(self.tableWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnAdd = QtGui.QToolButton(ConfDialog)
        self.btnAdd.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.btnAdd.setObjectName(_fromUtf8("btnAdd"))
        self.horizontalLayout.addWidget(self.btnAdd)
        self.btnDelete = QtGui.QToolButton(ConfDialog)
        self.btnDelete.setObjectName(_fromUtf8("btnDelete"))
        self.horizontalLayout.addWidget(self.btnDelete)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.cbxShowTooltip = QtGui.QCheckBox(ConfDialog)
        self.cbxShowTooltip.setChecked(True)
        self.cbxShowTooltip.setTristate(False)
        self.cbxShowTooltip.setObjectName(_fromUtf8("cbxShowTooltip"))
        self.horizontalLayout_2.addWidget(self.cbxShowTooltip)
        self.cbxLoadAll = QtGui.QCheckBox(ConfDialog)
        self.cbxLoadAll.setTristate(False)
        self.cbxLoadAll.setObjectName(_fromUtf8("cbxLoadAll"))
        self.horizontalLayout_2.addWidget(self.cbxLoadAll)
        self.cbxCreateGroup = QtGui.QCheckBox(ConfDialog)
        self.cbxCreateGroup.setChecked(False)
        self.cbxCreateGroup.setTristate(False)
        self.cbxCreateGroup.setObjectName(_fromUtf8("cbxCreateGroup"))
        self.horizontalLayout_2.addWidget(self.cbxCreateGroup)
        
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(ConfDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(ConfDialog)
        self.buttonBox.accepted.connect(ConfDialog.accept)
        self.buttonBox.rejected.connect(ConfDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConfDialog)

    def retranslateUi(self, ConfDialog):
        ConfDialog.setWindowTitle(QtGui.QApplication.translate("ConfDialog", "Projects", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("ConfDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("ConfDialog", "QGis Project", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("ConfDialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("ConfDialog", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelete.setText(QtGui.QApplication.translate("ConfDialog", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.cbxShowTooltip.setText(QtGui.QApplication.translate("ConfDialog", "Show title && abstract in tooltip", None, QtGui.QApplication.UnicodeUTF8))
        self.cbxLoadAll.setText(QtGui.QApplication.translate("ConfDialog", "Load all layers item", None, QtGui.QApplication.UnicodeUTF8))
        self.cbxCreateGroup.setText(QtGui.QApplication.translate("ConfDialog", "Create group", None, QtGui.QApplication.UnicodeUTF8))

