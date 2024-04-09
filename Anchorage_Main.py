# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import scripts.general_mapping as gm
import scripts.mapping_stations as ms
import scripts.station_utils as su
import scripts.colormap_utils as cu



deployment_list = [['NP','2002-01-01','2024-01-01']]
region_bounds = [-150.4,-148,60.6,61.9]

station_inv = ms.find_multi_network(deployment_list,region_bounds)

# Plotting a local overview
cmap = cu.create_combined_color_map('usgs','colombia',max_elev=4500,max_depth=-1000)
local_projection = 'J-65/12c'
anchorage_local_fig = ms.plot_stations(station_inv,
                                        figure_name="Anchorage Strong-Motion Network",
                                        box_bounds=region_bounds,
                                        region=region_bounds,
                                        resolution="15s",
                                        cmap=cmap,
                                        margin=0.1,
                                        bathymetry=True,
                                        projection=local_projection)

anchorage_local_fig.show()

# Plotting a regional overview
cmap = cu.create_combined_color_map('usgs','colombia',max_elev=4000,max_depth=-6000)
regional_projection = 'J-65/12c'
anchorage_regional_fig = gm.plot_base_map(region=region_bounds,
                                          projection=regional_projection,
                                          figure_name='Study Area Within Alaska, USA',
                                          box_bounds=region_bounds,
                                          margin=5,
                                          cmap=cmap,
                                          resolution='03m',
                                          bathymetry=True)

anchorage_regional_fig = gm.plot_major_cities(anchorage_regional_fig,minpopulation=20000,
                                              offset=0.09)


anchorage_regional_fig.show()
                                     