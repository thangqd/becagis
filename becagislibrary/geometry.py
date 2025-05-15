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
from qgis.core import QgsGeometry, QgsPointXY, QgsVectorLayer,QgsFeature,QgsProcessingFeedback,QgsWkbTypes
# from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint, QgsProcessingFeedback
import qgis.processing as processing

import numpy as np
import math 
from pyproj.crs import CRS
import random

import numpy as np
import random
from qgis.core import QgsGeometry, QgsPointXY


def skeleton(polygon: QgsGeometry, density, simplified_tol, postprocessing) -> QgsFeature:
    poly_layer = QgsVectorLayer('Polygon', 'polygon_layer', 'memory')
    provider = poly_layer.dataProvider()

    # Create a feature and add the input polygon geometry
    feature = QgsFeature()
    feature.setGeometry(polygon)
    provider.addFeatures([feature])    

    if (density > 0):
        parameters3 = {'INPUT': poly_layer,
                    'DISTANCE' :	float(density),
                    'OUTPUT' : "memory:points"} 
        points = processing.run('qgis:pointsalonglines', parameters3,feedback=QgsProcessingFeedback())
    elif density==0:
        parameters3 = {'INPUT': poly_layer,
                    'OUTPUT' : "memory:points"} 
        points = processing.run('qgis:extractvertices', parameters3,feedback=QgsProcessingFeedback())

    # output = points['OUTPUT'].getFeatures() 

    parameters4 = {'INPUT': points['OUTPUT'],                  
                'BUFFER' : 0, # percentage
                'OUTPUT' : 'memory:voronoi'} 
    voronoipolygon = processing.run('qgis:voronoipolygons',parameters4,feedback=QgsProcessingFeedback())
    
    parameters5 = {'INPUT': voronoipolygon['OUTPUT'],
                    'OUTPUT' : 'memory:voronoipolyline'} 
    voronoipolyline = processing.run('qgis:polygonstolines',parameters5,feedback=QgsProcessingFeedback())
    
    
    parameters6 = {'INPUT': voronoipolyline['OUTPUT'],					
                    'OUTPUT' : 'memory:explode'}
    explode = processing.run('qgis:explodelines',parameters6,feedback=QgsProcessingFeedback())   
 
    
    parameters7 = {'INPUT': explode['OUTPUT'],
                    'PREDICATE' : [6], # within					
                    'INTERSECT':  poly_layer,                    	
                    'METHOD' : 0,
                    'OUTPUT' : 'memory:candidate'}
    candidate= processing.run('qgis:selectbylocation',parameters7,feedback=QgsProcessingFeedback())   
   
    
    parameters8 = {'INPUT':candidate['OUTPUT'],
                    'OUTPUT':  'memory:medialaxis'}
    medialaxis = processing.run('qgis:saveselectedfeatures',parameters8,feedback=QgsProcessingFeedback())    
 
    
    parameters9 = {'INPUT':medialaxis['OUTPUT'],
                    'OUTPUT':  'memory:deleteduplicategeometries'}
    deleteduplicategeometries = processing.run('qgis:deleteduplicategeometries',parameters9,feedback=QgsProcessingFeedback())    
 
    
    parameter10 =  {'INPUT':deleteduplicategeometries['OUTPUT'],
                    'OUTPUT':  "memory:medialaxis_dissolve"}
    medialaxis_dissolve = processing.run('qgis:dissolve',parameter10,feedback=QgsProcessingFeedback()) 
    
    
    parameter11 = {'INPUT':medialaxis_dissolve['OUTPUT'],
                    'METHOD' : 0,
                    'TOLERANCE' : float(simplified_tol), 
                    'OUTPUT':  "memory:simplify"}
    simplify = processing.run('qgis:simplifygeometries',parameter11,feedback=QgsProcessingFeedback())    

    parameter12 = {'INPUT':simplify['OUTPUT'],                    
                    'OUTPUT':  "memory:explode"}
    explode = processing.run('qgis:explodelines',parameter12,feedback=QgsProcessingFeedback()) 

          
    parameter13 = {'LINES':explode['OUTPUT'],
                    'ANGLE' : 30,
                    'TYPE' : 1, # Keep the attribute of the longest line
                    'OUTPUT':  "memory:skeleton"}
    ske = processing.run('becagis:directionalmerge',parameter13,feedback=QgsProcessingFeedback())    
    output =  ske['OUTPUT'].getFeatures()
    
    if postprocessing:        
        features = ske['OUTPUT'].getFeatures()
        longest_feature = next(features, None)  
        max_length = longest_feature.geometry().length()

        # crs = ske['OUTPUT'].crs().authid() 
        # centerline_candidate = QgsVectorLayer(f'MultiLineString?crs={crs}', 'Longest Geometry', 'memory')
        centerline_candidate = QgsVectorLayer(f'', 'Longest Geometry', 'memory')
        # Add fields to the new layer (same as input layer)
        centerline_candidate.dataProvider().addAttributes(ske['OUTPUT'].fields())
        centerline_candidate.updateFields()

        # Iterate through each feature and calculate its geometry length
        for feature in features:
            geom = feature.geometry()
            length = geom.length()  # Calculate length of the geometry

            if length > max_length:
                max_length = length
                longest_feature = feature

            # Add the longest feature to the new layer
        centerline_candidate.dataProvider().addFeature(longest_feature)

        parameter14 = {'INPUT':centerline_candidate,
                        'START_DISTANCE' : float(max_length/2),
                        'END_DISTANCE' : float(max_length/2),
                        'OUTPUT':  "memory:extended"}
        extended = processing.run('qgis:extendlines',parameter14,feedback=QgsProcessingFeedback())    

        parameter15 = {'INPUT': extended['OUTPUT'],
                    'OVERLAY': poly_layer,
                    'OVERLAY_FIELDS' : None,
                        'OUTPUT':  "memory:intersected"}
        intersected = processing.run('qgis:intersection',parameter15,feedback=QgsProcessingFeedback())    

        output =  intersected['OUTPUT'].getFeatures()
    
    return output


