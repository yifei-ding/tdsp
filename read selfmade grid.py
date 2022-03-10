# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 15:49:32 2022

@author: yifei
"""

import geopandas as gpd
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import momepy
import shapely 
from shapely.geometry import Point, LineString
from geojson import Point, Feature, FeatureCollection, dump
from tdsp import *
import datetime


MAP_FILE_NAME = 'selfmade sea grid map2.geojson'
TEST_FILE_NAME = 'test.csv'

def readMap():
    df = gpd.read_file(MAP_FILE_NAME)
    
    G = momepy.gdf_to_nx(df, approach="primal")
    
    #convert to weighted map
    weighted_G = nx.Graph()
    for data in G.edges(data=True):
       weighted_G.add_edge(data[0],data[1],weight=data[2]['length'])
    
    nodes, edges, W = momepy.nx_to_gdf(weighted_G, spatial_weights=True)
    
    #add x and y coordinate
    nodes['x'] = nodes['geometry'].x
    nodes['y'] = round(nodes['geometry'].y,1)
    
    #connect left most with right most: -180 to 180
    mask1 = nodes[nodes['x']==180].sort_values(by=['y']).reset_index()['nodeID']
    mask2 = nodes[nodes['x']== -180].sort_values(by=['y']).reset_index()['nodeID']
    
    n1 = mask1.shape[0]
    n2 = mask2.shape[0]
    if n1 == n2: #check whether the size is same
        new_df = pd.DataFrame()
        new_df['weight'] = pd.Series([0]*n1) #set weight to 0
        new_df['node_start'] = mask1
        new_df['node_end'] = mask2
    
    edges_new = pd.concat([edges,new_df],ignore_index = True)
    
    return nodes, edges_new

def runDijkstra(nodes,edges,from_node, to_node):

    g = MyGraph(nodes, edges)
    path = dijkstra(g, from_node, to_node, 0)
    
    return path
    #problem with 2134 to 2038 
def savePath(path,fileName):
    nodes_on_shortest_path = extractPath(path)
    savePath(nodes, nodes_on_shortest_path, fileName)
#%%

def default():
    #read map
    nodes, edges = readMap()
    #count time
    df = pd.read_csv(TEST_FILE_NAME)
        
    list1 = df['from'].tolist()
    list2 = df['to'].tolist()

    n = len(list1)
    
    start_time = datetime.datetime.now()
    for i in range(n):
        runDijkstra(nodes, edges, list1[i], list2[i])
        
    end_time = datetime.datetime.now()
    print('Time: ',end_time - start_time)



if __name__ == "__main__":    
    
    if len(sys.argv)>1:
        arg = sys.argv[1]        
        if arg == 'A star':
            print('run A star')
        else:
            print('Wrong argument')
    else:
        default()

#%%
# def printNeighbours(node):
#     print(nodes[nodes['nodeID'] == node])
#     print(g.getNeighbouringNodes(node))
#     for item in g.getNeighbouringNodes(node):
#         print(nodes[nodes['nodeID'] == item].to_string(header=False), g.getDistance(node, item))
        
# printNeighbours(2027)