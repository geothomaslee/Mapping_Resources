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
                color_by_date: bool=False,
                debug: bool=False,
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
        Start time for earthquake query.
    endtime : str
        End time for earthquake query.
    minlon : float
        Minimum longitude.
    maxlon : float
        Maximum longitude.
    minlat : float
        Minimum latitude.
    maxlat : float
        Maximum latitude.
    minmag : float
        Minimum magnitude.
    lin_scale : float, optional
        Linear scaling factor for symbol sizes. The default is 0.055.
    exp_scale : float, optional
        Exponential scaling factor for symbol sizes. The default is 1.45.
    fill : str, optional
        Fill color when color_by_date is False. The default is 'orange'.
    color_by_date : bool, optional
        If True, colors symbols by date with a colorbar. The default is False.
    debug : bool, optional
        Print detailed catalog information. The default is False.
    fig : pygmt.Figure, optional
        Existing figure to plot on. The default is None.
    **kwargs :
        Arguments to be passed to the base map (see general_mapping.plot_base_map).

    Returns
    -------
    fig : pygmt.Figure
        The figure with plotted earthquakes.
    """
    import pygmt
    import numpy as np
    from datetime import datetime

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

    if debug:
        print(catalog.__str__(print_all=True))
    print(f'{len(catalog)} events found')

    x = []
    y = []
    sizes = []
    dates = []

    for i, event in enumerate(catalog):
        x.append(event.preferred_origin().longitude)
        y.append(event.preferred_origin().latitude)
        sizes.append(lin_scale * (event.preferred_magnitude().mag ** exp_scale))

        if color_by_date:
            # Get datetime object and convert to timestamp (days since epoch)
            dt = event.preferred_origin().time.datetime
            # Convert to days since Unix epoch for PyGMT
            timestamp = dt.timestamp() / 86400  # seconds to days
            dates.append(timestamp)

    if color_by_date and len(dates) > 0:
        # Convert dates to decimal years for cleaner colorbar labels
        dates_years = []
        for i, event in enumerate(catalog):
            dt = event.preferred_origin().time.datetime
            # Convert to decimal year (e.g., 2024.5 for July 1, 2024)
            year = dt.year
            start_of_year = datetime(year, 1, 1)
            days_in_year = 366 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 365
            day_of_year = (dt - start_of_year).days + (dt - start_of_year).seconds / 86400
            decimal_year = year + day_of_year / days_in_year
            dates_years.append(decimal_year)

        # Convert to numpy array for colormap
        dates_array = np.array(dates_years)

        # Create colormap range
        min_year = dates_array.min()
        max_year = dates_array.max()

        # Create a NEW CPT specifically for the earthquake dates
        # This prevents conflicts with the topography CPT
        pygmt.makecpt(cmap='viridis', series=[min_year, max_year])

        # Plot with color based on date
        fig.plot(x=x,
                 y=y,
                 size=sizes,
                 style='cc',
                 fill=dates_years,
                 cmap=True,  # Use the current CPT
                 transparency=35,
                 pen='0.5p,black')

        # Add colorbar at the bottom with year labels
        # Annotate every 2 years
        fig.colorbar(
            position="JBC+w12c/0.5c+h",  # Bottom center, horizontal
            frame=["xa2f1+lYear"],  # Annotate every 2 years, tick every 1 year
            box="+gwhite+p0.5p",
        )

    else:
        # Original behavior - solid color
        fig.plot(x=x,
                 y=y,
                 size=sizes,
                 style='cc',
                 fill=fill,
                 transparency=35,
                 pen='0.5p,black')

    return fig