def split_polygon(polygon: QgsGeometry, points_number: int, k: int):
    """
    Splits a polygon by generating random points, clustering them, 
    creating Voronoi polygons, and intersecting them with the input polygon.

    Parameters:
        polygon (QgsGeometry): The input polygon geometry.
        points_number (int): Number of random points to generate.
        k (int): Number of clusters to create.

    Returns:
        list of QgsGeometry: Intersected Voronoi polygons confined within the input polygon.
    """
    # Generate random points within the polygon
    random_points = generate_random_points(polygon, points_number)
    
    # Cluster the random points
    clustered_points, clustered_centroids = k_means(random_points, k)
    
    # Create a temporary memory layer for the points
    # layer = QgsVectorLayer('Point?crs=EPSG:4326', 'temp_points_layer', 'memory')
    clustered_layer = QgsVectorLayer('Point', 'temp_points_layer', 'memory')
    provider = clustered_layer.dataProvider()

    # Add points to the clustered_layer
    features = []
    for point in clustered_centroids:
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(point))
        features.append(feature)
    provider.addFeatures(features)

    parameters = {'INPUT': clustered_layer,                  
                'BUFFER' : 200, # percentage
                'OUTPUT' : 'memory:voronoi'} 
    voronoi_polygons = processing.run('qgis:voronoipolygons',parameters,feedback=QgsProcessingFeedback())

    # Intersect Voronoi polygons with the original polygon
    voronoi_layer = voronoi_polygons['OUTPUT']
    intersected_polygons = []

    for feature in voronoi_layer.getFeatures():
        voronoi_geom = feature.geometry()
        intersection_geom = voronoi_geom.intersection(polygon)
        if not intersection_geom.isEmpty():
            intersected_polygons.append(intersection_geom)
    
    return intersected_polygons

def generate_random_points(polygon: QgsGeometry, points_number: int):
    """Generates random points within a given polygon."""
    points = []
    bbox = polygon.boundingBox()

    while len(points) < points_number:
        # Generate random coordinates within the bounding box
        x = random.uniform(bbox.xMinimum(), bbox.xMaximum())
        y = random.uniform(bbox.yMinimum(), bbox.yMaximum())
        point = QgsPointXY(x, y)
        
        # Check if the point is within the polygon
        if polygon.contains(QgsGeometry.fromPointXY(point)):
            points.append(point)
    
    return points

def k_means(points, k, max_iters=300, tol=1e-4):
    """Performs K-means clustering on QgsPointXY points and returns clusters and centroids."""
    
    # Convert QgsPointXY points to numpy array for easier manipulation
    point_coords = np.array([[point.x(), point.y()] for point in points])
    
    # Initialize centroids randomly
    np.random.seed(42)
    initial_indices = np.random.choice(len(point_coords), size=k, replace=False)
    centroids = point_coords[initial_indices]
    
    for _ in range(max_iters):
        # Assign points to the nearest centroid
        distances = np.linalg.norm(point_coords[:, np.newaxis] - centroids, axis=2)
        labels = np.argmin(distances, axis=1)
        
        # Compute new centroids
        new_centroids = np.array([point_coords[labels == i].mean(axis=0) for i in range(k)])
        
        # Check for convergence
        if np.linalg.norm(new_centroids - centroids) < tol:
            break
        
        centroids = new_centroids
    
    # Create a list of QgsPointXY centroids
    centroid_points = [QgsPointXY(centroid[0], centroid[1]) for centroid in centroids]
    
    # Create a list of clustered points with their cluster IDs
    result = [{
        'geometry': QgsPointXY(point[0], point[1]),
        'cluster_id': int(label)
    } for point, label in zip(point_coords, labels)]
    
    return result, centroid_points


