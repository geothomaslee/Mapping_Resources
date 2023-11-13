# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 08:35:58 2023

@author: tlee4
"""

import pygmt
from obspy.clients.fdsn import Client

if __name__ == '__main__':
    import general_mapping as gm
else:
    import scripts.general_mapping as gm
    
def find_events_in_region(times,region,
                          client='IRIS',magnitude=None,
                          depth=None):
    
    if type(times) != list:
        raise TypeError('Expected list for times: [starttime, endtime]')
        
    if magnitude == None:
        magnitude = [3, 10]
    elif type(magnitude) == int or type(magnitude) == float:
        magnitude = [magnitude, 10]
        
    if depth == None:
        depth = [0, 1000]
    elif type(depth) == int or type(depth) == float:
        depth = [depth, 1000]
        
    working_client=Client(client)
    
    catalog = working_client.get_events(minlongitude=region[0],
                                        maxlongitude=region[1],
                                        minlatitude=region[2],
                                        maxlatitude=region[3],
                                        starttime=times[0],
                                        endtime=times[1],
                                        minmagnitude=magnitude[0],
                                        maxmagnitude=magnitude[1],
                                        mindepth=depth[0],
                                        maxdepth=depth[1])
    
    print(f'{len(catalog)} events found in search region')

    return catalog

def find_events_around_point(times,latitude,longitude,radius,
                             client='IRIS',magnitude=None,
                             depth=None):

    working_client = Client(client)
    
    if type(radius) != list:
        raise TypeError('Expected list for radius: [minradius, maxradius]')
    if type(times) != list:
        raise TypeError('Expected list for times: [starttime, endtime]')
                        
    if magnitude == None:
        magnitude = [3, 10]
    elif type(magnitude) == int or type(magnitude) == float:
        magnitude = [magnitude, 10]
        
    if depth == None:
        depth = [0, 1000]
    elif type(depth) == int or type(depth) == float:
        depth = [depth, 1000]
        
    catalog = working_client.get_events(longitude=longitude,
                                        latitude=latitude,
                                        minradius=radius[0],
                                        maxradius=radius[1],
                                        starttime=times[0],
                                        endtime=times[1],
                                        minmagnitude=magnitude[0],
                                        maxmagnitude=magnitude[1],
                                        mindepth=depth[0],
                                        maxdepth=depth[1])
    print(f'{len(catalog)} events found in search radius!')

    return catalog

    
times = ['2015-01-01','2018-01-01']
radius = [0, 15]
magnitude = 5
test_catalog = find_events_around_point(times=times,
                                        latitude=45,
                                        longitude=-120,
                                        radius=radius,
                                        magnitude=magnitude)

print(test_catalog)





def plot_events(args):
    pass