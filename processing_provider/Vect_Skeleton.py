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
from becagistools.becagislibrary.imgs import Imgs
from becagistools.becagislibrary.voronoi import *

import processing
from qgis.processing import alg
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
        return self.tr('Create Skeleton from Polygon', 'Create Skeleton from Polygon')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('skeleton, voronoi diagram').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_skeleton.png'))

    txt_en = 'Creat skeleton from Polygon layer'
    txt_vi = 'Creat skeleton from Polygon layer'
    figure = 'images/vect_skeleton.png'

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
    dest_id = None

    def initAlgorithm(self, config=None):

        self.addParameter(
            # QgsProcessingParameterVectorLayer(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Input Polygon Layer', 'Chọn lớp Polygon đầu vào'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )      
       

        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Skeleton Layer', 'Skeleton Layer')
            )
        )       
       
    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )       
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))      
        
        parts = self.parameterAsInt(
            parameters,
            self.PARTS,
            context
        )
        random_points = self.parameterAsInt(
            parameters,
            self.RANDOM_POINTS,
            context
        )


        input_layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)    
        # input_source = self.parameterAsSource(parameters, self.INPUT, context)
    
        mem_layers = []
        # if 
        total = 100.0 / input_layer.featureCount() if source.featureCount() else 0             
        print (input_layer)
        for feature in input_layer.getFeatures() :
            print (feature)            
            mem_layer = QgsVectorLayer('Polygon','polygon','memory')
            mem_layer.dataProvider().setEncoding(input_layer.dataProvider().encoding())
            mem_layer.setCrs(input_layer.crs())
            mem_layer_data = mem_layer.dataProvider()
            attr = input_layer.dataProvider().fields().toList()
            mem_layer_data.addAttributes(attr)
            mem_layer.updateFields()
            mem_layer.startEditing()
            mem_layer.addFeature(feature)
            mem_layer.commitChanges()
            mem_layers.append(hcmgis_split_polygon(mem_layer,parts,random_points)) 
            del(mem_layer)   
            if feedback.isCanceled():
                break
            # feedback.setProgress(int(current * total))        
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
        if feedback.isCanceled():
            return {}       
        return {self.OUTPUT: merge['OUTPUT']}
