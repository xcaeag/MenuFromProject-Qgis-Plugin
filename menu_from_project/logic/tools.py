#! python3  # noqa: E265

# Standard library
import logging

# PyQGIS
from qgis.core import QgsApplication

# project
from menu_from_project.__about__ import DIR_PLUGIN_ROOT

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


def guess_type_from_location(qgs_location: str) -> str:
    if qgs_location.startswith("postgresql"):
        return "database"
    elif qgs_location.startswith("http"):
        return "remote_url"
    else:
        return "file"


def icon_per_type(qgs_location_type: str) -> str:
    if qgs_location_type == "file":
        return QgsApplication.iconPath("mIconFile.svg")
    elif qgs_location_type == "database":
        return QgsApplication.iconPath("mIconPostgis.svg")
    elif qgs_location_type == "remote_url":
        return str(DIR_PLUGIN_ROOT / "resources/globe.svg")
    else:
        return QgsApplication.iconPath("mIconFile.svg")
