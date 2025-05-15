# -*- coding: utf-8 -*-

"""
/***************************************************************************
 becagis
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
from PyQt5.QtWidgets import *
from qgis.core import (QgsProcessingAlgorithm,
                       QgsApplication,
                       QgsExpression)
# from PyQt5.QtCore import QCoreApplication

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from .becagis_provider import becagisProvider
from .expressions import *


exprs =(antipode,tcvn3_unicode,unicode_tcvn3,vni_unicode,unicode_vni,capitalize)

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class becagisPlugin(object):

    def __init__(self, iface):
        self.provider = None
        self.plugin_dir = os.path.dirname(__file__)
        self.iface = iface
        self.becagis_menu = None

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = becagisProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)


    def initGui(self):
        self.initProcessing()
        for expr in exprs:
            if not QgsExpression.isFunctionName(expr.name()):
                QgsExpression.registerFunction(expr)
        # self.becagis_menu = QMenu(QCoreApplication.translate("BecaGIS", "BecaGIS"))
        # self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.becagis_menu)
        
        # # OpenData_basemap submenu        
        # self.becagiscloud_menu = QMenu(u'BecaGIS Cloud')	
        # icon = QIcon(os.path.dirname(__file__) + "/images/becagis.svg")	
        # self.becagis_add_submenu2(self.becagiscloud_menu, icon)

        
        # # FontConverter Submenu
        # icon = QIcon(os.path.dirname(__file__) + "/images/becagis.svg")
        # self.becagiscloud_action = QAction(icon, u'BecaGIS Cloud', self.iface.mainWindow())
        # self.becagiscloud_action.triggered.connect(self.becagiscloud)
        # self.becagiscloud_menu.addAction(self.becagiscloud_action)	


    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
        for expr in exprs:
            if QgsExpression.isFunctionName(expr.name()):
                QgsExpression.unregisterFunction(expr.name())
        # if self.becagis_menu != None:
        #     self.iface.mainWindow().menuBar().removeAction(self.becagis_menu.menuAction())
        # else:
        #     self.iface.removePluginMenu("&BecaGIS", self.becagiscloud_menu.menuAction())          

    # def becagis_add_submenu(self, submenu):
    #     if self.becagis_menu != None:
    #         self.becagis_menu.addMenu(submenu)           
    #     else:
    #         self.iface.addPluginToMenu("&BecaGIS", submenu.menuAction())
    
    # def becagis_add_submenu2(self, submenu, icon):
    #     if self.becagis_menu != None:
    #         submenu.setIcon(QIcon(icon))
    #         self.becagis_menu.addMenu(submenu)           
    #     else:
    #         self.iface.addPluginToMenu("&BecaGIS", submenu.menuAction())  
    # def becagiscloud(self):
    #     # dialog = becagis_cloud_dialog(self.iface)
    #     # dialog.exec_()  
    #     return
   