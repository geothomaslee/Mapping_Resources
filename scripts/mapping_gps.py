# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 14:09:01 2024

@author: tlee4
"""

import os
import pandas as pd
from glob import glob


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

def make_gps_station_df(filelist):
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
            
        stat_df = pd.DataFrame({'Station' : stat_list,
                                'Longitude' : lon_list,
                                'Latitude' : lat_list})
        
    return stat_df
        
        
def plot_gps_stations(fig,stat_df,fill='black'):
    
    xvals = stat_df['Longitude']
    yvals = stat_df['Latitude']
    
    fig.plot(x=xvals,
             y=yvals,
             style='t0.35c',
             fill=fill)
    
    return fig

    

        


        

    
        


