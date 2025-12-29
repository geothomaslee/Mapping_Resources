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
from scipy import ndimage
import math

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

def get_margin_from_bounds(bounds,margin=0.1,one_point_fallback_margin: float=0.2):
    """
    Parameters
    ----------
    bounds : list of ints or floats
        Region to search for stations, in order [minlon, maxlon, minlat, maxlat]
    margin : int or float, optional
        Margin size, multiplied by the length of the bounds. 0.1 = 10% margin.
        The default is 0.1.
    one_point_fallback_margin: float, optional
        If the latitudes are equal AND the longitudes are equal, then a square
        of side length 2*one_point_fallback_margin centered on the single
        point will be returned as the bound.

    Returns
    -------
    marginal_bounds : list of ints or floats
        New bounds with added margin, same format as input bounds.

    """
    lons = [bounds[0],bounds[1]]
    lats = [bounds[2],bounds[3]]

    if len(set(lons)) == 1 and len(set(lats)) == 1:
        min_lon = lons[0] - one_point_fallback_margin
        max_lon = lons[1] + one_point_fallback_margin
        min_lat = lats[0] - one_point_fallback_margin
        max_lat = lats[1] + one_point_fallback_margin
    else:
        min_lon = min(lons) - (margin * abs(max(lons) - min(lons)))
        min_lat = min(lats) - (margin * abs(max(lats) - min(lats)))
        max_lon = max(lons) + (margin * abs(max(lons) - min(lons)))
        max_lat = max(lats) + (margin * abs(max(lats) - min(lats)))

    if min_lon > max_lon:
        new_max_lon = min_lon
        new_min_lon = max_lon

        min_lon = new_min_lon
        max_lon = new_max_lon

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

def plot_base_map(region,projection="Q15c+du",figure_name: str=None, resolution='01m',
                  cmap="./Resources/colormaps/cpt-city/colombia.cpt", frame: bool=True,
                  box_bounds=None,margin=0.1,bathymetry=False,
                  watercolor=None,colorbar_tick=2000,data_source: str='igpp',
                  map_scale: str=None,scalebar_height: float=10,
                  min_elev: float=0, max_elev: float=6000,
                  show_colorbar: bool=True):
    """
    Parameters
    ----------
    region : list of ints or floats
        Region to map in format [minlon, maxlon, minlat, maxlat]
    projection : string, optional
        GMT specs for projection. See GMT documentation for more details.
        The default is "Q15c+du".
    figure_name : string, optional
        Title of figure. The default is "figure!".
    resolution : string, optional
        Resolution of topo data. The default is '03s'. Can be any of '01d',
        '30m', '20m', '15m', '10m', '06m', '05m', '04m', '03m', '02m', '01m',
        '30s', '15s', '03s', '01s'
    cmap : string, optional
        Path to colormap. The default is "./Resources/colormaps/cpt-city/colombia.cpt".
    box_bounds : list of ints or floats, optional
        Bounds of box to draw on figure. If none given, none will be drawn.
    margin : float or int, optional
        Margin size, given as a decimal of the total dimensions. The default is 0.1.
    bathymetry : bool
        If False, will replace oceans with solid color. Default is false.
    watercolor : str
        If bathymetry is False, color of water. Defaults to skyblue.
    colorbar_tick : int or float
        Tick on elevation colorbar.
    show_colorbar : bool, optional
        If True, shows the topography colorbar. The default is True.
    Returns
    -------
    fig : pygmt.Figure
        PyGMT figure to use as basemap
    """
    if not watercolor:
        watercolor = "skyblue"
    bounds = get_margin_from_bounds(region,margin=margin)
    grid = pygmt.datasets.load_earth_relief(resolution=resolution, region=bounds,data_source=data_source)
    shade = pygmt.grdgradient(grid=grid, azimuth='0/90', normalize='t1')
    fig = pygmt.Figure()
    if cmap is not None:
        if '/' not in cmap:
            _cmap = True
            pygmt.makecpt(cmap=cmap, series=[min_elev, max_elev, 10])
        else:
            _cmap = cmap
        _grid = grid
    else: # If cmap is none, only plot the hillshade
        _grid = shade
        _cmap = True
        pygmt.makecpt(cmap="gray", series=[-1, 1, 0.01])
    if frame:
        fig.basemap(region=bounds,
                    projection=projection,
                    frame=frame)
    grdimage_kwargs = {
        'grid': _grid,
        'projection': projection,
        'frame': ["a", f"+t{figure_name}"] if figure_name and frame else (["a"] if frame else ["f"]),
        'cmap': _cmap
    }
    if cmap is not None:
        grdimage_kwargs['shading'] = shade
    fig.grdimage(**grdimage_kwargs, region=bounds)
    if bathymetry and show_colorbar:
        fig.colorbar(frame=[f"a{colorbar_tick}", "x+lElevation (m)", "y+lm"])
    if not bathymetry:
        fig.coast(shorelines="4/0.5p,black",
                  projection=projection,
                  borders="a/1.2p,black",
                  water=watercolor,
                  resolution="f")
    if box_bounds != None:
        if len(bounds) != 4:
            raise ValueError(f'Expected 4 items in box_bounds, got {len(box_bounds)}')
        bminlon = box_bounds[0]
        bmaxlon = box_bounds[1]
        bminlat = box_bounds[2]
        bmaxlat = box_bounds[3]
        blats = [bminlat, bmaxlat, bmaxlat, bminlat, bminlat]
        blons = [bminlon, bminlon, bmaxlon, bmaxlon, bminlon]
        fig.plot(x=blons,
                 y=blats,
                 pen="1p")
    if map_scale != None:
        with pygmt.config(MAP_SCALE_HEIGHT=f"{scalebar_height}p"):
            fig.basemap(map_scale=map_scale)
    return fig

