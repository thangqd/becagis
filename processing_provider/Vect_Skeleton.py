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

from becagis.becagislibrary.geometry import skeleton, meters_to_geographic_distance
from becagis.becagislibrary.imgs import Imgs


class Skeleton(QgsProcessingFeatureBasedAlgorithm):
    """
    Algorithm to create Skeleton of Polygons.
    """
    DENSITY = 'DENSITY'
    POSTPROCESSING = 'POSTPROCESSING'
    
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
        return 'Skeleton'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_skeleton.png'))
    
    def displayName(self):
        return self.tr('Skeleton', 'Skeleton')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('Skeleton, Vornoi Diagram').split(',')
    
    txt_en = 'Skeleton'
    txt_vi = 'Skeleton'
    figure = 'images/tutorial/vect_skeleton.png'

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
        return (QgsWkbTypes.MultiLineString)   
        # return (QgsWkbTypes.Point)   
    
    def outputFields(self, input_fields):
        return(input_fields)

    def supportInPlaceEdit(self, layer):
        return False

    def initParameters(self, config=None):      
        param = QgsProcessingParameterNumber(
            self.DENSITY,
            self.tr('Density (meters)'),
            QgsProcessingParameterNumber.Double,
            defaultValue=1,
            minValue= 0,
            optional=False)
        param.setIsDynamic(True)
        param.setDynamicPropertyDefinition(QgsPropertyDefinition(
            self.DENSITY,
            self.tr('Density (meters)'),
            QgsPropertyDefinition.Double))
        param.setDynamicLayerParameterName('INPUT')
        self.addParameter(param)

        # Postprocessing
        param = QgsProcessingParameterBoolean(
            self.POSTPROCESSING,  
            self.tr('Postprocessing to get Centerlines from Skeletons'), 
            defaultValue=True 
        )
        
        self.addParameter(param)

    def prepareAlgorithm(self, parameters, context, feedback):
        self.density = self.parameterAsDouble(parameters, self.DENSITY, context)  
        if self.density < 0:
            feedback.reportError('Density parameter must be at least 0')
            return False
        self.density_dyn = QgsProcessingParameters.isDynamic(parameters, self.DENSITY)
        if self.density_dyn:
            self.density_dyn_property = parameters[self.DENSITY]
     
        self.postprocessing = self.parameterAsBoolean(parameters, self.POSTPROCESSING, context)


        source = self.parameterAsSource(parameters, 'INPUT', context)
        
        self.src_crs = source.sourceCrs()        
        self.src_extent = source.sourceExtent()
        if self.src_crs.isGeographic():
            self.density = meters_to_geographic_distance(self.density, self.src_crs, self.src_extent)

        self.total_features = source.featureCount()
        self.num_bad = 0
        return True
    
    def processFeature(self, feature, context, feedback):         
        # return [feature]
        try:
            # Evaluate density
            if self.density_dyn:
                density_dist, e = self.density_dyn_property.valueAsDouble(context.expressionContext(), self.density)
                if self.src_crs.isGeographic():
                    density_dist = meters_to_geographic_distance(density_dist, self.src_crs, self.src_extent)
                if not e or density_dist < 0:
                    self.num_bad += 1
                    return []
            else:
                density_dist = self.density
            

            # Evaluate simplified tolerance
            simplified_tol =  density_dist/3

            # Evaluate postprocessing
            postprocessing = self.postprocessing

            # Generate skeleton
            geom = feature.geometry()           
            attrs = feature.attributes()
            ske_geoms = skeleton(geom, density_dist, simplified_tol, postprocessing)
            # feedback.pushInfo(ske_geoms.geometry().asWkt())
            ske_features = []
            for ske in ske_geoms:
                ske_geom = ske.geometry()
                # feedback.pushInfo(ske.geometry().asWkt())
                ske_feature = QgsFeature()                
                ske_feature.setAttributes(attrs)         
                ske_feature.setGeometry(ske_geom) 
                ske_features.append(ske_feature)
                
            return ske_features        
        
        except Exception as e:
            self.num_bad += 1
            feedback.reportError(f"Error processing feature {feature.id()}: {str(e)}")
            return []


    def postProcessAlgorithm(self, context, feedback):
        if self.num_bad:
            feedback.pushInfo(self.tr("{} out of {} features had invalid parameters and were ignored.".format(self.num_bad, self.total_features)))
        return {}