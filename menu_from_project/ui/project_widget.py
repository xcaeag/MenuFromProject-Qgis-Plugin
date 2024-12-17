#! python3  # noqa: E265

# standard
import os

# PyQGIS
from qgis.core import QgsApplication, QgsMessageLog
from qgis.gui import QgsProviderGuiRegistry
from qgis.PyQt import QtCore, uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QFileDialog, QWidget
from qgis.utils import iface

# project
from menu_from_project.__about__ import __title__
from menu_from_project.datamodel.project import Project, ProjectCacheConfig
from menu_from_project.logic.cache_manager import CacheManager
from menu_from_project.logic.qgs_manager import QgsDomManager
from menu_from_project.logic.tools import icon_per_storage_type

# ############################################################################
# ########## Globals ###############
# ##################################


# ############################################################################
# ########## Classes ###############
# ##################################
class ProjectWidget(QWidget):
    """Widget to display project"""

    # Signal to indicate changes in project displayed
    projectChanged = QtCore.pyqtSignal()

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        uic.loadUi(
            os.path.dirname(os.path.realpath(__file__)) + "/project_widget.ui",
            self,
        )
        self.qgs_dom_manager = QgsDomManager()

        self.refreshIntervalSpinBox.setClearValue(-1, self.tr("None"))
        self.refreshIntervalSpinBox.setSuffix(self.tr(" days"))
        self.pathSelectionButton.clicked.connect(self._select_path)

        self.fileRatioButton.setIcon(QIcon(icon_per_storage_type("file")))
        self.postgresqlRadioButton.setIcon(QIcon(icon_per_storage_type("database")))
        self.urlRadioButton.setIcon(QIcon(icon_per_storage_type("http")))

        self.clearCacheButton.setIcon(
            QIcon(":images/themes/default/console/iconClearConsole.svg")
        )
        self.clearCacheButton.setToolTip(self.tr("Delete cache for this project"))

        self.validationFileLineEdit.setFilter("*.json")

        self.clearCacheButton.clicked.connect(self._delete_project_cache)

        self.mergePreviousCheckBox.clicked.connect(self._merge_location_changed)

        self._emit_changed_signal = True
        self._connect_update_signal()

    def enable_merge_option(self, enable: bool) -> None:
        """Enable merge option for project configuration

        :param enable: enable merge
        :type enable: bool
        """
        self._emit_changed_signal = False
        self.mergePreviousCheckBox.setEnabled(enable)
        if not enable:
            self.mergePreviousCheckBox.setToolTip(
                self.tr("Project in first position, no project to merge.")
            )
            self.mergePreviousCheckBox.setChecked(False)
        else:
            self.mergePreviousCheckBox.setToolTip("")
        self._emit_changed_signal = True

    def _merge_location_changed(self) -> None:
        """Disable other options if merge location is checked"""
        self.newMenuCheckBox.clicked.disconnect(self._project_changed)
        self.addLayerMenuCheckBox.clicked.disconnect(self._project_changed)
        if self.mergePreviousCheckBox.isChecked():
            self.newMenuCheckBox.setChecked(False)
            self.addLayerMenuCheckBox.setChecked(False)

            self.newMenuCheckBox.setEnabled(False)
            self.addLayerMenuCheckBox.setEnabled(False)
        else:
            self.newMenuCheckBox.setEnabled(True)
            self.addLayerMenuCheckBox.setEnabled(True)

        self.newMenuCheckBox.clicked.connect(self._project_changed)
        self.addLayerMenuCheckBox.clicked.connect(self._project_changed)

    def _project_changed(self) -> None:
        """Slot for projectChanged signal emit if enabled"""
        if self._emit_changed_signal:
            self.projectChanged.emit()

        project = self.get_project()

        if project.valid:
            self.pathLineEdit.setStyleSheet("color: {};".format("black"))
        else:
            self.pathLineEdit.setStyleSheet("color: {};".format("red"))

    def _connect_update_signal(self) -> None:
        """Connect update signal for project"""
        # Type storage update connection
        self.fileRatioButton.clicked.connect(self._project_changed)
        self.postgresqlRadioButton.clicked.connect(self._project_changed)
        self.urlRadioButton.clicked.connect(self._project_changed)

        # Location update connection
        self.addLayerMenuCheckBox.clicked.connect(self._project_changed)
        self.newMenuCheckBox.clicked.connect(self._project_changed)
        self.mergePreviousCheckBox.clicked.connect(self._project_changed)

        # Name/id/path update connection
        self.nameLineEdit.textChanged.connect(self._project_changed)
        self.idLineEdit.textChanged.connect(self._project_changed)
        self.pathLineEdit.textChanged.connect(self._project_changed)

        # Cache config update connection
        self.enableCacheCheckBox.clicked.connect(self._project_changed)
        self.refreshIntervalSpinBox.valueChanged.connect(self._project_changed)
        self.validationFileLineEdit.fileChanged.connect(self._project_changed)

    def set_project(self, project: Project) -> None:
        """Define display project

        :param project: displayed project
        :type project: Project
        """
        # Disable projectChanged signal emit
        self._emit_changed_signal = False

        self.idLineEdit.setText(project.id)
        self.nameLineEdit.setText(project.name)
        self.pathLineEdit.setText(project.file)

        self.enableCacheCheckBox.setChecked(project.cache_config.enable)
        if project.cache_config.refresh_days_period:
            self.refreshIntervalSpinBox.setValue(
                project.cache_config.refresh_days_period
            )
        else:
            self.refreshIntervalSpinBox.setValue(-1)

        self.validationFileLineEdit.setFilePath(
            project.cache_config.cache_validation_uri
        )

        self.newMenuCheckBox.setChecked(False)
        self.addLayerMenuCheckBox.setChecked(False)
        self.mergePreviousCheckBox.setChecked(False)

        if project.location == "new":
            self.newMenuCheckBox.setChecked(True)
        if project.location == "layer":
            self.addLayerMenuCheckBox.setChecked(True)
        if project.location == "merge":
            self.mergePreviousCheckBox.setChecked(True)

        if project.type_storage == "file":
            self.fileRatioButton.setChecked(True)
        elif project.type_storage == "database":
            self.postgresqlRadioButton.setChecked(True)
        elif project.type_storage == "http":
            self.urlRadioButton.setChecked(True)

        # Simulate merge location change to update check button
        self._merge_location_changed()

        # Restore projectChanged signal emit
        self._emit_changed_signal = True

    def get_project(self) -> Project:
        """Get displayed project

        :return: displayed project
        :rtype: Project
        """
        cache_config = ProjectCacheConfig(
            enable=self.enableCacheCheckBox.isChecked(),
            refresh_days_period=self.refreshIntervalSpinBox.value(),
            cache_validation_uri=self.validationFileLineEdit.filePath(),
        )
        location = "new"
        if self.newMenuCheckBox.isChecked():
            location = "new"
        if self.addLayerMenuCheckBox.isChecked():
            location = "layer"
        if self.mergePreviousCheckBox.isChecked():
            location = "merge"

        type_storage = "file"
        if self.fileRatioButton.isChecked():
            type_storage = "file"
        elif self.postgresqlRadioButton.isChecked():
            type_storage = "database"
        elif self.urlRadioButton.isChecked():
            type_storage = "http"

        return Project(
            id=self.idLineEdit.text(),
            name=self.nameLineEdit.text(),
            location=location,
            file=self.pathLineEdit.text(),
            type_storage=type_storage,
            cache_config=cache_config,
            valid=self._check_if_project_valid(),
        )

    def _select_path(self) -> None:
        """Select project path depending on current type storage:
        - file : search for local file
        - database : display project database ui
        """
        if self.fileRatioButton.isChecked():
            self._define_local_path()
        elif self.postgresqlRadioButton.isChecked():
            self._define_database_path()

    def _define_database_path(self) -> None:
        """Define project path from database"""
        pgr = QgsProviderGuiRegistry(QgsApplication.pluginPath())
        if "postgres" in pgr.providerList():
            psgp = pgr.projectStorageGuiProviders("postgres")
            if len(psgp) > 0:
                uri = psgp[0].showLoadGui()
                self.pathLineEdit.setText(uri)

                if not self.nameLineEdit.text():
                    try:
                        name = uri.split("project=")[-1]
                        name = name.split(".")[0]
                    except Exception:
                        name = ""
                    self.nameLineEdit.setText(name)

    def _define_local_path(self) -> None:
        """Define project path for local path"""
        file_widget = self.pathLineEdit

        filePath = QFileDialog.getOpenFileName(
            self,
            QgsApplication.translate(
                "menu_from_project", "Projects configuration", None
            ),
            file_widget.text(),
            QgsApplication.translate(
                "menu_from_project", "QGIS projects (*.qgs *.qgz)", None
            ),
        )
        if filePath[0]:
            file_widget.setText(filePath[0])

            if not self.nameLineEdit.text():
                try:
                    name = filePath[0].split("/")[-1]
                    name = name.split(".")[0]
                except Exception:
                    name = ""

                self.nameLineEdit.setText(name)

    def _delete_project_cache(self) -> None:
        """Delete displayed project cache"""
        cache_manager = CacheManager(iface)
        cache_manager.clear_project_cache(project=self.get_project())

    def _check_if_project_valid(self) -> bool:
        """Check if project is valid by reading Qgs project

        :return: True if project is valid, False otherwise
        :rtype: bool
        """
        valid = False
        text = self.pathLineEdit.text()
        try:
            doc, _ = self.qgs_dom_manager.getQgsDoc(text)
            valid = not doc.isNull()
        except Exception as err:
            self.log("Error during project reading: {}".format(err))
        return valid

    @staticmethod
    def log(message, application=__title__, indent=0):
        indent_chars = " .. " * indent
        QgsMessageLog.logMessage(
            f"{indent_chars}{message}", application, notifyUser=True
        )
