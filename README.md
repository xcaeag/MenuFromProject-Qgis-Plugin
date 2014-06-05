MenuFromProject-Qgis-Plugin
===========================

Build layers shortcuts menus based on QGis projects

Allow easy opening of layers maintaining their style.

Principle

When the plugin is configured (choice of a project via the plugin menu), a new menu appears, based on all the layers that contain the original project.
Tip : a separator can be configured by creating (in the original project) a layer group named "-"

Option of the plugin "Load all layers item" if it is checked load all the layers of the same level submenu
Create group" option put the new layer in a group with the name of the parent level menu 

MenuFromProject-Qgis-Plugin (Français)
--------------------------------------

Construit des menus basés sur des projets QGis
	
Objectif
Faciliter l'ouverture des couches fréquement utilisées, avec leurs styles, en enrichissant la barre de menu à partir de projets "modèles".

Principe
Lorsque le plugin est configuré (choix des projets et attribution d'un nom associé via le menu Extensions - Layers menu from projects), de nouveaux menus apparaissent, pour chacun des projets sélectionnés. Chaque item de menu correspond alors à une couche du projet et déclenche son ouverture.
Astuce : des séparateurs seront crées à l'emplacement des groupes de couche nommés "-" dans le projet original.

L'option du plugin "option de menu 'tout ajouter'", si elle est cochée permet de charger l'ensemble des couches d'un même niveau de sous-menu
L'option "Créer un groupe au chargement de la couche" place la nouvelle couche sous un groupe portant le nom du menu 
