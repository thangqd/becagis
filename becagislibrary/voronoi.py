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
from PyQt5.QtCore import *

def splitpolygon(layer, parts,random_points):		
    parameters1 = {'INPUT': layer,
                        'INCLUDE_POLYGON_ATTRIBUTES' : True,
                        'MAX_TRIES_PER_POINT' : None,
                        'MIN_DISTANCE' : 0,
                        'MIN_DISTANCE_GLOBAL' : 0,
                        'POINTS_NUMBER' : random_points, 
                        'SEED' : None ,
                        'OUTPUT' : "memory:points"} 
    points = processing.run('qgis:randompointsinpolygons', parameters1)	
    
    parameters2 =  {'INPUT': points['OUTPUT'],
                'CLUSTERS' :parts,
                'FIELD_NAME' : 'CLUSTER_ID',
                'SIZE_FIELD_NAME' : 'CLUSTER_SIZE',
                'OUTPUT' : 'memory:kmeansclustering'} 
    kmeansclustering = processing.run('qgis:kmeansclustering', parameters2)

    parameters3 = {'INPUT': kmeansclustering['OUTPUT'],                  
                'GROUP_BY' : 'CLUSTER_ID',
                'AGGREGATES' : [],
                'OUTPUT' : 'memory:aggregate'} 
    aggregate = processing.run('qgis:aggregate',parameters3)

    parameters4 = {'INPUT': aggregate['OUTPUT'],                  
                'ALL_PARTS' : False,
                'OUTPUT' : 'memory:centroids'} 
    centroids = processing.run('qgis:centroids',parameters4)

    parameters5 = {'INPUT': centroids['OUTPUT'],                  
                'BUFFER' : 1000,
                'OUTPUT' : 'memory:voronoi'} 
    voronoi = processing.run('qgis:voronoipolygons',parameters5)

    parameters6 = {'INPUT': layer,  
                'OVERLAY':   voronoi['OUTPUT'],           
                'OUTPUT' : 'TEMPORARY_OUTPUT'
            } 
    intersection = processing.run('qgis:intersection',parameters6)
    output = intersection['OUTPUT']
    return output

def skeleton(layer, field, density, tolerance):		
    ## create skeleton/ media axis 
    parameters3 = {'INPUT': layer,
                   'DISTANCE' :	density,
                   'OUTPUT' : "memory:points"} 
    points = processing.run('qgis:pointsalonglines', parameters3)	
     
    parameters4 = {'INPUT': points['OUTPUT'],
                    'BUFFER' : 0, 'OUTPUT' : 'memory:voronoipolygon'} 
    voronoipolygon = processing.run('qgis:voronoipolygons', parameters4)
   
                  
    
    parameters5 = {'INPUT': voronoipolygon['OUTPUT'],
                    'OUTPUT' : 'memory:voronoipolyline'} 
    voronoipolyline = processing.run('qgis:polygonstolines',parameters5)
    
    
    parameters6 = {'INPUT': voronoipolyline['OUTPUT'],					
                    'OUTPUT' : 'memory:explode'}
    explode = processing.run('qgis:explodelines',parameters6)   
 
    
    parameters7 = {'INPUT': explode['OUTPUT'],
                    'PREDICATE' : [6], # within					
                    'INTERSECT':  layer,	
                    ##############################	
                    # 'INTERSECT': layer,		
                    'METHOD' : 0,
                    'OUTPUT' : 'memory:candidate'}
    candidate= processing.run('qgis:selectbylocation',parameters7)   
   
    
    parameters8 = {'INPUT':candidate['OUTPUT'],
                    'OUTPUT':  'memory:medialaxis'}
    medialaxis = processing.run('qgis:saveselectedfeatures',parameters8)    
 
    
    parameters9 = {'INPUT':medialaxis['OUTPUT'],
                    'OUTPUT':  'memory:deleteduplicategeometries'}
    deleteduplicategeometries = processing.run('qgis:deleteduplicategeometries',parameters9)    
 
    
    parameter10 =  {'INPUT':deleteduplicategeometries['OUTPUT'],
                    'FIELD' : field,
                    'OUTPUT':  "memory:medialaxis_dissolve"}
    medialaxis_dissolve = processing.run('qgis:dissolve',parameter10) 
       
    parameter11 = {'INPUT':medialaxis_dissolve['OUTPUT'],
                    'METHOD' : 0,
                    'TOLERANCE' : tolerance, # 0.1m
                    'OUTPUT':  "memory:simplify"}
    simplify = processing.run('qgis:simplifygeometries',parameter11)    

    parameter12 = {'INPUT':simplify['OUTPUT'],                    
                    'OUTPUT':  "memory:explode"}
    explode = processing.run('qgis:explodelines',parameter12) 

          
    parameter13 = {'LINES':explode['OUTPUT'],
                    'ANGLE' : 30,
                    'TYPE' : 1, # Keep the attribute of the longest line
                    'OUTPUT':  "memory:skeleton"}
    skeleton = processing.run('becagistools:directionalmerge',parameter13)    
 
    output = skeleton['OUTPUT']
    return output

