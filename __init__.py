# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataManager
                                 A QGIS plugin
 This plugin manages  Layers, Tables, Joins and Relates in PostgreSQL/PostGIS database
                             -------------------
        begin                : 2016-11-08
        copyright            : (C) 2016 by George Ioannou / Cartologic
        email                : gmioannou@cartologic.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DataManager class from file DataManager.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .data_manager import DataManager
    return DataManager(iface)
