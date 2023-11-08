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
                                              level="station",)
    return station_inv

def find_multi_network(deployment_list,bounds,client="IRIS"):
    
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

def get_marginal_bounds(bounds,margin=0.1):
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
    

def plot_stations(inventory,projection="Q15c+du",figure_name="figure!",resolution='03s',region=None,cmap="dem2"):
    
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
                 pen="0.2p")
    
    return fig

def plot_bounding_box(fig, bounds):
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

def save_fig(fig,name,dpi=720,ftype="png"):
    fname = name + "." + ftype
    print(fname)
    fig.savefig(fname=fname,
                dpi=dpi)

deployment_list = [["UW","2015-01-01","2017-12-31"],["XU","2007-01-01","2011-12-31"],
                   ["XD","2014-01-01","2016-12-31","M*"],["TA","2006-01-01","2023-11-6"],
                   #["YW","2005-08-11","2005-12-31"],
                   ["CC","2020-10-22","2023-11-7"],["NP","2013-01-01","2013-01-02"]
                   ]
region_bounds = [-122, -120.5, 45.6, 47.25]
box_bounds = [-122, -121, 46.35, 47.1]

station_inv = find_multi_network(deployment_list,region_bounds)

fig = plot_stations(station_inv,
                    figure_name="Rainier Region Seismic Stations",
                    cmap="../Resources/colormaps/colombia.cpt""")
fig_box = plot_bounding_box(fig, box_bounds)
fig_box.show()
#save_fig(fig_box,"Regional_Stations")

fig2 = plot_stations(station_inv,region=box_bounds,
                     figure_name="Stations within Bounding Box")
fig2_box = plot_bounding_box(fig2, box_bounds)
fig2_box.show()
#save_fig(fig2_box,"Local_View_Stations")