def isolation(layer, field):		
    ## Find the most isolated Point from a Point Layer
    # Create Delaunay Triangulation
    parameters1 = {'INPUT': layer,
                   'OUTPUT' : "memory:points"} 
    delaunay_triangulation = processing.run('qgis:delaunaytriangulation', parameters1)                 
    
    parameters2 = {'INPUT': delaunay_triangulation['OUTPUT'],
                    'OUTPUT' : 'memory:voronoipolyline'} 
    delaunay_polyline = processing.run('qgis:polygonstolines',parameters2)    
    
    parameters3 = {'INPUT': delaunay_polyline['OUTPUT'],					
                    'OUTPUT' : 'memory:explode'}
    explode = processing.run('qgis:explodelines',parameters3)  
       
    parameters4 = {'INPUT':explode['OUTPUT'],
                    'OUTPUT':  'memory:deleteduplicategeometries'}
    deleteduplicategeometries = processing.run('qgis:deleteduplicategeometries',parameters4) 

    parameters5 = {'INPUT':deleteduplicategeometries['OUTPUT'],
                    'JOIN': layer,
                    'PREDICATE':[3], #touch
                    'METHOD':0, # one to many
                    'DISCARD_NONMATCHING':False,
                    'JOIN_FIELDS': [],
                    'PREFIX':'',
                    'OUTPUT':  'memory:join_layer'}
    join_layer = processing.run('qgis:joinattributesbylocation',parameters5)['OUTPUT']
    join_layer.startEditing() 
    join_layer.dataProvider().addAttributes([QgsField('length', QVariant.Double)])
    join_layer.updateFields()
    idx = join_layer.fields().indexOf('length')
    d = QgsDistanceArea()
    d.setSourceCrs(join_layer.crs(), QgsProject.instance().transformContext())
    d.setEllipsoid(QgsProject.instance().ellipsoid())

    for feature in join_layer.getFeatures():
        join_layer.changeAttributeValue(feature.id(), idx,d.convertLengthMeasurement(d.measureLength(feature.geometry()), 1)*1000)
    join_layer.commitChanges()

    parameters6 = {'INPUT':join_layer,
                    'VALUES_FIELD_NAME':'length',
                    'CATEGORIES_FIELD_NAME':[field],                    
                    'OUTPUT':  'memory:statistics'}    
    statistics = processing.run('qgis:statisticsbycategories',parameters6)['OUTPUT']

    idx =  statistics.dataProvider().fieldNameIndex("min")

    max_distance = 0
    isolated = None
    for feature in statistics.getFeatures():
        if max_distance < feature.attributes()[idx]:
            max_distance = feature.attributes()[idx]
            isolated = feature[field]    
    return isolated,max_distance