def meters_to_geographic_distance(distance_meters, src_crs, src_extent):
        y_max = src_extent.yMaximum()
        y_min = src_extent.yMinimum()        
        EPSG = int(src_crs.authid().split(':')[-1])
        proj_crs = CRS.from_epsg(EPSG)
        a = proj_crs.ellipsoid.semi_major_metre
        f = 1 / proj_crs.ellipsoid.inverse_flattening
        e2 = f * (2 - f)
        lat_rad = np.radians((y_min + y_max) / 2)
        N = a / np.sqrt(1 - e2 * (np.sin(lat_rad)) ** 2)  # Radius of curvature 1 degree vertical
        M = a * (1 - e2) / (1 - e2 * (np.sin(lat_rad)) ** 2) ** (3 / 2.)  # Meridian Curvature Radius
        R = np.sqrt(M * N)  # Gaussian mean radius
        theta_distance = distance_meters / R
        distance_degrees = np.degrees(theta_distance)  # Radian to degree   
        return distance_degrees

def wedge_buffer(geometry, outer_radius, inner_radius=0, num_sectors=1, azimuth=0, num_segments=36):
    """
    Create wedge-shaped buffers around a point geometry for the given number of sectors,
    with support for an inner and outer radius, and an optional azimuth (degree from north).
    If num_sectors is 1, a full circular buffer is created.

    :param geometry: QgsGeometry of the point around which to create the buffer.
    :param outer_radius: Outer radius of the wedge buffer.
    :param inner_radius: Inner radius of the wedge buffer.
    :param num_sectors: Number of circular sectors.
    :param azimuth: Azimuth (degree from north) where the first wedge starts. Default is 0 (north).
    :param num_segments: Number of segments to use for circle approximation.
    :return: List of dictionaries containing QgsGeometry objects and their wedge_id attributes.
    """
    # Validate input
    if num_sectors <= 0:
        raise ValueError("Number of sectors must be greater than 0.")
    
    # Get the point geometry
    point = geometry.asPoint()
    
    # Initialize the list for storing geometries with wedge_id
    wedge_geometries = []
    
    # Counter for wedge_id
    wedge_id_counter = 1
    
    if num_sectors > 1:
        # Normalize azimuth to the range 0° to 360°
        azimuth = azimuth % 360

        # Handle the general case for wedge-shaped buffers
        angle_step = 360 / num_sectors

        for sector in range(num_sectors):
            angle_start = azimuth + sector * angle_step
            angle_end = azimuth + (sector + 1) * angle_step
            
            angle_start_rad = math.radians(angle_start)
            angle_end_rad = math.radians(angle_end)
            
            outer_arc_points = []
            inner_arc_points = []
            
            for i in range(num_segments + 1):
                angle = angle_start_rad + i * (angle_end_rad - angle_start_rad) / num_segments
                x_outer = point.x() + outer_radius * math.cos(angle)
                y_outer = point.y() + outer_radius * math.sin(angle)
                x_inner = point.x() + inner_radius * math.cos(angle)
                y_inner = point.y() + inner_radius * math.sin(angle)
                
                outer_arc_points.append(QgsPointXY(x_outer, y_outer))
                inner_arc_points.append(QgsPointXY(x_inner, y_inner))
            
            # Reverse inner_arc_points to maintain correct winding order
            inner_arc_points.reverse()
            
            wedge_points = outer_arc_points + inner_arc_points
            wedge_geom = QgsGeometry.fromPolygonXY([wedge_points])
            
            # Append dictionary with geometry and wedge_id
            wedge_geometries.append({
                'wedge_id': wedge_id_counter,
                'geometry': wedge_geom
            })
            
            # Increment the wedge_id_counter
            wedge_id_counter += 1
    
    else: # num_sectors == 1
        # Create outer and inner rings
        outer_ring = []
        inner_ring = []

        # Create outer ring
        for i in range(num_segments):
            angle = (2 * math.pi * i) / num_segments
            x = point.x() + outer_radius * math.cos(angle)
            y = point.y() + outer_radius * math.sin(angle)
            outer_ring.append(QgsPointXY(x, y))
        
        # Create inner ring
        for i in range(num_segments):
            angle = (2 * math.pi * i) / num_segments
            x = point.x() + inner_radius * math.cos(angle)
            y = point.y() + inner_radius * math.sin(angle)
            inner_ring.append(QgsPointXY(x, y))

        # Close rings
        outer_ring.append(outer_ring[0])
        inner_ring.append(inner_ring[0])

        # Create QgsGeometry objects
        outer_geom = QgsGeometry.fromPolygonXY([outer_ring])
        inner_geom = QgsGeometry.fromPolygonXY([inner_ring])
        
        # Create donut geometry by difference
        wedge_geom = outer_geom.difference(inner_geom)
        
        # Append dictionary with geometry and wedge_id
        wedge_geometries.append({
            'wedge_id': wedge_id_counter,
            'geometry': wedge_geom
        })
        
    return wedge_geometries

