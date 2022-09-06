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
        <li><a href="#create-antipodal-layer">Create antipodal layer</a></li>
        <li><a href="#split-polygon">Split Polygon</a></li>
      </ul>
  </ol>
</details>


## Vector

### Create antipodal layer

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