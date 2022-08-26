# -*- coding: utf-8 -*-

"""
/***************************************************************************
 BecaGISTools
                                 A QGIS plugin
 GeoPorocessing Tools based on lftools https://github.com/LEOXINGU/lftools
                              -------------------
        Date                : 2022-08-25
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
"""

__author__ = 'Thang Quach'
__date__ = '2022-08-25'
__copyright__ = '(L) 2022 by Thang Quach'


from qgis.core import *
from qgis.gui import *
from qgis.utils import qgsfunction
from BecaGISTools.becagislibrary.latlong import (antipode as ANTIPODE)
group_name = 'BecaGIS Tools'
# https://qgis.org/pyqgis/3.2/core/Expression/QgsExpression.html

LOC = QgsApplication.locale()[:2]
def tr(*string):
    # Translate to Vietnamese: arg[0] - English (translate), arg[1] - Vietnamese
    if LOC == 'vi':
        if len(string) == 2:
            return string[1]
        else:
            return string[0]
    else:
        return string[0]

@qgsfunction(args='auto', group=group_name)
def antipode(lat,lon, feature, parent):
    """
    Calculate antipode from a (lat, long) input.

    <h4>Syntax</h4>
    <p><b>antipode</b>(<i>lat, long</i>) or <b>antipode</b>(<i>y, x</i>) in WGS84 CRS </p>

    <h4>Example usage</h4>
    <ul>
      <li><b>antipode</b>(10.784229903855978, 106.70356815497277) &rarr; returns a point geometry</li>
      <li><b>geom_to_wkt(antipode</b>(10.784229903855978, 106.70356815497277)) &rarr; 'Point (-73.29643185 -10.7842299)'</li>
    </ul>
    """
    antipode_lat,antipode_lon =  ANTIPODE(lat,lon)      
    antipode_point = QgsPointXY(antipode_lon, antipode_lat)
    return(QgsGeometry.fromPointXY(antipode_point))