def plot_base_map3d(region, max_depth: -6000, max_elev: 6200, projection="Q15c+du",
                    figure_name: str=None, resolution='01m', perspective = [180, 30],
                    cmap = os.path.join(os.path.dirname( __file__ ), '..', 'Resources', 'colormaps', 'cpt-city', 'colombia.cpt'),
                    box_bounds=None,margin=0.1,bathymetry=False,
                    watercolor=None,colorbar_tick=2000,data_source: str='igpp',
                    map_scale: str=None,scalebar_height: float=10):
    """
    Parameters
    ----------
    region : list of ints or floats
        Region to map in format [minlon, maxlon, minlat, maxlat]
    projection : string, optional
        GMT specs for projection. See GMT documentation for more details.
        The default is "Q15c+du".
    figure_name : string, optional
        Title of figure. The default is "figure!".
    resolution : string, optional
        Resolution of topo data. The default is '03s'. Can be any of '01d',
        '30m', '20m', '15m', '10m', '06m', '05m', '04m', '03m', '02m', '01m',
        '30s', '15s', '03s', '01s'
    cmap : string, optional
        Path to colormap. The default is "./Resources/colormaps/cpt-city/colombia.cpt".
    box_bounds : list of ints or floats, optional
        Bounds of box to draw on figure. If none given, none will be drawn.
    margin : float or int, optional
        Margin size, given as a decimal of the total dimensions. The default is 0.1.
    bathymetry : bool
        If False, will replace oceans with solid color. Default is false.
    watercolor : str
        If bathymetry is False, color of water. Defaults to skyblue.
    colorbar_tick : int or float
        Tick on elevation colorbar.

    Returns
    -------
    fig : pygmt.Figure
        PyGMT figure to use as basemap
    """
    if not watercolor:
        watercolor = "skyblue"

    bounds = get_margin_from_bounds(region,margin=margin)

    grid = pygmt.datasets.load_earth_relief(resolution=resolution, region=bounds,data_source=data_source)
    shade = pygmt.grdgradient(grid=grid, azimuth='90/50', normalize='t1')

    fig = pygmt.Figure()
    if figure_name is not None:
        fig.grdview(region=bounds,
                    grid=grid,
                    projection=projection,
                    cmap=cmap,
                    surftype='s',
                    perspective=perspective,
                    zsize='1c',
                    frame=True,
                    plane=f'{max_depth}+gazure',
                    #frame=["a",f"+t{figure_name}"],
                    shading=True)
    else:
        fig.grdview(region=bounds,
                    grid=grid,
                    projection=projection,
                    cmap=cmap,
                    surftype='s',
                    perspective=perspective,
                    frame=["a"],
                    contourpen='1p')

    """
    if figure_name is not None:
        fig.grdimage(grid=grid,
                     shading=shade,
                     projection=projection,
                     frame=["a",f"+t{figure_name}"],
                     cmap=cmap)
    else:
        fig.grdimage(grid=grid,
                     shading=shade,
                     projection=projection,
                     frame=["a"],
                     cmap=cmap)

    if bathymetry:
        fig.colorbar(frame=[f"a{colorbar_tick}", "x+lElevation (m)", "y+lm"])
    if not bathymetry:
        fig.coast(shorelines="4/0.5p,black",
                  projection=projection,
                  borders="a/1.2p,black",
                  water=watercolor,
                  resolution="f")
    """

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


