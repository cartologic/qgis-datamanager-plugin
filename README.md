# Data Manager plugin for QGIS

## Introduction

This plugin provides a full field domain experience for PostGIS/QGIS.  

What is different is that the attribute domains are defined and maintained in the PostGIS database instead of the QGIS project. Once the plugin is installed and configured then adding data using the plugin will create the necessary joins and relates within the QGIS project. The plugin will automatically define for each layer:
  - Coded value domains (will be loaded as layer joins and list of values)
  - One to many relations (will be loaded as project relations)

## Installation

1. Download or clone the plugin
2. Rename the plugin’s folder to _DataManager_
3. Copy the plugin's folder in qgis plugins folder: `[HOME]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
4. Restart QGIS.

From QGIS click the _Plugins_ pull down menu and navigate to the _Manage and Install Plugins_. Search for the _Data Manager_ plugin and activate it using the checkbox.

### Configuration:

1. Direct loading of data to PostGIS
  - Define the necessary indexes and constraints describing the relationships between layers and lookup tables in the database, using sql either from psql or pgadmin.
  - Modify information schema views. Run this script [Information Schema Views.sql](https://github.com/cartologic/qgis-datamanager-plugin/blob/master/core/sql/information_schema_views.sql) directly in the database from psql/pgadmin, alternatively connect the first time as supper user (database owner) from the plugin and the information schema views will be updated automatically.
2. Loading of data from ESRI file geodatabase
  - Users migrating their data from ESRI file geodatabase using [fgdb2postgis]( https://pypi.python.org/pypi/fgdb2postgis) will have all the indexes, constraints and information schema views defined by default.

## Usage

Access the plugin either from the _Plugins_ pull down menu or from its toolbar button. Data manager dockable window will be shown in the lower left corner of the QGIS window.

If a PostGIS database connection exists, the plugin will make use of it in order to connect to the database. The database connection should be created in advance, using the _Browser Panel_ and it will be shown at the top of the widget. Schemas can be expanded using the plus (**+**) icon, which enables the navigation to the various layers and tables.

_Layers and tables_ can be added to QGIS canvas by double click on their name in the list of layers. If the corresponding checkboxes at the bottom of the plugin window are checked then the joined and related tables will be added to the canvas and the Layers Panel as well, otherwise only the selected layer or table will be added. Moreover, joins and relates will be created automatically by the plugin.

_Joins_ are offering the domain and subtype experience of feature class visualization and editing similar to other proprietary GIS desktop software. They can be used for styling and labeling in map production processes and additionally during editing, they serve as lookup tables listing valid values for the fields they are assigned to. Data manager is taking care of the necessary configuration in order for the layer to be shown as required, with limited interaction from the user, thus the user experience is improved.

_Relates_ are offering the presentation of the one-to-many relationship among layers and tables. For example when the user identifies a _Monitoring Station_, the _Readings_ of this particular station will be displayed as well on the editing form.

## Note
It is highly recommended to use this plugin in combination with [fgdb2postgis]( https://pypi.python.org/pypi/fgdb2postgis) python package, because both software resulted from the same project and thus there are well tested on working together.

## Advanced

- The plugin detects the constraints for layers and tables within the database.
- The plugin constructs joins and relates using this information in the QGIS project.
- It utilizes the joins to:
  - Change the _Edit widget_ of the referenced fields from _Text Edit_ to _Value Maps_  
  - To compose the list of valid domain values.

## License
GNU Public License (GPL) Version 3
