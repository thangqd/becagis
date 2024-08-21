# -*- coding: utf-8 -*-


"""
Vect_Wedge.py
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


from qgis.core import (
    QgsField,  QgsWkbTypes, QgsPropertyDefinition)

from qgis.core import (
    QgsFeature,
    QgsProcessing,
    QgsProcessingParameters,
    QgsProcessingFeatureBasedAlgorithm,
    QgsProcessingParameterNumber
    )
from qgis.core import QgsApplication

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication,QVariant, QUrl

from becagis.becagislibrary.imgs import Imgs
from becagis.becagislibrary.geometry import wedge_buffer
import os
from pyproj.crs import CRS
import numpy as np


class Wedge(QgsProcessingFeatureBasedAlgorithm):    
    OUTER_RADIUS = 'OUTER_RADIUS'
    INNER_RADIUS = 'INNER_RADIUS'
    SECTNUM = 'SECTNUM'
    SEGNUM = 'SEGNUM'
    AZIMUTH = 'AZIMUTH' 
    
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
        return Wedge()

    def name(self):
        return 'Wedge Buffers'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_wedge.png'))
    
    def displayName(self):
        return self.tr('Wedge Buffers', 'Wedge Buffers')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('Wedge Buffers, Circle Sectors').split(',')
    
    txt_en = 'Wedge Buffers'
    txt_vi = 'Wedge Buffers'
    figure = 'images/tutorial/vect_wedge.png'

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

    def helpUrl(self):
        file = os.path.dirname(__file__) + '/index.html'
        if not os.path.exists(file):
            return ''
        return QUrl.fromLocalFile(file).toString(QUrl.FullyEncoded)
    
    def inputLayerTypes(self):
        return [QgsProcessing.TypeVectorPoint]
    
    def outputName(self):
        return self.tr('Output layer')

    def outputWkbType(self):
        return (QgsWkbTypes.Polygon)   
    
    def supportInPlaceEdit(self, layer):
        return False
    
    def initParameters(self, config=None):
        param = QgsProcessingParameterNumber(
            self.OUTER_RADIUS,
            self.tr('Outer Radius (meters)'),
            QgsProcessingParameterNumber.Double,
            defaultValue=20000,
            minValue=0,
            optional=False)
        param.setIsDynamic(True)
        param.setDynamicPropertyDefinition(QgsPropertyDefinition(
            self.OUTER_RADIUS,
            self.tr('Outer Radius (meters)'),
            QgsPropertyDefinition.Double))
        param.setDynamicLayerParameterName('INPUT')
        self.addParameter(param)

        param = QgsProcessingParameterNumber(
            self.INNER_RADIUS,
            self.tr('Inner Radius (meters)'),
            QgsProcessingParameterNumber.Double,
            defaultValue=0,
            minValue=0,
            optional=False)
        param.setIsDynamic(True)
        param.setDynamicPropertyDefinition(QgsPropertyDefinition(
            self.INNER_RADIUS,
            self.tr('Inner Radius (meters)'),
            QgsPropertyDefinition.Double))
        param.setDynamicLayerParameterName('INPUT')
        self.addParameter(param)
        
        param = QgsProcessingParameterNumber(
            self.SECTNUM,
            self.tr('Number of Circular Sectors'),
            QgsProcessingParameterNumber.Integer,
            defaultValue=4,
            minValue=2,
            optional=False)
        param.setIsDynamic(True)
        param.setDynamicPropertyDefinition(QgsPropertyDefinition(
            self.SECTNUM,
            self.tr('Number of Circular Sectors'),
            QgsPropertyDefinition.Integer))
        param.setDynamicLayerParameterName('INPUT')
        self.addParameter(param)
    
        param = QgsProcessingParameterNumber(
            self.AZIMUTH,
            self.tr('Azimuth (Degrees from North)'),
            QgsProcessingParameterNumber.Double,
            defaultValue=0,
            optional=True)
        param.setIsDynamic(True)
        param.setDynamicPropertyDefinition(QgsPropertyDefinition(
            self.AZIMUTH,
            self.tr('Azimuth (Degrees from North)'),
            QgsPropertyDefinition.Double))
        param.setDynamicLayerParameterName('INPUT')
        self.addParameter(param)
       
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SEGNUM,
                self.tr('Number of Wedge Segments'),
                QgsProcessingParameterNumber.Integer,
                defaultValue=36,
                minValue=4,
                optional=True)
        )    
               
    def prepareAlgorithm(self, parameters, context, feedback):
        self.outer_radius = self.parameterAsDouble(parameters, self.OUTER_RADIUS, context)  
        if self.outer_radius <= 0:
            feedback.reportError('Outer radius parameter must be greater than 0')
            return False
        self.outer_radius_dyn = QgsProcessingParameters.isDynamic(parameters, self.OUTER_RADIUS)
        if self.outer_radius_dyn:
            self.outer_radius_property = parameters[self.OUTER_RADIUS]

        self.inner_radius = self.parameterAsDouble(parameters, self.INNER_RADIUS, context)
        if self.outer_radius < 0:
            feedback.reportError('Inner radius parameter must be equal or greater than 0')
            return False         
        self.inner_radius_dyn = QgsProcessingParameters.isDynamic(parameters, self.INNER_RADIUS)
        if self.inner_radius_dyn:
            self.inner_radius_property = parameters[self.INNER_RADIUS]                      

        self.sectnum = self.parameterAsInt(parameters, self.SECTNUM, context)
        if self.sectnum <= 2:
            feedback.reportError('Number of sectors must be greater than 1')
            return False    
        self.sectnum_dyn = QgsProcessingParameters.isDynamic(parameters, self.SECTNUM)
        if self.sectnum_dyn:
            self.sectnum_property = parameters[self.SECTNUM]                      

        self.azimuth = self.parameterAsDouble(parameters, self.AZIMUTH, context) 
        self.azimuth_dyn = QgsProcessingParameters.isDynamic(parameters, self.AZIMUTH)
        if self.azimuth_dyn:
            self.azimuth_property = parameters[self.AZIMUTH]                      
        
        self.segnum = self.parameterAsInt(parameters, self.SEGNUM, context) 
        if self.segnum < 4:
            feedback.reportError('Number of sectors must be greater than 4')
            return False 
        
        source = self.parameterAsSource(parameters, 'INPUT', context)
        
        src_crs = source.sourceCrs()        
        extend = source.sourceExtent()
        y_max = extend.yMaximum()
        y_min = extend.yMinimum()        
        if src_crs.isGeographic():
            EPSG = int(src_crs.authid().split(':')[-1])
            proj_crs = CRS.from_epsg(EPSG)
            a = proj_crs.ellipsoid.semi_major_metre
            f = 1 / proj_crs.ellipsoid.inverse_flattening
            e2 = f * (2 - f)
            lat_rad = np.radians((y_min + y_max) / 2)
            N = a / np.sqrt(1 - e2 * (np.sin(lat_rad)) ** 2)  # Radius of curvature 1 degree vertical
            M = a * (1 - e2) / (1 - e2 * (np.sin(lat_rad)) ** 2) ** (3 / 2.)  # Meridian Curvature Radius
            R = np.sqrt(M * N)  # Gaussian mean radius
            theta_outer_radius = self.outer_radius / R
            theta_inner_radius = self.inner_radius / R
            self.outer_radius = np.degrees(theta_outer_radius)  # Radian to degree
            self.inner_radius = np.degrees(theta_inner_radius)  # Radian to degree
                      

        self.total_features = source.featureCount()
        self.num_bad = 0
        return True
    
    def processFeature(self, feature, context, feedback):
        try:
            # Evaluate outer radius
            if self.outer_radius_dyn:
                outer_rad, e = self.outer_radius_property.valueAsDouble(context.expressionContext(), self.outer_radius)
                if not e or outer_rad < 0:
                    self.num_bad += 1
                    return []
            else:
                outer_rad = self.outer_radius

            # Evaluate inner radius
            if self.inner_radius_dyn:
                inner_rad, e = self.inner_radius_property.valueAsDouble(context.expressionContext(), self.inner_radius)
                if not e or inner_rad < 0:
                    self.num_bad += 1
                    return []
            else:
                inner_rad = self.inner_radius
            
            if self.sectnum_dyn:
                sect_num, e = self.sectnum_property.valueAsInt(context.expressionContext(), self.sectnum)
                if not e or sect_num <= 1:
                    self.num_bad += 1
                    return []
            else:
                sect_num = self.sectnum

            if self.azimuth_dyn:
                azimuth_degree, e = self.outer_radius_property.valueAsDouble(context.expressionContext(), self.azimuth)
                if not e:
                    self.num_bad += 1
                    return []
            else:
                azimuth_degree = self.azimuth

            seg_num = self.segnum

            # Generate wedge geometries using the evaluated radii
            geom = feature.geometry()
            wedge_geoms = wedge_buffer(geom, outer_rad, inner_rad, sect_num, azimuth_degree, seg_num)
            
            wedge_features = []
            for wedge_geom in wedge_geoms:
                if wedge_geom.isGeosValid():
                    wedge_feature = QgsFeature()
                    wedge_feature.setGeometry(wedge_geom)
                    wedge_feature.setAttributes(feature.attributes())
                    wedge_features.append(wedge_feature)
                else:
                    feedback.reportError(f"Invalid geometry for feature {feature.id()}")
                    self.num_bad += 1

            return wedge_features

        except Exception as e:
            self.num_bad += 1
            feedback.reportError(f"Error processing feature {feature.id()}: {str(e)}")
            return []

    def postProcessAlgorithm(self, context, feedback):
        if self.num_bad:
            feedback.pushInfo(self.tr("{} out of {} features had invalid parameters and were ignored.".format(self.num_bad, self.total_features)))
        return {}