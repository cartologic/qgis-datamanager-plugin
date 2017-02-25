# Data Manager plugin for QGIS

## Introduction

It detects the foreign key constraints for layers and tables within PostgreSQL/PostGIS database, to construct joins and relates in QGIS projects. It utilizes the joins to change the _Edit widget_ of the referenced fields from _Text Edit_ to _Value Maps_ and additionally it composes the list of valid values, like subtypes and domains.

## Installation

Download or clone the plugin, rename the plugin’s folder to _DataManager_ and copy in the following location, then restart QGIS.

```
$HOME/.qgis2/python/plugins/
```
From QGIS interface click the _Plugins_ pull down menu and navigate to the _Manage and Install Plugins_. Search for the _Data Manager_ plugin and activate it using the checkbox.

## Usage

Access the plugin either from the _Plugins_ pull down menu or from its toolbar button. Data manager dockable window will be shown in the lower left corner of the QGIS window.

If a PostGIS database connection exists, the plugin will make use of it in order to connect to the database. The database connection should be created in advance, using the _Browser Panel_ and it will be shown at the top of the widget. Schemas can be expanded using the plus (**+**) icon, which enables the navigation to the various layers and tables.

_Layers and tables_ can be added to QGIS canvas by double click on their name in the list of layers. If the corresponding checkboxes at the bottom of the plugin window are checked then the joined and related tables will be added to the canvas and the Layers Panel as well, otherwise only the selected layer or table will be added. Moreover, joins and relates will be created automatically by the plugin.

_Joins_ are offering the domain and subtype experience of feature class visualization and editing similar to other proprietary GIS desktop software. They can be used for styling and labeling in map production processes and additionally during editing, they serve as lookup tables listing valid values for the fields they are assigned to. Data manager is taking care of the necessary configuration in order for the layer to be shown as required, with limited interaction from the user, thus the user experience is improved.

_Relates_ are offering the presentation of the one-to-many relationship among layers and tables. For example when the user identifies a _Monitoring Station_, the _Readings_ of this particular station will be displayed as well on the editing form.

## Note
It is highly recommended to use this plugin in combination with [File Geodatabase to PostGIS Converter](https://github.com/cartologic/fgdb2postgis.git) python package, simply because both software resulted from the same project and thus there are well tested on working together.

## License
GNU Public License (GPL) Version 3
