# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 14:45:59 2024

@author: tlee4
"""

import scripts.mapping_stations as ms
import scripts.general_mapping as gm


akutan_region = [-167.8, -162.6, 53, 54.9]

projection = 'J-65/12c'

akutan_regional_fig = gm.plot_base_map(akutan_region,projection=projection,
                                       figure_name='Akutan_Region',
                                       cmap="./Resources/colormaps/pnw_1113_test.cpt",
                                       bathymetry=False)

akutan_regional_fig = gm.plot_holocene_volcanoes(akutan_regional_fig)

akutan_regional_fig = gm.plot_label(akutan_regional_fig,54.136,-165.96,
                                    label='Akutan Volcano',offset=0.05)

akutan_regional_fig.show()


"""

aleutian_region = [-170, -140, 52, 65]
projection = 'J-65/12c'

aleutian_regional_fig = gm.plot_base_map(aleutian_region,projection=projection,
                                         figure_name='Akutan_Region',resolution='03m')

aleutian_regional_fig = gm.plot_holocene_volcanoes(aleutian_regional_fig)

aleutian_regional_fig = gm.plot_major_cities(aleutian_regional_fig)

aleutian_regional_fig.show()

"""

