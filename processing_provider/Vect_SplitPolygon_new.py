# -*- coding: utf-8 -*-


"""
Vect_SpiralWedge.py
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
from geographiclib.geodesic import Geodesic

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

from becagis.becagislibrary.geometry import wedge_buffer, meters_to_geographic_distance
from becagis.becagislibrary.imgs import Imgs

class SplitPolygon_new(QgsProcessingFeatureBasedAlgorithm):
    """
    Split Polygon layer into almost equal parts.
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
        return SplitPolygon_new()

    def name(self):
        return 'Split Polygon New'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_split_polygon.png'))
    
    def displayName(self):
        return self.tr('Split Polygon New', 'Split Polygon New')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('Split Polygon, Equal parts').split(',')
    
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
                      </p>'''+ social_BW + '''
                    </div>
                    '''
        return self.tr(self.txt_en, self.txt_vi) + footer    

    def inputLayerTypes(self):
        return [QgsProcessing.TypeVectorPolygon]

    def outputName(self):
        return self.tr('Output layer')
    
    def outputWkbType(self, input_wkb_type):
        return (QgsWkbTypes.Polygon)   

    def outputFields(self, input_fields):
        # input_fields.append(QgsField("part_id", QVariant.Int))
        return(input_fields)

    def supportInPlaceEdit(self, layer):
        return False

    def initParameters(self, config=None):      
        param = QgsProcessingParameterNumber(
            self.PARTS,
            self.tr('Number of parts to split'),
            QgsProcessingParameterNumber.Integer,
            defaultValue=5,
            minValue=1,
            optional=False)
        param.setIsDynamic(True)
        param.setDynamicPropertyDefinition(QgsPropertyDefinition(
            self.PARTS,
            self.tr('Number of parts to split'),
            QgsPropertyDefinition.Integer))
        param.setDynamicLayerParameterName('INPUT')
        self.addParameter(param)

        param = QgsProcessingParameterNumber(
            self.RANDOM_POINTS,
            self.tr('Number of random points'),
            QgsProcessingParameterNumber.Integer,
            defaultValue = 1000,
            minValue=10,  
            optional=False)
        param.setIsDynamic(True)
        param.setDynamicPropertyDefinition(QgsPropertyDefinition(
            self.RANDOM_POINTS,
            self.tr('Number of random points'),
            QgsPropertyDefinition.Double))
        param.setDynamicLayerParameterName('INPUT')
        self.addParameter(param)
        
    def prepareAlgorithm(self, parameters, context, feedback):
        self.part_no = self.parameterAsInt(parameters, self.PARTS, context)  
        if self.part_no <= 1:
            feedback.reportError('Outer radius parameter must be greater than 0')
            return False
        self.part_no_dyn = QgsProcessingParameters.isDynamic(parameters, self.PARTS)
        if self.part_no_dyn:
            self.part_no_property = parameters[self.PARTS]
        
        self.point_no = self.parameterAsInt(parameters, self.RANDOM_POINTS, context) 
        if self.point_no < 10:
            feedback.reportError('Outer radius parameter must be equal or greater than 10')
            return False
        self.point_no_dyn = QgsProcessingParameters.isDynamic(parameters, self.RANDOM_POINTS)
        if self.point_no_dyn:
            self.point_no_property = parameters[self.RANDOM_POINTS]

        source = self.parameterAsSource(parameters, 'INPUT', context)       
     
        self.total_features = source.featureCount()
        self.num_bad = 0
        return True
    
    def processFeature(self, feature, context, feedback):         
        return [feature]
        # try:
        #     # Evaluate outer radius
        #     if self.outer_radius_dyn:
        #         outer_rad, e = self.outer_radius_property.valueAsDouble(context.expressionContext(), self.outer_radius)
        #         if self.src_crs.isGeographic():
        #             outer_rad = meters_to_geographic_distance(outer_rad, self.src_crs, self.src_extend)
        #         if not e or outer_rad < 0:
        #             self.num_bad += 1
        #             return []
        #     else:
        #         outer_rad = self.outer_radius

        #     # Evaluate inner radius
        #     if self.inner_radius_dyn:
        #         inner_rad, e = self.inner_radius_property.valueAsDouble(context.expressionContext(), self.inner_radius)
        #         if self.src_crs.isGeographic():
        #             inner_rad = meters_to_geographic_distance(inner_rad, self.src_crs, self.src_extend)
        #         if not e or inner_rad < 0:
        #             self.num_bad += 1
        #             return []
        #     else:
        #         inner_rad = self.inner_radius
            
        #     if self.sectnum_dyn:
        #         sect_num, e = self.sectnum_property.valueAsInt(context.expressionContext(), self.sectnum)
        #         if not e or sect_num <= 1:
        #             self.num_bad += 1
        #             return []
        #     else:
        #         sect_num = self.sectnum

        #     if self.azimuth_dyn:
        #         azimuth_degree, e = self.azimuth_property.valueAsDouble(context.expressionContext(), self.azimuth)
        #         if not e:
        #             self.num_bad += 1
        #             return []
        #     else:
        #         azimuth_degree = self.azimuth

        #     seg_num = self.segnum

        #     # Generate wedge geometries using the evaluated radii
        #     geom = feature.geometry()           
        #     attrs = feature.attributes()
        #     wedge_geoms = wedge_buffer(geom, outer_rad, inner_rad, sect_num, azimuth_degree, seg_num)
            
        #     wedge_features = []
        #     for wedge in wedge_geoms:
        #         wedge_geom = wedge['geometry']
        #         wedge_id = wedge['wedge_id']                
        #         wedge_feature = QgsFeature()                
        #         wedge_feature.setAttributes(attrs + [wedge_id])         
        #         wedge_feature.setGeometry(wedge_geom) 
        #         wedge_features.append(wedge_feature)
                
        #     return wedge_features        
        
        # except Exception as e:
        #     self.num_bad += 1
        #     feedback.reportError(f"Error processing feature {feature.id()}: {str(e)}")
        #     return []


    def postProcessAlgorithm(self, context, feedback):
        if self.num_bad:
            feedback.pushInfo(self.tr("{} out of {} features had invalid parameters and were ignored.".format(self.num_bad, self.total_features)))
        return {}
