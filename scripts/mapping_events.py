# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 08:35:58 2023

@author: tlee4
"""

import pygmt
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
import scripts.general_mapping as gm

def plot_events(starttime: str,
                endtime: str,
                minlon: float,
                maxlon: float,
                minlat: float,
                maxlat: float,
                minmag: float,
                lin_scale: float=0.055,
                exp_scale: float=1.45,
                fill: str='orange',
                fig=None,
                **kwargs):
    """
    Plots earthquakes on a PyGMT figure. The formula for the scaling of the
    point sizes is lin_scale * (magnitude ^ exp_scale). Increasing exp_scale
    will increase the size disparity between different size events, lin_scale
    will linearly expand or shrink all sizes equally.

    Parameters
    ----------
    starttime : str
        DESCRIPTION.
    endtime : str
        DESCRIPTION.
    minlon : float
        DESCRIPTION.
    maxlon : float
        DESCRIPTION.
    minlat : float
        DESCRIPTION.
    maxlat : float
        DESCRIPTION.
    minmag : float
        DESCRIPTION.
    lin_scale : float, optional
        DESCRIPTION. The default is 0.055.
    exp_scale : float, optional
        DESCRIPTION. The default is 1.45.
    fig : TYPE, optional
        DESCRIPTION. The default is None.
    **kwargs : see general_mapping.plot_base_map
        Arguments to be passed to the base map.

    Returns
    -------
    fig : TYPE
        DESCRIPTION.

    """
    if fig is None:
        fig = gm.plot_base_map(**kwargs)

    cl = Client('USGS')

    catalog = cl.get_events(starttime=UTCDateTime(starttime),
                  endtime=UTCDateTime(endtime),
                  minlongitude=minlon,
                  maxlongitude=maxlon,
                  minlatitude=minlat,
                  maxlatitude=maxlat,
                  minmagnitude=minmag)
    print(catalog.__str__(print_all=True))

    print(f'{len(catalog)} events found')

    x = []
    y = []
    sizes = []
    for i, event in enumerate(catalog):
        x.append(event.preferred_origin().longitude)
        y.append(event.preferred_origin().latitude)
        sizes.append(lin_scale * (event.preferred_magnitude().mag ** exp_scale))

    fig.plot(x=x,
             y=y,
             size=sizes,
             style='cc',
             fill=fill,
             transparency=35,
             pen='0.5p,black')

    return fig
