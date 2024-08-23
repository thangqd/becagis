# -*- coding: utf-8 -*-


"""
Vect_SplitPolygon.py
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
import string
from qgis.processing import alg
import os
from qgis.PyQt.QtGui import QIcon

class SplitPolygon(QgsProcessingAlgorithm):

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
        return SplitPolygon()

    def name(self):
        return 'splitpolygon'
        # name = "".join([
        #     character for character in self.displayName().lower()
        #     if character in string.ascii_letters
        # ])
        # return name

    def displayName(self):
        return self.tr('Split Polygon', 'Split Polygon')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('split polygon, voronoi diagram').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_split_polygon.png'))

    txt_en = 'Split Polygon layer into almost equal parts using Voronoi Diagram'
    txt_vi = 'Split Polygon layer into almost equal parts using Voronoi Diagram'
    figure = 'images/tutorial/vect_split_polygon.png'

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
    PARTS = 'PARTS'
    RANDOM_POINTS = 'RANDOM_POINTS'
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
                self.OUTPUT,
                self.tr('Splitted Layer', 'Splitted Layer')
            )
        )
       
        self.addParameter(
            QgsProcessingParameterNumber(
                self.PARTS,
                self.tr('Number of equal parts', 'Số Polygon'),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue = 5,
                optional=False,
                minValue=1              
                )  
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.RANDOM_POINTS,
                self.tr('Number of random points', 'Số điểm ngẫu nhiên trong Polygon'),
                QgsProcessingParameterNumber.Integer,
                defaultValue = 1000,
                minValue=10,  
                )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # source = self.parameterAsSource(
        #     parameters,
        #     self.INPUT,
        #     context
        # )       
        # if source is None:
        #     raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))  
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
        if not selected:
            features = input_layer.getFeatures()
            feature_count = input_layer.featureCount() 
        else:
            features = input_layer.getSelectedFeatures()
            feature_count = input_layer.selectedFeatureCount()
            
        total = 100.0 / feature_count if feature_count else 0
        if (feature_count<=0): 
            return {} 
        else:
            count = 0
            mem_layers = []  
            ids = [f.id() for f in features]
            for id in ids:
                input_layer.selectByIds([id])
                sourceDef = QgsProcessingFeatureSourceDefinition(input_layer.id(), True)
                mem_layers.append(splitpolygon(sourceDef,parts,random_points))
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
