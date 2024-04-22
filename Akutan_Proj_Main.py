# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 14:45:59 2024

@author: tlee4
"""

import scripts.general_mapping as gm
import scripts.mapping_gps as mg
import scripts.colormap_utils as cu
from glob import glob
import os

akutan_region = [-167.8, -162.6, 53.2, 55.1]
akutan_island_bounds = [-166.1464,-165.6164,54.0402,54.2301]
projection = 'J-65/12c'
        
#-----------------------------------

filelist = glob(os.path.expanduser('~/Documents/Xue_Data/gps/Akutan_Stations/*'))

if len(filelist) == 0:
    raise ValueError('No files found')
station_df = mg.make_gps_station_df(filelist)

"""
disps = mg.make_gps_station_displacement_df_degrandpre(filelist,starttime=2009,endtime=2013.5)


cmap = cu.create_combined_color_map('usgs','colombia',max_elev=2000,max_depth=-1000)
akutan_island_fig = gm.plot_base_map(akutan_island_bounds,projection=projection,
                                     resolution='03s',cmap=cmap,figure_name='Akutan Island',
                                     bathymetry=True, colorbar_tick=500)

akutan_island_fig = mg.plot_displacement_vectors_degrandpre(akutan_island_fig,
                                                            disps,scaling_factor=10000000)

akutan_island_fig.show()




#akutan_island_fig = mg.plot_gps_velocity_vectors(akutan_island_fig,station_df,
                                                 #vel_dict)
                                                 
"""
#------------------------------------
cmap = cu.create_combined_color_map('usgs','colombia',max_elev=6000,max_depth=-8000)
aleutian_region_fig = gm.plot_base_map(region=akutan_region,
                                       projection=projection,
                                       cmap=cmap,
                                       figure_name='Aleutian Islands Region',
                                       margin=3.5,
                                       resolution='30s',
                                       box_bounds=akutan_region,
                                       bathymetry=True)

aleutian_region_fig = gm.plot_holocene_volcanoes(aleutian_region_fig)


aleutian_region_fig.show()


#------------------------------------

cmap = cu.create_combined_color_map('usgs','colombia',max_elev=1500,max_depth=-7000)
akutan_regional_fig = gm.plot_base_map(akutan_region,projection=projection,
                                       figure_name='Akutan Region',
                                       cmap=cmap, bathymetry=True)

akutan_regional_fig = gm.plot_holocene_volcanoes(akutan_regional_fig)

akutan_regional_fig = gm.plot_label(akutan_regional_fig,54.136,-165.96,
                                    label='Akutan Volcano',offset=0.05)

akutan_regional_fig.show()

#-------------------------------------
"""

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
