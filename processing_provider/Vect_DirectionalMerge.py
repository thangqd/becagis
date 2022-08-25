# -*- coding: utf-8 -*-


"""
Vect_DirectionalMerge.py
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

from operator import truediv
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsFeature,
                       QgsProcessing,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from math import atan2, degrees, fabs
from BecaGISTools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon

class DirectionalMerge(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def translate(self, string):
        return QCoreApplication.translate('Processing', string)

    def tr(self, *string):
        # Translate to vietnamese: arg[0] - english (translate), arg[1] - vietnamese
        if self.LOC == 'vi':
            if len(string) == 2:
                return string[1]
            else:
                return self.translate(string[0])
        else:
            return self.translate(string[0])

    def createInstance(self):
        return DirectionalMerge()

    def name(self):
        return 'directionalmerge'

    def displayName(self):
        return self.tr('Merge lines in direction', 'Gộp các đường cùng hướng')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('merge,dissolve,directional,touches,lines,connect,drainage,network').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'This algorithm merges lines that touch at their starting or ending points and has the same direction (given a tolerance in degrees). <p>For the attributes can be considered:</p>1 - merge lines that have the same attributes; or</li><li>2 - keep the attributes of the longest line.</li>'
    txt_vi = 'This algorithm merges lines that touch at their starting or ending points and has the same direction (given a tolerance in degrees). <p>For the attributes can be considered:</p>1 - merge lines that have the same attributes; or</li><li>2 - keep the attributes of the longest line.</li>'
    figure = 'images/tutorial/vect_directional_merge.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Thang Quach','Tác giả: Thang Quach')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_vi) + footer

    LINES = 'LINES'
    TYPE = 'TYPE'
    ANGLE = 'ANGLE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LINES,
                self.tr('Line Layer', 'Line Layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        tipo = [self.tr('merge lines that have the same attributes','Gộp các đường có cùng thuộc tính'),
                self.tr('keep the attributes of the longest line','Lấy thuộc tính của đường dài nhất')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Attributes', 'Thuộc tính'),
				options = tipo,
                defaultValue= 1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ANGLE,
                self.tr('Tolerance in degrees', 'Ngưỡng (độ)'),
                type =1,
                defaultValue = 30
                )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Merged lines', 'Đường gộp')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        lines = self.parameterAsSource(
            parameters,
            self.LINES,
            context
        )
        if lines is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LINES))


        attributes = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )

        tol = self.parameterAsDouble(
            parameters,
            self.ANGLE,
            context
        )
        if tol is None or tol > 90 or tol < 0:
            raise QgsProcessingException(self.tr('The input angle must be between 0 and 90 degrees!', 'Góc phải >0 độ và <90 độ!'))


        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            lines.fields(),
            lines.wkbType(),
            lines.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Create list with feature information
        feedback.pushInfo(self.tr('Calculating feature informations...', 'Tính toán thông tin đối tượng...'))
        list = []
        for feature in lines.getFeatures():
            list += self.ang_points(feature)

        # Create a new list with the final features merged
        new_list = []
        # Remove linear rings from the list and add them to the new list
        idx = 0
        while idx < len(list)-1:
            P_ini = list[idx][1]
            P_end = list[idx][2]
            if P_ini==P_end:
                new_list+= [list[idx][0]]
                del  list[idx]
            else:
                idx +=1

        # Merge lines that touch and have the same direction (with the same attribute)
        feedback.pushInfo(self.tr('Merging lines...', 'Gộp đường....'))
        if attributes == 0:
            while len(list)>1:
                length = len(list)
                for i in range(0,length-1):
                    merged = False
                    # Start and end point of feature A
                    coord_A = list[i][0]
                    P_ini_A = list[i][1]
                    P_end_A = list[i][2]
                    ang_ini_A = list[i][3]
                    ang_end_A = list[i][4]
                    att_A = list[i][5]
                    for j in range(i+1,length):
                        # Start and end point of feature B
                        coord_B = list[j][0]
                        P_ini_B = list[j][1]
                        P_end_B = list[j][2]
                        ang_ini_B = list[j][3]
                        ang_end_B = list[j][4]
                        att_B = list[j][5]
                        if att_A == att_B:
                            # 4 possibilidades
                            # 1 - End point of A equals start point of B
                            if (P_end_A == P_ini_B) and (fabs(ang_end_A-ang_ini_B)<tol or fabs(360-fabs(ang_end_A-ang_ini_B))<tol):
                                merged = True
                                break
                            # 2 - Start point of A equals end point of B
                            elif (P_ini_A == P_end_B) and (fabs(ang_ini_A-ang_end_B)<tol or fabs(360-fabs(ang_ini_A-ang_end_B))<tol):
                                merged = True
                                break
                            # 3 - Start point of A equal to start point of B
                            elif (P_ini_A == P_ini_B) and (fabs(ang_ini_A- self.contraAz(ang_ini_B))<tol or fabs(360-fabs(ang_ini_A - self.contraAz(ang_ini_B)))<tol):
                                merged = True
                                break
                            # 4 - End point of A equals end point of B
                            elif (P_end_A == P_end_B) and (fabs(ang_end_A - self.contraAz(ang_end_B))<tol or fabs(360-fabs(ang_end_A - self.contraAz(ang_end_B)))<tol):
                                merged = True
                                break
                    if merged:
                        geom_A = QgsGeometry.fromPolylineXY(coord_A)
                        geom_B = QgsGeometry.fromPolylineXY(coord_B)
                        new_geom = geom_A.combine(geom_B)

                        new_feat = QgsFeature()
                        new_feat.setAttributes(att_A)
                        new_feat.setGeometry(new_geom)

                        if new_geom.isMultipart():
                            new_list += [[coord_A, att_A], [coord_B, att_B]]
                            del list[i], list[j-1]
                            break
                        else:
                            del list[i], list[j-1]
                            list = self.ang_points(new_feat)+list
                            break
                    if not(merged):
                        # Remove geometry that doesn't connect to anything from the list
                        new_list += [[coord_A, att_A]]
                        del list[i]
                        break
                if len(list)==1:
                    new_list += [[list[0][0], list[0][5]]]

        # Merge those that touch and have the same direction (preserve attributes of the longer line)
        if attributes == 1:
            while len(list)>1:
                length = len(list)
                for i in range(0,length-1):
                    merged = False
                    # Start and end point of feature A
                    coord_A = list[i][0]
                    P_ini_A = list[i][1]
                    P_end_A = list[i][2]
                    ang_ini_A = list[i][3]
                    ang_end_A = list[i][4]
                    att_A = list[i][5]
                    for j in range(i+1,length):
                        # Start and end point of feature B
                        coord_B = list[j][0]
                        P_ini_B = list[j][1]
                        P_end_B = list[j][2]
                        ang_ini_B = list[j][3]
                        ang_end_B = list[j][4]
                        att_B = list[j][5]
                        # 4 possibilidades
                        # 1 - End point of A equals start point of B
                        if (P_end_A == P_ini_B) and (fabs(ang_end_A-ang_ini_B)<tol or fabs(360-fabs(ang_end_A-ang_ini_B))<tol):
                            merged = True
                            break
                        # 2 - Start point of A equals end point of B
                        elif (P_ini_A == P_end_B) and (fabs(ang_ini_A-ang_end_B)<tol or fabs(360-fabs(ang_ini_A-ang_end_B))<tol):
                            merged = True
                            break
                        # 3 - Start point of A equals end point of B
                        elif (P_ini_A == P_ini_B) and (fabs(ang_ini_A - self.contraAz(ang_ini_B))<tol or fabs(360-fabs(ang_ini_A - self.contraAz(ang_ini_B)))<tol):
                            merged = True
                            break
                        # 4 - End point of A equals end point of B
                        elif (P_end_A == P_end_B) and (fabs(ang_end_A - self.contraAz(ang_end_B))<tol or fabs(360-fabs(ang_end_A - self.contraAz(ang_end_B)))<tol):
                            merged = True
                            break
                    if merged:
                        geom_A = QgsGeometry.fromPolylineXY(coord_A)
                        geom_B = QgsGeometry.fromPolylineXY(coord_B)
                        new_geom = geom_A.combine(geom_B)

                        length_A = geom_A.length()
                        length_B = geom_B.length()
                        if length_A > length_B:
                            att = att_A
                        else:
                            att = att_B
                        new_feat = QgsFeature()
                        new_feat.setAttributes(att)
                        new_feat.setGeometry(new_geom)

                        if new_geom.isMultipart():
                            new_list += [[coord_A, att_A], [coord_B, att_B]]
                            del list[i], list[j-1]
                            break
                        else:
                            del list[i], list[j-1]
                            list = self.ang_points(new_feat)+list
                            break
                    if not(merged):
                        # Remove geometry that doesn't connect to anything from the list
                        new_list += [[coord_A, att_A]]
                        del list[i]
                        break
                if len(list)==1:
                    new_list += [[list[0][0], list[0][5]]]

        # Creating the output shapefile
        feedback.pushInfo(self.tr('Saving output...', 'Lưu kết quả...'))
        n_pnts = len(new_list)
        total = 100.0 /n_pnts if n_pnts else 0
        for k, item in enumerate(new_list):
            try:
                fet = QgsFeature()
                fet.setGeometry(QgsGeometry.fromPolylineXY(item[0]))
                fet.setAttributes(item[1])
                sink.addFeature(fet, QgsFeatureSink.FastInsert)
            except: pass
            if feedback.isCanceled():
                break
            feedback.setProgress(int((k+1) * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Hoàn thành!'))
        feedback.pushInfo(self.tr('Thang Quach - M.Sc in GIS', 'Thang Quach - M.Sc in GIS'))

        return {self.OUTPUT: dest_id}

    def ang_points(self, feature):
            att = feature.attributes()
            geom = feature.geometry()
            if not geom.isMultipart():
                coord = geom.asPolyline()
                # Tangent between the first and second point
                Xa = coord[0].x()
                Xb = coord[1].x()
                Ya = coord[0].y()
                Yb = coord[1].y()
                ang_ini = degrees(atan2(Yb-Ya,Xb-Xa))
                Xa = coord[-2].x()
                Xb = coord[-1].x()
                Ya = coord[-2].y()
                Yb = coord[-1].y()
                ang_end = degrees(atan2(Yb-Ya,Xb-Xa))
                return [[coord, coord[0], coord[-1], ang_ini, ang_end, att]]
            else:
                coord = geom.asMultiPolyline()
                items = []
                for item in coord:
                    Xa = item[0].x()
                    Xb = item[1].x()
                    Ya = item[0].y()
                    Yb = item[1].y()
                    ang_ini = degrees(atan2(Yb-Ya,Xb-Xa))
                    Xa = item[-2].x()
                    Xb = item[-1].x()
                    Ya = item[-2].y()
                    Yb = item[-1].y()
                    ang_end = degrees(atan2(Yb-Ya,Xb-Xa))
                    items += [[item, item[0], item[-1], ang_ini, ang_end, att]]
                return items

    # Function to give the opposite direction
    def contraAz(self, x):
        if x<=0:
            return x+180
        else:
            return x-180
    
    def checkclosedline(self, feature):
        geom = feature.geometry()
        if not geom.isMultipart():
            coord = geom.asPolyline()
            if (coord[0] == coord[-1] ):
                return True
            else: 
                return False
        else:
            coord = geom.asMultiPolyline()
            if (coord[0][0] == coord[-1][-1] ):
                return True
            else: 
                return False
