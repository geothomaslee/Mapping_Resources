# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:05:26 2023

@author: tlee
"""

from obspy.clients.fdsn import Client
import pygmt
import numpy as np
from tqdm import tqdm

if __name__ == '__main__':
    import general_mapping as gm
else:
    import scripts.general_mapping as gm


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
            
    station_total = 0
    for network in station_inv:
        station_total += len(network)
        
    print(f'{station_total} stations found in {len(station_inv)} networks!')
            
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
    

def plot_stations(inventory,fig=None,projection="Q15c+du",figure_name="figure!",
                  resolution='03s',region=None,
                  cmap="./Resources/colormaps/colombia.cpt",
                  box_bounds=None,margin=0.1,
                  plot_holo_vol=False):
    """
    Parameters
    ----------
    inventory : obspy.core.inventory.Inventory
        ObsPy inventory containing the stations to plot.
    fig : pygmt.Figure
        Give a pygmt figure to plot stations on top of an existing figure.
        Otherwise, a basemap will be created automatically.
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
    margin : int or float, optional
        Margin size, multiplied by the length of the bounds. 0.1 = 10% margin. 
        The default is 0.1.

    Returns
    -------
    fig : pygmt.Figure
        PyGMT figure with plotted data.

    """
    
    if __name__ == '__main__':
        cmap="../Resources/colormaps/colombia.cpt",
    
    lats,lons,elevs = get_coordinate_list(inventory)
    
    if region == None:
        bounds = gm.get_margin_from_lat_lon(lats,lons,margin=margin)
    else:
        bounds = gm.get_margin_from_bounds(region,margin=margin)
        
    if fig == None:
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
    
    
    colors = ["cyan","yellow","green","blue","purple","orange","red"]

    for i, network in enumerate(inventory):
        lats,lons,elevs = get_coordinates_from_network(network)
        fig.plot(x=lons,
                 y=lats,
                 style="t0.4c",
                 fill=colors[i],
                 label=network.code,
                 pen="0.2p",
                 connection='r')
        
    fig.legend()
        
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
    
    if plot_holo_vol == True:
        fig = gm.plot_holocene_volcanoes(fig)
    
    return fig

def plot_cross_station_paths(inventory, fig):
                              
    lats,lons,elevs = get_coordinate_list(inventory)
        
    coord_pairs = list(zip(lats, lons))
    
    """
    for index, pair in enumerate(tqdm(coord_pairs)):
        for index2 in np.arange(index+1,len(coord_pairs),1):
            pair2 = coord_pairs[index2]
            
            cross_pair_lons = [pair[0],pair2[0]]
            cross_pair_lats = [pair[1],pair2[1]]
            
            fig.plot(x=cross_pair_lons,
                     y=cross_pair_lats,
                     pen='1p,black')
    """
    """
    for index in tqdm(np.arange(0, 1)):
        pair = coord_pairs[index]
        print(f'starting pair {pair}')
        for index2 in tqdm(np.arange(index+1,len(coord_pairs),1)):
            pair2 = coord_pairs[index2]
            
            cross_pair_lons = [pair[1],pair2[1]]
            cross_pair_lats = [pair[0],pair2[0]]
            
            if index2 == 3:
                print(pair2)
                print(cross_pair_lons)
                print(cross_pair_lats)
            
            fig.plot(x=cross_pair_lons,
                     y=cross_pair_lats,
                     pen='0.2p')
            
    return fig
    
    """
    
    coord1 = coord_pairs[0]
    coord2 = coord_pairs[1]
    coord3 = coord_pairs[2]
    
    lons1 = [coord1[1],coord2[1]]
    lons2 = [coord2[1],coord3[1]]
    
    lats1 = [coord1[0],coord2[0]]
    lats2 = [coord2[0],coord3[0]]
    
    lons = [lons1, lons2]
    lats = [lats1, lats2]
    
    print(lons)
    print(lats)
    
    fig.plot(x=lons,
             y=lats,
             pen='0.1p')
    
    return fig
            
            
    
        


region_bounds = [-122.5, -120.5, 45, 47.25]
box_bounds = [-122.5, -120.9, 46.1, 47.3]
deployment_list = [["UW","2015-01-01","2017-12-31"],["XU","2007-01-01","2011-12-31"],
                   ["XD","2014-01-01","2016-12-31","M*"],["TA","2006-01-01","2023-11-6"],
                   ["CC","2020-10-22","2023-11-7"],["YH","2016-01-01","2016-12-31"]]
station_inv = find_multi_network(deployment_list,box_bounds)

regional_fig = plot_stations(station_inv,
                             figure_name="Rainier Region Seismic Stations",
                             resolution="15s",
                             margin=0.1,
                             region=box_bounds)


regional_fig.show()
"""
cross_fig = plot_cross_station_paths(inventory=station_inv,fig=regional_fig)

cross_fig.show()
                """                






    