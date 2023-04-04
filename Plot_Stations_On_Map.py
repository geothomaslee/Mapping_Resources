#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 22:36:14 2023

@author: tlee


Quick script for plotting the stations of a given seismic network.

The first plot is a local map of the stations within the specified network and
has a small margin around the deployment area (set with LOCAL_MARGIN).

The second plot is a broader regional overview of the study area and plots
a black box around the area of the first map. By default plots Holocene age
volcanoes and removes any that are within the study area.
"""

from obspy.clients.fdsn import Client
from obspy import UTCDateTime
import pygmt
import pandas as pd

CLIENT = "IRIS" # Client to use for catalogging. Generally, use IRIS
STARTTIME=("2015-01-01") # Start time in UTC
ENDTIME=("2017-12-31") # End time in UTC
NETWORK = "ZR" # Network code
STATION = "*" # Set to * to select all stations in network
CHANNEL_PREFIX ="??" # Set to * or ?? if unknown
LOCAL_MARGIN = 0.2 # Margin around the area covered by the stations
REGIONAL_MARGIN = 6
FIGURE_NAME = 'Laguna Maule Seismic Deployment' # Name for figure
FILE_TYPE = 'png' # See pygmt documentation for more options. Default png
PROJECTION="Q15c+du" #Default Q15c+du
HIDE_VOL_IN_STUDY_AREA = False # True removes volcano symbols in study area

CHANNELS = CHANNEL_PREFIX + "*"
VERTICAL_CHANNEL = CHANNEL_PREFIX + "Z"
client = Client(CLIENT)
starttime = UTCDateTime(STARTTIME)
endtime = UTCDateTime(ENDTIME)

station_inv = client.get_stations(starttime=starttime, endtime=endtime,
                                      network=NETWORK, station=STATION,
                                      level="channel", channel=CHANNELS)

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

station_count = len(station_df.index)

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

bound_min_lon = min(station_lons) - (LOCAL_MARGIN * abs(max(station_lons) - min(station_lons)))
bound_min_lat = min(station_lats) - (LOCAL_MARGIN * abs(max(station_lats) - min(station_lats)))
bound_max_lon = max(station_lons) + (LOCAL_MARGIN * abs(max(station_lons) - min(station_lons)))
bound_max_lat = max(station_lats) + (LOCAL_MARGIN * abs(max(station_lats) - min(station_lats)))

bound_min_lon = check_lon(bound_min_lon)
bound_max_lon = check_lon(bound_max_lon)
bound_min_lat =  check_lat(bound_min_lat)
bound_max_lat = check_lat(bound_max_lat)

region = [bound_min_lon, bound_max_lon, bound_min_lat, bound_max_lat]
grid = pygmt.datasets.load_earth_relief(resolution="03s", region=region)

fig = pygmt.Figure()
fig.basemap(region=region,
             projection=PROJECTION)
fig.grdimage(grid=grid,
             projection=PROJECTION,
             frame=["a",f'+t{FIGURE_NAME}'],
             cmap='dem2')
fig.coast(shorelines="4/0.5p,black",
          projection=PROJECTION,
          borders="1/1.2p,black",
          water="skyblue",
          resolution="f")
fig.plot(x=station_lons,
         y=station_lats,
         style="d1c",
         fill="cyan",
         pen="0.2p")
fig.text(text=station_codes,
         x=station_lons,
         y=station_lats,
         font="9p,Helvetica-Bold,black")
fig.show()

FILENAME = FIGURE_NAME.replace(' ','_')
FILENAME += f'_Local_Map.{FILE_TYPE}'
fig.savefig(fname=FILENAME,
            dpi=720)



"""Regional overview"""
region_min_lon = min(station_lons) - (REGIONAL_MARGIN * abs(max(station_lons) - min(station_lons)))
region_min_lat = min(station_lats) - (REGIONAL_MARGIN * abs(max(station_lats) - min(station_lats)))
region_max_lon = max(station_lons) + (REGIONAL_MARGIN * abs(max(station_lons) - min(station_lons)))
region_max_lat = max(station_lats) + (REGIONAL_MARGIN * abs(max(station_lats) - min(station_lats)))

region = [region_min_lon, region_max_lon, region_min_lat, region_max_lat]
grid = pygmt.datasets.load_earth_relief(resolution="15s", region=region)

bound_lons = [bound_min_lon, bound_min_lon, bound_max_lon, bound_max_lon, bound_min_lon]
bound_lats = [bound_min_lat, bound_max_lat, bound_max_lat, bound_min_lat, bound_min_lat]

VOL_URL = 'https://raw.githubusercontent.com/geothomaslee/Mapping_Resources/master/Resources/GVP_Volcano_List_Holocene.csv'
holo_volc_df = pd.read_csv(VOL_URL)
holocene_vol_lon_list = holo_volc_df['Longitude'].tolist()
holocene_vol_lat_list = holo_volc_df['Latitude'].tolist()

if HIDE_VOL_IN_STUDY_AREA is True:
    for i, lon in enumerate(holocene_vol_lon_list):
        lat = holocene_vol_lat_list[i]
        if lon < bound_max_lon and lon > bound_min_lon:
            if lat < bound_max_lat and lat > bound_min_lat:
                del holocene_vol_lon_list[i]
                del holocene_vol_lat_list[i]

fig = pygmt.Figure()
fig.basemap(region=region,
             projection=PROJECTION)
fig.grdimage(grid=grid,
             projection=PROJECTION,
             frame=["a",f'+t{FIGURE_NAME}'],
             cmap='geo')
fig.coast(shorelines="4/0.5p,black",
          projection=PROJECTION,
          borders="1/1.2p,black",
          water="skyblue",
          resolution="f")
fig.plot(x=bound_lons,
         y=bound_lats,
         pen='3p,black',
         label='Study Region')
fig.plot(x=station_lons,
         y=station_lats,
         style="d0.25c",
         fill="cyan",
         pen="0.05p",
         label='Broadband Stations')
fig.plot(x=holocene_vol_lon_list,
         y=holocene_vol_lat_list,
         style='t0.525c',
         fill='red',
         label='Holocene Volcanoes')
fig.legend(position='JBR+jBR+o0.2c',
           box='+gwhite+p1p')
fig.show()

FILENAME = FIGURE_NAME.replace(' ','_')
FILENAME += f'_Regional_Map.{FILE_TYPE}'
fig.savefig(fname=FILENAME,
            dpi=720)

