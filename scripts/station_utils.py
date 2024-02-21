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
import matplotlib.pyplot as plt


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
    channels = []


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
            
            if len(station.channels) == 1:
                channels.append(station.channels[0].code)
            else:
                code_list = []
                for channel_index in range(len(station.channels)):
                    code = station.channels[channel_index].code
                    code_list.append(code)
                channels.append(code_list)
                    


    stat_dict = {'Network' : networks, 'Station' : stations,
                 'Latitudes' : latitudes, 'Longitudes' : longitudes,
                 'Start Date' : start_dates, 'End Date' : end_dates,
                 'Channels' : channels}

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
    channels = []


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
            channels.append(station.channels)


    stat_dict = {'Network' : networks, 'Station' : stations,
                 'Latitudes' : latitudes, 'Longitudes' : longitudes,
                 'Start Date' : start_dates, 'End Date' : end_dates,
                 'Channels' : channels}

    stat_df = pd.DataFrame(stat_dict)
    stat_df.to_csv(filename)
    
    
def station_availability_from_df(df,startdate,enddate=None):
    """
    Finds the number of stations available over time given a Data Frame created
    by get_station_df. Outputs the information into a DataFrame and creates a
    plot showing the stations available over time
    
    Parameters
    ----------
    df : pandas.DataFrame
        Data Frame containing relevant station information, intended to be used
        with DFs created by station_utils.get_station_df.
    startdate : obspy.core.utcdatetime.UTCDateTime or string
        Start date, either as a UTCDateTime object or a string that can be
        converted to one by UTCDateTime
    enddate : obspy.core.utcdatetime.UTCDateTime or string, optional
        End date, either as a UTCDateTime object or a string that can be
        converted to one by UTCDateTime. If none is set, then the current time
        will be used as the end date.

    Returns
    -------
    df_station_count : pandas.DataFrame
        DataFrame containing the station count per network, and overall, for
        every given month and year.
    """
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
    start_month = startdate.month
    start_year = startdate.year
  
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
            
    datetime_bin_list = []
    for i, time_bin in enumerate(time_bins):
        
        # Reset the network counter so all networks are at 0
        network_count = {}
        for network in network_list:
            network_count[network] = [0]
        network_count['Total Stations'] = [0]
        
        year = time_bin[0]
        month = time_bin[1]

        # Create the months as UTCDateTime objects so that they can be plotted
        # Later with actual time stamps
        """
        if month < 10:
            time_string = str(year) + ',' + '0' + str(month) + ',01,00:00:00'
        else:
            time_string = str(year) + ',' + str(month) + ',01,00:00:00' 
        """
        datetime_bin_list.append(datetime(year, month, 1, 0, 0))
       
        # Determine the station count for each network and put it into a dict        
        for index in range(len(df)):
            startyear = df['Start Date'][index].year
            startmonth = df['Start Date'][index].month
            endyear = df['End Date'][index].year
            endmonth = df['End Date'][index].month
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
        # Putting it into a DataFrame to export as CSV and easier plotting
        if i == 0:
            df_station_count = pd.DataFrame.from_dict(network_count)
        else:
            df_station_row = pd.DataFrame.from_dict(network_count)
            _combine_ = [df_station_count, df_station_row]
            df_station_count = pd.concat(_combine_,ignore_index=True)
    
    df_station_count.insert(0,"Year",years_list)
    df_station_count.insert(1,"Month",months_list)
    
    count_list = []
    for months_since_start in range(len(df_station_count)):
        total_stations = df_station_count['Total Stations'][months_since_start]
        count_list.append(total_stations)
        
    # Plotting the stations available over time    
    fig, ax = plt.subplots(dpi=200)
    ax.plot(datetime_bin_list,
            count_list)
    ax.set(ylabel='Online Station Count',
           title='Stations Available Over Time')
    
    plt.savefig(fname='Station_Availability_Over_Time.png')
    plt.show()
        
    return df_station_count
                
    
                
            
            
    
    
        
    
        
        
    
        
    

