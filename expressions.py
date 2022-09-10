# -*- coding: utf-8 -*-

"""
/***************************************************************************
 becagistools
                                 A QGIS plugin
 GeoPorocessing Tools based on lftools https://github.com/LEOXINGU/lftools
                              -------------------
        Date                : 2022-08-25
        copyright            : (L) 2022 by Thang Quach
        email                : quachdongthang@gmail.com
 ***************************************************************************/

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


from qgis.core import *
from qgis.gui import *
from qgis.utils import qgsfunction
from becagistools.becagislibrary.latlong import (antipode as ANTIPODE)
from becagistools.becagislibrary.attribute import (tcvn3_unicode as TCVN3_UNICODE,
                                                   unicode_tcvn3 as UNICODE_TCVN3,
                                                   vni_unicode as VNI_UNICODE,
                                                   unicode_vni as UNICODE_VNI,
                                                   capitalize as CAPITALIZE,
                                                   unaccent as UNACCENT)
from becagistools.becagislibrary.imgs import Imgs
group_name = 'BecaGIS Tools'

# https://qgis.org/pyqgis/3.2/core/Expression/QgsExpression.html

LOC = QgsApplication.locale()[:2]
def tr(*string):
    # Translate to Vietnamese: arg[0] - English (translate), arg[1] - Vietnamese
    if LOC == 'vi':
        if len(string) == 2:
            return string[1]
        else:
            return string[0]
    else:
        return string[0]

# @qgsfunction(args='auto', group=group_name,usesgeometry=True)
@qgsfunction(args='auto', group=group_name)
def antipode(lat,lon, feature, parent):
    """ <style type="text/css">
      .function {
      color: #05688f;
      font-weight: bold;
      }
      .parameters {
      color: red;
      font-style:italic
      }
    </style>
    Calculate antipode of a (lat, long) input.
    <h4>Syntax</h4>    
      <li><span class = function>antipode</span>(<span class = parameters>lat</span>, <span class = parameters>long</span>) 
      or <span class = function>antipode</span>(<span class = parameters>$y</span>, <span class = parameters>$x</span>) in WGS84 CRS</li>    
    <h4>Example usage</h4>
    <ul>
      <li><span class = function>antipode</span>(<span class = parameters>10.784229903855978</span>, <span class = parameters>106.70356815497277</span>) &rarr; returns a point geometry</li>
      <li><span class = function>geom_to_wkt</span>(<span class = function>antipode</span>(<span class = parameters>10.784229903855978</span>, <span class = parameters>106.70356815497277</span>)) &rarr; 'Point (-73.29643185 -10.7842299)'</li>
    </ul>
    """   
    # lat= feature.geometry().asPoint().x()
    # lon = feature.geometry().asPoint().y()

    antipode_lat,antipode_lon =  ANTIPODE(lat,lon)      
    antipode_point = QgsPointXY(antipode_lon, antipode_lat)
    return(QgsGeometry.fromPointXY(antipode_point))
    

@qgsfunction(args='auto', group=group_name)
def capitalize(string, feature, parent):
  """<style type="text/css">
    .function {
    color: #05688f;
    font-weight: bold;
    }
    .parameters {
    color: red;
    font-style:italic
    }
  </style>
  Convert text to Capitalized.
  <h4>Syntax</h4>    
    <li><span class = function>capitalize</span>(<span class = parameters>string</span>)</li>
  <h4>Example usage</h4>

  <ul>
    <li><span class = function>capitalize</span>(<span class = parameters>'quách đồng Thắng''</span>)&rarr; 'Quách đồng Thắng'</li>
  </ul>    
  """ 
  return(CAPITALIZE(string))    


@qgsfunction(args='auto', group=group_name)
def tcvn3_unicode(string, feature, parent):
    """<style type="text/css">
      .function {
      color: #05688f;
      font-weight: bold;
      }
      .parameters {
      color: red;
      font-style:italic
      }
    </style>
    Convert TCVN3 to Unicode.
    <h4>Syntax</h4>    
      <li><span class = function>tcvn3_unicode</span>(<span class = parameters>string</span>)</li>
    <h4>Example usage</h4> 
    <ul>
      <li><span class = function>tcvn3_unicode</span>(<span class = parameters>'Qu¸ch §ång Th¾ng'</span>)&rarr; 'Quách Đồng Thắng'</li>
    </ul>    
    """ 
    return(TCVN3_UNICODE(string)) 

@qgsfunction(args='auto', group=group_name)
def unaccent(string, feature, parent):
  """<style type="text/css">
    .function {
    color: #05688f;
    font-weight: bold;
    }
    .parameters {
    color: red;
    font-style:italic
    }
  </style>
  Convert unicode text to unacceted.
  <h4>Syntax</h4>    
    <li><span class = function>unaccent</span>(<span class = parameters>string</span>)</li>
  <h4>Example usage</h4>

  <ul>
    <li><span class = function>unaccent</span>(<span class = parameters>'Quách Đồng Thắng'</span>)&rarr; 'Quach Dong Thang'</li>
  </ul>    
  """  
  return(UNACCENT(string))     

@qgsfunction(args='auto', group=group_name)
def unicode_tcvn3(string, feature, parent):
  """<style type="text/css">
  .function {
  color: #05688f;
  font-weight: bold;
  }
  .parameters {
  color: red;
  font-style:italic
  }
</style>
Convert Unicode to TCVN3.
<h4>Syntax</h4>    
  <li><span class = function>unicode_tcvn3</span>(<span class = parameters>string</span>)</li>
<h4>Example usage</h4>

<ul>
  <li><span class = function>unicode_tcvn3</span>(<span class = parameters>'Quách Đồng Thắng'</span>)&rarr; 'Qu¸ch §ång Th¾ng'</li>
</ul>    
  """
  return(UNICODE_TCVN3(string))   

@qgsfunction(args='auto', group=group_name)
def unicode_vni(string, feature, parent):
  """<style type="text/css">
  .function {
  color: #05688f;
  font-weight: bold;
  }
  .parameters {
  color: red;
  font-style:italic
  }
  </style>
  Convert Unicode to VNI Windows.
  <h4>Syntax</h4>    
  <li><span class = function>unicode_vni</span>(<span class = parameters>string</span>)</li>
  <h4>Example usage</h4>

  <ul>
  <li><span class = function>unicode_vni</span>(<span class = parameters>'Quách Đồng Thắng'</span>)&rarr; 'Quaùch Ñoàng Thaéng'</li>
  </ul>    
  """    
  return(UNICODE_VNI(string)) 

@qgsfunction(args='auto', group=group_name)
def vni_unicode(string, feature, parent):
  """<style type="text/css">
  .function {
  color: #05688f;
  font-weight: bold;
  }
  .parameters {
  color: red;
  font-style:italic
  }
  </style>
  Convert VNI Windows to Unicode.
  <h4>Syntax</h4>    
  <li><span class = function>vni_unicode</span>(<span class = parameters>string</span>)</li>
  <h4>Example usage</h4>

  <ul>
  <li><span class = function>vni_unicode</span>(<span class = parameters>''Quaùch Ñoàng Thaéng''</span>)&rarr; 'Quách Đồng Thắng'</li>
  </ul>    
  """
  return(VNI_UNICODE(string))