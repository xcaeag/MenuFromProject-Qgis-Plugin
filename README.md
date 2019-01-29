MenuFromProject-Qgis-Plugin 
===========================

That plugin provides a convenient way to add prestyled and configured frequently used layers using dropdown menus built by simply reading existing QGis projects (qgs, qgz, postgres)

Styling, actions, labeling, metadata - every layer options in fact except joins - are reused as defined in source qgs projects

Whole documentation is available just here :


How to use it ?
----------------

When the plugin is configured (choice of a project via the plugin menu), a new menu appears, based on all the layers that contain the original project.

Tip : a separator can be configured by creating (in the original project) a layer group named "-".

Attention : the project must be configured to record absolute paths.

The project might be stored in a PostgreSQL database (https://qgis.org/en/site/forusers/visualchangelog32/index.html#feature-saving-and-loading-projects-in-postgresql-database). You need to copy/paste the project URI (Project properties -> General) into the field.
...and QGZ (https://qgis.org/en/site/forusers/visualchangelog30/index.html#feature-new-zipped-project-file-format-qgz)

Option of the plugin "Load all layers item" if it is checked load all the layers of the same level submenu.

"Create group" option put the new layer in a group with the name of the parent level menu.

You can hide the administration dialog of the plugin by adding a `menu_from_project/is_setup_visible` to `false` in the QGIS INI file. This is useful when you deploy QGIS within an organization.

MenuFromProject-Qgis-Plugin (Français)
======================================

Cette extension pour QGIS permet de construire automatiquement des menus déroulants permettant d'ajouter des couches préstylées définies dans des projets qgis externes "modèles" (qgs, qgz, postgres). 

Tous les paramètrages des couches, le style, les étiquettes, les actions, les métadonnées.. sont conservés. La maintenance se résume à la gestion de quelques projets QGIS centralisés. 

Comment l'utiliser?
-------------------

Lorsque le plugin est configuré (choix des projets et attribution d'un nom associé via le menu Extensions - Layers menu from projects), de nouveaux menus apparaissent, pour chacun des projets sélectionnés. 
Chaque item de menu correspond alors à une couche du projet et déclenche son ouverture.

Astuce : des séparateurs seront crées à l'emplacement des groupes de couche nommés "-" dans le projet original.

Attention : le projet doit être configuré de façon à enregistrer des chemins absolus.

Le projet peut-être stocké en base PostgreSQL (https://qgis.org/en/site/forusers/visualchangelog32/index.html#feature-saving-and-loading-projects-in-postgresql-database). Pour cela il faut copier/coller le chemin/URI du projet (Propriétés du projet -> Général) dans le champ...  
...et QGZ (https://qgis.org/en/site/forusers/visualchangelog30/index.html#feature-new-zipped-project-file-format-qgz)

L'option du plugin "option de menu 'tout ajouter'", si elle est cochée permet de charger l'ensemble des couches d'un même niveau de sous-menu.

L'option "Créer un groupe au chargement de la couche" place la nouvelle couche sous un groupe portant le nom du menu.

Vous pouvez cacher la fenêtre d'administration du plugin en ajoutant une variable `menu_from_project/is_setup_visible` à `false` dans le fichier INI de QGIS. Ceci est utile quand QGIS est déployé au sein d'une organisation.


