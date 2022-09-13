<!-- PROJECT LOGO -->
<p align="center">
    <img src="images/becagistools_logo.png" alt="Logo" width="90" height="75">
  <h3 align="center">BecaGIS Tools</h3>
  <p align="center">
    <b><i>BecaGIS GeoProcessing Tools for QGIS</i><b>
    <br />
  </p>
</p>

## Descriptions
<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>BecaGIS GeoProcessing Tools for QGIS</summary>
  <div align="center">
  <img src="images/tutorial/vect_voronoi.png">
</div>
  <ol>
    <li>         
      <a href="#vector">Vector</a>     
      <ul>
        <li><a href="#antipodal-layer">Antipodal layer</a></li>
        <li><a href="#closest-farthest">The closest and farthest pair of points</a></li>
        <li><a href="#isolation">The most isololated point of a point set</a></li>
        <li><a href="#lec">The largest empty circle of a point set</a></li>
        <li><a href="#skeleton">Skeleton/ Medial Axis of Polygons</a></li>
        <li><a href="#split-polygon">Split Polygon</a></li>
      </ul>
       <li>         
      <a href="#attribute">Attribute</a>     
      <ul>
        <li><a href="#vietnamese-font-converter">Vietnamese Font Converter</a></li>
      </ul>
      <li>  
      <a href="#expressions">Expressions</a>     
      <ul>
        <li><a href="#antipode">antipode</a></li>
        <li><a href="#capitalize">capitalize</a></li>
        <li><a href="#unaccent">unaccent</a></li>
        <li><a href="#swapcase">swapcase</a></li>
        <li><a href="#tcvn3_unicode">tcvn3_unicode</a></li>
        <li><a href="#unicode_tcvn3">unicode_tcvn3</a></li>
        <li><a href="#vni_unicode">vni_unicode</a></li>
        <li><a href="#unicode_vni">unicode_vni</a></li>
      </ul>
  </ol>
</details>


## Vector

### Antipodal layer

The antipodes of any place on Earth are distant from it by 180° of longitude and as many degrees to the North of the equator as the original is to the South (or vice versa).

If the coordinates (longitude and latitude) of a point on the Earth’s surface are (θ, φ), then the coordinates of the antipodal point are (θ ± 180°,−φ). This relation holds true whether the Earth is approximated as a perfect sphere or as a reference ellipsoid.

<div align="center">
  <img src="images/tutorial/vect_antipode.png">
</div>


<div align="center">
  <img src="images/readme/vect_antipodal_layer.png">
</div>

### Closest-farthest

The closest and farthest pair of Points
<div align="center">
  <img src="images/readme/vect_closest_farthest.png">
</div>


### Isolation

The most isololated point of a point set
<div align="center">
  <img src="images/readme/vect_isolation.png">
</div>

### LEC

The largest empty circle of a point set
<div align="center">
  <img src="images/readme/vect_lec.png">
</div>

### Skeleton

Skeleton/ Medial Axis of Polygons (Output should be manually refined)
<div align="center">
  <img src="images/readme/vect_skeleton.png">
</div>

### Split Polygon

Split Polygon layer into almost equal parts using Voronoi Diagram
<div align="center">
  <img src="images/readme/vect_split_polygon.png">
</div>

### Vietnamese Font Converter
Vietnamese Font Converter: TCVN3 <--> Unicode <--> VNI-Windows <--> Unaceented; UPPER CASE <--> lower case <--> Capitalize Each Word <--> Sentence case <--> sWAP Case
<div align="center">
  <img src="images/readme/att_fontconvert.png">
</div>

## Expressions
<style type="text/css">
.function {
color: #05688f;
font-weight: bold;
}
.parameters {
color: red;
font-style:italic
}
</style>

### antipode

Calculate antipode of a (lat, long) input.

