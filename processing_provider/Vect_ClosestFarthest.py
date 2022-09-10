# -*- coding: utf-8 -*-

"""
Vect_ClosestFarthest.py
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
import numpy as np
from pyproj.crs import CRS
import os
from qgis.PyQt.QtGui import QIcon

class ClosestFarthest(QgsProcessingAlgorithm):

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
        return ClosestFarthest()

    def name(self):
        return 'closestfarthest'

    def displayName(self):
        return self.tr('Closest and farthest pair of Points', 'Tìm cặp điểm gần nhất và xa nhất của một tập điểm')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('Closest pair of points, fartherst pair of points, voronoi diagram').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_closestfarthest.png'))

    txt_en = 'Closest and farthest pair of Points of a Point layer'
    txt_vi = 'Cặp điểm gần nhất và xa nhất của một tập điểm'
    figure = 'images/tutorial/vect_closestfarthest.png'

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
    UNIQUE_FIELD = 'UNIQUE_FIELD'  
    CLOSEST = 'CLOSEST'
    FARTHEST = 'FARTHEST'
      
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
                self.CLOSEST,
                self.tr('Closest pair of Points', 'Cặp điểm gần nhất')
            )
        )  
          
        self.addParameter(
             QgsProcessingParameterVectorDestination(
                # QgsProcessingParameterFeatureSink(
                self.FARTHEST,
                self.tr('Farthest pair of Points', 'Cặp điểm xa nhất')
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
  

        closest, farthest= closestfarthest(source, unique_field)       
          
        closest.startEditing() 
        closest.dataProvider().addAttributes([QgsField("length",  QVariant.Double)]) # define/add field data type
        closest.updateFields() # tell the vector layer to fetch changes from the provider    
        fieldnumber =closest.fields().count()    
        for feature in  closest.getFeatures():   
            d = QgsDistanceArea()
            length = d.convertLengthMeasurement(d.measureLength(feature.geometry()),0) #convert to meters
            closest.changeAttributeValue(feature.id(), fieldnumber-1,length )
        closest.commitChanges()     
        
        values = []
        idx =  closest.dataProvider().fieldNameIndex("length")
        for feat in closest.getFeatures():
            attrs = feat.attributes()
            values.append(attrs[idx]) 
        min_value = min(values)	
        closest_pair = processing.run(
        'native:extractbyattribute',
        {
            # Here we pass on the original parameter values of INPUT
            # and BUFFER_OUTPUT to the buffer algorithm.
            'INPUT': closest,
            'FIELD': 'length',
            'OPERATOR':0, # =
            'VALUE': min_value,
            'OUTPUT': parameters['CLOSEST'],
        },          
        is_child_algorithm=True,           
        context=context,
        feedback=feedback)

        
        farthest.startEditing()
        farthest.dataProvider().addAttributes([QgsField("length",  QVariant.Double)]) # define/add field data type
        farthest.updateFields() # tell the vector layer to fetch changes from the provider    
        fieldnumber =farthest.fields().count()    
        for feature in  farthest.getFeatures():   
            d = QgsDistanceArea()
            length = d.convertLengthMeasurement(d.measureLength(feature.geometry()),0) #convert to meters
            farthest.changeAttributeValue(feature.id(), fieldnumber-1,length )  
        farthest.commitChanges()

        values = []
        idx =  farthest.dataProvider().fieldNameIndex("length")
        for feat in farthest.getFeatures():
            attrs = feat.attributes()
            values.append(attrs[idx]) 
        max_value = max(values)	
        farthest_pair = processing.run(
        'native:extractbyattribute',
        {
            # Here we pass on the original parameter values of INPUT
            # and BUFFER_OUTPUT to the buffer algorithm.
            'INPUT': farthest,
            'FIELD': 'length',
            'OPERATOR':0, # =
            'VALUE': max_value,
            'OUTPUT': parameters['FARTHEST'],
        },          
        is_child_algorithm=True,           
        context=context,
        feedback=feedback)

        return {self.CLOSEST: closest_pair['OUTPUT'],
                self.FARTHEST: farthest_pair['OUTPUT']}