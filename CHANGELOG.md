# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## X.y.z - YYYY-DD-mm

-->

## 2.2.0-beta2 - 2024-11-29

## What's Changed

### Bugs fixes 🐛

* fix(project read): must check if layer is available in qgs project by @jmkerloch in https://github.com/aeag/MenuFromProject-Qgis-Plugin/pull/126

## 2.2.0-beta1 - 2024-11-13

- Layer notes as tooltip
- Minimum QGIS version is 3.28
- Defer menu creation in QThreads (funded by EPTB Loire, ANFSI and Charente Eaux Rivière)
- Add a cache mechanism to improve performances (funded by EPTB Loire, ANFSI and Charente Eaux Rivière)
- Refactoring project's tooling, documentation and CI/CD (funded by Agences de l'Eau)
- Move GitHub project under Agence de l'eau Adour Garonne organization to allow better access management

## 2.1.0 - 2024-01-30

- Support relations, fix #20

## 2.1.0-beta1 - 2023-08-07

- #51 Support relations

## 2.0.8 - 2023-04-28

- Minimum Version is 3.14

## 2.0.7 - 2023-04-26

- fix #77

## 2.0.6 - 2022-11-08

- Added some icons (<https://github.com/nicogodet>) #72

## 2.0.5 - 2022-09-02

- fix #67

## 2.0.4 - 2022-09-01

- Japanese translation, thanks to Yamamoto Ryuzo (<https://github.com/yamamoto-ryuzo>), Tokimasasogo (<https://github.com/Tokimasasogo>)

## 2.0.3 - 2022-02-28

- fix #53 Help not showing Extensions

## 2.0.2 - 2021-11-26

- fix #50 Alternatively use metadata as tooltip instead of OGC metadata

## 2.0.1 - 2021-05-21

- fix #48 (Load above in ToC), better configuration interface

## 2.0.0 - 2021-05-21

- Allow pointing to http/https online qgs-qgz project file,
- Support of Joined layers
- Minor refactoring and tooling made by @Guts, funded by Oslandia and ANFSI

## 1.1.0 - 2020-09-04

- It is now possible to merge two projects (#27).

## 1.0.6

- Build menus on initializationCompleted, otherwise tooltips are imperfect

## 1.0.5

- fix #25

## 1.0.4

- Add support for "trusted project" option, thanks to <https://github.com/Djedouas>

## 1.0.3

- fix #20 - Layer doesn't appear when sourced from "Integrate layers and group"

## 1.0.2

- Load all styles from DB if the plugin DB-Style-Manager is setup

## 1.0.1

- Bugfix #18. Relative paths mode

## 1.0.0

- Display geometry type icon, new location possible: "add layer" menu, code cleaning. Thanks to Etienne Trimaille (<https://github.com/Gustry>)
- Fix load-all failure

## 0.9.0

- Allow a project stored in database, thanks to Etienne Trimaille (<https://github.com/Gustry>)
- Allow qgz projects

## 0.8.3 - 2018-06-11

- When create group option is checked, the original layer visibility is preserved. Thanks to Eric LAZZARETTI.

## 0.8.2

- Code cleaning

## 0.8.1

- QGIS 2.99 compatible: Python 3, QT5

## 0.8.0

- Migration for QGIS3

## 0.7.6 - 2016-12-29

- Better documentation

## 0.7.5

- Tooltip refinement

## 0.7.4

- Some python cleaning

## 0.7.3

- New layer id without special characters

## 0.7.2

- Some optimizations

## 0.7.1

- QGIS 2.4 compatible. Deprecated functions are deleted

## 0.7.0 - 2014-06-10

- works with "relative path" projects, and embedded layers

## 0.6.0

- 2.2 compatible

## 0.5.0 - 2013-08-06

- 2.0 compatible

## 0.4.1 - 2013-03-21

- Load all layers item, create group option (dev version 1.9)
