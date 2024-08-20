# -*- coding: utf-8 -*-


"""
Vect_Reversed_X.py
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
from becagis.becagislibrary.latlong import reversed_x
from processing.gui.AlgorithmExecutor import execute_in_place
import processing
import os
from qgis.PyQt.QtGui import QIcon

class Reversed_X(QgsProcessingAlgorithm):

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
        return Reversed_X()

    def name(self):
        return 'Reversed_X'

    def displayName(self):
        return self.tr('Reversed X', 'Reversed X')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('Reversed X, Reversed Lat').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vect_reversed_X.png'))

    txt_en = 'Reversed_X Layer'
    txt_vi = 'Reversed_X Layer'
    figure = 'images/tutorial/vect_Reversed_X.svg'

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
    OUTPUT = 'OUTPUT'
    SELECTED = 'SELECTED'
    dest_id = None

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterVectorLayer(
            # QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Layer', 'Lớp dữ liệu đầu vào'),
                # [QgsProcessing.TypeVectorLine,
                #  QgsProcessing.TypeVectorPolygon]
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
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Reversed X Layer', 'Reversed X Layer')
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
       

        # if format(input_layer.sourceCrs().authid())!= 'EPSG:4326':
        if not input_layer.crs().isGeographic():
            params = {
                'INPUT': input_layer,
                'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }
            reproject = processing.run('native:reprojectlayer', params)
            input_layer = reproject['OUTPUT'] 

        # (sink, dest_id) = self.parameterAsSink(
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            input_layer.fields(),
            input_layer.wkbType(),
            input_layer.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        if not selected:
            features = input_layer.getFeatures()
            feature_count = input_layer.featureCount() 
        else:
            features = input_layer.getSelectedFeatures()
            feature_count = input_layer.selectedFeatureCount()
            
        if (feature_count<=0): 
            return {} 
        else:
            total = 100.0 / input_layer.featureCount() if input_layer.featureCount() else 0             
            for current, feature in enumerate(features):
                geom= feature.geometry()
                if geom.type() == 0: # Point
                    if not geom.isMultipart(): #Single part  
                        new_geom = self.Reversed_X_geom(feature.geometry().asPoint())
                        new_feature = QgsFeature()
                        new_feature.setGeometry(new_geom)
                        new_feature.setAttributes(feature.attributes()) 
                        sink.addFeature(new_feature, QgsFeatureSink.FastInsert)   
                    else: #Multi point                        
                        multipoint = geom.asMultiPoint() 
                        new_multipoint =[] 
                        for point in multipoint:         
                            new_point = QgsPointXY(self.Reversed_X_geom(point).asPoint())
                            new_multipoint.append(new_point)  
                        new_multipoints= QgsGeometry.fromMultiPointXY(new_multipoint)                            
                        new_feature = QgsFeature()
                        new_feature.setGeometry(new_multipoints)
                        new_feature.setAttributes(feature.attributes()) 
                        sink.addFeature(new_feature, QgsFeatureSink.FastInsert)
                 
                elif geom.type() == 1: #Single part Polyline  
                    if not geom.isMultipart(): #Single part  
                        vertices = geom.asPolyline() 
                        new_vertices = []
                        for vertice in vertices:
                            new_vertice  = self.Reversed_X_geom(vertice)
                            new_vertices.append(QgsPointXY(new_vertice.asPoint()))
                        new_polyline = QgsGeometry.fromPolylineXY(new_vertices)
                        new_feature = QgsFeature()
                        new_feature.setGeometry(new_polyline)
                        new_feature.setAttributes(feature.attributes()) 
                        sink.addFeature(new_feature, QgsFeatureSink.FastInsert)
                    else: #Multi Polyline
                        parts = geom.asMultiPolyline() 
                        new_vertices = [[],[]]
                        for id, part in enumerate(parts):
                            for vertice in part:
                                new_vertice = self.Reversed_X_geom(vertice)
                                new_vertices[id].append(QgsPointXY(new_vertice.asPoint()))  
                        new_polyline = QgsGeometry.fromMultiPolylineXY(new_vertices)                            
                        new_feature = QgsFeature()
                        new_feature.setGeometry(new_polyline)
                        new_feature.setAttributes(feature.attributes()) 
                        sink.addFeature(new_feature, QgsFeatureSink.FastInsert)                     

                elif (geom.type() == 2): 
                    if not geom.isMultipart(): #Single part Polygon  
                        vertices = geom.asPolygon() 
                        new_vertices =[]
                        n = len(vertices[0])
                        for i in range(n):
                            new_vertice  = self.Reversed_X_geom(vertices[0][i])
                            new_vertices.append(QgsPointXY(new_vertice.asPoint()))                        
                        new_vertices_polygon = [[QgsPointXY(i[0], i[1] ) for i in new_vertices]]
                        new_polygon = QgsGeometry.fromPolygonXY(new_vertices_polygon)
                        new_feature = QgsFeature()
                        new_feature.setGeometry(new_polygon)
                        new_feature.setAttributes(feature.attributes()) 
                        sink.addFeature(new_feature, QgsFeatureSink.FastInsert)
                    else: #Multipolygon
                        multipolygon = geom.asMultiPolygon() 
                        new_multipolygon =[]
                        for polygon in multipolygon:
                            new_polygon=[]
                            for ring in polygon:
                                new_ring = []
                                for vertice in ring:                                    
                                    new_vertice = self.Reversed_X_geom(vertice)
                                    new_ring.append(QgsPointXY(new_vertice.asPoint()) )
                                new_polygon.append(new_ring)
                            new_multipolygon.append(new_polygon)

                        new_multipolygons= QgsGeometry.fromMultiPolygonXY(new_multipolygon)                            
                        new_feature = QgsFeature()
                        new_feature.setGeometry(new_multipolygons)
                        new_feature.setAttributes(feature.attributes()) 
                        sink.addFeature(new_feature, QgsFeatureSink.FastInsert)          

                if feedback.isCanceled():
                    break
                feedback.setProgress(int(current * total))    
                # feedback.pushInfo(self.tr('Operation completed successfully!', 'Hoàn thành!'))          
            return {self.OUTPUT: dest_id}
    
    def postProcessAlgorithm(self, context, feedback):
        # processed_layer = QgsProcessingUtils.mapLayerFromString(self.OUTPUT: dest_id, context)
        # Do smth with the layer, e.g. style it
        # create a new symbol
        # symbol = QgsLineSymbol.createSimple({'color': 'red'})
        # # apply symbol to layer renderer
        # processed_layer.renderer().setSymbol(symbol)
        # # repaint the layer
        # processed_layer.triggerRepaint()
        # processed_layer.loadNamedStyle("C:/QGIS points.qml")
        # processed_layer.triggerRepaint()
        return {self.OUTPUT: self.dest_id}

    def Reversed_X_geom(self, geom):      
        lat = geom.y()
        lon = geom.x()
        reversed_lat,reversed_lon =  reversed_x(lat,lon)      
        reversed_point = QgsPointXY(reversed_lon, reversed_lat)
        return(QgsGeometry.fromPointXY(reversed_point)) 