#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 10:02:18 2024

@author: thomaslee
"""

import obspy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
from obspy import UTCDateTime
from datetime import datetime, timezone
from matplotlib.patches import Rectangle, PathPatch
from matplotlib.text import TextPath


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


def plot_station_availability(station_avail_df,interval_width=75,textsize=None,
                              highlighted_intervals=None,interval_color='gray',interval_alpha=0.2,
                              label_offset=0.03,label_network=None,bracket_vert_offset=0.32):
    
    if highlighted_intervals:
        if type(highlighted_intervals) != list:
            raise TypeError('Highlighted_intervals must be a list of lists (1)')
        for interval in highlighted_intervals:
            if type(interval) != list:
                raise TypeError('Highlighted_intervals must be a list of lists')
            if len(interval) != 2:
                raise ValueError('Lists in highlighted_intervals must have length 2 and be date ranges')
            if interval[1] < interval[0]:
                raise ValueError('x2 must be > x1 for intervals')
            
    
    if textsize == None:
        textsize = interval_width / 4
    
    years = station_avail_df['Year'].tolist()
    months = station_avail_df['Month'].tolist()
    
    times = []
    for i, year in enumerate(years):
        month = months[i]
        decimal_year = year + (month/12)
        times.append(decimal_year)
        
    networks = station_avail_df.columns.values.tolist()[2:-1]
    
    # Sorting the networks by their max station count
    max_counts = []
    for network in networks:
        max_counts.append(max(station_avail_df[network].tolist()))
    
    sorted_max_counts = np.array(max_counts)
    sort_index = np.argsort(max_counts)
    
    sorted_networks = []
    for index in sort_index:
        sorted_networks.append(networks[index])
        
    networks = sorted_networks
    date_range = times[-1] - times[0]
        
    fig, ax = plt.subplots(figsize=(20,10))
    all_interval_dict = {}
    for j,network in enumerate(networks):
        avail_counts = station_avail_df[network].tolist()
        interval_dict = {}
        prev_val = 0
        first_row = True
        for i,time in enumerate(times):
            avail = avail_counts[i]
            
    
            if first_row:
                if avail != 0: # Don't create the first row if it's 0
                    int_num = len(interval_dict) + 1
                    interval_dict[f'int{int_num}'] = [time,avail]
                    first_row = False
            else: # If we haven't already created the first row
                if avail == prev_val:
                    pass # Skip if the count doesn't change
                else:
                    int_num = len(interval_dict)
                    interval_dict[f'int{int_num}'].append(time) # Adds current time as end of previous step
                    
                    int_num = len(interval_dict) + 1
                    interval_dict[f'int{int_num}'] = [time,avail]
                    
            prev_val = avail
            
        interval_dict[list(interval_dict.keys())[-1]].append(times[-1])
        
        all_interval_dict[network] = interval_dict # Storing the interval dict for each network in a dict
                    

        anchor_level = interval_width * j + 10
        dash_x = [times[0],times[-1]]
        dash_y = [anchor_level,anchor_level]
        ax.plot(dash_x,dash_y,linestyle='--',linewidth=0.25,color='Black')
        
        for interval in interval_dict:
            interval_info = interval_dict[interval]
            startdate = interval_dict[interval][0]
            count = interval_dict[interval][1]
            enddate = interval_dict[interval][2]
            
            y_anchor = anchor_level - (0.5*count)
            xy = [startdate,y_anchor]
            width = enddate-startdate
            height = count
            rect = Rectangle(xy,width,count,facecolor='Black',zorder=2)
            
            ax.add_patch(rect)
            
        ax.text(times[0] - date_range*label_offset, anchor_level, network,fontsize=textsize)
        
    if label_network == None:
        # Figuring out which network has the least variation over time, will be
        # used later to add a scale bar to that station
        vary_dict = {}
        for network in networks:
            counts = station_avail_df[network].tolist()
            counts = [i for i in counts if i != 0]
            mean = np.mean(counts)
            max_count = max(counts)
            min_count = min(counts)
            
            vary_score = np.mean([abs(mean-max_count),abs(mean-min_count)])
            vary_dict[network] = vary_score
            
        # Finding the minimum variation, then selecting stations with similarly 
        # low variations
        min_vary = min(vary_dict.values())
        networks_low_vary = [k for k,v in vary_dict.items() if float(v) <= 2*min_vary]
        
        best_network = networks_low_vary[0]
        best_network_val = max(station_avail_df[best_network].tolist())
        for network in networks_low_vary:
            if max(station_avail_df[network].tolist()) > best_network_val:
                best_network = network
                best_network_val = max(station_avail_df[network].tolist())
                
        label_network = best_network
            
    scale_anchor_level = (networks.index(label_network) * interval_width) + 10
    
    counts = station_avail_df[label_network].tolist()
    x = all_interval_dict[label_network][list(interval_dict.keys())[0]][0] - 0.05*date_range
    y = scale_anchor_level - bracket_vert_offset*max(counts)
    scale = max(counts)
    
    tp = TextPath((0, 0), "{", size=1)
    trans = mtrans.Affine2D().scale(1, scale) + \
    mtrans.Affine2D().translate(x,y) + ax.transData
    pp = PathPatch(tp, lw=0, fc="k", transform=trans)
    ax.add_artist(pp)
    
    for interval in highlighted_intervals:
        ax.axvspan(interval[0],interval[1],color=interval_color,alpha=interval_alpha)
    

    ax.text(x - (3*label_offset*date_range),scale_anchor_level-(0.25*bracket_vert_offset*max(counts)),f'{max(station_avail_df[label_network].tolist())} stations',
            fontsize=textsize)
        
    ax.set_title('Station Availability Over Time',fontsize=textsize)
    
    ax.set_ylim(0,interval_width*len(networks))  
    ax.get_yaxis().set_visible(False)
    
    ax.set_xlim(times[0],times[-1])       
    ax.tick_params(axis='x',labelsize=textsize)
    fig.show()
        
        
                
                
                
        
        
    
                
    
                
            
            
    
    
        
    
        
        
    
        
    