def plot_holocene_volcanoes(fig,size: float=0.35,
                            style: str='t', fill: str='red'):
    """
    Parameters
    ----------
    fig : pygmt.Figure
        Figure to draw volcanoes on. If only plotting figure, use plot_base_map
        to create initial figure.
    size : float
        Size of markers.

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
             style=f'{style}/{size}c',
             fill=fill)

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
                      fontsize=14,offset=0.02,size=0.35,symbol='c',
                      color='black',label_color='black',
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
                 style=f'{symbol}{size}',
                 fill=color,
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
                 font=f'{fontsize}p,Helvetica-Bold,{label_color}',
                 fill='white@15')

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

def plot_outline(fig, x, y, linewidth: float=2.5, style: str='-.-'):
    fig.plot(x=x,
             y=y,
             pen=f'{linewidth}p,{style}')
    return fig

def plot_curve(fig, x, y, size: float=2, color: str='black',
               style: str='-', **kwargs):
    from scipy.interpolate import splprep, splev
    try:
        tck, u = splprep([x, y], **kwargs)
    except TypeError as e:
        if 'k' in str(e) and ('must hold') in str(e):
            raise ValueError('k must be less than or equal to the number of control points')
        else:
            raise e
    t_new = np.linspace(0, 1, 25)
    x_smooth_bspline, y_smooth_bspline = splev(t_new, tck)
    fig.plot(x=x_smooth_bspline,
             y=y_smooth_bspline,
             pen=f"{size}p,{color},{style}")
    return fig

def plot_text(fig, text, **kwargs):
    fig.text(text=text, **kwargs)
    return fig

def plot_arrow_and_label(fig: pygmt.Figure, label: str, x: int or float,
                         y: int or float, angle: int or float,
                         label_dx: int or float=0.1, label_dy: int or float=0.1,
                         arrow_dx: int or float=0, arrow_dy: int or float=0,
                         arrowh_color='red', label_transparency: int=50, arrowh_width: int or float=1,
                         arrow_length: int or float=10, arrow_width: int or float=1,
                         arrowh_angle: int or float=50, arrowh_sharpness: int or float=0.5,
                         font_size: int or float=12,arrow_color: str='black'):
    fig.plot(x=x + arrow_dx,
             y=y + arrow_dy,
             projection='M15c',
             style=f'v{arrowh_width}c+e+h{arrowh_sharpness}+a{arrowh_angle}',
             direction=([angle],[arrow_length]),
             pen=f'{arrow_width}p,{arrow_color}',
             fill=arrowh_color)
    fig.text(text=label,
             font=f'{font_size}p,Helvetica-Bold,black',
             x=x + label_dx,
             y=y + label_dy,
             transparency=label_transparency)
    return fig

def find_least_populated_area(lats, lons, bounds, grid_size=(10, 10), buffer_ratio=0.3):
    """
    Find the least populated area on a map using grid-based density analysis.

    Parameters:
    lats: array-like of latitude coordinates
    lons: array-like of longitude coordinates
    bounds: tuple of (min_lon, max_lon, min_lat, max_lat)
    grid_size: tuple of (rows, cols) for grid resolution
    buffer_ratio: fraction of map size to use as buffer from edges

    Returns:
    best_position: (lat, lon) of least populated area
    density_grid: 2D array of point counts per grid cell
    """
    lats = np.array(lats)
    lons = np.array(lons)
    min_lon, max_lon, min_lat, max_lat = bounds

    # Create grid
    lat_edges = np.linspace(min_lat, max_lat, grid_size[0] + 1)
    lon_edges = np.linspace(min_lon, max_lon, grid_size[1] + 1)

    # Count points in each grid cell
    density_grid, _, _ = np.histogram2d(
        lats, lons,
        bins=[lat_edges, lon_edges]
    )

    # Apply Gaussian smoothing to avoid edge artifacts and prefer areas away from points
    smoothed_density = ndimage.gaussian_filter(density_grid, sigma=0.8)

    # Create buffer mask to avoid placing labels too close to edges
    buffer_lat = (max_lat - min_lat) * buffer_ratio
    buffer_lon = (max_lon - min_lon) * buffer_ratio

    lat_centers = (lat_edges[:-1] + lat_edges[1:]) / 2
    lon_centers = (lon_edges[:-1] + lon_edges[1:]) / 2

    # Create mask for valid (non-edge) positions
    valid_mask = np.ones_like(smoothed_density, dtype=bool)

    # Apply buffer
    lat_mask = (lat_centers >= min_lat + buffer_lat) & (lat_centers <= max_lat - buffer_lat)
    lon_mask = (lon_centers >= min_lon + buffer_lon) & (lon_centers <= max_lon - buffer_lon)

    valid_mask[~lat_mask, :] = False
    valid_mask[:, ~lon_mask] = False

    # Find minimum density position within valid area
    masked_density = np.where(valid_mask, smoothed_density, np.inf)
    min_idx = np.unravel_index(np.argmin(masked_density), masked_density.shape)

    best_lat = lat_centers[min_idx[0]]
    best_lon = lon_centers[min_idx[1]]

    return best_lon, best_lat

def haversine_distance(lon1, lat1, lon2, lat2):
    R = 6371.0
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # Distance in kilometers
    distance = R * c
    return distance

def haversine_distance_degrees(lon1, lat1, lon2, lat2):
    R = 6371.0
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # Distance in kilometers
    distance = R * c
    return distance

def azimuthal_direction(lon1, lat1, lon2, lat2):
    """
    Calculate the azimuthal direction from point 1 to point 2 on Earth's surface.

    Args:
        lon1, lat1: Longitude and latitude of starting point (degrees)
        lon2, lat2: Longitude and latitude of ending point (degrees)

    Returns:
        Azimuth in degrees (0 = North, positive counterclockwise)
    """
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon_rad = math.radians(lon2 - lon1)

    # Calculate azimuth using spherical trigonometry
    y = math.sin(dlon_rad) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))

    # Calculate azimuth in radians
    azimuth_rad = math.atan2(y, x)

    # Convert to degrees
    azimuth_deg = math.degrees(azimuth_rad)

    # Ensure result is in range [0, 360)
    azimuth_deg = (azimuth_deg + 360) % 360

    return azimuth_deg

def draw_rectangle(fig, minlon, maxlon, minlat, maxlat,
                   linewidth=1,linecolor='black', transparency=0):

    # Create rectangle coordinates (closed polygon)
    x = [minlon, maxlon, maxlon, minlon, minlon]
    y = [minlat, minlat, maxlat, maxlat, minlat]

    # Draw the rectangle with no fill
    fig.plot(
        x=x,
        y=y,
        pen=f'{linewidth}p,{linecolor}',
        transparency=transparency,
        straight_line=True
    )

    return fig