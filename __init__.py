# -*- coding: utf-8 -*-

"""
/***************************************************************************
 BecaGISTools
                                 A QGIS plugin
 Tools for Geoprocessing in QGIS.
                              -------------------
        begin                : 2022-08-25
        copyright            : (L) 2022 by Thang Quach
        email                : quachdongthang@gmail.com
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

__author__ = 'Thang Quach'
__date__ = '2022-08-25'
__copyright__ = '(L) 2022 by Thang Quach'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load BecaGISTools class from file BecaGISTools.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .BecaGISTools import BecaGISToolsPlugin
    return BecaGISToolsPlugin()
