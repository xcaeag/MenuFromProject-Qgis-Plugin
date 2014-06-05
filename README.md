MenuFromProject-Qgis-Plugin
===========================

Build layers shortcuts menus based on QGis projects

Allow easy opening of layers maintaining their style.

Principle

When the plugin is configured (choice of a project via the plugin menu), a new menu appears, based on all the layers that contain the original project.
Tip : a separator can be configured by creating (in the original project) a layer group named "-"
Attention : the project must be configured to record absolute paths

Option of the plugin "Load all layers item" if it is checked load all the layers of the same level submenu
Create group" option put the new layer in a group with the name of the parent level menu (v 1.9)
