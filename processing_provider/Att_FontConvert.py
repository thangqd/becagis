# -*- coding: utf-8 -*-


"""
Att_FontConvert.py
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
                       QgsProcessing,
                       QgsProcessingParameterEnum,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSink)

from becagistools.becagislibrary.imgs import Imgs
import becagistools.becagislibrary.attribute as attribute
import os
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant

class FontConvert(QgsProcessingAlgorithm):

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
        return FontConvert()

    def name(self):
        return 'fontconvert'

    def displayName(self):
        return self.tr('Vietnamese Font Converter', 'Vietnamese Font Converter')

    def group(self):
        return self.tr('Attribute', 'Attribute')

    def groupId(self):
        return 'Attribute'

    def tags(self):
        return self.tr('vietnamese font, convert').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/att_fontconvert.png'))

    txt_en = 'Vietnamese Font Converter'
    txt_vi = 'Vietnamese Font Converter'
    figure = 'images/att_fontconvert.png'

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
    SOURCE_FONT = 'SOURCE_FONT'
    TARGET_FONT = 'TARGET_FONT'
    CASE = 'CASE'
    OUTPUT = 'OUTPUT'
    dest_id = None
    
    source_font_list = ['TCVN3', 'VNI-Windows', 'Unicode']             
    target_font_list = ['Unicode', 'VNI-Windows', 'TCVN3', 'ANSI (Khong dau)']
    case_list = ['None','UPPER CASE','lower case','Capitalize Each Word','Sentence case', 'sWAP Case']

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
            # QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Layer/ Attribute Table', 'Dữ liệu đầu vào'),
                [QgsProcessing.TypeVector]
            )
        )     
               
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SOURCE_FONT,
                self.tr('Source Font', 'Source Font'),
				options = self.source_font_list,
                defaultValue = 2
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TARGET_FONT,
                self.tr('Target Font', 'Target Font'),
				options = self.target_font_list,
                defaultValue = 0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.CASE,
                self.tr('Change case', 'Change case'),
                defaultValue = 0,
				options = self.case_list
            )
        )

        self.addParameter(
            # QgsProcessingParameterFeatureSink(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output', 'Output')
            )
        )
       
    def processAlgorithm(self, parameters, context, feedback):
        input_layer = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )
        if input_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT)) 
       
        source_font_idx = self.parameterAsEnum(
            parameters,
            self.SOURCE_FONT,
            context
        )

        target_font_idx = self.parameterAsEnum(
            parameters,
            self.TARGET_FONT,
            context
        )

        case_idx = self.parameterAsEnum(
            parameters,
            self.CASE,
            context
        )

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

        source_font_text = self.source_font_list[source_font_idx]
        target_font_text = self.target_font_list[target_font_idx] 
        source_font = attribute.GetEncodeIndex(source_font_text)
        target_font = attribute.GetEncodeIndex(target_font_text)
        case = attribute.GetCaseIndex(case_idx)           

        fields = []
        for field in input_layer.fields():
            if field.type() == QVariant.String:
                fields.append (field.name())
        featureCount = input_layer.featureCount()
        total = 100.0 /featureCount if featureCount else 0
        for current, feat in enumerate(input_layer.getFeatures()):
            for field in fields:
                feat[field] = attribute.convertfont(feat[field], source_font, target_font, case)					                        
            sink.addFeature(feat)      
            if feedback.isCanceled():
                break
        feedback.setProgress(int(current * total))    
        feedback.pushInfo(self.tr('Font Convert completed successfully!', 'Hoàn thành!'))          
        return {self.OUTPUT: dest_id}