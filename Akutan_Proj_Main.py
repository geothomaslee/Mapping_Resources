# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 14:45:59 2024

@author: tlee4
"""

import scripts.general_mapping as gm
import scripts.mapping_gps as mg
import scripts.colormap_utils as cu

akutan_region = [-167.8, -162.6, 53.2, 55.1]
akutan_island_bounds = [-166.1464,-165.6164,54.0402,54.2301]
projection = 'J-65/12c'
        
#-----------------------------------

ak_dir =  '~/Documents/Grad School/Spring 2024/PHYS581/Alaska_Project/Xue_Data/gps'
stat_files = mg.find_files_in_bounds(ak_dir,akutan_island_bounds,'.pfiles')
stat_df = mg.make_gps_station_df(stat_files)

cmap = cu.create_combined_color_map('usgs','colombia',max_elev=2000,max_depth=-1000)
akutan_island_fig = gm.plot_base_map(akutan_island_bounds,projection=projection,
                                     resolution='03s',cmap=cmap,figure_name='Akutan Island',
                                     bathymetry=True, colorbar_tick=500)

akutan_island_fig = mg.plot_gps_displacement_vectors(akutan_island_fig,stat_df,
                                                     scaling_factor=1000000)

#akutan_island_fig = mg.plot_gps_stations(akutan_island_fig,stat_df)

akutan_island_fig.show()

"""
#------------------------------------

cmap = cu.create_combined_color_map('usgs','colombia',max_elev=2000,max_depth=-8000)
akutan_regional_fig = gm.plot_base_map(akutan_region,projection=projection,
                                       figure_name='Akutan Region',
                                       cmap=cmap, bathymetry=True)

akutan_regional_fig = gm.plot_holocene_volcanoes(akutan_regional_fig)

akutan_regional_fig = gm.plot_label(akutan_regional_fig,54.136,-165.96,
                                    label='Akutan Volcano',offset=0.05)

akutan_regional_fig.show()

#-------------------------------------

cmap = cu.create_combined_color_map('usgs','colombia',max_elev=6000,max_depth=-8000)
aleutian_region = [-170, -140, 52, 65]
projection = 'J-65/12c'

aleutian_regional_fig = gm.plot_base_map(aleutian_region,projection=projection,
                                         figure_name='Alaska',resolution='03m',
                                         cmap=cmap,bathymetry=True)

aleutian_regional_fig = gm.plot_holocene_volcanoes(aleutian_regional_fig)

aleutian_regional_fig = gm.plot_major_cities(aleutian_regional_fig,offset=0.05)

aleutian_regional_fig.show()
"""

