#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 13:52:22 2023

@author: tlee

Quick script to plot the general region around Laguna Maule.
"""

from obspy.clients.fdsn import Client
from obspy import UTCDateTime
import pygmt
import pandas as pd

min_lon = -109
max_lon = -102
min_lat = 31
max_lat = 37
projection='M15c'
figure_name = 'Laguna Maule Regional Overview'
file_type = 'png'
plot_holocene_volcanoes = True

client = Client('IRIS') # Client to use for catalogging. Generally, use IRIS
starttime=("2015-01-01") # Start time in UTC
endtime=("2017-12-31") # End time in UTC
network = "ZR" # Network code
station = "*" # Set to * to select all stations in network
channel_prefix ="??" # Set to * or ?? if unknown
margin = 0.2 # Margin around the area covered by the stations

channels = channel_prefix + "*"
certical_channel = channel_prefix + "Z"
starttime = UTCDateTime(starttime)
endtime = UTCDateTime(endtime)

station_inv = client.get_stations(starttime=starttime, endtime=endtime,
                                      network=network, station=station,
                                      level="channel", channel=channels)

station_lats = []
station_lons = []
station_codes = []
station_elevs = []

for current_network in station_inv:
    if len(station_inv.networks) != 0:
        for station in station_inv.networks[0]:
            station_lats.append(station.latitude)
            station_lons.append(station.longitude)
            station_codes.append(station.code)
            station_elevs.append(station.elevation)

station_df = pd.DataFrame({'lat':station_lats,'lon':station_lons,
                           'elev':station_elevs},
                          index = station_codes)

region = [min_lon, max_lon, min_lat, max_lat]
grid = pygmt.datasets.load_earth_relief(resolution="01m", region=region)

url = 'https://raw.githubusercontent.com/geothomaslee/Mapping_Resources/master/Resources/GVP_Volcano_List_Holocene.csv'
holo_volc_df = pd.read_csv(url)
holocene_vol_lon_list = holo_volc_df['Longitude'].tolist()
holocene_vol_lat_list = holo_volc_df['Latitude'].tolist()


fig = pygmt.Figure()


fig.basemap(region=region,
             projection=projection,
             frame=True)
fig.grdimage(grid=grid,
             projection=projection,
             frame=["a",f'+t{figure_name}'],
             cmap='geo')
fig.coast(shorelines="4/0.5p,black",
          projection=projection,
          borders="1/1.2p,black",
          resolution="f")
if plot_holocene_volcanoes is True:
    fig.plot(x=holocene_vol_lon_list,
             y=holocene_vol_lat_list,
             style='t0.35c',
             fill='red')
fig.plot(x=(sum(station_lons) / len(station_lons)),
         y=(sum(station_lats) / len(station_lats)),
         style='a1c',
         fill='yellow')



fig.show()


FILENAME = figure_name.replace(' ','_')
FILENAME += f'_Map.{file_type}'
fig.savefig(fname=FILENAME,
            dpi=720)