"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Thang Quach'
__date__ = '2022-08-25'
__copyright__ = '(L) 2022 by Thang Quach'

import unicodedata
from qgis.core import *

#_Unicode, _TCVN3, _VNIWin, _KhongDau
_Unicode = [
u'â',u'Â',u'ă',u'Ă',u'đ',u'Đ',u'ê',u'Ê',u'ô',u'Ô',u'ơ',u'Ơ',u'ư',u'Ư',u'á',u'Á',u'à',u'À',u'ả',u'Ả',u'ã',u'Ã',u'ạ',u'Ạ',
u'ấ',u'Ấ',u'ầ',u'Ầ',u'ẩ',u'Ẩ',u'ẫ',u'Ẫ',u'ậ',u'Ậ',u'ắ',u'Ắ',u'ằ',u'Ằ',u'ẳ',u'Ẳ',u'ẵ',u'Ẵ',u'ặ',u'Ặ',
u'é',u'É',u'è',u'È',u'ẻ',u'Ẻ',u'ẽ',u'Ẽ',u'ẹ',u'Ẹ',u'ế',u'Ế',u'ề',u'Ề',u'ể',u'Ể',u'ễ',u'Ễ',u'ệ',u'Ệ',u'í',u'Í',u'ì',u'Ì',u'ỉ',u'Ỉ',u'ĩ',u'Ĩ',u'ị',u'Ị',    
u'ó',u'Ó',u'ò',u'Ò',u'ỏ',u'Ỏ',u'õ',u'Õ',u'ọ',u'Ọ',u'ố',u'Ố',u'ồ',u'Ồ',u'ổ',u'Ổ',u'ỗ',u'Ỗ',u'ộ',u'Ộ',u'ớ',u'Ớ',u'ờ',u'Ờ',u'ở',u'Ở',u'ỡ',u'Ỡ',u'ợ',u'Ợ',    
u'ú',u'Ú',u'ù',u'Ù',u'ủ',u'Ủ',u'ũ',u'Ũ',u'ụ',u'Ụ',u'ứ',u'Ứ',u'ừ',u'Ừ',u'ử',u'Ử',u'ữ',u'Ữ',u'ự',u'Ự',u'ỳ',u'Ỳ',u'ỷ',u'Ỷ',u'ỹ',u'Ỹ',u'ỵ',u'Ỵ',u'ý',u'Ý'    
]
_TCVN3 = [
u'©',u'¢',u'¨',u'¡',u'®',u'§',u'ª',u'£',u'«',u'¤',u'¬',u'¥',u'­',u'¦',u'¸',u'¸',u'µ',u'µ',u'¶',u'¶',u'·',u'·',u'¹',u'¹',
u'Ê',u'Ê',u'Ç',u'Ç',u'È',u'È',u'É',u'É',u'Ë',u'Ë',u'¾',u'¾',u'»',u'»',u'¼',u'¼',u'½',u'½',u'Æ',u'Æ',
u'Ð',u'Ð',u'Ì',u'Ì',u'Î',u'Î',u'Ï',u'Ï',u'Ñ',u'Ñ',u'Õ',u'Õ',u'Ò',u'Ò',u'Ó',u'Ó',u'Ô',u'Ô',u'Ö',u'Ö',u'Ý',u'Ý',u'×',u'×',u'Ø',u'Ø',u'Ü',u'Ü',u'Þ',u'Þ',    
u'ã',u'ã',u'ß',u'ß',u'á',u'á',u'â',u'â',u'ä',u'ä',u'è',u'è',u'å',u'å',u'æ',u'æ',u'ç',u'ç',u'é',u'é',u'í',u'í',u'ê',u'ê',u'ë',u'ë',u'ì',u'ì',u'î',u'î',    
u'ó',u'ó',u'ï',u'ï',u'ñ',u'ñ',u'ò',u'ò',u'ô',u'ô',u'ø',u'ø',u'õ',u'õ',u'ö',u'ö',u'÷',u'÷',u'ù',u'ù',u'ú',u'ú',u'û',u'û',u'ü',u'ü',u'þ',u'þ',u'ý',u'ý'     
]

