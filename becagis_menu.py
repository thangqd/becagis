#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------
#    becagis_menu - QGIS plugins menu class
#
#    begin                : 01/02/2018
#    copyright            : (c) 2018 by Quach Dong Thang
#    email                : quachdongthang@gmail.com
# --------------------------------------------------------

"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License v3.0.            *
 *                                                                         *
 ***************************************************************************/
 """

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from PyQt5.QtWidgets import *
import os 

# from .becagis_dialogs import *
# from .becagis_library import *

# ---------------------------------------------
class becagis_menu ():
    def __init__(self, iface):
        self.iface = iface
        self.becagis_menu = None

    def becagis_add_submenu(self, submenu):
        if self.becagis_menu != None:
            self.becagis_menu.addMenu(submenu)           
        else:
            self.iface.addPluginToMenu("&BecaGIS", submenu.menuAction())
    
    def becagis_add_submenu2(self, submenu, icon):
        if self.becagis_menu != None:
            submenu.setIcon(QIcon(icon))
            self.becagis_menu.addMenu(submenu)           
        else:
            self.iface.addPluginToMenu("&BecaGIS", submenu.menuAction())

    def initGui(self):
        # Uncomment the following two lines to have becagis accessible from a top-level menu
        self.becagis_menu = QMenu(QCoreApplication.translate("BecaGIS", "BecaGIS"))
        self.iface.mainWindow().menuBar().insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.becagis_menu)
        
        # OpenData_basemap submenu        
        self.becagiscloud_menu = QMenu(u'BecaGIS Cloud')	
        icon = QIcon(os.path.dirname(__file__) + "/images/becagis_logo.png")	
        self.becagis_add_submenu2(self.becagiscloud_menu, icon)

        
        # FontConverter Submenu
        icon = QIcon(os.path.dirname(__file__) + "/images/becagis_logo.png")
        self.becagiscloud_action = QAction(icon, u'BecaGIS Cloud', self.iface.mainWindow())
        self.becagiscloud_action.triggered.connect(self.becagiscloud)
        self.becagiscloud_menu.addAction(self.becagiscloud_action)	

        
        
    def unload(self):
        if self.becagis_menu != None:
            self.iface.mainWindow().menuBar().removeAction(self.becagis_menu.menuAction())
        else:
            self.iface.removePluginMenu("&becagis", self.becagiscloud_menu.menuAction())            
         
    
    ##########################	
    def becagiscloud(self):
        # dialog = becagis_cloud_dialog(self.iface)
        # dialog.exec_()  
        return
   