def lec(layer,field):  
    try:
        if layer.isValid():
            if (layer.wkbType() == QgsWkbTypes.MultiPoint):
                parameters0 = {'INPUT':layer,
                            'OUTPUT':  "memory:singlepart"}
                singlepart = processing.run('qgis:multiparttosingleparts',parameters0)
                point_layer = singlepart['OUTPUT']       
            else:
                point_layer = layer
    except:
        temp = QgsVectorLayer(layer, QFileInfo(layer).baseName(), 'ogr') # for running LEC in QGIS console  
        if (temp.wkbType() == QgsWkbTypes.MultiPoint):
            parameters0 = {'INPUT':temp,
                            'OUTPUT':  "memory:singlepart"}
            singlepart = processing.runAndLoadResults('qgis:multiparttosingleparts',parameters0)
            point_layer = singlepart['OUTPUT']  
            print (point_layer)     
        else:
            print ('POINT')
            point_layer = temp
            print (point_layer)
            QgsProject.instance().addMapLayer(point_layer)
   
    parameters1 = {'INPUT': point_layer,
                  'BUFFER' : 0, 'OUTPUT' : 'memory:voronoipolygon'
                  } 
    voronoipolygon = processing.run('qgis:voronoipolygons', parameters1)
    
    parameters2 = {'INPUT': point_layer,
                'FIELD' : None,
                 'TYPE' : 3,
                    'OUTPUT' : 'memory:convexhull'} 
    convexhull = processing.run('qgis:minimumboundinggeometry', parameters2)	
   
    parameter2_1 =  {'INPUT': convexhull['OUTPUT'],					 
                  'OUTPUT':  "memory:convexhull_vertices"}
    convexhull_vertices = processing.run('qgis:extractvertices',parameter2_1) 
    
    parameter2_2 =  {'INPUT': convexhull_vertices['OUTPUT'],					 
                  'OUTPUT':  "memory:convexhull_vertices_clean"}
    convexhull_vertices_clean = processing.run('qgis:deleteduplicategeometries',parameter2_2) 
     
    parameter3 =  {'INPUT': voronoipolygon['OUTPUT'],	
                   'OVERLAY': convexhull['OUTPUT'], 
                  'OUTPUT':  "memory:voronoi_clip"}
    voronoi_clip = processing.run('qgis:clip',parameter3) 
    
    parameter4 =  {'INPUT': voronoi_clip['OUTPUT'],					 
                  'OUTPUT':  "memory:voronoi_vertices"}
    voronoi_vertices = processing.run('qgis:extractvertices',parameter4)
   
    parameter5 =  {'INPUT': voronoi_vertices['OUTPUT'],					 
                  'OUTPUT':  "memory:voronoi_vertices_clean"}
    voronoi_vertices_clean = processing.run('qgis:deleteduplicategeometries',parameter5) 
    
    parameter6 =  {'INPUT': voronoi_vertices_clean['OUTPUT'],
                   'INTERSECT':convexhull_vertices_clean['OUTPUT'],
                   'PREDICATE' : [2],#disjoint				 
                   'OUTPUT':  "memory:candidates"}
    candidates = processing.run('qgis:extractbylocation',parameter6) 
        
    parameter7 =  {'INPUT': candidates['OUTPUT'],
                    'FIELD': field,
                    'HUBS' : point_layer,
                    'UNIT' : 0,
                    'OUTPUT':  "memory:distances"}
    max_distances = processing.run('qgis:distancetonearesthubpoints',parameter7) 
      
    values = []
    centers = max_distances['OUTPUT']
    idx =  centers.dataProvider().fieldNameIndex("HubDist")
    for feat in centers.getFeatures():
        attrs = feat.attributes()
        values.append(attrs[idx])
    
    max_value = max(values)	
    max_values_tr = str(max(values))	
    
    selection = centers.getFeatures(QgsFeatureRequest(QgsExpression('"HubDist"' + '=' + max_values_tr)))
    ids = [s.id() for s in selection]
    centers.selectByIds(ids)

    parameters8 = {'INPUT':centers,
                    'OUTPUT':  "memory:center"}
    center = processing.run('qgis:saveselectedfeatures',parameters8)   
    
    return center['OUTPUT'], max_value   

