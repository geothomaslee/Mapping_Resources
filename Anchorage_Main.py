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
region_bounds = [-152.3,-147.7,60.3,62.1]
projection = 'J-65/12c'

station_inv = ms.find_multi_network(deployment_list,region_bounds)

# Creating a nice colormap
cmap = cu.create_combined_color_map('usgs','colombia',max_elev=1000,max_depth=-1500)

# Plotting a regional overview
anchorage_region_fig = ms.plot_stations(station_inv,
                                        figure_name="Anchorage Strong-Motion Network",
                                        box_bounds=region_bounds,
                                        resolution="06s",
                                        cmap=cmap,
                                        margin=0.1,
                                        bathymetry=True,
                                        projection=projection)

anchorage_region_fig.show()
                                     