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
from geopy import distance


def find_files_in_bounds(directory,bounds,filetype=None):
    """
    If given a file directory containing GPS files and lat/lon boundaries in the
    form [min_lon,max_lon,min_lat,max_lat], will read in the GPS files and figure
    out which ones are in the boundaries.
    
    
    Parameters
    ----------
    directory : str
        The name of the directory containing GPS files.
    bounds : list
        Boundaries to search for stations, in the form [min_lon,max_lon,min_lat,max_lat].
    filetype : str, optional
        File extension of the GPS files. The default is None.

    Returns
    -------
    inside_stat_list : list
        List of filepaths to files that are inside the desired bounds.

    """
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
    """
    Parameters
    ----------
    inside_stat_file_list : list
        List of file paths to the files to set aside.
    folder_name : str, optional
        The folder name to put the desired stations in. The default is None.

    """
    if not folder_name:
        folder_name = 'Stations_In_Bounds'
    set_aside_directory = os.path.split(inside_stat_file_list[0])[0] + f'/{folder_name}'
    
    if not os.path.isdir(set_aside_directory):
        os.mkdir(set_aside_directory)
        
    for file in inside_stat_file_list:
        shutil.copy(file,set_aside_directory)
        
def make_gps_station_df(filelist):
    """
    Makes a DataFrame containing the initial positions of the GPS stations,
    primarily for plotting purposes.

    Parameters
    ----------
    filelist : list
        List of filepaths to GPS files.

    Returns
    -------
    stat_df : pandas.DataFrame
        DataFrame containing GPS station info.

    """
    file_name = os.path.split(filelist[0])[1]
    
    lon_list = []
    lat_list = []
    height_list = []
    stat_list = []
    
    if '.pfiles' in file_name:
        cols = ['Time','Station_Name','Period?','Longitude','Latitude','Height','E_Uncer','N_Uncer','H_Uncer',
                'E-N_Corr,','E-H_Corr','N-H_Corr']
        
        for i,file in enumerate(filelist):
            stat_df = pd.read_csv(file,delim_whitespace=True,names=cols)
            stat_list.append(stat_df.iloc[0,1])
            lon_list.append(stat_df.iloc[0,3])
            lat_list.append(stat_df.iloc[0,4])
            height_list.append(stat_df.iloc[0,5])
            
    stat_df = pd.DataFrame({'Station' : stat_list,
                            'Longitude' : lon_list,
                            'Latitude' : lat_list,
                            'Height' : height_list})
    
    return stat_df
        

def make_gps_station_displacement_df(filelist):
    """
    Makes a DataFrame containing GPS initial positions and their total 
    displacement over the entire time span given in the GPS file. Useful for 
    seeing absolute deformation, but not local deformation. Ex. stations on a
    volcanic island in a subduction zone will have their absolute motion 
    dominanted by the convergence rate of the subduction zone, not the 
    actual deformation from the volcanic edifice.
    
    Parameters
    ----------
    filelist : list
        List of filepaths to GPS files of interest.

    Returns
    -------
    stat_df : pandas.DataFrame
        DataFrame containing GPS initial positions and their total displacement
        over the entire time span given in the GPS file. Useful for seeing
        absolute deformation, but not local deformation. Ex. stations on a
        volcanic island in a subduction zone will have their absolute motion
    """
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

