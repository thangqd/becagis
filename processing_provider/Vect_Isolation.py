# -*- coding: utf-8 -*-


"""
Vect_Isolation.py
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

class Isolation(QgsProcessingAlgorithm):

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
        return Isolation()

    def name(self):
        return 'isolation'

    def displayName(self):
        return self.tr('Isolation', 'Isolation')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('Isolation, voronoi diagram').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_isolation.png'))

    txt_en = 'Find the most isolated point of a Point layer'
    txt_vi = 'Find the most isolated point of a Point layer'
    figure = 'images/tutorial/vect_isolation.png'

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
    OUTPUT = 'OUTPUT'
    CIRCLE = 'CIRCLE'
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
            # QgsProcessingParameterVectorDestination(
                QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Isolated Point', 'Isolated Point')
            )
        )  
          
        self.addParameter(
             QgsProcessingParameterVectorDestination(
                # QgsProcessingParameterFeatureSink(
                self.CIRCLE,
                self.tr('Circle', 'Circle')
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

    # result = isolation(parameters[self.INPUT], unique_field) 

        isolated_field, max_distance= isolation(parameters[self.INPUT], parameters[self.UNIQUE_FIELD])
        
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
            theta_max_distance = max_distance/R
            max_distance = format(np.degrees(theta_max_distance),'f') # Radian to degree
               
        isolated = processing.run(
                'native:extractbyattribute',
                {
                    'INPUT': parameters[self.INPUT],   
                    'FIELD': unique_field ,
                    'OPERATOR':0, # =
                    'VALUE': isolated_field,
                    'OUTPUT' : parameters[self.OUTPUT]           
                },
                
                is_child_algorithm=True,
                #
                # It's important to pass on the context and feedback objects to
                # child algorithms, so that they can properly give feedback to
                # users and handle cancelation requests.
                context=context,
                feedback=feedback)
                
        circle = processing.run(
            'native:buffer',
            {
                # Here we pass on the original parameter values of INPUT
                # and BUFFER_OUTPUT to the buffer algorithm.
                'INPUT': isolated['OUTPUT'],
                'OUTPUT': parameters['CIRCLE'],
                'DISTANCE': max_distance,
                'SEGMENTS': 64,
                'DISSOLVE': True,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 10
            },          
            is_child_algorithm=True,           
            context=context,
            feedback=feedback)
     
        return {self.OUTPUT: isolated['OUTPUT'],
                self.CIRCLE: circle['OUTPUT'] }
