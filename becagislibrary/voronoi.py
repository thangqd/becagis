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


def hcmgis_split_polygon(layer, parts,random_points):		
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