def spiralwedge_buffer(geometry, outer_radius, inner_radius=0, num_sectors=1, azimuth=0, num_segments=36, increment_percentage=10):
    """
    Create wedge-shaped buffers around a point geometry for the given number of sectors,
    with support for an inner and outer radius, and an optional azimuth (degree from north).
    The outer radius increases by a specified percentage for each sector.

    :param geometry: QgsGeometry of the point around which to create the buffer.
    :param outer_radius: Base outer radius of the wedge buffer.
    :param inner_radius: Inner radius of the wedge buffer.
    :param num_sectors: Number of circular sectors.
    :param azimuth: Azimuth (degree from north) where the first wedge starts. Default is 0 (north).
    :param num_segments: Number of segments to use for circle approximation.
    :param increment_percentage: Percentage increase of outer radius for each sector. Default is 10%.
    :return: List of dictionaries containing QgsGeometry objects and their wedge_id attributes.
    """
    # Validate input
    if num_sectors <= 0:
        raise ValueError("Number of sectors must be greater than 0.")
    if increment_percentage < 0:
        raise ValueError("Increment percentage must be non-negative.")
    
    # Get the point geometry
    point = geometry.asPoint()
    
    # Initialize the list for storing geometries with wedge_id
    wedge_geometries = []
    
    # Counter for wedge_id
    wedge_id_counter = 1
    if num_sectors > 1:        
        # Normalize azimuth to the range 0° to 360°
        azimuth = azimuth % 360

        # Handle the general case for wedge-shaped buffers
        angle_step = 360 / num_sectors

        for sector in range(num_sectors):
            # Calculate the incremented outer radius
            sector_outer_radius = outer_radius * (1 + increment_percentage / 100 * sector)
            
            angle_start = azimuth + sector * angle_step
            angle_end = azimuth + (sector + 1) * angle_step
            
            angle_start_rad = math.radians(angle_start)
            angle_end_rad = math.radians(angle_end)
            
            outer_arc_points = []
            inner_arc_points = []
            
            for i in range(num_segments + 1):
                angle = angle_start_rad + i * (angle_end_rad - angle_start_rad) / num_segments
                x_outer = point.x() + sector_outer_radius * math.cos(angle)
                y_outer = point.y() + sector_outer_radius * math.sin(angle)
                x_inner = point.x() + inner_radius * math.cos(angle)
                y_inner = point.y() + inner_radius * math.sin(angle)
                
                outer_arc_points.append(QgsPointXY(x_outer, y_outer))
                inner_arc_points.append(QgsPointXY(x_inner, y_inner))
            
            # Reverse inner_arc_points to maintain correct winding order
            inner_arc_points.reverse()
            
            wedge_points = outer_arc_points + inner_arc_points
            wedge_geom = QgsGeometry.fromPolygonXY([wedge_points])
            
            # Append dictionary with geometry and wedge_id
            wedge_geometries.append({
                'wedge_id': wedge_id_counter,
                'geometry': wedge_geom
            })
            
            # Increment the wedge_id_counter
            wedge_id_counter += 1
    
    else: # num_sectors == 1
        # Create outer and inner rings
        outer_ring = []
        inner_ring = []

        # Create outer ring
        for i in range(num_segments):
            angle = (2 * math.pi * i) / num_segments
            x = point.x() + outer_radius * math.cos(angle)
            y = point.y() + outer_radius * math.sin(angle)
            outer_ring.append(QgsPointXY(x, y))
        
        # Create inner ring
        for i in range(num_segments):
            angle = (2 * math.pi * i) / num_segments
            x = point.x() + inner_radius * math.cos(angle)
            y = point.y() + inner_radius * math.sin(angle)
            inner_ring.append(QgsPointXY(x, y))

        # Close rings
        outer_ring.append(outer_ring[0])
        inner_ring.append(inner_ring[0])

        # Create QgsGeometry objects
        outer_geom = QgsGeometry.fromPolygonXY([outer_ring])
        inner_geom = QgsGeometry.fromPolygonXY([inner_ring])
        
        # Create donut geometry by difference
        wedge_geom = outer_geom.difference(inner_geom)
        
        # Append dictionary with geometry and wedge_id
        wedge_geometries.append({
            'wedge_id': wedge_id_counter,
            'geometry': wedge_geom
        })
        
    return wedge_geometries


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