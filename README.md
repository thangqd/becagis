<!-- PROJECT LOGO -->
<p align="center">
    <img src="images/becagis_logo.png" alt="Logo" width="90" height="75">
  <h3 align="center">BecaGIS</h3>
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
        <li><a href="#mic">The maximum inscribed circle of polygons</a></li>
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


### MIC

The maximum inscribed circle of polygons
<div align="center">
  <img src="images/readme/vect_mic.png">
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

### antipode

Calculate antipode of a (lat, long) input.
<h4>Syntax</h4>
<li>
<code>antipode(lat, long) or antipode($y, $x)</span> in WGS84 CRS</code>
</li> 
<h4>Example usage</h4>
<li>
<code> antipode(10.784229903855978, 106.70356815497277) → returns a point geometry </code>
</li>
<li>
<code>geom_to_wkt(antipode(10.784229903855978, 106.70356815497277)) → 'Point (-73.29643185 -10.7842299)'</code>
</li>
<br/>
<div align="center">
  <img src="images/readme/vect_antipode_x.png">
</div> 
<div align="center">
  <img src="images/readme/vect_antipode_y.png">
</div> 

### capitalize

Convert text to Capitalized.

<h4>Syntax</h4>
<li>
<code>capitalize(string)</code>
</li> 
<h4>Example usage</h4>
<li>
<code> capitalize('quách đồng thắng') → 'Quách đồng thắng' </code>
</li>
<br/>
<div align="center">
  <img src="images/readme/att_capitalize.png">
</div> 
       

### unaccent
Convert text to unaccented.

<h4>Syntax</h4>
<li>
<code>unaccent(string)</code>
</li> 
<h4>Example usage</h4>
<li>
<code> unaccent('Quách Đồng Thắng') → 'Quach Dong Thang' </code>
</li>
<br/>

<div align="center">
  <img src="images/readme/att_unaccent.png">
</div>

### tcvn3_unicode
Convert TCVN3 to Unicode.
<h4>Syntax</h4>
<li>
<code>tcvn3_unicode(string)</code>
</li> 
<h4>Example usage</h4>
<li>
<code> tcvn3_unicode('Qu¸ch §ång Th¾ng') → 'Quách Đồng Thắng' </code>
</li>
<br/>
<div align="center">
  <img src="images/readme/att_tcnv3_unicode.png">
</div>

### unicode_tcvn3

Convert Unicode to TCVN3.

<h4>Syntax</h4>
<li>
<code>unicode_tcvn3(string)</code>
</li> 
<h4>Example usage</h4>
<li>
<code> unicode_tcvn3('Quách Đồng Thắng') → 'Qu¸ch §ång Th¾ng' </code>
</li>
<br/>
<div align="center">
  <img src="images/readme/att_unicode_tcnv3.png">
</div>

### vni_unicode
Convert VNI Windows to Unicode.
<h4>Syntax</h4>
<li>
<code>vni_unicode(string)</code>
</li> 
<h4>Example usage</h4>
<li>
<code> vni_unicode('Quaùch Ñoàng Thaéng') → 'Quách Đồng Thắng' </code>
</li>
<br/>
<div align="center">
  <img src="images/readme/att_vni_unicode.png">
</div>


### unicode_vni

Convert Unicode to VNI Windows.

<h4>Syntax</h4>
<li>
<code>unicode_vni(string)</code>
</li> 
<h4>Example usage</h4>
<li>
<code> unicode_vni('Quách Đồng Thắng') → 'Quaùch Ñoàng Thaéng' </code>
</li>
<br/>
<div align="center">
  <img src="images/readme/att_unicode_vni.png">
</div>


### swapcase

sWAP Case of input text

<h4>Syntax</h4>
<li>
<code>swapcase(string)</code>
</li> 
<h4>Example usage</h4>
<li>
<code> swapcase('Quách Đồng Thắng') → 'qUÁCH đỒNG tHẮNG' </code>
</li>
<br/>
<div align="center">
  <img src="images/readme/att_swapcase.png">
</div> 
