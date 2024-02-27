# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 14:09:01 2024

@author: tlee4
"""

import os
import pandas as pd
from glob import glob
import numpy as np
import shutil
import matplotlib.pyplot as plt
import pyproj


def find_files_in_bounds(directory,bounds,filetype=None):
    min_lon = bounds[0]
    max_lon = bounds[1]
    min_lat = bounds[2]
    max_lat = bounds[3]

    
    dir_path = os.path.expanduser(directory)
    if not os.path.isdir(dir_path):
        raise ValueError('Could not find directory')
        
    if not filetype:
        print('No file type specified, will attempt to read any files in directory')
        filelist = glob(dir_path + '/*')
    else:
        print('Make sure your file type includes the . in the extension name')
        filelist = glob(dir_path + f'/*{filetype}')
        
    if filetype == '.pfiles':
        cols = ['Time','Station_Name','Period?','Longitude','Latitude','Height','E_Uncer','N_Uncer','H_Uncer',
                'E-N_Corr,','E-H_Corr','N-H_Corr']
        
    outside_stat_list = []
    inside_stat_list = []
    
    for i,file in enumerate(filelist):
        stat_df = pd.read_csv(file,delim_whitespace=True,names=cols)
        stat_df['Longitude'] = (stat_df['Longitude'] + 180) % 360 - 180
        
        stat_df.drop(stat_df[stat_df.Longitude > max_lon].index, inplace=True)
        stat_df.drop(stat_df[stat_df.Longitude < min_lon].index, inplace=True)
        stat_df.drop(stat_df[stat_df.Latitude < min_lat].index, inplace=True)
        stat_df.drop(stat_df[stat_df.Latitude > max_lat].index, inplace=True)
        
        if stat_df.empty:
            outside_stat_list.append(file)
        else:
            inside_stat_list.append(file)
            
    return inside_stat_list

def set_aside_inside_stat_list(inside_stat_file_list,folder_name=None):
    if not folder_name:
        folder_name = 'Stations_In_Bounds'
    set_aside_directory = os.path.split(inside_stat_file_list[0])[0] + f'/{folder_name}'
    
    if not os.path.isdir(set_aside_directory):
        os.mkdir(set_aside_directory)
        
    for file in inside_stat_file_list:
        shutil.copy(file,set_aside_directory)
        
def make_gps_station_df(filelist):
    # FOR PLOTTING THE INITIAL STATION POSITIONS
    file_name = os.path.split(filelist[0])[1]
    
    lon_list = []
    lat_list = []
    stat_list = []
    
    if '.pfiles' in file_name:
        cols = ['Time','Station_Name','Period?','Longitude','Latitude','Height','E_Uncer','N_Uncer','H_Uncer',
                'E-N_Corr,','E-H_Corr','N-H_Corr']
        
        for i,file in enumerate(filelist):
            stat_df = pd.read_csv(file,delim_whitespace=True,names=cols)
            stat_list.append(stat_df.iloc[0,1])
            lon_list.append(stat_df.iloc[0,3])
            lat_list.append(stat_df.iloc[0,4])

            
    # Do same as above but with different file format
            
    stat_df = pd.DataFrame({'Station' : stat_list,
                            'Longitude' : lon_list,
                            'Latitude' : lat_list})
    
    return stat_df
        

def make_gps_station_displacement_df(filelist):
    file_name = os.path.split(filelist[0])[1]
    
    lon_list = []
    lat_list = []
    stat_list = []
    e_disp_list = []
    n_disp_list = []
    h_disp_list = []

    if '.pfiles' in file_name:
        cols = ['Time','Station_Name','Period?','Longitude','Latitude','Height','E_Uncer','N_Uncer','H_Uncer',
                'E-N_Corr,','E-H_Corr','N-H_Corr']
        
        for i,file in enumerate(filelist):
            stat_df = pd.read_csv(file,delim_whitespace=True,names=cols)
            stat_list.append(stat_df.iloc[0,1])
            lon_list.append(stat_df.iloc[0,3])
            lat_list.append(stat_df.iloc[0,4])
            e_disp_list.append(stat_df.iloc[-1,3] - stat_df.iloc[0,3])
            n_disp_list.append(stat_df.iloc[-1,4] - stat_df.iloc[0,4])
            h_disp_list.append(stat_df.iloc[-1,5] - stat_df.iloc[0,5])
            
    # Do same as above but with different file format
            
    stat_df = pd.DataFrame({'Station' : stat_list,
                            'Longitude' : lon_list,
                            'Latitude' : lat_list,
                            'E_Disp' : e_disp_list,
                            'N_Disp' : n_disp_list,
                            'H_Disp': h_disp_list})
    
    return stat_df

def make_gps_relative_displacement_df(filelist,ref_station,starttime=None,endtime=None):
    pass
    """
    FOR NOW ONLY CAN READ .PFILES
    """
    # ref_station is a station code
    # For every station, we calculate the displacement relative to the ref station at
    # every time stamp (at least the ones within the timeframe)
    
    for file in filelist:
        if ref_station in file:
            ref_file = file
        
    cols = ['Time','Station_Name','Period','Longitude','Latitude','Height','E_Uncer','N_Uncer','H_Uncer',
                'E-N_Corr,','E-H_Corr','N-H_Corr']
        
    ref_df = pd.read_csv(ref_file,delim_whitespace=True,names=cols)
    ref_df = ref_df.drop(columns=['Period'])
    
    ref_lon = ref_df['Longitude'].tolist()
    ref_lat = ref_df['Latitude'].tolist()
    ref_times= ref_df['Time'].tolist()
    
    ref_lat_fit = np.polyfit(ref_times,ref_lat,1)
    ref_lat_poly = np.poly1d(ref_lat_fit)
    
    ref_lon_fit = np.polyfit(ref_times,ref_lon,1)
    ref_lon_poly = np.poly1d(ref_lon_fit)
    
    plt.plot(ref_times,ref_lat,'.',ref_times,ref_lat_poly(ref_times),'--')
    plt.ylabel('Latitude')
    plt.xlabel('Time')
    plt.title('Reference Station Latitude Over Time AKMO')
    plt.show()
    
    plt.plot(ref_times,ref_lon,'.',ref_times,ref_lon_poly(ref_times),'--')
    plt.ylabel('Latitude')
    plt.xlabel('Time')
    plt.title('Reference Station Longitude Over Time AKMO')
    plt.show()
    
    for file in filelist:
        if file == ref_file:
            pass
        else:
            cols = ['Time','Station_Name','Period','Longitude','Latitude','Height','E_Uncer','N_Uncer','H_Uncer',
                        'E-N_Corr,','E-H_Corr','N-H_Corr']
                
            stat_df = pd.read_csv(ref_file,delim_whitespace=True,names=cols)
            stat_df = stat_df.drop(columns=['Period'])
            
            stat_df = 
            stat_lon = stat_df['Longitude'].tolist()
            stat_lat = stat_df['Latitude'].tolist()
            stat_times = stat_df['Time'].tolist()
            
            lon_disp = []
            lat_disp = []
            
            for i,time in enumerate(stat_times):
                ref_lon_at_time = ref_lon_poly(time)
                if i == 0:
                    initial_lon_diff = ref_lon_at_time - stat_lon[i]
                    lon_disp.append(0)
                    print('INITIAL DIFF: ')
                    print(initial_lon_diff)
                else:
                    current_lon_diff = ref_lon_at_time - stat_lon[i]
                    total_displacement = initial_lon_diff - current_lon_diff
                    lon_disp.append(total_displacement)
      
            plt.plot(ref_times,lon_disp)
                
        
            
    

    
    
    

    
    

filelist = glob('C:/Users/tlee4/Documents/Grad School/Spring 2024/PHYS581/Alaska_Project/Xue_Data/gps/Akutan_Stations/*')
make_gps_relative_displacement_df(filelist,'AKMO')
    
        
def plot_gps_stations(fig,stat_df,fill='black'):
    
    xvals = stat_df['Longitude']
    yvals = stat_df['Latitude']

    fig.plot(x=xvals,
             y=yvals,
             style='t0.35c',
             fill=fill)
    
    return fig

def plot_gps_displacement_vectors(fig,stat_df,scaling_factor=1000):
    lats = stat_df['Latitude'].tolist()
    lons = stat_df['Longitude'].tolist()
    e_disp = stat_df['E_Disp'].tolist()
    n_disp = stat_df['N_Disp'].tolist()
    
    angle_list = []
    length_list = []
    for i in range(len(e_disp)):
        angle_list.append(np.rad2deg(np.arctan(n_disp[i]/e_disp[i])))
        length_list.append((e_disp[i]**2 + n_disp[i]**2)**0.5)
        
    length_list = [val*scaling_factor for val in length_list]
        

    fig.plot(x=lons,
             y=lats,
             style="v0.6c+e",
             direction=[angle_list, length_list],
             pen="2p",
             color="red3")
            

    return fig

    