def make_gps_relative_displacement_df_dict(filelist,ref_station,
                                           plot_lats=False,plot_lons=False,
                                           plot_elevs=False,plot_ref=False):
    """
    Parameters
    ----------
    filelist : list of str
        List of GPS files to include. Currently can only read .pfiles.
    ref_station : str
        Name of reference station.
    plot_lats : bool, optional
        Will produce a figure showing the latitudinal displacement for every
        station. The default is False.
    plot_lons : bool, optional
        Will produce a figure showing the longitudinal displacement for every
        station. The default is False.
    plot_elevs : bool, optional
        Will produce a figure showing the elevation displacement for every
        station. The default is False.
    plot_ref : bool, optional
        Will plot the absolute GPS positions over time for the reference station
        in question. The default is False.

    Returns
    -------
    df_dict : dict
        A dictionary where each key is a station name and the value is a 
        corresponding Pandas DataFrame. The DataFrame contains the 
        displacement of each station over time, in millimeters, relative to 
        the reference station.
    """
    for file in filelist:
        if ref_station in file:
            ref_file = file
        
    cols = ['Time','Station_Name','Period','Longitude','Latitude','Height','E_Uncer','N_Uncer','H_Uncer',
                'E-N_Corr,','E-H_Corr','N-H_Corr']
        
    ref_df = pd.read_csv(ref_file,delim_whitespace=True,names=cols)
    ref_df = ref_df.drop(columns=['Period'])
    
    ref_lon = ref_df['Longitude'].tolist()
    ref_lat = ref_df['Latitude'].tolist()
    ref_height = ref_df['Height'].tolist()
    ref_times= ref_df['Time'].tolist()
    
    ref_lat_fit = np.polyfit(ref_times,ref_lat,1)
    ref_lat_poly = np.poly1d(ref_lat_fit)
    
    ref_lon_fit = np.polyfit(ref_times,ref_lon,1)
    ref_lon_poly = np.poly1d(ref_lon_fit)
    
    ref_height_fit = np.polyfit(ref_times,ref_height,1)
    ref_height_poly = np.poly1d(ref_height_fit)
    
    if plot_ref:
        plt.plot(ref_times,ref_height,'.',ref_times,ref_height_poly(ref_times),'--')
        plt.ylabel('Elevation')
        plt.xlabel('Time')
        plt.title(f'Reference Station Elevation Over Time {ref_station}')
        plt.show()
        
        plt.plot(ref_times,ref_lon,'.',ref_times,ref_lon_poly(ref_times),'--')
        plt.ylabel('Latitude')
        plt.xlabel('Time')
        plt.title(f'Reference Station Longitude Over Time {ref_station}')
        plt.show()
        
        plt.plot(ref_times,ref_lat,'.',ref_times,ref_lat_poly(ref_times),'--')
        plt.ylabel('Latitude')
        plt.xlabel('Time')
        plt.title(f'Reference Station Latitude Over Time {ref_station}')
        plt.show()

    df_dict = {}
    for file in filelist:
        if file == ref_file:
            pass
        else:
            cols = ['Time','Station_Name','Period','Longitude','Latitude','Height','E_Uncer','N_Uncer','H_Uncer',
                        'E-N_Corr,','E-H_Corr','N-H_Corr']
                
            stat_df = pd.read_csv(file,delim_whitespace=True,names=cols)
            stat_df = stat_df.drop(columns=['Period'])
            
            stat_name = stat_df['Station_Name'].tolist()[0]
            stat_lon = stat_df['Longitude'].tolist()
            stat_lat = stat_df['Latitude'].tolist()
            stat_height = stat_df['Height'].tolist()
            stat_times = stat_df['Time'].tolist()
            
            lon_disp = []
            lat_disp = []
            height_disp = []
            
            for i,time in enumerate(stat_times):
                ref_lon_at_time = ref_lon_poly(time)
                ref_lat_at_time = ref_lat_poly(time)
                ref_height_at_time = ref_height_poly(time)
                if i == 0:
                    
                    
                    # Fix lon and calculate lat diff
                    initial_lat_diff = distance.distance([ref_lat_at_time,ref_lon_at_time],
                                                         [stat_lat[i],ref_lon_at_time]).km
                    # FIx lat and calculate lon diff
                    initial_lon_diff = distance.distance([ref_lat_at_time,ref_lon_at_time],
                                                         [ref_lat_at_time,stat_lon[i]]).km
                    lon_disp.append(0)
                    lat_disp.append(0)
                    
                    initial_height_diff = ref_height_at_time - stat_height[i]
                    height_disp.append(0)
                else:
                    current_lon_diff = distance.distance([ref_lat_at_time,ref_lon_at_time],
                                                         [ref_lat_at_time,stat_lon[i]]).km
                    lon_displacement = current_lon_diff - initial_lon_diff
                    lon_disp.append(lon_displacement)
                    
                    current_lat_diff = distance.distance([ref_lat_at_time,ref_lon_at_time],
                                                         [stat_lat[i],ref_lon_at_time]).km
                    lat_displacement = current_lat_diff - initial_lat_diff
                    lat_disp.append(lat_displacement)
                    
                    current_height_diff = ref_height_at_time - stat_height[i]
                    height_displacement = initial_height_diff - current_height_diff
                    height_disp.append(height_displacement)
                    
            lon_disp = [x * 100000 for x in lon_disp]
            lat_disp = [x * 100000 for x in lat_disp]
            height_disp = [x * 1000 for x in height_disp]
        
            if plot_lons:
                plt.plot(stat_times,lon_disp)
                plt.plot(stat_times,lon_disp,'o')
                plt.title(f'East Displacement at {stat_name} Relative to {ref_station}')
                plt.ylabel('East Displacement (mm)')
                plt.xlabel('Time')
                plt.show()
                
            if plot_lats:
                plt.plot(stat_times,lat_disp)
                plt.plot(stat_times,lat_disp,'o')
                plt.title(f'North Displacement at {stat_name} Relative to {ref_station}')
                plt.ylabel('North Displacement (mm)')
                plt.xlabel('Time')
                plt.show()
                
            if plot_elevs:
                plt.plot(stat_times,height_disp)
                plt.plot(stat_times,height_disp,'o')
                plt.title(f'Vertical Displacement at {stat_name} Relative to {ref_station}')
                plt.ylabel('Vertical Change (mm)')
                plt.xlabel('Time')
                plt.show()
                
            current_station_df = pd.DataFrame({'Time' : stat_times,
                                               'E_Disp' : lon_disp,
                                               'N_Disp' : lat_disp,
                                               'Vert_Disp' : height_disp})
            
            df_dict[stat_name] = current_station_df
            
    return df_dict
                
