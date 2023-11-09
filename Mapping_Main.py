# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:05:02 2023

@author: tlee
"""

import scripts.mapping_stations as ms


deployment_list = [["UW","2015-01-01","2017-12-31"],["XU","2007-01-01","2011-12-31"],
                   ["XD","2014-01-01","2016-12-31","M*"],["TA","2006-01-01","2023-11-6"],
                   #["YW","2005-08-11","2005-12-31"],
                   ["CC","2020-10-22","2023-11-7"],["NP","2013-01-01","2013-01-02"]
                   ]

region_bounds = [-122, -120.5, 45.6, 47.25]
box_bounds = [-122, -121, 46.35, 47.1]

station_inv = ms.find_multi_network(deployment_list,region_bounds)

fig = ms.plot_stations(station_inv,
                       figure_name="Rainier Region Seismic Stations",
                       box_bounds=box_bounds)
                    
fig.show()
ms.save_fig(fig,"Regional_Stations")

fig2 = ms.plot_stations(station_inv,region=box_bounds,
                        figure_name="Stations within Bounding Box",
                        box_bounds=box_bounds)
                       
                     
fig2.show()
ms.save_fig(fig2,"Local_View_Stations")