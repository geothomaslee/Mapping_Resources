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
import numpy as np
import shutil

resource_folder = os.path.join(os.path.dirname(__file__),'../resources')

def check_lon(coord):
    """
    Checks if longitudes are in range -180 < coordinate < 180
    Parameters
    ----------
    coord : int or float
        Longitude.

    Returns
    -------
    coord : int or float
        Longitude
    """
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
    coord : int or float
        Latitude.

    Returns
    -------
    coord : int or float
        Latitude
    """
    if coord < -90:
        coord = -90
    elif coord > 90:
        coord = 90
    return coord

def get_margin_from_lat_lon(lats,lons,margin=0.1):
    """
    Parameters
    ----------
    lats : list of ints or floats
        List of latitudes to search for bounds.
    lons : list of ints or floats
        List of longitudes to search for bounds.
    margin : float or int, optional
        Margin size, given as a decimal of the total dimensions. The default is 0.1.

    Returns
    -------
    bounds : list of ints or floats
        [min_lon, max_lon, min_lat, max_lat]
    """
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
    """
    Parameters
    ----------
    lat : int or float
        Latitude of point to check.
    lon : int or float
        Longitude of point to check.
    bounds : list of ints or floats
        [min_lon, max_lon, min_lat, max_lat]

    Returns
    -------
    is_in_bounds : bool
        If point in bounds.
    """
    min_lon = bounds[0]
    max_lon = bounds[1]
    min_lat = bounds[2]
    max_lat = bounds[3]
    if lat > min_lat and lat < max_lat and lon > min_lon and lon < max_lon:
        is_in_bounds = True
    else:
        is_in_bounds = False
        
    return is_in_bounds

def get_bounds_from_figure(fig):
    """
    Parameters
    ----------
    fig : pygmt.Figure
        Figure to find bounds of

    Returns
    -------
    bounds_list : list of ints or floats
        [min_lon, max_lon, min_lat, max_lat]
    """
    region = fig.region
    bounds_list = region.tolist()
    
    return bounds_list

def find_elevation_range(grid):
    grid_np = grid.values
    max_elev = np.amax(grid_np)
    min_elev = np.amin(grid_np)
    
    return min_elev, max_elev

def convert_color_map(filepath,min_elev=-8000,max_elev=8000,
                      bathymetric_cmap=None):
    filepath = os.path.expanduser(filepath)
    basename = os.path.basename(filepath)
    if basename[-4:] != '.cpt':
        raise ValueError('Given file is not a cpt file')
        
    if not bathymetric_cmap:
        bathymetric_cmap = os.path.expanduser('~/Documents/GitHub/Mapping_Resources/Resources/colormaps/colombia.cpt')
        
    names = ['Bottom_Bound', 'R1', 'G1', 'B1','Upper_Bound', 'R2', 'G2', 'B2']
    cmap_df = pd.read_csv(filepath,delim_whitespace=True,comment='#',names=names)
    cmap_df = cmap_df.dropna()
    
    lower_bound_list = cmap_df['Bottom_Bound'].tolist()
    upper_bound_list = cmap_df['Upper_Bound'].tolist()
    lower_bound_list = [float(val) for val in lower_bound_list]
    lower_bound_list = [float(val) for val in lower_bound_list]
    
    max_bound = max(upper_bound_list)
    min_bound = min(lower_bound_list)
    bound_range = max_bound - min_bound
    
    if min_bound >= 0:
        print(f'Colormap does not contain bathymetric values, using {os.path.split(bathymetric_cmap)[1]}')
        bathy_df = pd.read_csv(bathymetric_cmap,delim_whitespace=True,comment='#',names=names)
        bathy_df.drop(bathy_df[bathy_df.Upper_Bound > 0].index, inplace=True)
        bathy_file_path = os.path.split(bathymetric_cmap)[0] + '/temp_bathymetry.cpt'
        
    col_space = [5, 3, 3, 3, 5, 3, 3, 3 ]
    bathy_df.to_string(bathy_file_path, col_space=col_space, index=None,header=False,
                       justify='left')
        
        
    elev_range = max_elev - min_elev
    new_lower_bound_list = []
    new_upper_bound_list = []

    
    for i in range(len(lower_bound_list)):
        lower_bound = lower_bound_list[i]
        upper_bound = upper_bound_list[i]
        
        new_lower_bound = round((lower_bound * elev_range) / bound_range)
        new_upper_bound = round((upper_bound * elev_range) / bound_range)
    
        new_lower_bound_list.append(new_lower_bound)
        new_upper_bound_list.append(new_upper_bound)
        
    new_bound_df = pd.DataFrame({'Bottom_Bound' : new_lower_bound_list,
                                 'Upper_Bound' : new_upper_bound_list})
    cmap_df['Bottom_Bound'] = new_bound_df['Bottom_Bound']
    cmap_df['Upper_Bound'] = new_bound_df['Upper_Bound']
    
    
    RGB_col_list = ['R1','G1','B1','R2','G2','B2']
    for col in RGB_col_list:
        color_list = cmap_df[col].tolist()
        color_list = [int(round(val)) for val in color_list]
        new_color_df = pd.DataFrame({col : color_list})
        cmap_df[col] = new_color_df[col]
            
    path_split = os.path.split(filepath)
    topo_file_path = path_split[0] + '/temp_topo.cpt'
    print(topo_file_path)
    
    cmap_df.to_string(topo_file_path, col_space=col_space, index=None,header=False,
                      justify='left')
    
    final_out_file = path_split[0] + '/converted_' + path_split[1]
    
    if min_bound >= 0:
        filenames = [bathy_file_path, topo_file_path]
        with open(final_out_file,'wb') as wfd:
            for f in filenames:
                with open(f,'rb') as fd:
                    shutil.copyfileobj(fd, wfd)
                    wfd.write(b"\n")
                    
        #os.remove(bathy_file_path)
        #os.remove(topo_file_path)
                
    else:
        cmap_df.to_string(final_out_file, col_space=col_space, index=None,header=False,
                          justify='left')
        #os.remove(topo_file_path)
        

def plot_base_map(region,projection="Q15c+du",figure_name="figure!",
                  resolution='03s',
                  cmap="./Resources/colormaps/colombia.cpt",
                  box_bounds=None,margin=0.1,bathymetry=False,
                  watercolor=None):
    """
    Parameters
    ----------
    bounds : list of ints or floats
        Region to search for stations, in order [minlon, maxlon, minlat, maxlat]
    projection : string, optional
        GMT specs for projection. See GMT documentation for more details.
        The default is "Q15c+du".
    figure_name : string, optional
        Title of figure. The default is "figure!".
    resolution : string, optional
        Resolution of topo data. See pygmt.load_earth_relief for more. 
        The default is '03s'.
    cmap : string, optional
        Path to colormap. The default is "./Resources/colormaps/colombia.cpt".
    box_bounds : list of ints or floats, optional
        Bounds of box to draw on figure. If none given, none will be drawn.
    margin : float or int, optional
        Margin size, given as a decimal of the total dimensions. The default is 0.1.
    bathymetry : bool
        If False, will replace oceans with solid color. Default is false.

    Returns
    -------
    fig : pygmt.Figure
        PyGMT figure to use as basemap
    """
    if not watercolor:
        watercolor = "skyblue"
    
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
    fig.colorbar(frame=["a1000", "x+lElevation", "y+lm"])
    if not bathymetry:
        fig.coast(shorelines="4/0.5p,black",
                  projection=projection,
                  borders="a/1.2p,black",
                  water=watercolor,
                  resolution="f")
    
    return fig

def plot_label(fig,lat,lon,style='b0.35c',fill='black',label=None,
               offset=0.02,hor_offset_multiplier=3.5,
               fontsize=12,label_color='black'):
    if label:
        if type(label) != str:
            raise TypeError('Label must be string')
            
    bounds = get_bounds_from_figure(fig)
    
    height,width,diag = get_map_dimensions(fig)
    
    min_lon = bounds[0]
    max_lon = bounds[1]
    min_lat = bounds[2]
    max_lat = bounds[3]
    
    standard_offset_height = height * offset
    standard_offset_width = width * offset * hor_offset_multiplier
    
    if label:
        
        if max_lat - lat <= standard_offset_height:
            label_y_val = lat - standard_offset_height
        else:
            label_y_val = lat + standard_offset_height
        
        if abs(max_lon - lon) <= standard_offset_width:
            label_x_val = lon - standard_offset_width
            label_y_val = lat
        elif abs(min_lon - lon) <= standard_offset_width:
            label_x_val = lon + standard_offset_width
            label_y_val = lat
        else:
            label_x_val = lon
            
        fig.text(x=label_x_val,
                 y=label_y_val,
                 text=label,
                 font=f'{fontsize}p,Helvetica-Bold,{label_color}')
        
    return fig
    

def plot_holocene_volcanoes(fig):
    """
    Parameters
    ----------
    fig : pygmt.Figure
        Figure to draw volcanoes on. If only plotting figure, use plot_base_map
        to create initial figure.

    Returns
    -------
    fig : pygmt.Figure
        Figure with added volcanoes.

    """
    vol_file = os.path.join(resource_folder,'GVP_Volcano_List_Holocene.csv')
    holo_volc_df = pd.read_csv(vol_file)
    holocene_vol_lon_list = holo_volc_df['Longitude'].tolist()
    holocene_vol_lat_list = holo_volc_df['Latitude'].tolist()
    
    fig.plot(x=holocene_vol_lon_list,
             y=holocene_vol_lat_list,
             style='t0.35c',
             fill='red')
    
    return fig

def get_map_dimensions(fig):
    """
    Parameters
    ----------
    fig : pygmt.Figure
        Figure to find dimensions of.

    Returns
    -------
    height : int or float
        Y-range.
    width : int or float
        X-range.
    diag : int or float
        Length of diagonal of figure, to give some idea of the "size" of the figure.

    """
    bounds = get_bounds_from_figure(fig)
    height = abs(bounds[3] - bounds[2])
    width = abs(bounds[1] - bounds[0])
    diag = ((height ** 2) + (width **2) ** 0.5)
    
    return height,width,diag

def plot_major_cities(fig,bounds=None,minpopulation=100000,
                      fontsize=14,offset=0.02,dotsize=0.35,
                      dot_color='black',label_color='black',
                      close_threshhold = 0.005,
                      hor_offset_multiplier=3.5):
    """
    Parameters
    ----------
    fig : pygmt.Figure
        Figure to add cities on. Use plot_base_map to make initial figure.
    bounds : list of ints or floats
        Region to search for stations, in order [minlon, maxlon, minlat, maxlat]
    minpopulation : int, optional
        Minimum population of cities to plot. The default is 100000.
    fontsize : int or float, optional
        Font size for city label. The default is 14.
    offset : float, optional
        Offset of label from dot, as a fraction of total figure size. 
        The default is 0.02.
    dot_color : string, optional
        Color of dots for cities. The default is 'black'.
    label_color : string, optional
        Color of city labels. The default is 'black'.
    close_threshhold: float, optional
        Distance, as a fraction of the length of the figure diagonal, below
        which two very close cities will only plot the larger of the two.
    hor_offset_multiplier: float, optional
        For cities that are near the longitudinal boundaries, their label will
        be shifted inward. This multiplier chooses how far in they will be shifted,
        and will need to be adjusted depending on your font size and the length
        of your longest city name that needs adjusting.

    Returns
    -------
    fig : pygmt.Figure
        Figure with added cities.
    """
    if bounds == None:
        bounds = get_bounds_from_figure(fig)
    
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
    
    city_list = []
    for index, row in df_meets_crit.iterrows():
        city = [row['lat'],row['lng'],row['city_ascii'],row['population']]
        city_list.append(city)
        
    height,width,diag = get_map_dimensions(fig)
    threshhold_distance = diag * close_threshhold 
    
    num_cities = len(city_list)
    last_city_index = num_cities
    problem_pair_list = []

    for i, city in enumerate(city_list):
        for index in np.arange(i+1,last_city_index,1):
            city2 = city_list[index]
            lat1 = city[0]
            lon1 = city[1]
            lat2 = city2[0]
            lon2 = city2[1]
            
            distance = (((lat1-lat2) **2) + (lon1-lon2) **2) **0.5
            if distance < threshhold_distance:
                problem_pair = [i, index]
                problem_pair_list.append(problem_pair)
                
    if len(problem_pair_list) > 0: 
        if len(problem_pair_list) <= 5:           
            print('WARNING: These cities are too close:')
            for pair in problem_pair_list:
        
                prob1 = pair[0]
                prob2 = pair[1]
                
                print(f'{city_list[prob1][2]} and {city_list[prob2][2]}')
            print('The larger of the two cities will be plotted. Decrease close_threshhold to change this behavior')
        else:
            print('Warning: more than 5 cities are too close')
            print('The largest of these cities will be plotted. Decrease close_threshhold to change this behavior')
    
        to_remove_list = []
        for pair in problem_pair_list:
            prob1 = pair[0]
            prob2 = pair[1]
        
            # If you're getting an error here with index out of bound, it's because
            # your close_threshhold is too high and too many cities are being
            # removed, which makes this script very confused.
            if city_list[prob1][3] > city_list[prob2][3]:
                to_remove_list.append(city_list[prob2])
            else:
                to_remove_list.append(city_list[prob1])
             
        city_list = [e for e in city_list if e not in to_remove_list]
            
    standard_offset_height = height * offset
    standard_offset_width = width * offset * hor_offset_multiplier
     
    for city in city_list:  
        fig.plot(x=city[1],
                 y=city[0],
                 style=f'c{dotsize}',
                 fill=dot_color,
                 label=city[2])
        
        # Fixes labels near the map edge from going off map
        
        if max_lat - city[0] <= standard_offset_height:
            label_y_val = city[0] - standard_offset_height
        else:
            label_y_val = city[0] + standard_offset_height
        
        if abs(max_lon - city[1]) <= standard_offset_width:
            label_x_val = city[1] - standard_offset_width
            label_y_val = city[0]
        elif abs(min_lon - city[1]) <= standard_offset_width:
            label_x_val = city[1] + standard_offset_width
            label_y_val = city[0]
        else:
            label_x_val = city[1]
            
        fig.text(x=label_x_val,
                 y=label_y_val,
                 text=city[2],
                 font=f'{fontsize}p,Helvetica-Bold,{label_color}')
        
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