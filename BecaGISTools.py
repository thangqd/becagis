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

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys
import inspect

from qgis.core import (QgsProcessingAlgorithm,
                       QgsApplication,
                       QgsExpression)
from PyQt5.QtCore import QCoreApplication
from .BecaGISTools_provider import BecaGISToolsProvider
from .expressions import *

exprs = (dd2dms, dms2dd,to_do)

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class BecaGISToolsPlugin(object):

    def __init__(self):
        self.provider = None
        self.plugin_dir = os.path.dirname(__file__)

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = BecaGISToolsProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)


    def initGui(self):
        self.initProcessing()
        for expr in exprs:
            if not QgsExpression.isFunctionName(expr.name()):
                QgsExpression.registerFunction(expr)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
        for expr in exprs:
            if QgsExpression.isFunctionName(expr.name()):
                QgsExpression.unregisterFunction(expr.name())
