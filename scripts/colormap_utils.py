# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 11:45:49 2024

@author: tlee4
"""
import pandas as pd
import os
import shutil


def clean_colormap_df(filepath):
    filepath = os.path.expanduser(filepath)
    basename = os.path.basename(filepath)
    if basename[-4:] != '.cpt':
        raise ValueError('Given file is not a cpt file')
        
    names = ['Bottom_Bound', 'R1', 'G1', 'B1','Upper_Bound', 'R2', 'G2', 'B2']
    cmap_df = pd.read_csv(filepath,delim_whitespace=True,comment='#',names=names)
    cmap_df = cmap_df.dropna()
    
    print(cmap_df)
    
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

def add_bathymetry(topo_cmap_df,bathy_cmap_df):
    bathy_cmap_df = bathy_cmap_df.drop(bathy_cmap_df[bathy_cmap_df.Upper_Bound > 0].index, inplace=True)
    print(bathy_cmap_df)
    
    combined_df = pd.concat([bathy_cmap_df, topo_cmap_df], ignore_index=True)  # Concatenate and reset index
    indices = len(bathy_cmap_df) + len(topo_cmap_df)
    combined_df = combined_df.reindex(range(indices))
    
    print(combined_df)
    
    
topo_cmap_path = os.path.expanduser('~/Documents/GitHub/Mapping_Resources/Resources/colormaps/usgs.cpt')
topo_cmap_df = clean_colormap_df(topo_cmap_path)
bathy_cmap_path = os.path.expanduser('~/Documents/GitHub/Mapping_Resources/Resources/colormaps/colombia.cpt')
bathy_cmap_df = clean_colormap_df(bathy_cmap_path)



        
        




def convert_color_map(filepath,min_elev=-8000,max_elev=8000,
                      bathymetric_cmap=None):
    filepath = os.path.expanduser(filepath)
    basename = os.path.basename(filepath)
    if basename[-4:] != '.cpt':
        raise ValueError('Given file is not a cpt file')
        
    if not bathymetric_cmap:
        bathymetric_cmap = os.path.expanduser('~/Documents/GitHub/Mapping_Resources/Resources/colormaps/colombia.cpt')
        
    names = ['Bottom_Bound', 'R1', 'G1', 'B1','Upper_Bound', 'R2', 'G2', 'B2']
    cmap_df = pd.read_csv(filepath,delim_whitespace=True,comment='#',names=names)
    cmap_df = cmap_df.dropna()
    
    lower_bound_list = cmap_df['Bottom_Bound'].tolist()
    upper_bound_list = cmap_df['Upper_Bound'].tolist()
    lower_bound_list = [float(val) for val in lower_bound_list]
    lower_bound_list = [float(val) for val in lower_bound_list]
    
    max_bound = max(upper_bound_list)
    min_bound = min(lower_bound_list)
    bound_range = max_bound - min_bound
    
    if min_bound >= 0:
        print(f'Colormap does not contain bathymetric values, using {os.path.split(bathymetric_cmap)[1]}')
        bathy_df = pd.read_csv(bathymetric_cmap,delim_whitespace=True,comment='#',names=names)
        bathy_df.drop(bathy_df[bathy_df.Upper_Bound > 0].index, inplace=True)
        bathy_file_path = os.path.split(bathymetric_cmap)[0] + '/temp_bathymetry.cpt'
        
    col_space = [5, 3, 3, 3, 5, 3, 3, 3 ]
    bathy_df.to_string(bathy_file_path, col_space=col_space, index=None,header=False,
                       justify='left')
        
        
    elev_range = max_elev - min_elev
    new_lower_bound_list = []
    new_upper_bound_list = []

    
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
    
    
    RGB_col_list = ['R1','G1','B1','R2','G2','B2']
    for col in RGB_col_list:
        color_list = cmap_df[col].tolist()
        color_list = [int(round(val)) for val in color_list]
        new_color_df = pd.DataFrame({col : color_list})
        cmap_df[col] = new_color_df[col]
            
    path_split = os.path.split(filepath)
    topo_file_path = path_split[0] + '/temp_topo.cpt'
    print(topo_file_path)
    
    cmap_df.to_string(topo_file_path, col_space=col_space, index=None,header=False,
                      justify='left')
    
    final_out_file = path_split[0] + '/converted_' + path_split[1]
    
    if min_bound >= 0:
        filenames = [bathy_file_path, topo_file_path]
        with open(final_out_file,'wb') as wfd:
            for f in filenames:
                with open(f,'rb') as fd:
                    shutil.copyfileobj(fd, wfd)
                    wfd.write(b"\n")
                    
        #os.remove(bathy_file_path)
        #os.remove(topo_file_path)
                
    else:
        cmap_df.to_string(final_out_file, col_space=col_space, index=None,header=False,
                          justify='left')
        #os.remove(topo_file_path)