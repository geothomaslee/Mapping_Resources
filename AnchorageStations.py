#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 13:17:22 2025

@author: thomaslee
"""

import pygmt

import obspy
from obspy import UTCDateTime
from obspy.clients.fdsn import Client

from scripts import general_mapping as gm
from scripts import mapping_events as me
from scripts import colormap_utils as cu
from scripts import mapping_stations as ms


color = ['lightseagreen','darkslategray1','orange']
#=============================Regional Overview================================
cmap = cu.create_combined_color_map('usgs','colombia',max_elev=3000,max_depth=-500)

bounds = [-151.7, -148.8, 60.6, 62.1]

fig = gm.plot_base_map(region=bounds,
                       projection='M-150.2/61.3/12c',
                       resolution='15s',
                       cmap=cmap,
                       data_source='gebco',
                       bathymetry=True,margin=0.02,
                       map_scale="n0.2/0.96+w50k+f+u",
                       scalebar_height=10,
                       colorbar_tick=500)

c = Client('IRIS')

inv = c.get_stations(starttime=UTCDateTime('2000-01-01'),
                     endtime=UTCDateTime('2025-04-01'),
                     minlatitude=bounds[2],
                     maxlatitude=bounds[3],
                     minlongitude=bounds[0],
                     maxlongitude=bounds[1],
                     network='AK,NP')

for i, net in enumerate(inv):
    lons = []
    lats = []
    for stat in net:
        lons.append(stat.longitude)
        lats.append(stat.latitude)
    
    fig.plot(x=lons,
             y=lats,
             style='i0.5c',
             pen='0.2p',
             fill=f'{color[i]}',
             label=f'{net.code}')
        
fig.legend()

gm.save_fig(fig,'AnchorageRegion',dpi=960)

fig.show()

#=============================AK Only Velocity================================
bounds = [-150.5, -148.8, 60.8, 61.65]
fig = gm.plot_base_map(region=bounds,
                       projection='M-150.2/61.3/12c',
                       resolution='15s',
                       data_source='gebco',
                       cmap=cmap,
                       bathymetry=True,margin=0.02,
                       map_scale="n0.2/0.96+w25k+f+u",
                       scalebar_height=10,
                       colorbar_tick=500)

c = Client('IRIS')

inv = c.get_stations(starttime=UTCDateTime('2000-01-01'),
                     endtime=UTCDateTime('2025-04-01'),
                     minlatitude=bounds[2],
                     maxlatitude=bounds[3],
                     minlongitude=bounds[0],
                     maxlongitude=bounds[1],
                     network='AK',
                     channel='*HZ')

for i, net in enumerate(inv):
    lons = []
    lats = []
    for stat in net:
        lons.append(stat.longitude)
        lats.append(stat.latitude)
    
    fig.plot(x=lons,
             y=lats,
             style='i0.5c',
             pen='0.2p',
             fill=f'{color[0]}',
             label=f'{net.code}')
        
fig.legend()
gm.save_fig(fig,'AnchorageAK_Vel_Only',dpi=960)

fig.show()

#=============================AK Overview================================
bounds = [-150.5, -148.8, 60.8, 61.65]
fig = gm.plot_base_map(region=bounds,
                       projection='M-150.2/61.3/12c',
                       resolution='15s',
                       data_source='gebco',
                       cmap=cmap,
                       bathymetry=True,margin=0.02,
                       map_scale="n0.2/0.96+w25k+f+u",
                       scalebar_height=10,
                       colorbar_tick=500)

c = Client('IRIS')

inv = c.get_stations(starttime=UTCDateTime('2000-01-01'),
                     endtime=UTCDateTime('2025-04-01'),
                     minlatitude=bounds[2],
                     maxlatitude=bounds[3],
                     minlongitude=bounds[0],
                     maxlongitude=bounds[1],
                     network='AK')

for i, net in enumerate(inv):
    lons = []
    lats = []
    for stat in net:
        lons.append(stat.longitude)
        lats.append(stat.latitude)
    
    fig.plot(x=lons,
             y=lats,
             style='i0.5c',
             pen='0.2p',
             fill=f'{color[0]}',
             label=f'{net.code}')
        
fig.legend()
gm.save_fig(fig,'AnchorageAK',dpi=960)

fig.show()

#=============================NP Overview================================
bounds = [-150.5, -148.8, 60.8, 61.65]
fig = gm.plot_base_map(region=bounds,
                       projection='M-150.2/61.3/12c',
                       resolution='15s',
                       data_source='gebco',
                       cmap=cmap,
                       bathymetry=True,margin=0.02,
                       map_scale="n0.2/0.96+w25k+f+u",
                       scalebar_height=10,
                       colorbar_tick=500)

c = Client('IRIS')

inv = c.get_stations(starttime=UTCDateTime('2000-01-01'),
                     endtime=UTCDateTime('2025-04-01'),
                     minlatitude=bounds[2],
                     maxlatitude=bounds[3],
                     minlongitude=bounds[0],
                     maxlongitude=bounds[1],
                     network='NP')

for i, net in enumerate(inv):
    lons = []
    lats = []
    for stat in net:
        lons.append(stat.longitude)
        lats.append(stat.latitude)
    
    fig.plot(x=lons,
             y=lats,
             style='i0.5c',
             pen='0.2p',
             fill=f'{color[1]}',
             label=f'{net.code}')
        
fig.legend()
gm.save_fig(fig,'AnchorageNP',dpi=960)

fig.show()

#=============================Raspberry Shake Overview================================
bounds = [-150.5, -148.8, 60.8, 61.65]
fig = gm.plot_base_map(region=bounds,
                       projection='M-150.2/61.3/12c',
                       resolution='15s',
                       data_source='gebco',
                       cmap=cmap,
                       bathymetry=True,margin=0.02,
                       map_scale="n0.2/0.96+w25k+f+u",
                       scalebar_height=10,
                       colorbar_tick=500)

c = Client('RASPISHAKE')

inv2 = c.get_stations(starttime=UTCDateTime('2023-01-01'),
                     endtime=UTCDateTime('2025-04-01'),
                     minlatitude=bounds[2],
                     maxlatitude=bounds[3],
                     minlongitude=bounds[0],
                     maxlongitude=bounds[1],
                     network='AM')

for i, net in enumerate(inv2):
    lons = []
    lats = []
    for stat in net:
        lons.append(stat.longitude)
        lats.append(stat.latitude)
    
    fig.plot(x=lons,
             y=lats,
             style='i0.5c',
             pen='0.2p',
             fill=f'{color[2]}',
             label=f'{net.code}')
        
fig.legend()
gm.save_fig(fig,'AnchorageRaspShake',dpi=960)

fig.show()

#================All Stations===================================
c = Client('IRIS')

inv = c.get_stations(starttime=UTCDateTime('2000-01-01'),
                     endtime=UTCDateTime('2025-04-01'),
                     minlatitude=bounds[2],
                     maxlatitude=bounds[3],
                     minlongitude=bounds[0],
                     maxlongitude=bounds[1],
                     network='AK,NP')

inv = inv + inv2

bounds = [-150.5, -148.8, 60.8, 61.65]

fig = gm.plot_base_map(region=bounds,
                       projection='M-150.2/61.3/12c',
                       resolution='15s',
                       data_source='gebco',
                       cmap=cmap,
                       bathymetry=True,margin=0.02,
                       map_scale="n0.2/0.96+w25k+f+u",
                       scalebar_height=10,
                       colorbar_tick=500)

for i, net in enumerate(inv):
    lons = []
    lats = []
    for stat in net:
        lons.append(stat.longitude)
        lats.append(stat.latitude)
    
    fig.plot(x=lons,
             y=lats,
             style='i0.5c',
             pen='0.2p',
             fill=f'{color[i]}',
             label=f'{net.code}')
        
fig.legend()
gm.save_fig(fig,'AnchorageLocalAllStations',dpi=960)

fig.show()
                        