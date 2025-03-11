# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:05:02 2023

@author: tlee
"""

import scripts.mapping_stations as ms
import scripts.general_mapping as gm
import scripts.station_utils as su
import scripts.colormap_utils as cu


deployment_list = [["UW","2015-01-01","2017-12-31"],["XU","2007-01-01","2011-12-31"],
                   ["XD","2014-01-01","2016-12-31","M*"],["TA","2006-01-01","2023-11-6"],
                   ["CC","2020-10-22","2023-11-7"],["YH","2016-01-01","2016-12-31"]]


studyAreaBounds = [-122.8625, -120.25, 46.0796, 47.8242]

#station_inv = ms.find_multi_network(deployment_list,studyAreaBounds)

"""
# Saving relevant station information, specifically designed for ambient noise
# Studies but will contain useful info for any deployment
station_df = su.get_station_df(station_inv)
station_df.to_csv('Stations_To_Correlate.csv')

station_avail_df = su.station_availability_from_df(station_df,startdate='2000-01-01')
station_avail_df.to_csv('Station_Availability_Over_Time.csv')

# Defining intervals to highlight that are actually used
ints = [[2006.583333,2009],[2014.51666,2017],[2023,2024]]
su.plot_station_availability(station_avail_df,highlighted_intervals=ints)
"""

#====Creating a nice colormap
cmap = cu.create_combined_color_map('usgs','colombia',max_elev=4500,max_depth=0)

"""
# Plotting a regional overview
pnw_regional_fig = ms.plot_stations(station_inv,
                                    figure_name="Rainier Region Seismic Stations",
                                    box_bounds=studyAreaBounds,
                                    resolution="01m",
                                    cmap=cmap,
                                    margin=0.5,
                                    bathymetry=True)

pnw_regional_fig = gm.plot_major_cities(pnw_regional_fig,minpopulation=200000,
                                        close_threshhold=0.01,offset=0.03,
                                        dotsize=0.25,hor_offset_multiplier=3.5)
pnw_regional_fig.show()

gm.save_fig(pnw_regional_fig,"PNW Regional Overview")
"""

seis_fig = gm.plot_base_map(region=[-122.3,-121.19,46.5,47.1],
                            cmap=cmap,
                            projection='M-122/47/12c',
                            resolution='01s',
                            margin=0.05,
                            figure_name='Rainier Region Seismicity M>1, 1980-2025',
                            bathymetry=True)


from obspy.clients.fdsn import Client
from obspy import UTCDateTime
cl = Client('IRIS')
catalog = cl.get_events(starttime=UTCDateTime('1980-01-01'),
              endtime=UTCDateTime('2025-03-01'),
              minlongitude=-122.3,
              maxlongitude=-121.19,
              minlatitude=46.5,
              maxlatitude=47.1,
              minmagnitude=1)


x = []
y = []
sizes = []
for i, event in enumerate(catalog):
    x.append(event.preferred_origin().longitude)
    y.append(event.preferred_origin().latitude)
    sizes.append(0.055 * (event.preferred_magnitude().mag ** 1.45))

seis_fig.plot(x=x,
              y=y,
              size=sizes,
              style='cc',
              fill='orange',
              transparency=35,
              pen='0.5p,black')

from scipy.interpolate import CubicSpline, splprep, splev
import numpy as np
wrszx_e = [-121.87,-121.84,-121.69,-121.61]
wrszy_e = [46.97,46.73,46.64,46.59]

wrszx_e = [-121.84,-121.84,-121.67]
wrszy_e = [46.97,46.73,46.56]

tck, u = splprep([wrszx_e, wrszy_e], k=2, s=0)

# Generate points along the curve
t_new = np.linspace(0, 1, 25)
x_smooth_bspline, y_smooth_bspline = splev(t_new, tck)


seis_fig.plot(x=x_smooth_bspline,
              y=y_smooth_bspline,
              pen="2p,black,-")  # 2 point thickness, red color, dashed line

#==============================================================================
wrszx_w = [-122.06,-122.06,-121.93]
wrszy_w = [47,46.87,46.52]
tck, u = splprep([wrszx_w, wrszy_w], k=2, s=0)

# Generate points along the curve
t_new = np.linspace(0, 1, 25)
x_smooth_bspline, y_smooth_bspline = splev(t_new, tck)

seis_fig.plot(x=x_smooth_bspline,
              y=y_smooth_bspline,
              pen="2p,black,-")  # 2 point thickness, red color, dashed line

#=====================================================================
seis_fig.plot(x=-121.76,
              y=46.852,
              style='t1c',
              fill='red',
              pen='black')

seis_fig.show()
gm.save_fig(seis_fig,'RainierSeismicity',dpi=960)

"""
# Plotting a narrower regional interview
rainier_region_fig = ms.plot_stations(station_inv,
                                      figure_name="Rainier Region Seismic Stations",
                                      cmap=cmap,
                                      box_bounds=studyAreaBounds,
                                      bathymetry=True,
                                      resolution='03s')

rainier_region_fig.show()
gm.save_fig(rainier_region_fig,"Regional_Stations")

# Plotting the bounding box
local_fig = ms.plot_stations(station_inv,region=studyAreaBounds,
                             figure_name="Stations within Bounding Box",
                             cmap=cmap,
                             box_bounds=studyAreaBounds,
                             bathymetry=True,
                             resolution='03s')

local_fig.show()
gm.save_fig(local_fig,"Local_View_Stations")
"""
