# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:05:26 2023

@author: tlee
"""

from obspy.clients.fdsn import Client
import pygmt

def find_stations(network, starttime,endtime,station='*',client="IRIS"):
    """
    Parameters
    ----------
    network : string
        Network name.
    starttime : string
        Starttime formattted as yyyy-mm-ddT00.00.00.000. Can exclude T.
    endtime : string
        Endtime formatted as yyyy-mm-ddT00.00.00.000. Can exclude T.
    station : string, optional
        Glob compatible station selection. The default is '*'.
    client : string, optional
        Data host. If unsure use default. The default is "IRIS".

    Returns
    -------
    station_inv : obspy.core.inventory.Inventory
        ObsPy inventory object containing the selected stations.

    """
    working_client = Client(client)
    station_inv = working_client.get_stations(starttime=starttime,
                                              endtime=endtime,
                                              network=network, 
                                              station=station,
                                              level="station",)
    return station_inv

def find_multi_network(deployment_list,bounds,client="IRIS"):
    """
    Parameters
    ----------
    deployment_list : list of lists of strings
        List of lists, each sublist containing 3 or 4 strings giving information
        for the deployment. Requires network, starttime, endtime, station, in
        that order. See find_stations for details
    bounds : list of ints or floats
        Region to search for stations, in order [minlon, maxlon, minlat, maxlat]
    client : string, optional
        Data host. If unsure use default. The default is "IRIS".
        
    Returns
    -------
    station_inv : obspy.core.inventory.Inventory
        ObsPy inventory object containing the stations.
    """
    
    if len(bounds) != 4:
        raise ValueError(f'Expected 4 items in bounds, got {len(bounds)}')
        
    minlon = bounds[0]
    maxlon = bounds[1]
    minlat = bounds[2]
    maxlat = bounds[3]
    
    working_client = Client(client)
    for i, deployment in enumerate(deployment_list):
        network = deployment[0]
        starttime = deployment[1]
        endtime = deployment[2]
        
        if len(deployment) == 3:
            stations = "*"
        elif len(deployment) == 4:
            stations = deployment[3]
        else:
            raise ValueError("Expected 3 or 4 arguments for network {network}, got {len(deployment})")
        
        if i < 1:
            station_inv = working_client.get_stations(starttime=starttime,
                                                      endtime=endtime,
                                                      network=network, 
                                                      station=stations,
                                                      level="station",
                                                      minlatitude=minlat,
                                                      maxlatitude=maxlat,
                                                      minlongitude=minlon,
                                                      maxlongitude=maxlon)
        else:
            secondary_inv = working_client.get_stations(starttime=starttime,
                                                        endtime=endtime,
                                                        network=network, 
                                                        station=stations,
                                                        level="station",
                                                        minlatitude=minlat,
                                                        maxlatitude=maxlat,
                                                        minlongitude=minlon,
                                                        maxlongitude=maxlon)
            station_inv += secondary_inv
            
    return station_inv

def get_coordinates_from_network(network):
    """
    Parameters
    ----------
    network : obspy.core.network.Network
        ObsPy network object containing the stations.

    Returns
    -------
    lat_list : list
        List of latitudes.
    lon_list : list
        List of longitudes.
    elev_list : list
        List of elevations.

    """
    lat_list = []
    lon_list = []
    elev_list = []
    
    for station in network:
        lat_list.append(station.latitude)
        lon_list.append(station.longitude)
        elev_list.append(station.elevation)
        
    return lat_list, lon_list, elev_list
    
def get_coordinate_list(inventory):
    """
    Parameters
    ----------
    inventory : obspy.core.inventory.Inventory
        ObsPy inventory object containing the network(s).

    Reeturns
    -------
    lat_list : list
        List of latitudes.
    lon_list : list
        List of longitudes.
    elev_list : list
        List of elevations.

    """
    
    lat_list = []
    lon_list = []
    elev_list = []
    
    for network in inventory:
        lats, lons, elevs = get_coordinates_from_network(network)
        lat_list += lats
        lon_list += lons
        elev_list += elevs
    
    return lat_list, lon_list, elev_list

def check_lon(coord):
    """Checks if coordinates are -180 < coord < 180 and wraps if out of range"""
    if coord < -180:
        coord = 180 + (coord - -180)
    elif coord > 180:
        coord = -180 + (coord - 180)
    return coord

def check_lat(coord):
    """Checks if latitudes are in range -90 < coordinate < 90"""
    if coord < -90:
        coord = -90
    elif coord > 90:
        coord = 90
    return coord

def get_map_bounds(lats,lons,margin=0.1):
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

def get_marginal_bounds(bounds,margin=0.1):
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

def plot_bounding_box(fig, bounds):
    """
    Parameters
    ----------
    fig : pygmt.Figure
        PyGMT figure to draw on.
    bounds : list of ints or floats
        Region to search for stations, in order [minlon, maxlon, minlat, maxlat]

    Returns
    -------
    fig : pygmt.Figure
        Input figure with box added.
    """
    
    if len(bounds) != 4:
        raise ValueError(f'Expected 4 items in bounds, got {len(bounds)}')
        
    minlon = bounds[0]
    maxlon = bounds[1]
    minlat = bounds[2]
    maxlat = bounds[3]
    
    lats = [minlat, maxlat, maxlat, minlat, minlat]
    lons = [minlon, minlon, maxlon, maxlon, minlon]
    
    fig.plot(x=lons,
             y=lats,
             pen="1p")
    
    return fig
    

def plot_stations(inventory,projection="Q15c+du",figure_name="figure!",
                  resolution='03s',region=None,
                  cmap="./Resources/colormaps/colombia.cpt",
                  box_bounds=None):
    """
    Parameters
    ----------
    inventory : obspy.core.inventory.Inventory
        ObsPy inventory containing the stations to plot.
    projection : string, optional
        GMT flag for specifying projection. The default is "Q15c+du".
    figure_name : string, optional
        Title for figure. The default is "figure!".
    resolution : int, optional
        Resolution of the topographic data to be loaded. The default is '03s'.
        See PyGMT.load_earth_relief for more options.
    region : list of ints or floats, optional
        Region to plot, in order [minlon, maxlon, minlat, maxlat]
    cmap : TYPE, optional
        DESCRIPTION. The default is "../Resources/colormaps/colombia.cpt".
    box_bounds : list of ints or floats, optional
        Region to draw a box around, in order [minlon, maxlon, minlat, maxlat].
        If none is set, no box will be drawn

    Returns
    -------
    fig : pygmt.Figure
        PyGMT figure with plotted data.

    """
    
    lats,lons,elevs = get_coordinate_list(inventory)
    
    if region == None:
        bounds = get_map_bounds(lats,lons)
    else:
        bounds = get_marginal_bounds(region)
    
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
              rivers="1/2p,blue",
              projection=projection,
              borders="2/1.2p,black",
              water="skyblue",
              resolution="f")
    
    colors = ["cyan","yellow","green","blue","purple","orange","red"]

    for i, network in enumerate(inventory):
        lats,lons,elevs = get_coordinates_from_network(network)
        fig.plot(x=lons,
                 y=lats,
                 style="t0.4c",
                 fill=colors[i],
                 label=network.code,
                 pen="0.2p")
        
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
        
    fig.legend()
    
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
    