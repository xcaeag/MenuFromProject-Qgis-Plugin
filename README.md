MenuFromProject-Qgis-Plugin (English version)
===========================

That plugin provides a convenient way to add prestyled and configured frequently used layers using dropdown menus built by simply reading existing QGis projects

Styling, actions, labeling, metadata - every layer options in fact except joins - are reused as defined in source qgs projects

Whole documentation is available just here :


How to use it ?
----------------

When the plugin is configured (choice of a project via the plugin menu), a new menu appears, based on all the layers that contain the original project.
Tip : a separator can be configured by creating (in the original project) a layer group named "-"

Option of the plugin "Load all layers item" if it is checked load all the layers of the same level submenu
Create group" option put the new layer in a group with the name of the parent level menu 

MenuFromProject-Qgis-Plugin (Français)
======================================

Cette extension pour QGIS permet de construire automatiquement des menus déroulants permettant d'ajouter des couches préstylées définies dans des projets qgis externes. 
Tous les paramètrages des couches, le style, les étiquettes, les actions, les métadonnées.. sont conservées. La maintenance se résume à la gestion de quelques projets QGIS centralisés. 

Comment l'utiliser?
-------------------

Lorsque le plugin est configuré (choix des projets et attribution d'un nom associé via le menu Extensions - Layers menu from projects), de nouveaux menus apparaissent, pour chacun des projets sélectionnés. Chaque item de menu correspond alors à une couche du projet et déclenche son ouverture.

Astuce : des séparateurs seront crées à l'emplacement des groupes de couche nommés "-" dans le projet original.

L'option du plugin "option de menu 'tout ajouter'", si elle est cochée permet de charger l'ensemble des couches d'un même niveau de sous-menu
L'option "Créer un groupe au chargement de la couche" place la nouvelle couche sous un groupe portant le nom du menu 
