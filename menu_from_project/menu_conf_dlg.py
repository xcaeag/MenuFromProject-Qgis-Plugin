"""
Dialog for setting up the plugin.
"""

from os.path import join, dirname

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QRect
from qgis.PyQt.QtWidgets import (
    QHeaderView,
    QApplication,
    QTableWidgetItem,
    QToolButton,
    QLineEdit,
    QDialog,
    QFileDialog,
    QComboBox,
)

FORM_CLASS, _ = uic.loadUiType(join(dirname(__file__), "conf_dialog.ui"))


class MenuConfDialog(QDialog, FORM_CLASS):
    def __init__(self, parent, plugin):
        self.plugin = plugin
        self.parent = parent
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.defaultcursor = self.cursor

        self.LOCATIONS = {
            "new": {
                "index": 0,
                "label": QApplication.translate("ConfDialog", "New menu", None),
            },
            "layer": {
                "index": 1,
                "label": QApplication.translate("ConfDialog", "Add layer menu", None),
            },
            "merge": {
                "index": 2,
                "label": QApplication.translate(
                    "ConfDialog", "Merge with previous", None
                ),
            },
        }

        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.tableWidget.setRowCount(len(self.plugin.projects))
        self.buttonBox.accepted.connect(self.onAccepted)
        self.btnAdd.clicked.connect(self.onAdd)
        self.btnDelete.clicked.connect(self.onDelete)
        self.btnUp.clicked.connect(self.onMoveUp)
        self.btnDown.clicked.connect(self.onMoveDown)

        for idx, project in enumerate(self.plugin.projects):
            pushButton = QToolButton(self.parent)
            pushButton.setGeometry(QRect(0, 0, 20, 20))
            pushButton.setObjectName("x")
            pushButton.setText("...")

            itemName = QTableWidgetItem(project["name"])
            itemName.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tableWidget.setItem(idx, 2, itemName)

            itemFile = QTableWidgetItem(project["file"])
            itemFile.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tableWidget.setItem(idx, 1, itemFile)

            # button
            self.tableWidget.setCellWidget(idx, 0, pushButton)

            # uri
            le = QLineEdit()
            le.setText(project["file"])
            try:
                le.setStyleSheet(
                    "color: {};".format("black" if project["valid"] else "red")
                )
            except Exception:
                le.setStyleSheet("color: {};".format("black"))

            self.tableWidget.setCellWidget(idx, 1, le)
            le.textChanged.connect(self.onTextChanged)

            # name
            le = QLineEdit()
            le.setText(project["name"])
            le.setPlaceholderText(self.tr("Use project title"))
            self.tableWidget.setCellWidget(idx, 2, le)

            # location
            location_combo = QComboBox()
            for pk in self.LOCATIONS:
                if not (pk == "merge" and idx == 0):
                    location_combo.addItem(self.LOCATIONS[pk]["label"], pk)

            try:
                location_combo.setCurrentIndex(
                    self.LOCATIONS[project["location"]]["index"]
                )
            except Exception:
                location_combo.setCurrentIndex(0)
            self.tableWidget.setCellWidget(idx, 3, location_combo)

            # checkbox 'merge with previous'
            # cb = QCheckBox(self.parent)
            # cb.setChecked(False)
            # self.tableWidget.setCellWidget(idx, 4, cb)

            # helper = lambda _idx: (lambda: self.onFileSearchPressed(_idx))
            pushButton.clicked.connect(
                lambda checked, idx=idx: self.onFileSearchPressed(idx)
            )

        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.tableWidget.horizontalHeader().resizeSection(0, 20)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Interactive
        )
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.Interactive
        )

        self.cbxLoadAll.setChecked(self.plugin.optionLoadAll)
        self.cbxLoadAll.setTristate(False)

        self.cbxCreateGroup.setCheckState(self.plugin.optionCreateGroup)
        self.cbxCreateGroup.setTristate(False)

        self.cbxShowTooltip.setCheckState(self.plugin.optionTooltip)
        self.cbxShowTooltip.setTristate(False)

    def onFileSearchPressed(self, row):
        item = self.tableWidget.item(row, 1)

        filePath = QFileDialog.getOpenFileName(
            self,
            QApplication.translate("menu_from_project", "Projects configuration", None),
            item.text(),
            QApplication.translate(
                "menu_from_project", "QGIS projects (*.qgs *.qgz)", None
            ),
        )

        if filePath:
            try:
                file_widget = self.tableWidget.cellWidget(row, 1)
                file_widget.setText(filePath[0])

                name_widget = self.tableWidget.cellWidget(row, 2)
                name = name_widget.text()
                if not name:
                    try:
                        name = filePath[0].split("/")[-1]
                        name = name.split(".")[0]
                    except Exception:
                        name = ""

                    name_widget.setText(name)

            except Exception:
                pass

    def onAccepted(self):
        self.plugin.projects = []
        # self.plugin.log("count : {}".format(self.tableWidget.rowCount()))
        for row in range(self.tableWidget.rowCount()):
            file_widget = self.tableWidget.cellWidget(row, 1)
            # self.plugin.log("row : {}".format(row))
            if file_widget and file_widget.text():
                # self.plugin.log("row {} : {}".format(row, file_widget.text()))

                name_widget = self.tableWidget.cellWidget(row, 2)
                name = name_widget.text()
                filename = file_widget.text()

                location_widget = self.tableWidget.cellWidget(row, 3)
                location = location_widget.itemData(location_widget.currentIndex())

                self.plugin.projects.append(
                    {"file": filename, "name": name, "location": location}
                )

        self.plugin.optionTooltip = self.cbxShowTooltip.isChecked()
        self.plugin.optionLoadAll = self.cbxLoadAll.isChecked()
        self.plugin.optionCreateGroup = self.cbxCreateGroup.isChecked()

        self.plugin.store()

    def onAdd(self):
        row = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(row + 1)

        pushButton = QToolButton(self.parent)
        pushButton.setGeometry(QRect(0, 0, 20, 20))
        pushButton.setObjectName("x")
        pushButton.setText("...")

        itemName = QTableWidgetItem()
        itemName.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.tableWidget.setItem(row, 2, itemName)

        itemFile = QTableWidgetItem()
        itemFile.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.tableWidget.setItem(row, 1, itemFile)

        self.tableWidget.setCellWidget(row, 0, pushButton)

        filepath_lineedit = QLineEdit()
        filepath_lineedit.textChanged.connect(self.onTextChanged)
        self.tableWidget.setCellWidget(row, 1, filepath_lineedit)

        name_lineedit = QLineEdit()
        name_lineedit.setPlaceholderText(self.tr("Use project title"))
        self.tableWidget.setCellWidget(row, 2, name_lineedit)

        location_combo = QComboBox()
        for pk in self.LOCATIONS:
            if not (pk == "merge" and row == 0):
                location_combo.addItem(self.LOCATIONS[pk]["label"], pk)

        location_combo.setCurrentIndex(0)
        self.tableWidget.setCellWidget(row, 3, location_combo)

        pushButton.clicked.connect(
            lambda checked, row=row: self.onFileSearchPressed(row)
        )

    def onDelete(self):
        sr = self.tableWidget.selectedRanges()
        try:
            self.tableWidget.removeRow(sr[0].topRow())
        except Exception:
            pass

    def onMoveUp(self):
        sr = self.tableWidget.selectedRanges()
        try:
            r = sr[0].topRow()
            if r > 0:
                fileA = self.tableWidget.cellWidget(r - 1, 1).text()
                fileB = self.tableWidget.cellWidget(r, 1).text()
                self.tableWidget.cellWidget(r - 1, 1).setText(fileB)
                self.tableWidget.cellWidget(r, 1).setText(fileA)

                nameA = self.tableWidget.cellWidget(r - 1, 2).text()
                nameB = self.tableWidget.cellWidget(r, 2).text()
                self.tableWidget.cellWidget(r - 1, 2).setText(nameB)
                self.tableWidget.cellWidget(r, 2).setText(nameA)

                locA = self.tableWidget.cellWidget(r - 1, 3).currentIndex()
                locB = self.tableWidget.cellWidget(r, 3).currentIndex()
                if locB == 2 and r == 1:
                    locB = 0
                self.tableWidget.cellWidget(r - 1, 3).setCurrentIndex(locB)
                self.tableWidget.cellWidget(r, 3).setCurrentIndex(locA)

                self.tableWidget.setCurrentCell(r - 1, 1)
        except Exception:
            pass

    def onMoveDown(self):
        sr = self.tableWidget.selectedRanges()
        nbRows = self.tableWidget.rowCount()
        try:
            r = sr[0].topRow()
            if r < nbRows - 1:
                fileA = self.tableWidget.cellWidget(r, 1).text()
                fileB = self.tableWidget.cellWidget(r + 1, 1).text()
                self.tableWidget.cellWidget(r, 1).setText(fileB)
                self.tableWidget.cellWidget(r + 1, 1).setText(fileA)

                nameA = self.tableWidget.cellWidget(r, 2).text()
                nameB = self.tableWidget.cellWidget(r + 1, 2).text()
                self.tableWidget.cellWidget(r, 2).setText(nameB)
                self.tableWidget.cellWidget(r + 1, 2).setText(nameA)

                locA = self.tableWidget.cellWidget(r, 3).currentIndex()
                locB = self.tableWidget.cellWidget(r + 1, 3).currentIndex()
                if locB == 2 and r == 0:
                    locB = 0
                self.tableWidget.cellWidget(r, 3).setCurrentIndex(locB)
                self.tableWidget.cellWidget(r + 1, 3).setCurrentIndex(locA)

                self.tableWidget.setCurrentCell(r + 1, 1)
        except Exception:
            pass

    def onTextChanged(self, text):
        file_widget = self.sender()
        try:
            self.plugin.getQgsDoc(text)
            file_widget.setStyleSheet("color: {};".format("black"))
        except Exception:
            file_widget.setStyleSheet("color: {};".format("red"))
            pass
