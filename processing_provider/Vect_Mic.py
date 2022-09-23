# -*- coding: utf-8 -*-


"""
Vect_Mic.py
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
from becagis.becagislibrary.geometry import mic
import processing
import string
from qgis.processing import alg
import os
from qgis.PyQt.QtGui import QIcon
from pyproj.crs import CRS
import numpy as np



class Mic(QgsProcessingAlgorithm):

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
        return Mic()

    def name(self):
        return 'mic'
        # name = "".join([
        #     character for character in self.displayName().lower()
        #     if character in string.ascii_letters
        # ])
        # return name

    def displayName(self):
        return self.tr('Maximum Inscribed Circle', 'Maximum Inscribed Circle')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('maximum inscribed circle').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_mic.png'))

    txt_en = 'Maximum inscribed circle of polygons'
    txt_vi = 'Maximum inscribed circle of polygons'
    figure = 'images/tutorial/vect_mic.png'

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
    MIC = 'MIC'
    TOLERANCE = 'TOLERANCE'
    SELECTED = 'SELECTED'

    dest_id = None

    def initAlgorithm(self, config=None):
        self.addParameter(
                QgsProcessingParameterVectorLayer(
            # QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Polygon Layer', 'Chọn lớp Polygon đầu vào'),
                types=[QgsProcessing.TypeVectorPolygon],
                defaultValue=None
            )
        )      
       
        
        self.addParameter(
           QgsProcessingParameterBoolean(
                self.SELECTED,
                self.tr('Selected features only', 'Chỉ những đối tượng được chọn'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.CENTER,
                self.tr('Center of MIC', 'Center of MIC')
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.MIC,
                self.tr('Maximum Inscribed Circle', 'Maximum Inscribed Circle')
            )
        )
       
        self.addParameter(
            QgsProcessingParameterNumber(
                self.TOLERANCE,
                self.tr('Tolerance (m)', 'Tolerance (m)'),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.1, 
                maxValue=100, 
                defaultValue=0.1             
                )  
            )
        

    def processAlgorithm(self, parameters, context, feedback):
       
        input_layer = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )
        if input_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))   

        selected = self.parameterAsBool(
            parameters,
            self.SELECTED,
            context            
        )
        if selected is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SELECTED))
 
        
        tolerance = self.parameterAsDouble(
            parameters,
            self.TOLERANCE,
            context
        )
       
        if not selected:
            features = input_layer.getFeatures()
            feature_count = input_layer.featureCount() 
        else:
            features = input_layer.getSelectedFeatures()
            feature_count = input_layer.selectedFeatureCount()

        extend = input_layer.sourceExtent()
        y_max = extend.yMaximum()
        y_min = extend.yMinimum()

        if input_layer.crs().isGeographic():
            EPSG = int(input_layer.crs().authid().split(':')[-1])
            proj_crs = CRS.from_epsg(EPSG)
            a=proj_crs.ellipsoid.semi_major_metre
            f=1/proj_crs.ellipsoid.inverse_flattening
            e2 = f*(2-f)
            N = a/np.sqrt(1-e2*(np.sin((y_min+y_max)/2))**2) # Radius of curvature 1 degree vertical
            M = a*(1-e2)/(1-e2*(np.sin((y_min+y_max)/2))**2)**(3/2.) # Meridian Curvature Radius
            R = np.sqrt(M*N) # Gaussian mean radius
            theta_tolerance  = tolerance /R
            tolerance_degree  = format(np.degrees(theta_tolerance),'f') # Radian to degree
            tolerance  = tolerance_degree         
        total = 100.0 / feature_count if feature_count else 0
        if (feature_count<=0): 
            return {} 
        else:
            count = 0
            mem_layers = [] 
            ids = [f.id() for f in features]
            for id in ids:
                input_layer.selectByIds([id])
                selected_feature = QgsProcessingFeatureSourceDefinition(input_layer.id(), True)
                mem_layers.append(mic(selected_feature, tolerance))
                count+=1
                if feedback.isCanceled():
                    return {}   
                feedback.setProgress(int(count * total))             

            center = processing.run(
                'native:mergevectorlayers',
                {
                    'LAYERS': mem_layers,                
                    'OUTPUT' : parameters[self.CENTER]           
                },
                
                is_child_algorithm=True,
                #
                # It's important to pass on the context and feedback objects to
                # child algorithms, so that they can properly give feedback to
                # users and handle cancelation requests.
                context=context,
                feedback=feedback)
            del(mem_layers)             

            _mic = processing.run(
            'native:buffer',
            {
                # Here we pass on the original parameter values of INPUT
                # and BUFFER_OUTPUT to the buffer algorithm.
                'INPUT': center['OUTPUT'],
                'OUTPUT': parameters[self.MIC],
                'DISTANCE': QgsProperty.fromExpression('"dist_pole"') ,
                'SEGMENTS': 64,
                'DISSOLVE': False,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 2
            },          
            is_child_algorithm=True,           
            context=context,
            feedback=feedback)
            return {self.CENTER: center['OUTPUT'],
                    self.MIC: _mic['OUTPUT']}          