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
                fig=None,
                **kwargs):
    if fig is None:
        fig = gm.plot_base_map(**kwargs)

    cl = Client('IRIS')

    catalog = cl.get_events(starttime=UTCDateTime('1980-01-01'),
                  endtime=UTCDateTime('2025-03-01'),
                  minlongitude=minlon,
                  maxlongitude=maxlon,
                  minlatitude=minlat,
                  maxlatitude=maxlat,
                  minmagnitude=minmag)


    x = []
    y = []
    sizes = []
    for i, event in enumerate(catalog):
        x.append(event.preferred_origin().longitude)
        y.append(event.preferred_origin().latitude)
        sizes.append(0.055 * (event.preferred_magnitude().mag ** 1.45))

    fig.plot(x=x,
             y=y,
             size=sizes,
             style='cc',
             fill='orange',
             transparency=35,
             pen='0.5p,black')

    return fig
