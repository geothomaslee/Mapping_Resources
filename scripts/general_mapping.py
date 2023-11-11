# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 09:16:25 2023

@author: tlee


A set of general mapping functions that are frequently used in other, more
specific mapping scripts.
"""

import os
import pandas as pd
import pygmt

resource_folder = os.path.join(os.path.dirname(__file__),'../resources')

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

def check_if_in_bounds(lat,lon,bounds):
    min_lon = bounds[0]
    max_lon = bounds[1]
    min_lat = bounds[2]
    max_lat = bounds[3]
    if lat > min_lat and lat < max_lat and lon > min_lon and lon < max_lon:
        is_in_bounds = True
    else:
        is_in_bounds = False
        
    return is_in_bounds

def plot_base_map(region,projection="Q15c+du",figure_name="figure!",
                  resolution='03s',
                  cmap="./Resources/colormaps/colombia.cpt",
                  box_bounds=None,margin=0.1):
    
    bounds = get_margin_from_bounds(region,margin=margin)
    
    grid = pygmt.datasets.load_earth_relief(resolution=resolution, region=bounds)
    
    fig = pygmt.Figure()
    fig.basemap(region=bounds,
                projection=projection,
                frame=True)
    fig.grdimage(grid=grid,
                 projection=projection,
                 frame=["a",f'+t{figure_name}'],
                 cmap=cmap)
    fig.coast(shorelines="4/0.5p,black",
              projection=projection,
              borders="2/1.2p,black",
              water="skyblue",
              resolution="f")
    
    return fig

def plot_holocene_volcanoes(fig):
    vol_file = os.path.join(resource_folder,'GVP_Volcano_List_Holocene.csv')
    holo_volc_df = pd.read_csv(vol_file)
    holocene_vol_lon_list = holo_volc_df['Longitude'].tolist()
    holocene_vol_lat_list = holo_volc_df['Latitude'].tolist()
    
    fig.plot(x=holocene_vol_lon_list,
             y=holocene_vol_lat_list,
             style='t0.35c',
             fill='red')
    
    return fig

def plot_major_cities(fig,bounds,minpopulation=100000):
    min_lon = bounds[0]
    max_lon = bounds[1]
    min_lat = bounds[2]
    max_lat = bounds[3]
    
    cities_csv = os.path.join(resource_folder,'worldcities.csv')
    cities_df = pd.read_csv(cities_csv)
    
    # Pulling cities that meet criteria
    df_in_lat = cities_df[cities_df['lat'].between(min_lat,max_lat)]
    df_in_bounds = df_in_lat[df_in_lat['lng'].between(min_lon,max_lon)]
    df_meets_crit = df_in_bounds[df_in_bounds['population'] >= minpopulation]
    
    for index, row in df_meets_crit.iterrows():
        fig.plot(x=row['lng'],
                 y=row['lat'],
                 style='c0.35',
                 fill='black',
                 label=row['city_ascii'])

    return fig

def save_fig(fig,name,dpi=720,ftype="png"):
    """
    Parameters
    ----------
    fig : pygmt.Figure
        Figure to save.
    name : string
        Name of file.
    dpi : int, optional
        DPI of figure. The default is 720.
    ftype : string, optional
        File extension, without the period. Will automatically save as the correct
        file type. The default is "png".

    Returns
    -------
    None.

    """
    fname = name + "." + ftype
    print(fname)
    fig.savefig(fname=fname,
                dpi=dpi)