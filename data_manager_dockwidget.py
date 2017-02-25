# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataManagerDockWidget
								 A QGIS plugin
 This plugin manages Layers, Tables, Joins and Relates in PostgreSQL/PostGIS database
							 -------------------
		begin				 : 2016-11-08
		git sha				 : $Format:%H$
		copyright			 : (C) 2016 by George Ioannou / Cartologic
		email				 : gmioannou@cartologic.com
 ***************************************************************************/

/***************************************************************************
 *																		   *
 *	 This program is free software; you can redistribute it and/or modify  *
 *	 it under the terms of the GNU General Public License as published by  *
 *	 the Free Software Foundation; either version 2 of the License, or	   *
 *	 (at your option) any later version.								   *
 *																		   *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal
from qgis.core import QgsMessageLog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'data_manager_dockwidget_base.ui'))


class DataManagerDockWidget(QtGui.QDockWidget, FORM_CLASS):

	closingPlugin = pyqtSignal()
	doubleClickLayer = pyqtSignal(str, str, str)
	connectingDatabase = pyqtSignal(str)	

	def __init__(self, parent=None):
		"""Constructor."""
		super(DataManagerDockWidget, self).__init__(parent)
		self.setupUi(self)

		self.connectButton.pressed.connect(self.changeDatabaseConenction)
		self.connectionsComboBox.currentIndexChanged.connect(self.changeDatabaseConenction)
		self.layersTreeWidget.itemDoubleClicked.connect(self.layer_doubleClicked)

	def layer_doubleClicked(self):
		"""When the user double click layer"""
		sel_items = self.layersTreeWidget.selectedItems()
		
		if(sel_items[0].parent() != None):
			layer = sel_items[0].text(0)
			schema = sel_items[0].text(1)
			geom = sel_items[0].text(2)

			self.doubleClickLayer.emit(schema, layer, geom)

	def changeDatabaseConenction(self):
		"""When the user changes database connection"""
		selConn = self.connectionsComboBox.currentText()
		
		if (selConn == ""):
			QgsMessageLog.logMessage("No database connection found...", "Data Manager")
			return()

		QgsMessageLog.logMessage(str(selConn), "Data Manager")
		
		self.layersTreeWidget.clear()
		self.connectingDatabase.emit(selConn)
		
	def closeEvent(self, event):
		self.closingPlugin.emit()
		event.accept()