_VNIWin = [
u'aâ',u'AÂ',u'aê',u'AÊ',u'ñ',u'Ñ',u'eâ',u'EÂ',u'oâ',u'OÂ',u'ô',u'Ô',u'ö',u'Ö',u'aù',u'AÙ',u'aø',u'AØ',u'aû',u'AÛ',u'aõ',u'AÕ',u'aï',u'AÏ',
u'aá',u'AÁ',u'aà',u'AÀ',u'aå',u'AÅ',u'aã',u'AÃ',u'aä',u'AÄ',u'aé',u'AÉ',u'aè',u'AÈ',u'aú',u'AÚ',u'aü',u'AÜ',u'aë',u'AË',
u'eù',u'EÙ',u'eø',u'EØ',u'eû',u'EÛ',u'eõ',u'EÕ',u'eï',u'EÏ',u'eá',u'EÁ',u'eà',u'EÀ',u'eå',u'EÅ',u'eã',u'EÃ',u'eä',u'EÄ',u'í',u'Í',u'ì',u'Ì',u'æ',u'Æ',u'ó',u'Ó',u'ò',u'Ò',    
u'où',u'OÙ',u'oø',u'OØ',u'oû',u'OÛ',u'oõ',u'OÕ',u'oï',u'OÏ',u'oá',u'OÁ',u'oà',u'OÀ',u'oå',u'OÅ',u'oã',u'OÃ',u'oä',u'OÄ',u'ôù',u'ÔÙ',u'ôø',u'ÔØ',u'ôû',u'ÔÛ',u'ôõ',u'ÔÕ',u'ôï',u'ÔÏ',    
u'uù',u'UÙ',u'uø',u'UØ',u'uû',u'UÛ',u'uõ',u'UÕ',u'uï',u'UÏ',u'öù',u'ÖÙ',u'öø',u'ÖØ',u'öû',u'ÖÛ',u'öõ',u'ÖÕ',u'öï',u'ÖÏ',u'yø',u'YØ',u'yû',u'YÛ',u'yõ',u'YÕ',u'î',u'Î',u'yù',u'YÙ'    
]

_KhongDau = [
u'a',u'A',u'a',u'A',u'd',u'D',u'e',u'E',u'o',u'O',u'o',u'O',u'u',u'U',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',
u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',u'a',u'A',
u'e',u'E',u'e',u'E',u'e',u'E',u'e',u'E',u'e',u'E',u'e',u'E',u'e','uE',u'e',u'E',u'e',u'E',u'e',u'E',u'i',u'I',u'i',u'I',u'i',u'I',u'i',u'I',u'i',u'I',
u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',u'o',u'O',
u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'u',u'U',u'y',u'Y',u'y',u'Y',u'y',u'Y',u'y',u'Y',u'y',u'Y'
]

_VniWindows1= [    
        u'ñ',u'Ñ',u'í',u'Í',u'ì',u'Ì',u'æ',u'Æ',u'ö',u'Ö',u'î',u'Î'    
]
_VniWindows2= [
            u'aâ',u'AÂ',u'aê',u'AÊ',u'eâ',u'EÂ',u'ô',u'Ô',u'aù',u'AÙ',u'aø',u'AØ',u'aû',u'AÛ',u'aõ',u'AÕ',u'aï',u'AÏ',
            u'aá',u'AÁ',u'aà',u'AÀ',u'aå',u'AÅ',u'aã',u'AÃ',u'aä',u'AÄ',u'aé',u'AÉ',u'aè',u'AÈ',u'aú',u'AÚ',u'aü',u'AÜ',u'aë',u'AË',
            u'eù',u'EÙ',u'eø',u'EØ',u'eû',u'EÛ',u'eõ',u'EÕ',u'eï',u'EÏ',u'eá',u'EÁ',u'eà',u'EÀ',u'eå',u'EÅ',u'eã',u'EÃ',u'eä',u'EÄ',u'ó',u'Ó',u'ò',u'Ò',    
            u'oû',u'OÛ',u'oõ',u'OÕ',u'oï',u'OÏ',u'oá',u'OÁ',u'oà',u'OÀ',u'oå',u'OÅ',u'oã',u'OÃ',u'oä',u'OÄ',u'ôù',u'ÔÙ',u'ôø',u'ÔØ',u'ôû',u'ÔÛ',u'ôõ',u'ÔÕ',u'ôï',u'ÔÏ',    
            u'uù',u'UÙ',u'uø',u'UØ',u'uû',u'UÛ',u'uõ',u'UÕ',u'uï',u'UÏ',u'öù',u'ÖÙ',u'öø',u'ÖØ',u'öû',u'ÖÛ',u'öõ',u'ÖÕ',u'öï',u'ÖÏ',u'yø',u'YØ',u'yû',u'YÛ',u'yõ',u'YÕ',u'yù',u'YÙ',
            u'où',u'OÙ',u'oø',u'OØ',u'oâ',u'OÂ'
    ]

_Unicode1= [   
        u'đ',u'Đ',u'í',u'Í',u'ì',u'Ì',u'ỉ',u'Ỉ',u'ư',u'Ư',u'ỵ',u'Ỵ'      
]   
_Unicode2= [
        u'â',u'Â',u'ă',u'Ă',u'ê',u'Ê',u'ơ',u'Ơ',u'á',u'Á',u'à',u'À',u'ả',u'Ả',u'ã',u'Ã',u'ạ',u'Ạ',
        u'ấ',u'Ấ',u'ầ',u'Ầ',u'ẩ',u'Ẩ',u'ẫ',u'Ẫ',u'ậ',u'Ậ',u'ắ',u'Ắ',u'ằ',u'Ằ',u'ẳ',u'Ẳ',u'ẵ',u'Ẵ',u'ặ',u'Ặ',
        u'é',u'É',u'è',u'È',u'ẻ',u'Ẻ',u'ẽ',u'Ẽ',u'ẹ',u'Ẹ',u'ế',u'Ế',u'ề',u'Ề',u'ể',u'Ể',u'ễ',u'Ễ',u'ệ',u'Ệ',u'ĩ',u'Ĩ',u'ị',u'Ị',    
        u'ỏ',u'Ỏ',u'õ',u'Õ',u'ọ',u'Ọ',u'ố',u'Ố',u'ồ',u'Ồ',u'ổ',u'Ổ',u'ỗ',u'Ỗ',u'ộ',u'Ộ',u'ớ',u'Ớ',u'ờ',u'Ờ',u'ở',u'Ở',u'ỡ',u'Ỡ',u'ợ',u'Ợ',    
        u'ú',u'Ú',u'ù',u'Ù',u'ủ',u'Ủ',u'ũ',u'Ũ',u'ụ',u'Ụ',u'ứ',u'Ứ',u'ừ',u'Ừ',u'ử',u'Ử',u'ữ',u'Ữ',u'ự',u'Ự',u'ỳ',u'Ỳ',u'ỷ',u'Ỷ',u'ỹ',u'Ỹ',u'ý',u'Ý',
        u'ó#',u'Ó#',u'ò#',u'Ò#',u'ô#',u'Ô#'
        ]

