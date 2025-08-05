# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 08:59:12 2025

@author: tlee
"""
import pygmt
import os
from scripts import general_mapping as gm
from scripts import mapping_events as me
from scripts import colormap_utils as cu


#=============================Regional Overview================================
cmap = cu.create_combined_color_map('usgs','colombia',max_elev=6200,max_depth=-6000)

reg = me.plot_events(starttime='1960-01-01',
                     endtime='2025-04-01',
                     minlon=-178,
                     maxlon=-138,
                     minlat=50,
                     maxlat=62,
                     minmag=7.5,
                     lin_scale=0.00004,
                     exp_scale=4.75,
                     fill='red',
                     region=[-178,-138,50,63],
                     projection='M-158/56.5/12c',
                     figure_name='Earthquakes >M6, 1960-2025',
                     resolution='30s',
                     cmap=cmap,
                     bathymetry=True)

reg.coast(borders=1)
reg.plot(x=-143.5,
         y=54,
         style="v1c+e+h0.5",
         direction=([111.5],[2.5]),
         pen="2p",
         fill="blue")

reg.text(text='46.9 mm/yr',
         x=-142,
         y=52.8,
         font='12p,Helvetica-Bold,black',
         fill='white@15')

reg.text(text='NORTH AMERICAN PLATE',
         x=-169.25,
         y=59.4,
         font='10p,Helvetica-Bold,black')

reg.text(text='PACIFIC PLATE',
         x=-165,
         y=50,
         font='10p,Helvetica-Bold,white')

reg = gm.plot_major_cities(reg,
                           symbol='a',
                           minpopulation=100000,
                           offset=0.08,
                           size=0.75,
                           color='yellow',
                           hor_offset_multiplier=2)

reg.show()
gm.save_fig(reg,name='AlaskaRegion',dpi=1280)

# Local Overview
