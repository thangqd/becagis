# -*- coding: utf-8 -*-


"""
Vect_Quadrant.py
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
import processing
import os
from qgis.PyQt.QtGui import QIcon
from pyproj.crs import CRS
import numpy as np
import math

def create_wedge_buffer(geometry, radius, num_quadrants, segment_count=72):
    """
    Create wedge-shaped buffers around a point geometry for the given number of quadrants.

    :param geometry: QgsGeometry of the point around which to create the buffer.
    :param radius: Radius of the wedge buffer.
    :param num_quadrants: Number of quadrants to create.
    :param segment_count: Number of segments to use for circle approximation.
    :return: List of QgsGeometry objects representing the wedge buffers.
    """
    # Get the center point of the geometry
    center = geometry.asPoint()
    
    # Calculate the angle range for each quadrant
    angle_step = 360 / num_quadrants
    
    wedge_geometries = []

    for quadrant in range(num_quadrants):
        angle_start = quadrant * angle_step
        angle_end = (quadrant + 1) * angle_step
        
        # Convert start and end angles to radians
        angle_start_rad = math.radians(angle_start)
        angle_end_rad = math.radians(angle_end)
        
        # Create a list of points that make up the circle
        points = []
        for i in range(segment_count + 1):
            angle = math.radians(360 * i / segment_count)
            x = center.x() + radius * math.cos(angle)
            y = center.y() + radius * math.sin(angle)
            points.append(QgsPointXY(x, y))
        
        # Create a list of points for the wedge
        wedge_points = [center]
        for i in range(segment_count + 1):
            angle = math.radians(360 * i / segment_count)
            if angle_start_rad <= angle <= angle_end_rad:
                wedge_points.append(points[i])
        
        # Close the wedge by adding the starting point
        wedge_points.append(center)
        
        # Check if the wedge has enough points to form a valid geometry
        if len(wedge_points) < 3:
            continue  # Skip this wedge if not enough points

        # Create the geometry for the wedge buffer
        wedge_geometry = QgsGeometry.fromPolygonXY([wedge_points])
        wedge_geometries.append(wedge_geometry)

    return wedge_geometries


class Quadrant(QgsProcessingAlgorithm):

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
        return Quadrant()

    def name(self):
        return 'Quadrant'

    def displayName(self):
        return self.tr('Quadrant', 'Quadrant')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('Quadrant, Wedge Buffer').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_Quadrant.png'))

    txt_en = 'Quadrant Layer'
    txt_vi = 'Quadrant Layer'
    figure = 'images/tutorial/vect_quadrant.png'

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


    INPUT = 'INPUT'
    UNIQUE_FIELD = 'UNIQUE_FIELD' 
    RADIUS = 'RADIUS'
    QUADNUM = 'QUADNUM'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Layer', 'Lớp dữ liệu đầu vào'),
                [QgsProcessing.TypeVectorPoint]
                # [QgsProcessing.TypeVectorPoint,
                #  QgsProcessing.TypeVectorPolygon]
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
            QgsProcessingParameterNumber(
                self.RADIUS,
                self.tr('Buffer Radius (meters)'),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=30000,
                optional=False,
                minValue=0.1
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.QUADNUM,
                self.tr('Number of quadrants'),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=4,
                optional=False,
                minValue=2)
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Quadrant Layer', 'Quadrant Layer')
            )
        )
    
    def processAlgorithm(self, parameters, context, feedback):
        # Use QgsProcessingParameterFeatureSource
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        unique_field = self.parameterAsString(parameters, self.UNIQUE_FIELD, context)
        if unique_field is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.UNIQUE_FIELD))
        
        radius = self.parameterAsDouble(parameters, self.RADIUS, context)  # Changed to Double for radius
        quadnum = self.parameterAsInt(parameters, self.QUADNUM, context)  # Changed to Double for radius

        # Source extent and CRS
        extend = source.sourceExtent()
        y_max = extend.yMaximum()
        y_min = extend.yMinimum()
        
        fieldsout = QgsFields(source.fields())
        layerCRS = source.sourceCrs()
        
        featureCount = source.featureCount()
        total = 100.0 / featureCount if featureCount else 0
        badFeatures = 0

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT,
            context, fieldsout, QgsWkbTypes.Polygon, layerCRS
        )
        
        if layerCRS.isGeographic():
            EPSG = int(layerCRS.authid().split(':')[-1])
            proj_crs = CRS.from_epsg(EPSG)
            a = proj_crs.ellipsoid.semi_major_metre
            f = 1 / proj_crs.ellipsoid.inverse_flattening
            e2 = f * (2 - f)
            lat_rad = np.radians((y_min + y_max) / 2)
            N = a / np.sqrt(1 - e2 * (np.sin(lat_rad)) ** 2)  # Radius of curvature 1 degree vertical
            M = a * (1 - e2) / (1 - e2 * (np.sin(lat_rad)) ** 2) ** (3 / 2.)  # Meridian Curvature Radius
            R = np.sqrt(M * N)  # Gaussian mean radius
            theta_radius = radius / R
            radius = np.degrees(theta_radius)  # Radian to degree

        # Buffering each feature
        iterator = source.getFeatures()
        for cnt, feature in enumerate(iterator):
            if feedback.isCanceled():
                break
            try:
                geom = feature.geometry()
                if not geom:
                    badFeatures += 1
                    continue
                    
                # Create buffer around the feature
                # buffer_geom = geom.buffer(radius, 64)  # 5 segments per quarter circle
                # Create wedge buffer around the feature
                
                wedge_geometries = create_wedge_buffer(geom, radius, quadnum)
            
                for wedge_geom in wedge_geometries:
                    # Create a new feature with the buffered geometry
                    wedge_feature = QgsFeature()
                    wedge_feature.setGeometry(wedge_geom)
                    wedge_feature.setAttributes(feature.attributes())
                    sink.addFeature(wedge_feature)
                    
            except Exception as e:
                feedback.pushInfo(f"Error processing feature {cnt}: {str(e)}")
                badFeatures += 1
                continue

            if cnt % 100 == 0:
                feedback.setProgress(int(cnt * total))

        if badFeatures > 0:
            msg = f"{featureCount - badFeatures} {self.tr('out of')} {featureCount} {self.tr('features were successfully buffered')}"
            feedback.pushInfo(msg)

        return {self.OUTPUT: dest_id}


        # iterator = source.getFeatures()
        # for cnt, feature in enumerate(iterator):
        #     if feedback.isCanceled():
        #         break
        #     try:
        #         coord = feature.geometry().centroid().asPoint()
        #         lat = coord.y()
        #         lon = coord.x()
        #     except Exception:
        #         badFeatures += 1
        #         continue
        #     f = QgsFeature()
        #     f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
        #     f.setAttributes(feature.attributes())
        #     sink.addFeature(f)

        #     if cnt % 100 == 0:
        #         feedback.setProgress(int(cnt * total))

        # if badFeatures > 0:
        #     msg = "{} {} {} {}".format(featureCount - badFeatures, self.tr('out of'), featureCount, self.tr('features contained valid coordinates'))
        #     feedback.pushInfo(msg)

        # return {self.OUTPUT: dest_id}
        # Call the 'qgis:buffer' algorithm
