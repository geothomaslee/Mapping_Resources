# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:05:02 2023

@author: tlee
"""

import scripts.mapping_stations as ms
import scripts.general_mapping as gm
import pandas as pd

deployment_list = [["UW","2015-01-01","2017-12-31"],["XU","2007-01-01","2011-12-31"],
                   ["XD","2014-01-01","2016-12-31","M*"],["TA","2006-01-01","2023-11-6"],
                   ["CC","2020-10-22","2023-11-7"],["YH","2016-01-01","2016-12-31"]]

region_bounds = [-122.5, -120.5, 45, 47.25]
box_bounds = [-122.5, -120.9, 46.1, 47.3]

station_inv = ms.find_multi_network(deployment_list,region_bounds)

""" Code For Saving The Stations Into a CSV for Book-Keeping Purposes
station_dict = station_inv.get_contents()
stations_only_dict = station_dict['stations']
export_station_dict = {'Stations' : stations_only_dict}
export_station_df = pd.DataFrame(export_station_dict)
export_station_df.to_csv('Stations_To_Correlate_List.csv')
"""

# Plotting a regional overview
regional_fig = ms.plot_stations(station_inv,
                                figure_name="Rainier Region Seismic Stations",
                                box_bounds=box_bounds,
                                resolution="15s",
                                margin=1)

regional_fig = gm.plot_major_cities(regional_fig,minpopulation=200000,
                                    close_threshhold=0.01,offset=0.03,
                                    dotsize=0.25,hor_offset_multiplier=3.5)
regional_fig.show()

gm.save_fig(regional_fig,"PNW Regional Overview")

# Plotting a narrower regional interview        
rainier_region_fig = ms.plot_stations(station_inv,
                                      figure_name="Rainier Region Seismic Stations",
                                      box_bounds=box_bounds)
                       
rainier_region_fig.show()
gm.save_fig(rainier_region_fig,"Regional_Stations")

# Plotting the bounding box
local_fig = ms.plot_stations(station_inv,region=box_bounds,
                             figure_name="Stations within Bounding Box",
                             box_bounds=box_bounds)
                        
local_fig.show()
gm.save_fig(local_fig,"Local_View_Stations")

