# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 15:49:32 2022

@author: yifei
"""
import datetime
import pickle
import sys


import pandas as pd
from datetime import date

from shapely.geometry import LineString
from geojson import Feature, FeatureCollection, dump

from model.Obstacle import Obstacle
from model.mygraph import MyGraphWithAdjacencyList

from tdsp import *

MAP_PICKLE_FILE_NAME = 'data/map.p'  # geojson map file converted to dict and stored in pickle file
TEST_FILE_NAME = 'data/test_50.csv'
OBSTACLE_FILE_NAME = 'data/obstacles.csv'


def run_dijkstra_and_return_path(g, from_node, to_node, start_time, heuristic_type='default', return_type='default'):
    path = dijkstra(g, from_node, to_node, start_time, heuristic_type, return_type)
    return path
    # problem with 2134 to 2038 solved


def run_dijkstra_and_return_all(g, from_node, to_node, start_time, heuristic_type='default', return_type='detailed'):
    return dijkstra(g, from_node, to_node, start_time, heuristic_type, return_type)


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


def get_obstacles(number_of_obstacles=10):
    df = pd.read_csv(OBSTACLE_FILE_NAME)
    df = df.sample(n=number_of_obstacles, random_state=1)
    # df = df[df['coefficient'] >= 1] #only slow obstacles
    result = []
    for i, row in df.iterrows():
        radius = row['radius'] * 1000 * 10  # to kilometers, and then multiply by 10 to further increase size
        x1, y1, x2, y2 = row['x1'], row['y1'], row['x2'], row['y2']
        start, end = row['start'], row['end']
        coefficient = row['coefficient']
        obstacle_temp = Obstacle(radius, x1, y1, x2, y2, start, end, coefficient)
        result.append(obstacle_temp)
    return result


# %%

def run_test(heuristic_type='default', str_append_to_file_name='a', save_path=False, number_of_obstacles=10,
             return_type='default'):
    # read map
    map_info = pickle.load(open(MAP_PICKLE_FILE_NAME, "rb"))
    nodes_new, nodes_with_coordinates, weights = map_info['nodes'], map_info['coordinates'], map_info['weights']
    # construct graph
    g = MyGraphWithAdjacencyList(nodes_new, nodes_with_coordinates, weights)
    # add obstacles from list
    # obstacle_list = get_obstacles(number_of_obstacles)
    # g.add_obstacle_by_list(obstacle_list)
    # run dijkstra and count time
    today = date.today()
    today_str = today.strftime("%m%d")
    df = pd.read_csv(TEST_FILE_NAME)
    df['time'] = ''
    df['total states'] = ''
    df['path length'] = ''
    df['path'] = ''
    if return_type == 'detailed':
        df['obstacles'] = ''
        df['unaccessible obstacles'] = ''

    for i, row in df.iterrows():
        from_node = row['from']
        to_node = row['to']
        # count time
        start_time = datetime.datetime.now()
        print(f'Querying {i}: from={from_node}, to={to_node}')
        path, number_of_states, number1, number2, _ = run_dijkstra_and_return_all(g, from_node, to_node, 0,
                                                                                  heuristic_type, )
        end_time = datetime.datetime.now()
        delta = end_time - start_time
        # to milliseconds
        df.at[i, 'time'] = round(delta.total_seconds(), 4)
        df.at[i, 'total states'] = number_of_states
        df.at[i, 'path'] = path
        df.at[i, 'path length'] = len(path)
        df.at[i, 'obstacles'] = number1
        df.at[i, 'unaccessible obstacles'] = number2

        # save each path to file
        if save_path:
            save_to_file(map_info['old_nodes'], path, 'output/test0321/path_' + str(from_node) + '-' + str(to_node) +
                         str_append_to_file_name + '_' + today_str)

    # save testing results
    df.to_csv('output/test_result_' + str_append_to_file_name + '_' +str(number_of_obstacles) + '_' +
              heuristic_type + '_' + today_str + '.csv')


if __name__ == "__main__":

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == 'test':
            run_test(str_append_to_file_name='rerun_test', heuristic_type='astar', save_path=False,
                     number_of_obstacles=50)
        if arg == 'test2':
            run_test(str_append_to_file_name='test_with_detail_results2_no_obstacle', heuristic_type='astar', save_path=False,
                     number_of_obstacles=50, return_type='detailed')
        else:
            print('Wrong argument')
    else:
        # run a single query and save path to file
        map_info = pickle.load(open(MAP_PICKLE_FILE_NAME, "rb"))
        nodes_new, nodes_with_coordinates, weights = map_info['nodes'], map_info['coordinates'], map_info['weights']

        g_2 = MyGraphWithAdjacencyList(nodes_new, nodes_with_coordinates, weights)
        # obstacle_list = get_obstacles(50)
        # g_2.add_obstacle_by_list(obstacle_list)

        from_node = 8004
        to_node = 4831
        today = date.today()
        today_str = today.strftime("%m%d")
        str_append_to_file_name = 'check_heuristic'
        heuristic_type = 'astar'
        start_time = datetime.datetime.now()
        path, number_of_states, total_obstacles, unaccessible_edges, explored = \
            run_dijkstra_and_return_all(g_2, from_node, to_node, 0, 'astar')
        end_time = datetime.datetime.now()
        delta = end_time - start_time
        print(f'path = {path}, time = {round(delta.total_seconds(), 4)}, states = {number_of_states}, total_obstacles = '
              f'{total_obstacles}, unaccessible_edges={unaccessible_edges}')
        # save_to_file(map_info['old_nodes'], path, 'output/test0417/path_' + str(from_node) + '-' + str(to_node) +
        #              str_append_to_file_name + '_' + heuristic_type + '_' + today_str)

