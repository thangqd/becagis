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
import processing
from qgis.core import *
import numpy as np
import math 

def mic(layer,tolerance):
    parameters1 = {'INPUT': layer,
                  'TOLERANCE': tolerance, 
                  'OUTPUT' : 'memory:center'
                  } 
    center = processing.run('qgis:poleofinaccessibility', parameters1)
    # idx =  center.dataProvider().fieldNameIndex("dist_pole")
    # for feat in center.getFeatures():
    #     radius = feat[idx]
    return center['OUTPUT']  

import math
from qgis.core import QgsGeometry, QgsPointXY

from qgis.core import QgsGeometry, QgsPointXY

import math
from qgis.core import QgsGeometry, QgsPointXY

def wedge_buffer(geometry, outer_radius, inner_radius, num_sectors, azimuth=0, num_segments=72):
    """
    Create wedge-shaped buffers around a point geometry for the given number of quadrants,
    with support for an inner and outer radius, and an optional azimuth (degree from north).

    :param geometry: QgsGeometry of the point around which to create the buffer.
    :param outer_radius: Outer radius of the wedge buffer.
    :param inner_radius: Inner radius of the wedge buffer.
    :param num_sectors: Number of quadrants to create.
    :param azimuth: Azimuth (degree from north) where the first wedge starts. Default is 0 (north).
    :param num_segments: Number of segments to use for circle approximation.
    :return: List of QgsGeometry objects representing the wedge buffers.
    """
    # Normalize azimuth to the range 0° to 360°
    azimuth = azimuth % 360

    # Get the center point of the geometry
    center = geometry.asPoint()
    
    # Calculate the angle range for each quadrant
    angle_step = 360 / num_sectors
    
    wedge_geometries = []

    for quadrant in range(num_sectors):
        # Calculate the start and end angles for the wedge, adjusted by the azimuth
        angle_start = azimuth + quadrant * angle_step
        angle_end = azimuth + (quadrant + 1) * angle_step
        
        # Convert start and end angles to radians
        angle_start_rad = math.radians(angle_start)
        angle_end_rad = math.radians(angle_end)
        
        # Create a list of points for the outer arc of the wedge
        outer_arc_points = []
        for i in range(num_segments + 1):
            angle = angle_start_rad + i * (angle_end_rad - angle_start_rad) / num_segments
            x = center.x() + outer_radius * math.cos(angle)
            y = center.y() + outer_radius * math.sin(angle)
            outer_arc_points.append(QgsPointXY(x, y))
        
        # Create a list of points for the inner arc of the wedge (in reverse order)
        inner_arc_points = []
        for i in range(num_segments, -1, -1):
            angle = angle_start_rad + i * (angle_end_rad - angle_start_rad) / num_segments
            x = center.x() + inner_radius * math.cos(angle)
            y = center.y() + inner_radius * math.sin(angle)
            inner_arc_points.append(QgsPointXY(x, y))
        
        # Combine the inner and outer arcs to form the wedge polygon
        wedge_points = outer_arc_points + inner_arc_points
        
        # Create the geometry for the wedge buffer
        wedge_geometry = QgsGeometry.fromPolygonXY([wedge_points])
        wedge_geometries.append(wedge_geometry)

    return wedge_geometries

