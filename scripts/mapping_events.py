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
    


def find_events_in_region(region,client='IRIS'):
    working_client=Client(client)

def find_events_around_point(pointlon,pointlat):
    pass

def plot_events(args):
    pass