# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataManager
								 A QGIS plugin
 This plugin manages Layers, Tables, Joins and Relates in PostgreSQL/PostGIS database
							  -------------------
		begin				 : 2016-10-28
		git sha				 : $Format:%H$
		copyright			 : (C) 2016 by George Ioannou
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
import psycopg2
from qgis.core import QgsMessageLog

class Pgdb:

	def __init__(self):
		"""Constructor."""
		self.database = ''
		self.host = ''
		self.port = ''
		self.username = ''
		self.password = ''

		self.dbcon = None
		self.schemata = []

		QgsMessageLog.logMessage('Initializing Pgdb...', 'Data Manager')

	def connect(self):
		"""Connect to the database"""
		conn_string = "dbname='{0}' \
					host='{1}' \
					port='{2}' \
					user='{3}' \
					password='{4}'".format(self.database, self.host, self.port, self.username, self.password)

		try:
			self.dbcon = psycopg2.connect(conn_string)
			QgsMessageLog.logMessage('Connected to database ' + self.database, 'Data Manager')
		except:
			print "Unable to connect to database"
			exit(1)

	def init_schemata(self):
		"""Init the database schemata and update its own propery list"""
		cur = self.dbcon.cursor()

		sql_string = "\
			SELECT schema_name \
			  FROM information_schema.schemata \
             WHERE schema_name <> 'information_schema' \
               AND schema_name NOT LIKE 'pg_%' \
			 ORDER BY schema_name;"

		cur.execute(sql_string)
		rows = cur.fetchall()

		self.schemata = [row[0] for row in rows]

		cur.close()

	def get_layers(self, schema):
		"""Get layers list from the database and return to the calling process"""
		cur = self.dbcon.cursor()

		sql_string = "\
			SELECT info.table_schema, \
				   info.table_name, \
				   geom.f_geometry_column, \
				   geom.srid, \
				   geom.type \
			  FROM information_schema.tables info \
		 LEFT JOIN geometry_columns geom \
				ON info.table_schema = geom.f_table_schema \
			   AND info.table_name = geom.f_table_name \
			 WHERE table_schema = '{0}' \
		  ORDER BY table_schema, table_name;".format(schema)

		cur.execute(sql_string)
		layers = cur.fetchall()

		cur.close()

		return(layers)

	def get_joined_tables(self, schema, layer):
		"""Get joined tables list from the database and return to the calling process"""
		cur = self.dbcon.cursor()

		sql_joins = "\
			SELECT * \
			  FROM foreign_key_constraints_vw \
			 WHERE table_schema = '{0}' and table_name = '{1}';".format(schema, layer)

		cur.execute(sql_joins)
		rows = cur.fetchall()

		cur.close()

		return(rows)

	def get_related_tables(self, schema, layer):
		"""Get related tables list from the database and return to the calling process"""
		cur = self.dbcon.cursor()

		sql_relations = "\
			SELECT * \
			  FROM foreign_key_constraints_vw \
			 WHERE f_table_schema = '{0}' and f_table_name = '{1}';".format(schema, layer)

		cur.execute(sql_relations)
		rows = cur.fetchall()

		cur.close()

		return(rows)
