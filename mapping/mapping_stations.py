# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:05:26 2023

@author: tlee
"""

from obspy.clients.fdsn import Client
import pygmt

def find_stations(network, starttime,endtime,station='*',client="IRIS"):
    working_client = Client(client)
    station_inv = working_client.get_stations(starttime=starttime,
                                              endtime=endtime,
                                              network=network, 
                                              station=station,
                                              level="station")
    return station_inv

def find_multi_network(deployment_list,client="IRIS"):
    working_client = Client(client)
    for i, deployment in enumerate(deployment_list):
        network = deployment[0]
        starttime = deployment[1]
        endtime = deployment[2]
        
        if i < 1:
            station_inv = working_client.get_stations(starttime=starttime,
                                                      endtime=endtime,
                                                      network=network, 
                                                      station='*',
                                                      level="station")
        else:
            secondary_inv = working_client.get_stations(starttime=starttime,
                                                        endtime=endtime,
                                                        network=network, 
                                                        station='*',
                                                        level="station")
            station_inv += secondary_inv
            
    return station_inv

def get_coordinates_from_network(network):
    lat_list = []
    lon_list = []
    elev_list = []
    
    for station in network:
        lat_list.append(station.latitude)
        lon_list.append(station.longitude)
        elev_list.append(station.elevation)
        
    return lat_list, lon_list, elev_list
    
def get_coordinate_list(inventory):
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

def plot_stations(bounds,projection="Q15c+du",figure_name="figure!"):
    
    grid = pygmt.datasets.load_earth_relief(resolution="03s", region=bounds)
    
    fig = pygmt.Figure()
    fig.basemap(region=bounds,
                projection=projection,
                frame=True)
    fig.grdimage(grid=grid,
                 projection=projection,
                 frame=["a",f'+t{figure_name}'],
                 cmap='dem2')
    fig.coast(shorelines="4/0.5p,black",
              projection=projection,
              borders="1/1.2p,black",
              water="skyblue",
              resolution="f")
    
    return fig
    
def plot_inventory(inventory):
    lats, lons, elevs = get_coordinate_list(inventory)
    bounds = get_map_bounds(lats,lons)
    fig = plot_stations(bounds)
    fig.show()
    

deployment_list = [["ZR","2015-01-01","2017-12-31"]]
station_inv = find_multi_network(deployment_list)
 
plot_inventory(station_inv)