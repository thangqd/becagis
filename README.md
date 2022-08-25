<!-- PROJECT LOGO -->
<p align="center">
    <img src="images/becagistools_logo.png" alt="Logo" width="90" height="75">
  <h3 align="center">BecaGIS Tools</h3>
  <p align="center">
    <b><i>BecaGIS GeoProcessing Tools</i><b>
    <br />
  </p>
</p>

## Tutorials
<div style="text-align: center;"><a
 style="font-weight: bold;"
 href="https://www.youtube.com/watch?v=n7-Iqj8FK_A">Click here to learn how to use the BecaGISTools plugin on YouTube</a></div>


## Description of each tool


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Set of Tools</summary>
  <ol>
    <li>     
      <a href="#vector">Vector</a>
      <ul>
        <li><a href="#calculate-polygon-angles">Calculate polygon angles</a></li>
      </ul>      
      <ul>
        <li><a href="#merge-lines-in-direction">Merge lines in direction</a></li>
      </ul>     
      <ul>
        <li><a href="#reverse--vertext-order">Reverse vertext order</a></li>
      </ul>
  </ol>
</details>


## Vector

### Calculate polygon angles
This algorithm calculates the inner and outer angles of the polygon vertices of a layer. The output layer corresponds to the points with the calculated angles stored in the respective attributes.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/vect_polygon_angles.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Merge lines in direction
This algorithm merges lines that touch at their starting or ending points and has the same direction (given a tolerance in degrees). <p>For the attributes can be considered:</p>1 - merge lines that have the same attributes; or</li><li>2 - keep the attributes of the longest line.</li>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/vect_directional_merge.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Reverse vertex order
Inverts vertex order for polygons and lines.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/vect_reverse_vertex_sequence.jpg"></td>
    </tr>
  </tbody>
</table>
</div>