<h4>Syntax</h4>    
<li><span class = function>antipode</span>(<span class = parameters>lat</span>, <span class = parameters>long</span>) 
or <span class = function>antipode</span>(<span class = parameters>$y</span>, <span class = parameters>$x</span>) in WGS84 CRS</li>    
<h4>Example usage</h4>
<ul>
<li><span class = function>antipode</span>(<span class = parameters>10.784229903855978</span>, <span class = parameters>106.70356815497277</span>) &rarr; returns a point geometry</li>
<li><span class = function>geom_to_wkt</span>(<span class = function>antipode</span>(<span class = parameters>10.784229903855978</span>, <span class = parameters>106.70356815497277</span>)) &rarr; 'Point (-73.29643185 -10.7842299)'</li>
</ul>

<div align="center">
  <img src="images/readme/vect_antipode_x.png">
</div> 
<div align="center">
  <img src="images/readme/vect_antipode_y.png">
</div> 

### capitalize

Convert text to Capitalized.

<h4>Syntax</h4>    
  <li><span class = function>capitalize</span>(<span class = parameters>string</span>)</li>
<h4>Example usage</h4>

<ul>
  <li><span class = function>capitalize</span>(<span class = parameters>'quách đồng thắng''</span>)&rarr; 'Quách đồng thắng'</li>
</ul>   
<div align="center">
  <img src="images/readme/att_capitalize.png">
</div> 
       

### unaccent
Convert text to unaccented.
<h4>Syntax</h4>    
  <li><span class = function>unaccent</span>(<span class = parameters>string</span>)</li>
<h4>Example usage</h4>

<ul>
  <li><span class = function>unaccent</span>(<span class = parameters>'Quách Đồng Thắng'</span>)&rarr; 'Quach Dong Thang'</li>
</ul>    
<div align="center">
  <img src="images/readme/att_unaccent.png">
</div>

### tcvn3_unicode
Convert TCVN3 to Unicode.
<h4>Syntax</h4>    
  <li><span class = function>tcvn3_unicode</span>(<span class = parameters>string</span>)</li>
<h4>Example usage</h4> 
<ul>
  <li><span class = function>tcvn3_unicode</span>(<span class = parameters>'Qu¸ch §ång Th¾ng'</span>)&rarr; 'Quách Đồng Thắng'</li>
</ul>  
<div align="center">
  <img src="images/readme/att_tcnv3_unicode.png">
</div>

### unicode_tcvn3

Convert Unicode to TCVN3.

<h4>Syntax</h4>    
  <li><span class = function>unicode_tcvn3</span>(<span class = parameters>string</span>)</li>
<h4>Example usage</h4>

<ul>
  <li><span class = function>unicode_tcvn3</span>(<span class = parameters>'Quách Đồng Thắng'</span>)&rarr; 'Qu¸ch §ång Th¾ng'</li>
</ul>    
<div align="center">
  <img src="images/readme/att_unicode_tcnv3.png">
</div>

### vni_unicode
Convert VNI Windows to Unicode.
<h4>Syntax</h4>    
<li><span class = function>vni_unicode</span>(<span class = parameters>string</span>)</li>
<h4>Example usage</h4>

<ul>
<li><span class = function>vni_unicode</span>(<span class = parameters>''Quaùch Ñoàng Thaéng''</span>)&rarr; 'Quách Đồng Thắng'</li>
</ul>    
<div align="center">
  <img src="images/readme/att_vni_unicode.png">
</div>


### unicode_vni

Convert Unicode to VNI Windows.

<h4>Syntax</h4>    
<li><span class = function>unicode_vni</span>(<span class = parameters>string</span>)</li>
<h4>Example usage</h4>

<ul>
<li><span class = function>unicode_vni</span>(<span class = parameters>'Quách Đồng Thắng'</span>)&rarr; 'Quaùch Ñoàng Thaéng'</li>
</ul>    
<div align="center">
  <img src="images/readme/att_unicode_vni.png">
</div>


### swapcase

sWAP Case of input text

<h4>Syntax</h4>    
  <li><span class = function>swapcase</span>(<span class = parameters>string</span>)</li>
<h4>Example usage</h4>

<ul>
  <li><span class = function>swapcase</span>(<span class = parameters>'Quách Đồng Thắng'</span>)&rarr; 'qUÁCH đỒNG tHẮNG'</li>
</ul>    
<div align="center">
  <img src="images/readme/att_swapcase.png">
</div> 