def unaccent(text):	
    try:
        text = text.replace(u'Đ', 'D') # For Vietnamese
        text = text.replace(u'đ', 'd')  # For Vietnamese
    except NameError:
        pass
    result = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode("utf-8")
    return result
#unaccent('Quách Đồng Thắng, Krč,Koloměřice,Údraž,Poněšice,Hvožďany,Myšenec')

def tcvn3_unicode (txt):
    result = u''
    if txt != None:
        for c in txt:
            if c in _TCVN3:
                idx = _TCVN3.index(c)
                if idx >= 0:
                    c = _Unicode[idx]        
            result += c
    return result

def unicode_tcvn3 (txt):
    result = u''
    if txt != None:
        for c in txt:
            if c in _Unicode:
                idx = _Unicode.index(c)
                if idx >= 0:
                    c = _TCVN3[idx]        
            result += c
    return result


def capitalize (txt):    
    return txt.capitalize()

def unicode_vni(txt):  
    result = u''
    if txt != None:
        for c in txt:
            if c in _Unicode:
                idx = _Unicode.index(c)
                if idx >= 0:
                    c = _VNIWin[idx]        
            result += c
    return result

def vni_unicode(txt):
    if txt != None: 
        for j in range (0,len(txt)-1):
            c = txt[j:j+2]     
            if c in _VniWindows2:      
                idx = _VniWindows2.index(c)
                if idx >= 0:
                    c = _Unicode2[idx]                
                txt = txt.replace(txt[j:j+2],c)

        for j in range (0,len(txt)):
            c = txt[j:j+1]
            if c in _VniWindows1:      
                idx = _VniWindows1.index(c)
                if idx >= 0:
                    c = _Unicode1[idx]                
                txt = txt.replace(txt[j:j+1],c)         

        for i in range (0,len(txt)):       
            c = txt[i:i+1]  
            if c == u'ó'and txt[i+1:i+2] != u'#':
                c= u'ĩ'
                txt = txt[:i] + c + txt[i+1:]
            elif c== u'Ó'and txt[i+1:i+2] != u'#':
                c= u'Ĩ'
                txt = txt[:i] + c + txt[i+1:]
            elif c== u'ò'and txt[i+1:i+2] != u'#':
                c= u'ị'
                txt = txt[:i] + c + txt[i+1:]
            elif c== u'Ò'and txt[i+1:i+2] != u'#':
                c= u'Ị'
                txt = txt[:i] + c + txt[i+1:]
            elif c== u'ô'and txt[i+1:i+2] != u'#':
                c= u'ơ'
                txt = txt[:i] + c + txt[i+1:]
            elif c== u'Ô'and txt[i+1:i+2] != u'#':
                c= u'Ơ'
                txt = txt[:i] + c + txt[i+1:]

        txt = txt.replace(u'ó#',u'ó')
        txt = txt.replace(u'Ó#',u'Ó')
        txt = txt.replace(u'ò#',u'ò')
        txt = txt.replace(u'Ò#',u'Ò')
        txt = txt.replace(u'ô#',u'ô')
        txt = txt.replace(u'Ô#',u'Ô')
    return txt

def Convert(txt,source,target):    
    result = u''
    for c in txt:
        if c in source:
            idx = source.index(c)
            if idx >= 0:
                c = target[idx]
        result += c
    return result

def GetEncodeIndex(encodeTxt):
     return{
        "Unicode" : _Unicode,
        "TCVN3" : _TCVN3,
        "VNI-Windows": _VNIWin,
        "ANSI (Khong dau)" : _KhongDau,
    }.get(encodeTxt,_Unicode)

def GetCaseIndex(cText):
    return{
        0: "upper",
        1: "lower",
        2: "capitalize",
        3 : "title",
    }.get(cText, "None")

def ChangeCase(str, caseIndex):
    result = u''
    # Character Case-setting
    if caseIndex == "upper":
        result = str.upper()
    elif caseIndex == "lower":
        result = str.lower()
    elif caseIndex == "capitalize":
        result = str.capitalize()
    elif caseIndex == "title":
        result = str.title()
    return result