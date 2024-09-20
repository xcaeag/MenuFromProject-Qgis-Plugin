# standard
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

# PyQGIS
from qgis.core import QgsLayerTreeNode, QgsMapLayerType, QgsProject, QgsWkbTypes


@dataclass
class MenuLayerConfig:
    """Class to store configuration for layer menu creation"""

    name: str
    layer_id: str
    filename: str
    visible: bool
    expanded: bool
    embedded: str
    is_spatial: bool
    layer_type: QgsMapLayerType
    metadata_abstract: str
    metadata_title: str
    abstract: str
    title: str
    geometry_type: Optional[QgsWkbTypes.GeometryType] = None


@dataclass
class MenuGroupConfig:
    """Class to store configuration for group menu creation"""

    name: str
    filename: str
    childs: List[Any]  # List of Union[MenuLayerConfig,MenuGroupConfig]
    embedded: bool


@dataclass
class MenuProjectConfig:
    """Class to store configuration for project menu creation"""

    filename: str
    uri: str
    root_group: MenuGroupConfig


def get_embedded_project_from_layer_tree(
    layer_tree: QgsLayerTreeNode, project: QgsProject
) -> str:
    """Get embedded project path from layer tree and his parent

    :param layer_tree: layer tree to inspect
    :type layer_tree: QgsLayerTreeNode
    :param project: project where layer tree is used
    :type project: QgsProject
    :return: path to embedded project
    :rtype: str
    """
    filename = project.readPath(layer_tree.customProperty("embedded_project"))
    if filename == "" and layer_tree.parent():
        return get_embedded_project_from_layer_tree(
            layer_tree=layer_tree.parent(), project=project
        )
    return filename


def read_embedded_properties(
    layer_tree: QgsLayerTreeNode, project: QgsProject
) -> Tuple[bool, str]:
    """Read embedded properties from a QgsLayerTreeNode in a QgsProject

    :param layer_tree: layer tree to inspect
    :type layer_tree: QgsLayerTreeNode
    :param project: project where layer tree is used
    :type project: QgsProject
    :return: Boolean indicating if the layer tree is embedded and the filename of the project used
    :rtype: Tuple[bool, str]
    """
    # Embedded property is not read if QgsProject.FlagDontResolveLayers flag is use when reading QgsProject
    if layer_tree.customProperty("embedded"):
        embedded = True
        filename = get_embedded_project_from_layer_tree(
            layer_tree=layer_tree, project=project
        )
    else:
        embedded = False
        filename = project.absoluteFilePath()
    return embedded, filename


def get_layer_menu_config(
    layer_tree: QgsLayerTreeNode, project: QgsProject
) -> MenuLayerConfig:
    """Get layer menu configuration from a QgsLayerTreeNode in a QgsProject

    :param layer_tree: layer tree to inspect
    :type layer_tree: QgsLayerTreeNode
    :param project: project where layer tree is used
    :type project: QgsProject
    :return: Layer menu configuration
    :rtype: MenuLayerConfig
    """

    embedded, filename = read_embedded_properties(
        layer_tree=layer_tree, project=project
    )

    # Get project map layer
    layer = project.mapLayer(layer_tree.layerId())

    return MenuLayerConfig(
        name=layer_tree.name(),
        layer_id=layer_tree.layerId(),
        filename=filename,
        visible=layer_tree.itemVisibilityChecked(),
        expanded=layer_tree.isExpanded(),
        embedded=embedded,
        layer_type=layer.type(),
        metadata_abstract=layer.metadata().abstract(),
        metadata_title=layer.metadata().title(),
        abstract=layer.abstract(),
        is_spatial=layer.isSpatial(),
        title=layer.title(),
        geometry_type=(
            layer.geometryType()
            if layer.type() == QgsMapLayerType.VectorLayer
            else None
        ),
    )


def get_group_menu_config(
    layer_tree: QgsLayerTreeNode, project: QgsProject
) -> MenuGroupConfig:
    """Get group menu configuration from a QgsLayerTreeNode in a QgsProject

    :param layer_tree: layer tree to inspect
    :type layer_tree: QgsLayerTreeNode
    :param project: project where layer tree is used
    :type project: QgsProject
    :return: Group menu configuration
    :rtype: MenuGroupConfig
    """
    embedded, filename = read_embedded_properties(
        layer_tree=layer_tree, project=project
    )

    childs = []

    for child in layer_tree.children():
        if child.nodeType() == QgsLayerTreeNode.NodeGroup:
            childs.append(get_group_menu_config(child, project))
        elif child.nodeType() == QgsLayerTreeNode.NodeLayer:
            childs.append(get_layer_menu_config(child, project))
    return MenuGroupConfig(
        name=layer_tree.name(), embedded=embedded, filename=filename, childs=childs
    )


def get_project_menu_config(qgs_project: QgsProject, uri: str) -> MenuProjectConfig:
    """Get project menu configuration from a QgsProject

    :param qgs_project: project
    :type qgs_project: QgsProject
    :param uri: initial uri of project (can be from local file / http / postgres)
    :type uri: str
    :return: Project menu configuration
    :rtype: MenuProjectConfig
    """
    return MenuProjectConfig(
        filename=qgs_project.absoluteFilePath(),
        uri=uri,
        root_group=get_group_menu_config(qgs_project.layerTreeRoot(), qgs_project),
    )
