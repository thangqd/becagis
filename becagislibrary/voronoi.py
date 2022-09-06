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