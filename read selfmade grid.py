# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 15:49:32 2022

@author: yifei
"""
import datetime
import sys

import geopandas as gpd
import momepy
import networkx as nx
import pandas as pd

from tdsp import *

MAP_FILE_NAME = 'selfmade sea grid map2.geojson'
TEST_FILE_NAME = 'test.csv'


def read_map():
    df = gpd.read_file(MAP_FILE_NAME)
    df.to_crs(epsg=4326)
    G = momepy.gdf_to_nx(df, approach="primal")

    # convert to weighted map
    weighted_G = nx.Graph()
    for data in G.edges(data=True):
        weighted_G.add_edge(data[0], data[1], weight=data[2]['length'])

    nodes, edges, W = momepy.nx_to_gdf(weighted_G, spatial_weights=True)

    # add x and y coordinate
    nodes['x'] = nodes['geometry'].x
    nodes['y'] = round(nodes['geometry'].y, 1)

    # connect left most with right most: -180 to 180
    mask1 = nodes[nodes['x'] == 180].sort_values(by=['y']).reset_index()['nodeID']
    mask2 = nodes[nodes['x'] == -180].sort_values(by=['y']).reset_index()['nodeID']

    n1 = mask1.shape[0]
    n2 = mask2.shape[0]
    if n1 == n2:  # check whether the size is same
        new_df = pd.DataFrame()
        new_df['weight'] = pd.Series([0] * n1)  # set weight to 0
        new_df['node_start'] = mask1
        new_df['node_end'] = mask2

    edges_new = pd.concat([edges, new_df], ignore_index=True)

    return nodes, edges_new


def run_dijkstra(g, from_node, to_node, start_time):
    path, _ = dijkstra(g, from_node, to_node, start_time)
    return path
    # problem with 2134 to 2038 solved


def run_dijkstra_and_return_all(g, from_node, to_node, start_time):
    return dijkstra(g, from_node, to_node, start_time)


def save_to_file(nodes, path, file_name):
    nodes_on_shortest_path = extract_path(path)
    save_path(nodes, nodes_on_shortest_path, file_name)


# %%

def run_test():
    # read map
    nodes, edges = read_map()
    # construct graph
    g = MyGraph(nodes, edges)
    # run dijkstra and count time
    df = pd.read_csv(TEST_FILE_NAME)
    df['time'] = ''
    df['total states'] = ''
    df['path length'] = ''
    df['path'] = ''
    for i, row in df.iterrows():
        from_node = row['from']
        to_node = row['to']
        # count time
        start_time = datetime.datetime.now()
        path, number_of_states = run_dijkstra_and_return_all(g, from_node, to_node, 0)
        end_time = datetime.datetime.now()
        delta = end_time - start_time
        # to milliseconds
        df.at[i, 'time'] = int(delta.total_seconds() * 1000)
        df.at[i, 'total states'] = number_of_states
        df.at[i, 'path'] = path
        df.at[i, 'path length'] = len(path)

    # save results
    df.to_csv('output/test_result_0312_with_states_3.csv')


if __name__ == "__main__":

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == 'test':
            print('run test')
            run_test()
        else:
            print('Wrong argument')
    else:
        # run a single query and save path to file
        nodes_1, edges_1 = read_map()
        g_1 = MyGraph(nodes_1, edges_1)
        path_1 = run_dijkstra(g_1, 4, 456, 0)
        save_to_file(nodes_1, path_1, '0313_4_456_change_visited')

# %%
# def printNeighbours(node):
#     print(nodes[nodes['nodeID'] == node])
#     print(g.getNeighbouringNodes(node))
#     for item in g.getNeighbouringNodes(node):
#         print(nodes[nodes['nodeID'] == item].to_string(header=False), g.getDistance(node, item))

# printNeighbours(2027)
