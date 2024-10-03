# -*- coding: utf-8 -*-


"""
Vect_Skeleton.py
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

class Skeleton(QgsProcessingAlgorithm):

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
        return Skeleton()

    def name(self):
        return 'skeleton'

    def displayName(self):
        return self.tr('Skeleton', 'Skeleton')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('skeleton, voronoi diagram').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_skeleton.png'))

    txt_en = 'Skeleton of a Polygon layer'
    txt_vi = 'Skeleton of a Polygon layer'
    figure = 'images/tutorial/vect_skeleton.png'

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
    DENSITY = 'DENSITY'
    SELECTED = 'SELECTED'
    UNIQUE_FIELD = 'UNIQUE_FIELD'
    dest_id = None

    def initAlgorithm(self, config=None):

        self.addParameter(
            # QgsProcessingParameterVectorLayer(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Input Polygon Layer (please select 1..20 features)', 'Chọn lớp Polygon đầu vào (Chọn 1 đến 20 đối tượng)'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )           
        
        # self.addParameter(
        #    QgsProcessingParameterBoolean(
        #         self.SELECTED,
        #         self.tr('Selected features only', 'Chỉ những đối tượng được chọn'),
        #         defaultValue=True
        #     )
        # )
        self.addParameter(
        QgsProcessingParameterNumber(
            self.DENSITY,
            self.tr('Density (m)', 'Mật độ điểm'),
            type=QgsProcessingParameterNumber.Double, 
            minValue=0, 
            maxValue=100000, 
            defaultValue=1
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
                self.OUTPUT,
                self.tr('Skeleton Layer', 'Skeleton Layer')
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

        # selected = self.parameterAsBool(
        #     parameters,
        #     self.SELECTED,
        #     context            
        # )
        # if selected is None:
        #     raise QgsProcessingException(self.invalidSourceError(parameters, self.SELECTED))
        
        unique_field = self.parameterAsString(
            parameters,
            self.UNIQUE_FIELD,
            context)
        if unique_field is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.UNIQUE_FIELD))
        
        density = self.parameterAsDouble(
            parameters,
            self.DENSITY,
            context)

        if density is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DENSITY))         
    
        # if selected:
            # features = input_layer.getFeatures()
            # feature_count = input_layer.featureCount() 
        features = input_layer.getSelectedFeatures()
        feature_count = input_layer.selectedFeatureCount()
        msg = str(feature_count) + ' features selected. Please select 1..20 features to create Skeleton!'
        if feature_count < 1 or feature_count > 100:
            raise QgsProcessingException(msg)             
        # else:            
        #     raise QgsProcessingException(msg)
        
        tolerance = 0.1 # for simplify geometry
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
            theta_density = density/R
            theta_tolerance = tolerance/R
            if (density > 0):
                density = format(np.degrees(theta_density),'f') # Radian to degree
            tolerance = format(np.degrees(theta_tolerance),'f')# Radian to degree
            print (density)
            # print (tolerance)
        
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
                ########## Percent of length instead of fixed value
                mem_layers.append(skeleton(selected_feature, unique_field, density, tolerance))
                count+=1
                if feedback.isCanceled():
                    return {}   
                feedback.setProgress(int(count * total))        
            merge = processing.run(
                'native:mergevectorlayers',
                {
                    'LAYERS': mem_layers,                
                    'OUTPUT' : parameters[self.OUTPUT]           
                },
                
                is_child_algorithm=True,
                #
                # It's important to pass on the context and feedback objects to
                # child algorithms, so that they can properly give feedback to
                # users and handle cancelation requests.
                context=context,
                feedback=feedback)
            del(mem_layers)
            return {self.OUTPUT: merge['OUTPUT']}