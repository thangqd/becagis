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

def antipode(lat,lon):
    antipode_lat = - lat
    if lon< 0:
        antipode_lon = lon + 180 
    else: antipode_lon = lon - 180  
    return (antipode_lat,antipode_lon)

def reversed_y(y,x):
    reversed_y = - y
    reversed_x = x
    return (reversed_y,reversed_x)

def reversed_x(y,x):
    reversed_y = y
    if x< 0:
        reversed_x = x + 180 
    else: reversed_x = x - 180  
    return (reversed_y,reversed_x)

def swap_xy(y,x):
    return (x,y)