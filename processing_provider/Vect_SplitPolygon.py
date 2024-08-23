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

import os

from qgis.core import (
    QgsFeature, QgsGeometry, QgsField,
    QgsProject, QgsWkbTypes, QgsCoordinateTransform, QgsPropertyDefinition)

from qgis.core import (
    QgsProcessing,
    QgsProcessingParameters,
    QgsProcessingFeatureBasedAlgorithm,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum)

from qgis.core import QgsApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant, QCoreApplication

from becagis.becagislibrary.imgs import Imgs
from becagis.becagislibrary.geometry import split_polygon

class SplitPolygon(QgsProcessingFeatureBasedAlgorithm):
    """
    Algorithm to create split polygons into almost equal parts.
    """
    PARTS = 'PARTS'
    RANDOM_POINTS = 'RANDOM_POINTS'
    
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
        return 'Split Polygons'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_split_polygon.png'))
    
    def displayName(self):
        return self.tr('Split Polygons', 'Split Polygons')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('split polygons, voronoi diagram, k-mean clustering').split(',')
    
    txt_en = 'Split Polygons'
    txt_vi = 'Split Polygons'
    figure = 'images/tutorial/vect_split_polygon.png'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                    </div>
                    <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Thang Quach', 'Author: Thang Quach')+'''</b>
                      </p>'''+ social_BW + '''
                    </div>
                    '''
        return self.tr(self.txt_en, self.txt_vi) + footer    

    def inputLayerTypes(self):
        return [QgsProcessing.TypeVectorPolygon]

    def outputName(self):
        return self.tr('Output layer')
    
    def outputWkbType(self, input_wkb_type):
        return (input_wkb_type) 
        # return [QgsProcessing.TypeVectorPoint]
    
    def outputFields(self, input_fields):
        return(input_fields)

    def supportInPlaceEdit(self, layer):
        return False

    def initParameters(self, config=None):      
        param = QgsProcessingParameterNumber(
            self.PARTS,
            self.tr('Number of equal parts'),
            QgsProcessingParameterNumber.Integer,
            defaultValue=5,
            minValue=2,
            optional=False)
        param.setIsDynamic(True)
        param.setDynamicPropertyDefinition(QgsPropertyDefinition(
            self.PARTS,
            self.tr('Number of equal parts'),
            QgsPropertyDefinition.Integer))
        param.setDynamicLayerParameterName('INPUT')
        self.addParameter(param)

        param = QgsProcessingParameterNumber(
            self.RANDOM_POINTS,
            self.tr('Number of random points in each polygon'),
            QgsProcessingParameterNumber.Integer,
            defaultValue=1000,
            minValue=10,
            optional=False)
        param.setIsDynamic(True)
        param.setDynamicPropertyDefinition(QgsPropertyDefinition(
            self.RANDOM_POINTS,
            self.tr('Number of random points in each polygon'),
            QgsPropertyDefinition.Integer))
        param.setDynamicLayerParameterName('INPUT')
        self.addParameter(param)
    
     

    def prepareAlgorithm(self, parameters, context, feedback):
        self.parts = self.parameterAsInt(parameters, self.PARTS, context)  
        if self.parts <= 2:
            feedback.reportError('Number of of equal part must be at least 2')
            return False
        self.parts_dyn = QgsProcessingParameters.isDynamic(parameters, self.PARTS)
        if self.parts_dyn:
            self.parts_property = parameters[self.PARTS]

        self.random_points = self.parameterAsInt(parameters, self.RANDOM_POINTS, context)  
        if self.random_points < 10:
            feedback.reportError('Outer radius parameter must be at least 10')
            return False
        self.random_points_dyn = QgsProcessingParameters.isDynamic(parameters, self.RANDOM_POINTS)
        if self.random_points_dyn:
            self.random_points_property = parameters[self.RANDOM_POINTS]

       
        source = self.parameterAsSource(parameters, 'INPUT', context)
        
        self.src_crs = source.sourceCrs()        
        self.total_features = source.featureCount()
        self.num_bad = 0
        return True
    
    def processFeature(self, feature, context, feedback):         
        # return [feature]
        # Evaluate random_points
        if self.random_points_dyn:
            random_points_no, e = self.random_points_property.valueAsInt(context.expressionContext(), self.random_points)
            if not e or random_points_no < 10:
                self.num_bad += 1
                return []
        else:
            random_points_no = self.random_points
        
        # Evaluate parts
        if self.parts_dyn:
            parts_no, e = self.parts_property.valueAsInt(context.expressionContext(), self.parts)
            if not e or parts_no < 2:
                self.num_bad += 1
                return []
        else:
            parts_no = self.parts

        try:
            geom = feature.geometry()
            
            # Check if geometry is valid
            if geom.isEmpty() or not geom.isGeosValid():
                self.num_bad += 1
                feedback.reportError(f"Invalid geometry for feature {feature.id()}")
                return []
            
            attrs = feature.attributes()
            splitted_polygons = split_polygon(geom, random_points_no, parts_no)

            splitted_features = []
            for splitted_polygon in splitted_polygons:                
                splitted_geom = splitted_polygon  
                splitted_feature = QgsFeature()
                splitted_feature.setAttributes(attrs)
                splitted_feature.setGeometry(splitted_geom)
                splitted_features.append(splitted_feature)
            
            return splitted_features

        except Exception as e:
            self.num_bad += 1
            feedback.reportError(f"Error processing feature {feature.id()}: {str(e)}")
            return []

    def postProcessAlgorithm(self, context, feedback):
        if self.num_bad:
            feedback.pushInfo(self.tr("{} out of {} features had invalid parameters and were ignored.".format(self.num_bad, self.total_features)))
        return {}
