#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 10:02:18 2024

@author: thomaslee
"""

import pandas as pd
import obspy
from obspy import UTCDateTime
from datetime import datetime, timezone


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
                end_dates.append(UTCDateTime(datetime.now(timezone.utc)))
                
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
                end_dates.append(UTCDateTime(datetime.now(timezone.utc)))
                
            latitudes.append(station.latitude)
            longitudes.append(station.longitude)


    stat_dict = {'Network' : networks, 'Station' : stations,
                 'Latitudes' : latitudes, 'Longitudes' : longitudes,
                 'Start Date' : start_dates, 'End Date' : end_dates}

    stat_df = pd.DataFrame(stat_dict)
    stat_df.to_csv(filename)
    
    
def station_availability_from_df(df,startdate,enddate=None):
    if type(df) != pd.DataFrame:
        raise TypeError('Expected pandas.DataFrame object as input')
    else:
        print(f'Read DataFrame with length {len(df)}')   
        

    if type(startdate) == obspy.core.utcdatetime.UTCDateTime:
        pass
    elif type(startdate) == str:
        startdate = UTCDateTime(startdate)
    else:
        raise TypeError('Startdate must be a UTCDateTime object or string')
        
    if type(enddate) == obspy.core.utcdatetime.UTCDateTime:
        pass
    elif type(enddate) == str:
        enddate = UTCDateTime(enddate)
    elif enddate == None:
        print('No end date specified, using current time as end date')
        enddate = UTCDateTime(datetime.now(timezone.utc))
    else:
        raise TypeError('End date must be a UTCDateTime object or string, or None to use current time')
        
    num_years = enddate.year - startdate.year
    
  
    time_bins = []
    
    years_list = []
    months_list = []

    for relative_year in range(num_years):
        year = startdate.year + relative_year
        for month in range(1, 13, 1):
            time_bin = (year, month)
            time_bins.append(time_bin)
            years_list.append(year)
            months_list.append(month)
         
    # Create a list of networks
    network_list = df.Network.unique()
    
    # Create a dictionary with time bins as keys and counter dict for that bin
    # as the values
    monthly_network_count = {}
    for time_bin in time_bins:
        monthly_network_count[time_bin] = None
            
    
    for i, time_bin in enumerate(time_bins):
        
        # Reset the network counter so all networks are at 0
        network_count = {}
        for network in network_list:
            network_count[network] = [0]
        network_count['Total Stations'] = [0]
        
        year = time_bin[0]
        month = time_bin[1]
       
        # Determine the station count for each network and put it into a dict        
        for index in range(len(df)):
            startyear = df['Start Date'][index].year
            startmonth = df['Start Date'][index].month
            endyear = df['End Date'][index].year
            endmonth = df['End Date'][index].month
            
            station = df['Station'][index]
            network = df['Network'][index]
            
            if (year - startyear) < 0:
                _inbin_ = False
            elif (year - startyear) == 0 and (month - startmonth) <0:
                _inbin_ = False
            elif (year - endyear) > 0:
                _inbin_ = False
            elif (year - endyear) == 0 and (month - endmonth) > 0 :
                _inbin_ = False
            else:
                _inbin_ = True
                
            if _inbin_ == True:
                network_count[network][0]+=1
                network_count['Total Stations'][0]+= 1
            if _inbin_ == False:
                pass
                    
        if i == 0:
            df_station_count = pd.DataFrame.from_dict(network_count)
        else:
            df_station_row = pd.DataFrame.from_dict(network_count)
            _combine_ = [df_station_count, df_station_row]
            df_station_count = pd.concat(_combine_)
    
    df_station_count.insert(0,"Year",years_list)
    df_station_count.insert(1,"Month",months_list)
    
    return df_station_count
                
    
                
            
            
    
    
        
    
        
        
    
        
    