def longestline_insidepolygon():
    points = QgsProject.instance().mapLayersByName('point')[0]
    polygons = QgsProject.instance().mapLayersByName('polygon')[0]
    azimuthsteps = 1 # number of trys, the lower the value the slower the performance but the better the result!!
    linedist = 1000000 # imaginary maximum line length

    vl = QgsVectorLayer("LineString?crs={}&index=yes".format(points.crs().authid()), "Longest_line", "memory")
    pr = vl.dataProvider()

    polygons_idx = QgsSpatialIndex(polygons.getFeatures()) # spatial index for polygonlayer

    with edit(vl):
        for point in points.getFeatures(): # iterate over pointlayer
            for pid in polygons_idx.intersects(point.geometry().boundingBox()): # iterate over intersecting polygons
                intersectingpolygon = polygons.getFeature(pid) # get current intersecting polygon
                linedict = {} # refresh the temporary featid linelength dictionary
                resultlines = [] # list of maximum linelengths id's
                step = 0 # reset the current step
                # create a temporary layer
                tmpvl = QgsVectorLayer("MultiLineString?crs={}&index=yes".format(points.crs().authid()), "tmplines", "memory")
                tmppr = tmpvl.dataProvider()
                for step in range(180,360, azimuthsteps): # iterate in the specified steps over the azimuths from current point
                    with edit(tmpvl):
                        tmplinefeat = QgsFeature() # create a feature
                        stepopposite = step - 180 # reverse the azimuth
                        pointpoint = QgsPoint(point.geometry().asPoint()) # make a QgsPoint out of the pointgeometry
                        startpoint = pointpoint.project(linedist,step) # Project a point in the given azimuth (step) from the current point and declare it as startpoint of the line
                        endpoint = pointpoint.project(linedist,stepopposite) # Project a point on the opposite site from the startpoint, so we get a straigt line
                        tmplinefeat.setGeometry(intersectingpolygon.geometry().intersection(QgsGeometry.fromPolyline([startpoint, endpoint]))) # create a line inside the polygon
                        tmpvl.addFeature(tmplinefeat) # add the feature
                        tmpvl.updateFeature(tmplinefeat) # update it
                # convert the temporary layer to a singleline-layer
                blubb = processing.run("native:multiparttosingleparts",{'INPUT':tmpvl,'OUTPUT':'TEMPORARY_OUTPUT'})
                singlelines = blubb['OUTPUT']
                singlelines_idx = QgsSpatialIndex(singlelines.getFeatures()) # spatial index for singlelines
                for slid in singlelines_idx.intersects(point.geometry().boundingBox()): # iterate over features of singlelines that intersect with their point
                    slidf = singlelines.getFeature(slid) # get the feature by the id from the index
                    linedict[slid] = slidf.geometry().length() # add line's featureid and length to the temporary dictionary
                resultlines.append(max(linedict, key=linedict.get, default=0)) # append the longest line's featureid from the temporary dictionary to the resultlist
                resultfeatures = [] # create an empty list of matching features
                for slf in singlelines.getFeatures(QgsFeatureRequest().setFilterFids(resultlines)): # iterate over the matching features in templayer
                    resultfeatures.append(slf) # append features to resultlist
                pr.addFeatures(resultfeatures) # copy all resultfeatures to final layer
                # remove the temporary layers
                QgsProject.instance().removeMapLayers([tmpvl.id()])
                QgsProject.instance().removeMapLayers([singlelines.id()])
    QgsProject.instance().addMapLayer(vl) # add the finalized layer to canvas

def lines_of_sight():
    polylyr = QgsProject.instance().mapLayersByName('polygon')[0]
    g = [f.geometry() for f in polylyr.getFeatures()][0]
    verts = [v for v in g.vertices()]

    pointlyr = QgsProject.instance().mapLayersByName('Grid')[0]
    point = QgsPoint([f.geometry() for f in pointlyr.getFeatures()][0].asPoint())

    linelist = []
    for vert in verts:
        Line = QgsGeometry.fromPolyline([vert, point])
        linelist.append(Line)

    vl = QgsVectorLayer("LineString?crs={}&index=yes".format(pointlyr.crs().authid()), "myLayer", "memory")
    provider = vl.dataProvider()

    for L in linelist:
        f = QgsFeature()
        f.setGeometry(L)
        provider.addFeature(f)

    QgsProject.instance().addMapLayer(vl)
#############
# --> Intersection
# --> Extract specific vertices (0/ -1)
# --> Create Polygon from specific vertices
    vertices = QgsProject.instance().mapLayersByName('Vertices')[0] 
    visibility = QgsVectorLayer("Polygon?crs={}&index=yes".format(vertices.crs().authid()), "myLayer", "memory")
    points=[]
    polygon_feature=QgsFeature()
    for feature in vertices.getFeatures():#    print (feature.id(),feature.geometry().asPoint())
        points.append(feature.geometry().asPoint()) 
        polygon_feature.setAttributes(feature.attributes())

    #print (points)
    polygon_geometry= QgsGeometry.fromPolygonXY([points])
    polygon_feature.setGeometry(polygon_geometry) 
    #print(polygon_feature.geometry())
    visibility.dataProvider().addFeature(polygon_feature)
    QgsProject.instance().addMapLayer(visibility)

    #    polygon = [[QgsPointXY(i[0], i[1]) for i in points]]                
    #    new_feature = QgsFeature()
    #    new_feature.setAttributes(feature.attributes())
    ##    new_feature.setGeometry(polygon)    
    #    visibility.dataProvider().addFeature(new_feature)
    #QgsProject.instance().addMapLayer(visibility)