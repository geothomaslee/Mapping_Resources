# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 09:16:25 2023

@author: tlee


A set of general mapping functions that are frequently used in other, more
specific mapping scripts.
"""

def check_lon(coord):
    if coord < -180:
        coord = 180 + (coord - -180)
    elif coord > 180:
        coord = -180 + (coord - 180)
    return coord

def check_lat(coord):
    """
    Checks if latitudes are in range -90 < coordinate < 90

    Parameters
    ----------
    coord : TYPE
        DESCRIPTION.

    Returns
    -------
    coord : TYPE
        DESCRIPTION.

    """
    if coord < -90:
        coord = -90
    elif coord > 90:
        coord = 90
    return coord

def get_margin_from_lat_lon(lats,lons,margin=0.1):
    min_lon = min(lons) - (margin * abs(max(lons) - min(lons)))
    min_lat = min(lats) - (margin * abs(max(lats) - min(lats)))
    max_lon = max(lons) + (margin * abs(max(lons) - min(lons)))
    max_lat = max(lats) + (margin * abs(max(lats) - min(lats)))
    
    min_lon = check_lon(min_lon)
    min_lat = check_lat(min_lat)
    max_lon = check_lon(max_lon)
    max_lat = check_lat(max_lat)
    
    bounds = [min_lon, max_lon, min_lat, max_lat]
    
    return bounds

def get_margin_from_bounds(bounds,margin=0.1):
    """
    Parameters
    ----------
    bounds : list of ints or floats
        Region to search for stations, in order [minlon, maxlon, minlat, maxlat]
    margin : int or float, optional
        Margin size, multiplied by the length of the bounds. 0.1 = 10% margin. 
        The default is 0.1.

    Returns
    -------
    marginal_bounds : list of ints or floats
        New bounds with added margin, same format as input bounds.

    """
    lons = [bounds[0],bounds[1]]
    lats = [bounds[2],bounds[3]]
            
    min_lon = min(lons) - (margin * abs(max(lons) - min(lons)))
    min_lat = min(lats) - (margin * abs(max(lats) - min(lats)))
    max_lon = max(lons) + (margin * abs(max(lons) - min(lons)))
    max_lat = max(lats) + (margin * abs(max(lats) - min(lats)))
    
    min_lon = check_lon(min_lon)
    min_lat = check_lat(min_lat)
    max_lon = check_lon(max_lon)
    max_lat = check_lat(max_lat)
    
    marginal_bounds = [min_lon, max_lon, min_lat, max_lat]
    
    return marginal_bounds