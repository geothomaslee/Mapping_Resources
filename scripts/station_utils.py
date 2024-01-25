#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 10:02:18 2024

@author: thomaslee
"""

import pandas as pd
import obspy

def get_station_df(inventory):
    """
    Parameters
    ----------
    inventory : obspy.core.inventory.Inventory
        ObsPy station inventory.

    Returns
    -------
    stat_df : pandas.DataFrame
        DataFrame containing the station info. To get a CSV, use 
        station_utils.get_station_csv

    """
    networks = []
    stations = []
    start_dates = []
    end_dates = []
    latitudes = []
    longitudes = []


    for network in inventory:
        for station in network:
            networks.append(network.code)
            stations.append(station.code)
            start_dates.append(station.start_date)
            
            end_date = station.end_date
            if end_date:
                end_dates.append(end_date)
            else:
                end_dates.append('Current')
                
            latitudes.append(station.latitude)
            longitudes.append(station.longitude)


    stat_dict = {'Network' : networks, 'Station' : stations,
                 'Latitudes' : latitudes, 'Longitudes' : longitudes,
                 'Start Date' : start_dates, 'End Date' : end_dates}

    stat_df = pd.DataFrame(stat_dict)

    return stat_df


def get_station_csv(inventory,filename='Stations.csv'):
    """
    Parameters
    ----------
    inventory : obspy.core.inventory.Inventory
        ObsPy station inventory.
    filename : string, optional
        Name of CSV. The default is 'Stations.csv'.

    Returns
    -------
    None.

    """
    networks = []
    stations = []
    start_dates = []
    end_dates = []
    latitudes = []
    longitudes = []


    for network in inventory:
        for station in network:
            networks.append(network.code)
            stations.append(station.code)
            start_dates.append(station.start_date)
            
            end_date = station.end_date
            if end_date:
                end_dates.append(end_date)
            else:
                end_dates.append('Current')
                
            latitudes.append(station.latitude)
            longitudes.append(station.longitude)


    stat_dict = {'Network' : networks, 'Station' : stations,
                 'Latitudes' : latitudes, 'Longitudes' : longitudes,
                 'Start Date' : start_dates, 'End Date' : end_dates}

    stat_df = pd.DataFrame(stat_dict)
    stat_df.to_csv(filename)
    
    
def station_availability_from_df(df):
    if type(df) != pd.DataFrame:
        raise TypeError('Expected pandas.DataFrame object as input')
    else:
        print(f'Read DataFrame with length {len(df)}')
        
    

