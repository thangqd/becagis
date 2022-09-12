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
  <summary>BecaGIS Processing Tools for QGIS</summary>
  <div align="center">
  <img src="images/tutorial/vect_voronoi.png">
</div>
  <ol>
    <li>         
      <a href="#vector">Vector</a>     
      <ul>
        <li><a href="#antipodal-layer">Antipodal layer</a></li>
        <li><a href="#split-polygon">Split Polygon</a></li>
        <li><a href="#closest-farthest">The closest and farthest pair of Points</a></li>
        <li><a href="#isolation">The most isololated point of a point set</a></li>
        <li><a href="#lec">The largest empty circle of a point set</a></li>
        <li><a href="#skeleton">Skeleton/ Medial Axis of Polygons</a></li>
      </ul>
       <li>         
      <a href="#attribute">Attribute</a>     
      <ul>
        <li><a href="#vietnamese-font-converter">Vietnamese Font Converter</a></li>
      </ul>
  </ol>
</details>


## Vector

### Antipodal layer

The antipodes of any place on Earth are distant from it by 180° of longitude and as many degrees to the North of the equator as the original is to the South (or vice versa).
<div align="center">
  <img src="images/tutorial/vect_antipode.png">
</div>
If the coordinates (longitude and latitude) of a point on the Earth’s surface are (θ, φ), then the coordinates of the antipodal point are (θ ± 180°,−φ). This relation holds true whether the Earth is approximated as a perfect sphere or as a reference ellipsoid.
<div align="center">
  <img src="images/tutorial/vect_antipodal_layer.png">
</div>

### Split Polygon

Split Polygon layer into almost equal parts using Voronoi Diagram
<div align="center">
  <img src="images/tutorial/vect_split_polygon.gif">
</div>

### Closest-farthest

The closest and farthest pair of Points
<div align="center">
  <img src="images/tutorial/vect_closestfarthest.png">
</div>

### isolation

The most isololated point of a point set
<div align="center">
  <img src="images/tutorial/vect_isolation.png">
</div>

### lec

The largest empty circle of a point set
<div align="center">
  <img src="images/tutorial/vect_lec.png">
</div>

### Skeleton

Skeleton/ Medial Axis of Polygons
<div align="center">
  <img src="images/tutorial/vect_skeleton.png">
</div>

### Vietnamese Font Converter
Vietnamese Font Converter
<div align="center">
  <img src="images/att_fontconvert.png">
</div>