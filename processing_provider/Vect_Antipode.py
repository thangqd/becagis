# -*- coding: utf-8 -*-


"""
Vect_reverseVertexOrder.py
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
from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsProcessing,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from BecaGISTools.becagislibrary.imgs import Imgs
from BecaGISTools.becagislibrary.latlong import antipode

import os
from qgis.PyQt.QtGui import QIcon

class Antipode(QgsProcessingAlgorithm):

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
        return Antipode()

    def name(self):
        return 'antipode'

    def displayName(self):
        return self.tr('Create Antipodal layer', 'Create Antipodal layer')

    def group(self):
        return self.tr('Vector', 'Vector')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('antipode, antipodes, antipodal layer').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vector.png'))

    txt_en = 'Create Antipodal layer'
    txt_vi = 'Create Antipodal layer'
    figure1 = 'images/tutorial/vect_antipode.png'
    figure2 = 'images/tutorial/vect_anipodal_layer.png'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure1) +'''">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure2) +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Thang Quach', 'Author: Thang Quach')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_vi) + footer


    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            # QgsProcessingParameterVectorLayer(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Layer', 'Lớp dữ liệu đầu vào'),
                # [QgsProcessing.TypeVectorLine,
                #  QgsProcessing.TypeVectorPolygon]
            )
        )
       
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Antipodal Layer', 'Antipodal Layer')
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

        
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        total = 100.0 / source.featureCount() if source.featureCount() else 0
        # antipodal_layer = QgsVectorFileWriter(self.OUTPUT, "UTF-8", layer.dataProvider().fields(),layer.wkbType(), layer.crs(),"ESRI Shapefile")               
        # for feat in  layer.getFeatures():                					                        
        #     shapeWriter.addFeature(feat)                                  
        # del shapeWriter
        for current, feat in enumerate(source.getFeatures()):
            geom = feat.geometry()
            new_geom = geom
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))     
      
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Hoàn thành!'))
        return {}

    def antipode_geom(self, geom):
        if geom.type() == 0: #Point
            if geom.isMultipart():
                # points = geom.asMultiPoint()
                # newLines = []
                # for line in lines:
                #     newLine = line[::-1]
                #     newLines += [newLine]
                # newGeom = QgsGeometry.fromMultiPolylineXY(newLines)
                # return newGeom
                pass
            else:
                point = geom.asPoint()
                antipode_lat,antipode_lon =  antipode(lat,lon)      
                antipode_point = QgsPointXY(antipode_lon, antipode_lat)
                return(QgsGeometry.fromPointXY(antipode_point))

                newLine = line[::-1]
                newGeom = QgsGeometry.fromPolylineXY(newLine)
                return newGeom

        # if geom.type() == 1: #Line
        #     if geom.isMultipart():
        #         lines = geom.asMultiPolyline()
        #         newLines = []
        #         for line in lines:
        #             newLine = line[::-1]
        #             newLines += [newLine]
        #         newGeom = QgsGeometry.fromMultiPolylineXY(newLines)
        #         return newGeom
        #     else:
        #         line = geom.asPolyline()
        #         newLine = line[::-1]
        #         newGeom = QgsGeometry.fromPolylineXY(newLine)
        #         return newGeom
       
        # elif geom.type() == 2: #Polygon
        #     if geom.isMultipart():
        #         poligonos = geom.asMultiPolygon()
        #         newPolygons = []
        #         for pol in poligonos:
        #             newPol = []
        #             for anel in pol:
        #                 newAnel = anel[::-1]
        #                 newPol += [newAnel]
        #             newPolygons += [newPol]
        #         newGeom = QgsGeometry.fromMultiPolygonXY(newPolygons)
        #         return newGeom
        #     else:
        #         pol = geom.asPolygon()
        #         newPol = []
        #         for anel in pol:
        #             newAnel = anel[::-1]
        #             newPol += [newAnel]
        #         newGeom = QgsGeometry.fromPolygonXY(newPol)
        #         return newGeom
        else:
            return None