def velocity_fits_from_dict(gps_disp_dict,max_degree_to_test=4):
    for station in gps_disp_dict:
        stat_dict = gps_disp_dict[station]
        
        times = stat_dict['Time'].tolist()
        E_Disp = stat_dict['E_Disp'].tolist()
        N_Disp = stat_dict['N_Disp'].tolist()
        Vert_Disp = stat_dict['Vert_Disp'].tolist()
        
        """ Interesting but I don't think it does anything useful
        for i in np.arange(1,max_degree_to_test+1,1):
            residual = np.polyfit(times,E_Disp,i,full=True)[1]
            if residual:
                if i == 1:
                    best_degree = i
                    best_residual = residual
                else:
                    if residual < best_residual:
                        best_degree = i
                        
        print(f'BEST DEGREE: {best_degree} for {station}')
        """
                        
        
        
        
        
        
filelist = glob('C:/Users/tlee4/Documents/Grad School/Spring 2024/PHYS581/Alaska_Project/Xue_Data/gps/Akutan_Stations/*')
df_dict = make_gps_relative_displacement_df_dict (filelist,'AKMO')
velocity_fits_from_dict(df_dict)





    
        
def plot_gps_stations(fig,stat_df,fill='black'):
    """
    Parameters
    ----------
    fig : pygmt.Figure
        PyGMT figure, see scripts.general_mapping.plot_base_map for a
        convenient base figure to start with.
    stat_df : pandas.DataFrame
        Pandas DataFrame with columns 'Latitude' and 'Longitude'. All other
        columns don't matter.
    fill : str, optional
        Color to fill station symbols with. The default is 'black'.

    Returns
    -------
    fig : pygmt.Figure
        Input figure with stations drawn on top.

    """
    xvals = stat_df['Longitude']
    yvals = stat_df['Latitude']

    fig.plot(x=xvals,
             y=yvals,
             style='t0.35c',
             fill=fill)
    
    return fig

def plot_gps_displacement_vectors(fig,stat_df,scaling_factor=1000):
    """
    Parameters
    ----------
    fig : pygmt.Figure
        PyGMT figure, see scripts.general_mapping.plot_base_map for a
        convenient base figure to start with.
    stat_df : pandas.DataFrame
        Pandas DataFrame with columns 'Latitude','Longitude','E_Disp', 'N_Disp'.
        All other columns don't matter.
    scaling_factor : int or float, optional
        Multiplier of the vector length. The default is 1000.

    Returns
    -------
    fig : pygmt.Figure
        Input figure with velocity vectors drawn on top.

    """
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

    