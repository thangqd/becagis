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
from becagistools.becagislibrary.attribute import *
import processing
import os
from qgis.PyQt.QtGui import QIcon

_Unicode = [
u'â',u'Â',u'ă',u'Ă',u'đ',u'Đ',u'ê',u'Ê',u'ô',u'Ô',u'ơ',u'Ơ',u'ư',u'Ư',u'á',u'Á',u'à',u'À',u'ả',u'Ả',u'ã',u'Ã',u'ạ',u'Ạ',
u'ấ',u'Ấ',u'ầ',u'Ầ',u'ẩ',u'Ẩ',u'ẫ',u'Ẫ',u'ậ',u'Ậ',u'ắ',u'Ắ',u'ằ',u'Ằ',u'ẳ',u'Ẳ',u'ẵ',u'Ẵ',u'ặ',u'Ặ',
u'é',u'É',u'è',u'È',u'ẻ',u'Ẻ',u'ẽ',u'Ẽ',u'ẹ',u'Ẹ',u'ế',u'Ế',u'ề',u'Ề',u'ể',u'Ể',u'ễ',u'Ễ',u'ệ',u'Ệ',u'í',u'Í',u'ì',u'Ì',u'ỉ',u'Ỉ',u'ĩ',u'Ĩ',u'ị',u'Ị',    
u'ó',u'Ó',u'ò',u'Ò',u'ỏ',u'Ỏ',u'õ',u'Õ',u'ọ',u'Ọ',u'ố',u'Ố',u'ồ',u'Ồ',u'ổ',u'Ổ',u'ỗ',u'Ỗ',u'ộ',u'Ộ',u'ớ',u'Ớ',u'ờ',u'Ờ',u'ở',u'Ở',u'ỡ',u'Ỡ',u'ợ',u'Ợ',    
u'ú',u'Ú',u'ù',u'Ù',u'ủ',u'Ủ',u'ũ',u'Ũ',u'ụ',u'Ụ',u'ứ',u'Ứ',u'ừ',u'Ừ',u'ử',u'Ử',u'ữ',u'Ữ',u'ự',u'Ự',u'ỳ',u'Ỳ',u'ỷ',u'Ỷ',u'ỹ',u'Ỹ',u'ỵ',u'Ỵ',u'ý',u'Ý'    
]

_VNIWin = [
u'aâ',u'AÂ',u'aê',u'AÊ',u'ñ',u'Ñ',u'eâ',u'EÂ',u'oâ',u'OÂ',u'ô',u'Ô',u'ö',u'Ö',u'aù',u'AÙ',u'aø',u'AØ',u'aû',u'AÛ',u'aõ',u'AÕ',u'aï',u'AÏ',
u'aá',u'AÁ',u'aà',u'AÀ',u'aå',u'AÅ',u'aã',u'AÃ',u'aä',u'AÄ',u'aé',u'AÉ',u'aè',u'AÈ',u'aú',u'AÚ',u'aü',u'AÜ',u'aë',u'AË',
u'eù',u'EÙ',u'eø',u'EØ',u'eû',u'EÛ',u'eõ',u'EÕ',u'eï',u'EÏ',u'eá',u'EÁ',u'eà',u'EÀ',u'eå',u'EÅ',u'eã',u'EÃ',u'eä',u'EÄ',u'í',u'Í',u'ì',u'Ì',u'æ',u'Æ',u'ó',u'Ó',u'ò',u'Ò',    
u'où',u'OÙ',u'oø',u'OØ',u'oû',u'OÛ',u'oõ',u'OÕ',u'oï',u'OÏ',u'oá',u'OÁ',u'oà',u'OÀ',u'oå',u'OÅ',u'oã',u'OÃ',u'oä',u'OÄ',u'ôù',u'ÔÙ',u'ôø',u'ÔØ',u'ôû',u'ÔÛ',u'ôõ',u'ÔÕ',u'ôï',u'ÔÏ',    
u'uù',u'UÙ',u'uø',u'UØ',u'uû',u'UÛ',u'uõ',u'UÕ',u'uï',u'UÏ',u'öù',u'ÖÙ',u'öø',u'ÖØ',u'öû',u'ÖÛ',u'öõ',u'ÖÕ',u'öï',u'ÖÏ',u'yø',u'YØ',u'yû',u'YÛ',u'yõ',u'YÕ',u'î',u'Î',u'yù',u'YÙ'    
]

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
    figure = 'images/tutorial/att_fontconvert.png'

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
    OPTION = 'OPTION'
    OUTPUT = 'OUTPUT'
    dest_id = None
    
    source_font_list = ['TCVN3', 'VNI-Windows', 'Unicode']             
    target_font_list = ['Unicode', 'VNI-Windows', 'TCVN3', 'ANSI (Khong dau)']
    option_list = ['UPPER CASE',
             'lower case',
            'Capitalize',
            'Title'
            ]

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
                optional = True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TARGET_FONT,
                self.tr('Target Font', 'Target Font'),
				options = self.target_font_list,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.OPTION,
                self.tr('Option', 'Option'),
				options = self.option_list,
                optional = True
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

        option_idx = self.parameterAsEnum(
            parameters,
            self.OPTION,
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
        print ('source font:', source_font_text)
        print ('target font:', target_font_text)
        source_font = GetEncodeIndex(source_font_text)
        target_font = GetEncodeIndex(target_font_text)
        print ('source font:', source_font)
        print ('target font:', target_font)
        option = GetCaseIndex(option_idx)
        print ('option:', option) 
        fields = []
        for field in input_layer.fields():
            if field.typeName() == 'String':
                fields.append (field.name())
        featureCount = input_layer.featureCount()
        total = 100.0 /featureCount if featureCount else 0
        for current, feat in enumerate(input_layer.getFeatures()):
            for tf in fields:
                oldValue = feat[tf]
                if oldValue != None:
                    if source_font == _VNIWin:
                        # Convert VNI-Win to Unicode
                        newValue = vni_unicode(oldValue)
                        # if targerEncode is not Unicode -> Convert to other options
                        if target_font != _Unicode:
                            newValue = Convert(newValue,_Unicode,target_font)
                    else:
                        newValue = Convert(oldValue,source_font,target_font)
                    # Character Case-setting                                
                    if option != "None":
                        newValue = ChangeCase(newValue, option)                        
                    # update new value
                    feat[tf] = newValue						
                else: pass									                        
            sink.addFeature(feat)      
            if feedback.isCanceled():
                break
        feedback.setProgress(int(current * total))    
        feedback.pushInfo(self.tr('Font Convert completed successfully!', 'Hoàn thành!'))          
        return {self.OUTPUT: dest_id}