def closestfarthest(layer,field):   
    try:
        if layer.isValid():
            if (layer.wkbType() == QgsWkbTypes.MultiPoint):
                parameters0 = {'INPUT':layer,
                              'OUTPUT':  "memory:singlepart"}
                singlepart = processing.run('qgis:multiparttosingleparts',parameters0)
                point_layer = singlepart['OUTPUT']       
            else:
                point_layer = layer
    except:
        temp = QgsVectorLayer(layer, QFileInfo(layer).baseName(), 'ogr') # for running centerline in QGIS console  
        if (temp.wkbType() == QgsWkbTypes.MultiPoint):
            parameters0 = {'INPUT':temp,
                            'OUTPUT':  "memory:singlepart"}
            singlepart = processing.run('qgis:multiparttosingleparts',parameters0)
            point_layer = singlepart['OUTPUT']       
        else:
            point_layer = temp
    ##########
    # Finding closest pair of points
    #########  
    parameters1 = {'INPUT':point_layer,
                    'OUTPUT':  "memory:delaunay_polygon"}
    delaunay_polygon = processing.run('qgis:delaunaytriangulation',parameters1)
    
    parameters2 = {'INPUT':delaunay_polygon['OUTPUT'],
                    'OUTPUT':  "memory:delaunay_polyline"}
    delaunay_polyline = processing.run('qgis:polygonstolines',parameters2)
    
    parameters3 = {'INPUT': delaunay_polyline['OUTPUT'],					
                    'OUTPUT' : 'memory:delaunay_explode'}
    delaunay_explode = processing.run('qgis:explodelines',parameters3)
   
    parameters4 = {'INPUT':delaunay_explode['OUTPUT'],
                    'OUTPUT':  "memory:delaunay_singlepart"}
    delaunay_singlepart = processing.run('qgis:multiparttosingleparts',parameters4)

    parameters5 =  {'INPUT': delaunay_singlepart['OUTPUT'],					 
                  'OUTPUT':  "memory:delaunay_clean"}
    delaunay_clean = processing.run('qgis:deleteduplicategeometries',parameters5) 
     
    ############
    #Finding farthest pair of points
    ############
    parameters6 = {'INPUT': delaunay_polygon['OUTPUT'],								
                   'OUTPUT' : 'memory:convexhull'}
    convexhull = processing.run('qgis:dissolve',parameters6)
      
    parameters7 = {'INPUT': convexhull['OUTPUT'],								
                     'OUTPUT' : 'memory:convexhull_vertices'}
    convexhull_vertices = processing.run('qgis:extractvertices',parameters7)
              
    parameters8 = {'INPUT':convexhull_vertices['OUTPUT'],
                    'OUTPUT':  "memory:singlepart"}
    vertices_singlepart = processing.run('qgis:multiparttosingleparts',parameters8)
      
    parameters9 =  {'INPUT': vertices_singlepart['OUTPUT'],					 
                  'OUTPUT':  "memory:clean"}
    clean = processing.run('qgis:deleteduplicategeometries',parameters9)
    vertices_clean = clean['OUTPUT']  
   
    parameters10 =  {'INPUT': convexhull['OUTPUT'],					 
                  'OUTPUT':  "memory:convexhull_line"}
    line = processing.run('qgis:polygonstolines',parameters10)
    convexhull_line = line['OUTPUT']  
   
    parameters11 = {'INPUT': convexhull_line,					
                    'OUTPUT' : 'memory:explode'}
    explode = processing.run('qgis:explodelines',parameters11)
       
    convexhull_explode = explode['OUTPUT']
    convexhull_explode.startEditing()
    for f1 in vertices_clean.getFeatures():
        point1 = f1.geometry().asPoint()
        for f2 in vertices_clean.getFeatures():            
            point2 = f2.geometry().asPoint()     
            if ( point1 != point2):
                seg = QgsFeature()
                seg.setGeometry(QgsGeometry.fromPolylineXY([point1,point2]))
                convexhull_explode.dataProvider().addFeature(seg)
    
    parameters12 = {'INPUT':convexhull_explode,
                    'OUTPUT':  "memory:singlepart"}
    convexhull_singlepart = processing.run('qgis:multiparttosingleparts',parameters12)

    parameters13 =  {'INPUT': convexhull_singlepart['OUTPUT'],					 
                  'OUTPUT':  "memory:convexhull_clean"}
    convexhull_clean = processing.run('qgis:deleteduplicategeometries',parameters13) 

    return delaunay_clean['OUTPUT'], convexhull_clean['OUTPUT']