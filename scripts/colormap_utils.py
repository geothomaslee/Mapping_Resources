# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 11:45:49 2024

@author: tlee4
"""
import pandas as pd
import os
import numpy as np
from glob import glob


def clean_colormap_df(filepath):
    filepath = os.path.expanduser(filepath)
    
    if not os.path.isfile(filepath):
        raise ValueError(f'Could not locate cpt file at {filepath}')
    
    
    basename = os.path.basename(filepath)
    if basename[-4:] != '.cpt':
        raise ValueError('Given file is not a cpt file')
        
    names = ['Bottom_Bound', 'R1', 'G1', 'B1','Upper_Bound', 'R2', 'G2', 'B2']
    cmap_df = pd.read_csv(filepath,delim_whitespace=True,comment='#',names=names)
    cmap_df = cmap_df.dropna()
    
    lower_bound_list = cmap_df['Bottom_Bound'].tolist()
    upper_bound_list = cmap_df['Upper_Bound'].tolist()
    lower_bound_list = [float(val) for val in lower_bound_list]
    upper_bound_list = [float(val) for val in upper_bound_list]

    cmap_df['Bottom_Bound'] = pd.DataFrame({'Bottom_Bound' : lower_bound_list})['Bottom_Bound']
    cmap_df['Upper_Bound'] = pd.DataFrame({'Upper_Bound' : upper_bound_list})['Upper_Bound']
    
    RGB_col_list = ['R1','G1','B1','R2','G2','B2']
    for col in RGB_col_list:
        color_list = cmap_df[col].tolist()
        color_list = [int(round(val)) for val in color_list]
        new_color_df = pd.DataFrame({col : color_list})
        cmap_df[col] = new_color_df[col]
        
    return cmap_df

def remap_cmap(cmap_df, min_elev, max_elev):
    lower_bound_list = cmap_df['Bottom_Bound'].tolist()
    upper_bound_list = cmap_df['Upper_Bound'].tolist()
    lower_bound_list = [float(val) for val in lower_bound_list]
    upper_bound_list = [float(val) for val in upper_bound_list]
    
    min_bound = min(lower_bound_list) # Calculating bounds of values currently in CPT
    max_bound = max(upper_bound_list)
    bound_range = max_bound - min_bound
    
    asymmetric_bathy_and_topo = None
    if min_bound == 0 and min_elev < 0:
        print('WARNING: Set negative elevation minimum, but colormap only contains values for positive elevation')
        min_elev = 0
        asymmetric_bathy_and_topo = False

    
    elev_range = max_elev - min_elev # Elevation range
    
    new_lower_bound_list = []
    new_upper_bound_list = []
    
    # If there is a symmetric bathymetric and topographic component
    if abs(min_bound) == abs(max_bound):
        print('AHJH')
        elev_range = abs(min_bound)
        bound_range = abs(min_bound)
        for i in range(len(lower_bound_list)):
            lower_bound = lower_bound_list[i]
            upper_bound = upper_bound_list[i]
            
            new_lower_bound = round((lower_bound * elev_range) / bound_range)
            new_upper_bound = round((upper_bound * elev_range) / bound_range)
        
            new_lower_bound_list.append(new_lower_bound)
            new_upper_bound_list.append(new_upper_bound)
        
        new_bound_df = pd.DataFrame({'Bottom_Bound' : new_lower_bound_list,
                                     'Upper_Bound' : new_upper_bound_list})
        cmap_df['Bottom_Bound'] = new_bound_df['Bottom_Bound']
        cmap_df['Upper_Bound'] = new_bound_df['Upper_Bound']
        
    # If there is an asymmetric bathymetric and topographic component
    elif abs(min_bound) != abs(max_bound) and asymmetric_bathy_and_topo:
        print('FEATURE COMING SOON')
        
    # If there is only bathymetry or topography
    elif min_bound == 0 or max_bound == 0:
        for i in range(len(lower_bound_list)):
            lower_bound = lower_bound_list[i]
            upper_bound = upper_bound_list[i]
            
            new_lower_bound = round((lower_bound * elev_range) / bound_range)
            new_upper_bound = round((upper_bound * elev_range) / bound_range)
        
            new_lower_bound_list.append(new_lower_bound)
            new_upper_bound_list.append(new_upper_bound)
            
        new_bound_df = pd.DataFrame({'Bottom_Bound' : new_lower_bound_list,
                                     'Upper_Bound' : new_upper_bound_list})
        cmap_df['Bottom_Bound'] = new_bound_df['Bottom_Bound']
        cmap_df['Upper_Bound'] = new_bound_df['Upper_Bound']
    return cmap_df

def isolate_bathymetry(bathy_cmap_df):
    bathy_cmap_df.drop(bathy_cmap_df[bathy_cmap_df.Bottom_Bound >= 0].index, inplace=True)
    
    return bathy_cmap_df

def add_bathymetry(topo_cmap_df,bathy_cmap_df,remap=True):
    
    if min(topo_cmap_df['Bottom_Bound'].tolist()) < 0:
        raise ValueError('Topo cmap contains bathymetric data, this function is for topo maps with elevation value 0')
    bathy_cmap_df.drop(bathy_cmap_df[bathy_cmap_df.Bottom_Bound >= 0].index, inplace=True)
    
    min_bathy = min(bathy_cmap_df['Bottom_Bound'].tolist())
    max_topo = max(bathy_cmap_df['Upper_Bound'].tolist())
    
    if remap:
        if abs(min_bathy) > abs(max_topo):
            topo_cmap_df = remap_cmap(topo_cmap_df,0,abs(min_bathy))
        elif abs(min_bathy) < abs(max_topo):
            bathy_cmap_df = remap_cmap(bathy_cmap_df,-abs(max_topo),0)
    else:
        print('add_bathymetry in colormap_utils: Remap set to False, change to True to auto rescale cmaps to match max scales')
    
    
    combined_df = pd.concat([bathy_cmap_df, topo_cmap_df], ignore_index=True)

    return combined_df

def interpolate_cmap(cmap_df,cuts=10):
    new_df = cmap_df.copy()
    new_df.drop(new_df[new_df.index > 0].index, inplace=True)
    
    for i in range(len(cmap_df)):
        names = ['Bottom_Bound', 'R1', 'G1', 'B1','Upper_Bound', 'R2', 'G2', 'B2']
        
        if i == 0:
            pass
        else:
            row = cmap_df[i:i+1]
            prev_row = new_df[-1:]
            
            interp_dict = {}
            for j, name in enumerate(names):
    
                interp_list = list(np.linspace(prev_row.iloc[0,j],row.iloc[0,j],num=cuts))
                interp_list = [round(val) for val in interp_list]
                interp_list = interp_list[1:]
                interp_dict[name] = interp_list
                
            
            interp_df = pd.DataFrame(interp_dict)
        
        if i != 0:
            new_df = pd.concat([new_df,interp_df], ignore_index=True)

            
    t = new_df['Bottom_Bound'].tolist()
    steps = [j-i for i, j in zip(t[:-1], t[1:])]
    new_upper_bound = [t[i] + steps[i] for i in range(len(steps))]
    new_upper_bound = new_upper_bound[:-1]
    new_upper_bound_df = pd.DataFrame({'Upper_Bound' : new_upper_bound})
    
    new_df['Upper_Bound'] = new_upper_bound_df['Upper_Bound']
    
    new_df.iat[-2,4] = new_df.iloc[-1,0]
    if new_df.iloc[-1,0] < 0:
        new_df.iat[-1,4] = 0
    else:
        new_df.iat[-1,4] = cmap_df.iat[-1,4]
    
    return new_df

def save_cmap_df_as_cpt(cmap_df,filepath):
    filepath=os.path.expanduser(filepath)
    
    if type(filepath) != str:
        raise TypeError('Filepath must be a string')
        
    col_space = [5, 3, 3, 3, 5, 3, 3, 3 ]        
    cmap_df.to_string(filepath, col_space=col_space, index=None,header=False,
                      justify='left')
    
def create_combined_color_map(topo_cmap,bathy_cmap,max_elev,max_depth,cmap_dir=None):
    if not cmap_dir:
        cmap_dir = '~/Documents/GitHub/Mapping_Resources/resources/colormaps'
    
    if '.cpt' in topo_cmap:
        topo_cmap = topo_cmap[:-4]
        print(topo_cmap)
        
    if '.cpt' in bathy_cmap:
        bathy_cmap = bathy_cmap[:-4]
        
    save_path = os.path.expanduser(cmap_dir) + '/colormap-utils/' + f'topo_{topo_cmap}_{max_elev}_bathy_{bathy_cmap}_{max_depth}' + '.cpt'
        
    if not os.path.isfile(topo_cmap):
        search_str = cmap_dir + '/**/' + topo_cmap + '.cpt'
        matching_cmap = glob(os.path.expanduser(search_str),recursive=True)
        if len(matching_cmap) == 0:
            raise ValueError('Could not find cpt that matches input for topo_filepath')
        elif len(matching_cmap) > 1:
            raise ValueError('Found multiple cpts that match input for topo_filepath')
        else:
            topo_cmap = matching_cmap[0]

    if not os.path.isfile(bathy_cmap):
        search_str = cmap_dir + '/**/' + bathy_cmap + '.cpt'
        matching_cmap = glob(os.path.expanduser(search_str),recursive=True)
        if len(matching_cmap) == 0:
            raise ValueError('Could not find cpt that matches input for topo_filepath')
        elif len(matching_cmap) > 1:
            raise ValueError('Found multiple cpts that match input for topo_filepath')
        else:
            bathy_cmap = matching_cmap[0]
            
    topo_cmap_df = clean_colormap_df(topo_cmap)
    topo_cmap_df = remap_cmap(topo_cmap_df,0,max_elev)
    topo_cmap_df = interpolate_cmap(topo_cmap_df,20)
    
    bathy_cmap_df = clean_colormap_df(bathy_cmap)
    bathy_cmap_df = isolate_bathymetry(bathy_cmap_df)
    bathy_cmap_df = remap_cmap(bathy_cmap_df,max_depth,0)
    bathy_cmap_df = interpolate_cmap(bathy_cmap_df,20)
    
    combined_cmap_df = add_bathymetry(topo_cmap_df, bathy_cmap_df,remap=False)
    
    save_cmap_df_as_cpt(combined_cmap_df,save_path)
    
    return save_path
        
cmap = create_combined_color_map('usgs','colombia',4000,-8000)



        
        

