# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataManager
                                 A QGIS plugin
 Manage Subtypes and Domains in PostGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-06-25
        git sha              : $Format:%H$
        copyright            : (C) 2019 by George Ioannou
        email                : gmioannou@cartologic.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMessageBox, QTreeWidget, QTreeWidgetItem
from qgis.core import QgsMessageLog, QgsVectorLayer, QgsVectorLayerJoinInfo, QgsRelation, QgsProject, QgsDataSourceUri, QgsEditorWidgetSetup

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .data_manager_dockwidget import DataManagerDockWidget
import os.path
import psycopg2

# Import Pgdb class
from .core.pgdb import Pgdb


class DataManager:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n',
                                   'DataManager_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Data Manager')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'DataManager')
        self.toolbar.setObjectName(u'DataManager')

        self.pluginIsActive = False
        self.dockwidget = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DataManager', message)

    def add_action(self,
                   icon_path,
                   text,
                   callback,
                   enabled_flag=True,
                   add_to_menu=True,
                   add_to_toolbar=True,
                   status_tip=None,
                   whats_this=None,
                   parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/data_manager/icon.png'
        self.add_action(icon_path,
                        text=self.tr(u'Data Manager'),
                        callback=self.run,
                        parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING DataManager"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD DataManager"

        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Data Manager'), action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------
    def initDatabaseConenctionsList(self):
        QgsMessageLog.logMessage('Init Connections List')

        self.dockwidget.connectionsComboBox.clear()

        s = QSettings()
        s.beginGroup("PostgreSQL/connections")

        keys = s.childGroups()

        if (len(keys) == 0):
            QgsMessageLog.logMessage("No database connections found",
                                     self.pluginName)
            return ()

        for key in keys:
            self.dockwidget.connectionsComboBox.addItem(str(key))
            QgsMessageLog.logMessage(key,  self.pluginName)

        s.endGroup()

        # Use the first connection to connect to the database
        self.onConnectDatabase(keys[0])

    #--------------------------------------------------------------------------
    def onConnectDatabase(self, connInfo):
        """
        Establish a connection to PostGIS database.
        Initialize the database schemas list
        Update the Layers Tree Widget
        """
        if (connInfo == None):
            return ()

        # get database connection settings
        qs = QSettings()
        qs.beginGroup("PostgreSQL/connections")

        self.pgdb.database = qs.value("{0}/database".format(connInfo))
        self.pgdb.host = qs.value("{0}/host".format(connInfo))
        self.pgdb.port = qs.value("{0}/port".format(connInfo))
        self.pgdb.username = qs.value("{0}/username".format(connInfo))
        self.pgdb.password = qs.value("{0}/password".format(connInfo))

        qs.endGroup()

        # conenct to the database
        self.pgdb.connect()

        # check if extension is initialized
        if self.pgdb.check_extension():
            QgsMessageLog.logMessage("Extension already initialized", self.pluginName)
        else:
            # if superuser connection initialize extension
            if self.pgdb.dbcon.get_parameter_status("is_superuser") == 'on':
                self.pgdb.init_extension()
            else:
                mline1 = "Data Manager plugin is not initialized in the database."
                mline2 = "\nPlease connect as super user or the database owner at least once to initialize."
                QMessageBox.information(None, self.pluginName, mline1 + mline2)
                return

        # initialize schemas and layers tree
        self.pgdb.init_schemata()
        self.initLayersTreeWidget()

    #--------------------------------------------------------------------------
    def initLayersTreeWidget(self):
        """
        Init layers tree widget
        Populate schemas and layers/tables from the database
        """
        tree = self.dockwidget.layersTreeWidget
        tree.clear()

        for schema in self.pgdb.schemata:
            parent = QTreeWidgetItem([schema])
            layers = self.pgdb.get_layers(schema)

            for lay in layers:
                schema = str(lay[0])
                layer = str(lay[1])
                geom = str(lay[2])

                child = QTreeWidgetItem([layer, schema, geom])
                parent.addChild(child)

            tree.addTopLevelItem(parent)

    #--------------------------------------------------------------------------
    def onDoubleClickLayer(self, schema, layer, geom):
        """
        Add Layer/Tables to the Layers List Panel.
        Call the appropriate routines to establish Joins and Relates.
        """
        if (geom != "None"):  #Layer
            self.addLayer(schema, layer, geom)
        else:  #Table
            self.addLayer(schema, layer)

        # Process joined tables
        if self.dockwidget.loadJoinsCheckBox.isChecked():
            self.processJoinedTables(schema, layer)

        # Process related tables
        if self.dockwidget.loadRelatesCheckBox.isChecked():
            self.processRelatedTables(schema, layer)

        self.iface.setActiveLayer(self.getLayerByName(layer))

    def addLayer(self, schema, layer, geom=None):
        """Add Layer/Table to the Layers Panel."""
        # check if the layer is already in Layers List
        lay = self.getLayerByName(layer)
        if (lay != None):
            QgsMessageLog.logMessage(
                "{} is already in Layers List".format(layer), self.pluginName)
            return ()

        sql = ""
        uri = QgsDataSourceUri()
        uri.setConnection(self.pgdb.host, self.pgdb.port, self.pgdb.database,
                          self.pgdb.username, self.pgdb.password,
                          QgsDataSourceUri.SslDisable)
        uri.setDataSource(schema, layer, geom)
        vlayer = QgsVectorLayer(uri.uri(), layer, "postgres")

        if vlayer.isValid():
            QgsProject.instance().addMapLayer(vlayer)
        else:
            QgsMessageLog.logMessage("Layer is not valid!", self.pluginName)

    def processRelatedTables(self, schema, layer):
        """Process related tables."""
        QgsMessageLog.logMessage("Loading Relates ...", self.pluginName)
        rows = self.pgdb.get_related_tables(schema, layer)

        for row in rows:
            d_schema = row[0]
            d_table = row[1]
            d_field = row[2]
            m_schema = row[3]
            m_table = row[4]
            m_field = row[5]

            self.addLayer(d_schema, d_table)

            d_layer = self.getLayerByName(d_table)
            m_layer = self.getLayerByName(m_table)
            rel_name = '{0}_{1}'.format(m_table, d_table)

            self.addRelation(d_layer, d_field, m_layer, m_field, rel_name)

    def processJoinedTables(self, schema, layer):
        """Process joined tables."""
        QgsMessageLog.logMessage("Loading Joins ...", self.pluginName)
        rows = self.pgdb.get_joined_tables(schema, layer)

        for row in rows:
            d_schema = row[0]
            d_table = row[1]
            d_field = row[2]
            m_schema = row[3]
            m_table = row[4]
            m_field = row[5]

            self.addLayer(m_schema, m_table)

            d_layer = self.getLayerByName(d_table)
            m_layer = self.getLayerByName(m_table)

            self.addJoin(d_layer, d_field, m_layer, m_field)
            self.setEditWidget(d_layer, d_field, m_layer, m_field)

    def addRelation(self, d_layer, d_field, m_layer, m_field, rel_name):
        """Add relation to the project."""
        rel = QgsRelation()
        rel.setReferencingLayer(d_layer.id())
        rel.setReferencedLayer(m_layer.id())
        rel.addFieldPair(d_field, m_field)
        rel.setId(rel_name)
        rel.setName(rel_name)

        if rel.isValid():
            QgsMessageLog.logMessage(rel_name, self.pluginName)
            QgsProject.instance().relationManager().addRelation(rel)
        else:
            QgsMessageLog.logMessage('Relation is NOT valid', self.pluginName)

    def addJoin(self, target_layer, target_field, join_layer, join_field):
        """Add join to the layer."""
        join = QgsVectorLayerJoinInfo()
        join.setJoinFieldName(join_field)
        join.setTargetFieldName(target_field)
        join.setUsingMemoryCache(True)
        join.setJoinLayer(join_layer)

        target_layer.addJoin(join)

    def setEditWidget(self, d_layer, d_field, m_layer, m_field):
        """set the edit widget for specific field."""

        fieldIndex = d_layer.fields().indexFromName(d_field)
        vmap_dict = self.getValueMapDict(m_layer)

        editorWidgetSetup = QgsEditorWidgetSetup('ValueMap', vmap_dict)

        d_layer.setEditorWidgetSetup(fieldIndex, editorWidgetSetup)

    def getValueMapDict(self, lut):
        """Get Value Map dictionary from the joind Lookup Table."""
        features = lut.getFeatures()

        vl_dict = {}
        for feat in features:
            values = feat.attributes()

            code = unicode(values[1])
            desc = unicode(values[2])

            # qgis expects them to be in this order
            vl_dict.update({desc: code})

        vmap_dict = {'map': vl_dict}

        return (vmap_dict)

    def getLayerByName(self, layer_name):
        """Get Layer object from the Layers Panel if exists."""
        layer = None
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == layer_name:
                layer = lyr
                break

        return (layer)

    #--------------------------------------------------------------------------
    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True
            self.pluginName = "Data Manager"

            # dockwidget may not exist if:
            #   first run of plugin
            #   removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = DataManagerDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # initializing postgres connections list
            self.pgdb = Pgdb()
            self.initDatabaseConenctionsList()
            self.dockwidget.connectingDatabase.connect(self.onConnectDatabase)
            self.dockwidget.doubleClickLayer.connect(self.onDoubleClickLayer)

            # show the dockwidget
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()