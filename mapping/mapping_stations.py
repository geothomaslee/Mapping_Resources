# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:05:26 2023

@author: Blumenwitz
"""

import obspy
from obspy.clients.fdsn import Client

def find_stations(network, starttime,endtime,station='*',client="IRIS"):
    working_client = Client(client)
    station_inv = working_client.get_stations(starttime=starttime,
                                              endtime=endtime,
                                              network=network, 
                                              station=station,
                                              level="station")
    return station_inv

def find_multi_network(deployment_list,client="IRIS"):
    working_client = Client(client)

    
    
    for i, deployment in enumerate(deployment_list):
        network = deployment[0]
        starttime = deployment[1]
        endtime = deployment[2]
        
        if i < 1:
            station_inv = working_client.get_stations(starttime=starttime,
                                                      endtime=endtime,
                                                      network=network, 
                                                      station='*',
                                                      level="station")
        else:
            secondary_inv = working_client.get_stations(starttime=starttime,
                                                        endtime=endtime,
                                                        network=network, 
                                                        station='*',
                                                        level="station")
            station_inv = station_inv + secondary_inv
            
    return station_inv
            
      
station_inv = find_stations("ZR","2015-01-01","2017-12-31")
station_inv.plot()
        
        
