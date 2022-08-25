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
from BecaGISTools.geocapt.topogeo import (dd2dms as DD2DMS,
                                     dms2dd as DMS2DD, to_do as TO_DO)
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

@qgsfunction(args='auto', group='BecaGIS Tools')
def dd2dms(dd, n_digits, feature, parent):
    """
    Transform decimal degrees to degrees, minutes and seconds.
    <h2>Example usage:</h2>
    <ul>
      <li>dd2dms(dd, 3) -> -12°12'34.741"</li>
    </ul>
    """
    return DD2DMS(dd, n_digits)


@qgsfunction(args='auto', group='BecaGIS Tools')
def dms2dd(txt, feature, parent):
    """
    Transform degrees, minutes, seconds coordinate to decimal degrees.
    <h2>Example usage:</h2>
    <ul>
      <li>dms2dd("dms") -> dd</li>
      <li>dms2dd('-10d30m00.0s') -> -10.5</li>
    </ul>
    """
    return DMS2DD(txt)

@qgsfunction(args='auto', group='BecaGIS Tools')
def to_do(digit, feature, parent):
    """
    Convert digit to string
    <h2>Example usage:</h2>
    <ul>
      <li>to_do(digit) -> 'digit'</li>
    </ul>
    """
    return TO_DO(digit)