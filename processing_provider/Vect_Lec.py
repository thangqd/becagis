# -*- coding: utf-8 -*-


"""
Vect_Lec.py
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'Thang Quach'
__date__ = '2022-08-25'
__copyright__ = '(L) 2022, Thang Quach'

from qgis.PyQt.QtCore import QCoreApplication
# from qgis.core import (QgsApplication,
#                        QgsProcessingParameterVectorLayer,
#                        QgsGeometry,
#                        QgsProcessing,
#                        QgsProcessingParameterField,
#                        QgsProcessingParameterBoolean,
#                        QgsFeatureSink,
#                        QgsProcessingException,
#                        QgsProcessingAlgorithm,
#                        QgsProcessingParameterFeatureSource,
#                        QgsProcessingParameterFeatureSink)
from qgis.core import *
from becagis.becagislibrary.imgs import Imgs
from becagis.becagislibrary.voronoi import *

import processing
from qgis.processing import alg
import numpy as np
from pyproj.crs import CRS
import os
from qgis.PyQt.QtGui import QIcon

class Lec(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def translate(self, string):
        return QCoreApplication.translate('Processing', string)

    def tr(self, *string):
        # Translate to Vietnamese: arg[0] - English (translate), arg[1] - Vietnamese
        if self.LOC == 'vi':
            if len(string) == 2:
                return string[1]
            else:
                return self.translate(string[0])
        else:
            return self.translate(string[0])

    def createInstance(self):
        return Lec()

    def name(self):
        return 'lec'

    def displayName(self):
        return self.tr('Largest Empty Circle', 'Đường tròn rỗng lớn nhất')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('Lec, voronoi diagram').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_Lec.png'))

    txt_en = 'Find the largest empty circle of a Point layer'
    txt_vi = 'Tìm đường tròn rỗng lớn nhất của một tập điểm'
    figure = 'images/tutorial/vect_lec.png'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Thang Quach', 'Author: Thang Quach')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_vi) + footer


    INPUT = 'INPUT'
    CENTER = 'CENTER'
    LEC = 'LEC'
    UNIQUE_FIELD = 'UNIQUE_FIELD'    

    def initAlgorithm(self, config=None):

        self.addParameter(
            # QgsProcessingParameterFeatureSource(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Input Point Layer', 'Chọn lớp Point đầu vào'),
                [QgsProcessing.TypeVectorPoint]
            )
        )           
        
        self.addParameter(
            QgsProcessingParameterField(
                self.UNIQUE_FIELD,
                self.tr('Unique Field', 'Chọn trường khóa'),
                parentLayerParameterName = self.INPUT,
                defaultValue = None,
            )
        )
        
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                # QgsProcessingParameterFeatureSink(
                self.LEC,
                self.tr('Largest Empty Circle', 'Đường tròn rỗng lớn nhất')
            )
        )  
          
        self.addParameter(
             QgsProcessingParameterVectorDestination(
                # QgsProcessingParameterFeatureSink(
                self.CENTER,
                self.tr('Center of the Largest Empty Circle', 'Tâm đường tròn rỗng lớn nhất')
            )
        )  
        
    def processAlgorithm(self, parameters, context, feedback):       

        # source = self.parameterAsSource(
        source = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))       
        
        unique_field = self.parameterAsString(
            parameters,
            self.UNIQUE_FIELD,
            context)
        if unique_field is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.UNIQUE_FIELD))     

    # result = Lec(parameters[self.INPUT], unique_field) 

        center, lec_radius= lec(source, unique_field)
        extend = source.sourceExtent()
        y_max = extend.yMaximum()
        y_min = extend.yMinimum()

        if source.crs().isGeographic():
            EPSG = int(source.crs().authid().split(':')[-1])
            proj_crs = CRS.from_epsg(EPSG)
            a=proj_crs.ellipsoid.semi_major_metre
            f=1/proj_crs.ellipsoid.inverse_flattening
            e2 = f*(2-f)
            N = a/np.sqrt(1-e2*(np.sin((y_min+y_max)/2))**2) # Radius of curvature 1 degree vertical
            M = a*(1-e2)/(1-e2*(np.sin((y_min+y_max)/2))**2)**(3/2.) # Meridian Curvature Radius
            R = np.sqrt(M*N) # Gaussian mean radius
            theta_lec_radius  = lec_radius /R
            lec_radius  = format(np.degrees(theta_lec_radius),'f') # Radian to degree
        
        lec_center = processing.run(
            'qgis:deleteduplicategeometries',
            {
                # Here we pass on the original parameter values of INPUT
                # and BUFFER_OUTPUT to the buffer algorithm.
                'INPUT': center,
                'OUTPUT': parameters['CENTER'],
            },          
            is_child_algorithm=True,           
            context=context,
            feedback=feedback)

        largest_empty_circle = processing.run(
            'native:buffer',
            {
                # Here we pass on the original parameter values of INPUT
                # and BUFFER_OUTPUT to the buffer algorithm.
                'INPUT': lec_center['OUTPUT'],
                'OUTPUT': parameters['LEC'],
                'DISTANCE': lec_radius,
                'SEGMENTS': 64,
                'DISSOLVE': True,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 10
            },          
            is_child_algorithm=True,           
            context=context,
            feedback=feedback)
     
        return {self.CENTER: lec_center['OUTPUT'],
                self.LEC: largest_empty_circle['OUTPUT'] }