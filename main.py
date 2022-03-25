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
from datetime import date

from model.Obstacle import Obstacle
from model.mygraph import MyGraphWithAdjacencyList
from tdsp import *

MAP_FILE_NAME = 'data/selfmade sea grid map2.geojson'
TEST_FILE_NAME = 'data/test_50.csv'


def read_map(file_name = MAP_FILE_NAME):
    df = gpd.read_file(file_name)
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


def get_neighbouring_nodes(node_id, edges):
    mask = (edges['node_start'] == node_id)
    list1 = list(edges[mask]['node_end'])

    mask = (edges['node_end'] == node_id)
    list2 = list(edges[mask]['node_start'])
    return list1 + list2


# 1
def create_adjacency_list(nodes, edges):
    result = {}
    nodes_list = nodes['nodeID'].to_list()
    for item in nodes_list:
        result[item] = get_neighbouring_nodes(item, edges)

    return result


# 2
def create_nodes_dict_with_coordinates(nodes):
    result = {}
    for i, row in nodes.iterrows():
        result[row['nodeID']] = (row['x'], row['y'])
    return result


# 3
def create_weight_dict(edges, nodes_with_coordinates):
    result = {}
    for i, row in edges.iterrows():
        # result[(row['node_start'], row['node_end'])] = row['weight']
        result[(row['node_start'], row['node_end'])] = utils.haversine(coord1=nodes_with_coordinates[row['node_start']],
                                                                       coord2=nodes_with_coordinates[row['node_end']])

    return result


def preprocessing_map_to_adjacency_list_and_weight_dict(nodes, edges):
    adjacency_list = create_adjacency_list(nodes, edges)
    nodes_with_coordinates = create_nodes_dict_with_coordinates(nodes)
    weight_dict = create_weight_dict(edges, nodes_with_coordinates)
    return adjacency_list, nodes_with_coordinates, weight_dict


def run_dijkstra(g, from_node, to_node, start_time, heuristic_type='default'):
    path, _ = dijkstra(g, from_node, to_node, start_time, heuristic_type)
    return path
    # problem with 2134 to 2038 solved


def run_dijkstra_and_return_all(g, from_node, to_node, start_time, heuristic_type='default'):
    return dijkstra(g, from_node, to_node, start_time, heuristic_type)


def save_to_file(nodes, path, file_name):
    nodes_on_shortest_path = extract_path(path)
    save_path(nodes, nodes_on_shortest_path, file_name)


def extract_path(path):
    result = []
    for item in path:
        result.append(item.get_node())
    return result


def save_path(nodes, nodes_on_shortest_path, file_name):
    points = []
    for item in nodes_on_shortest_path:
        mask = nodes['nodeID'] == item
        points.append(nodes[mask].iloc[0]['geometry'])

    linestring_for_export = LineString(points)

    features = [Feature(geometry=linestring_for_export)]
    feature_collection = FeatureCollection(features)
    fileName_str = file_name + '.geojson'
    with open(fileName_str, 'w') as f:
        dump(feature_collection, f)
    print('Saved!')


# %%

def run_test(heuristic_type='default', str_append_to_file_name='a', save_path = False):
    # read map
    nodes, edges = read_map()
    # construct graph
    nodes_new, nodes_with_coordinates, weights = preprocessing_map_to_adjacency_list_and_weight_dict(nodes, edges)
    g = MyGraphWithAdjacencyList(nodes_new, nodes_with_coordinates, weights)
    # add obstacles
    obstacle = Obstacle(1000, 40, 40, 70, 70, 0, 20000, 1.2)
    obstacle2 = Obstacle(100, -50, -50, -30, -30, 0, 10000, sys.maxsize)
    g.add_obstacle(obstacle)
    g.add_obstacle(obstacle2)
    # run dijkstra and count time
    today = date.today()
    today_str = today.strftime("%m%d")
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
        print(f'Querying {i}: from={from_node}, to={to_node}')
        path, number_of_states = run_dijkstra_and_return_all(g, from_node, to_node, 0, heuristic_type)
        end_time = datetime.datetime.now()
        delta = end_time - start_time
        # to milliseconds
        df.at[i, 'time'] = round(delta.total_seconds(), 4)
        df.at[i, 'total states'] = number_of_states
        df.at[i, 'path'] = path
        df.at[i, 'path length'] = len(path)
        # save path to file
        if save_path:
            save_to_file(nodes, path, 'output/test0321/path_' + str(from_node) + '-' + str(to_node)  +
                         str_append_to_file_name + '_' + today_str)

    # save testing results
    df.to_csv('output/test_result_' + str_append_to_file_name + '_' + today_str +'.csv')


if __name__ == "__main__":

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == 'test':
            run_test(str_append_to_file_name='with_obstacles_2_fix_hq_5', heuristic_type='astar', save_path=False)
        else:
            print('Wrong argument')
    else:
        # run a single query and save path to file
        nodes_1, edges_1 = read_map()
        nodes_new, nodes_with_coordinates, weights = preprocessing_map_to_adjacency_list_and_weight_dict(nodes_1,
                                                                                                         edges_1)
        g_2 = MyGraphWithAdjacencyList(nodes_new, nodes_with_coordinates, weights)
        obstacle = Obstacle(100, 40, 40, 70, 70, 0, 2000, sys.maxsize)
        obstacle2 = Obstacle(100, -50, -50, -30, -30, 2000, 3000, 1.5)
        g_2.add_obstacle(obstacle)
        g_2.add_obstacle(obstacle2)

        path_1 = run_dijkstra(g_2, 2892, 2592, 0, 'astar')
        print(path_1)
        # save_to_file(nodes_1, path_1, '0317_2892_2592_great_circle_distance')

# %%
