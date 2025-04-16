# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 10:01:14 2025

@author: tlee
"""

from scripts import general_mapping as gm
from scripts import colormap_utils as cu

cmap = cu.create_combined_color_map('usgs','colombia',max_elev=2500,max_depth=-5000)
reg = gm.plot_base_map(region=[22.5, 28.5, 34, 39],
                       resolution='03s',
                       projection='M25.5/37.5/12c',
                       figure_name='Santorini',
                       cmap=cmap,
                       bathymetry=True)

reg = gm.plot_holocene_volcanoes(reg,size=0.7)

gm.save_fig(reg, 'Santorini',dpi=960)