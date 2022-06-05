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
from geojson import Point, Feature, FeatureCollection, dump

import utils
from model.Obstacle import Obstacle
from model.mygraph import MyGraphWithAdjacencyList

from tdsp import *
import json

MAP_PICKLE_FILE_NAME = 'data/map2_with_landmarks_4.p'  # geojson map file converted to dict and stored in pickle file
TEST_FILE_NAME = 'data/test_50.csv'
OBSTACLE_FILE_NAME = 'data/obstacles.csv'

# OUTPUT_ROOT ='output/animation/'
OUTPUT_ROOT = '../../4 Online learning/js-samples/data/'  # to google js sample for animation


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
    fileName_str = OUTPUT_ROOT + file_name + '.geojson'
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
    landmarks = map_info['landmarks_distances']
    # construct graph
    g = MyGraphWithAdjacencyList(nodes_new, nodes_with_coordinates, weights, landmarks)
    # add obstacles from list
    obstacle_list = get_obstacles(number_of_obstacles)
    g.add_obstacle_by_list(obstacle_list)
    # run dijkstra and count time
    today = date.today()
    today_str = today.strftime("%m%d")
    df = pd.read_csv(TEST_FILE_NAME)
    df['time'] = ''
    df['total states'] = ''
    df['relaxed edges'] = ''
    df['path length'] = ''
    df['total obstacles'] = ''
    df['unaccessible obstacles'] = ''
    df['path'] = ''

    for i, row in df.iterrows():
        from_node = row['from']
        to_node = row['to']
        # count time
        start_time = datetime.datetime.now()
        print(f'Querying {i}: from={from_node}, to={to_node}')
        path, number_of_states, number1, number2, _, relaxed_edges = run_dijkstra_and_return_all(g, from_node, to_node,
                                                                                                 0,
                                                                                                 heuristic_type, )
        end_time = datetime.datetime.now()
        delta = end_time - start_time
        # to milliseconds
        df.at[i, 'time'] = round(delta.total_seconds(), 4)
        df.at[i, 'total states'] = number_of_states
        df.at[i, 'path'] = path
        df.at[i, 'path length'] = len(path)
        df.at[i, 'total obstacles'] = number1
        df.at[i, 'unaccessible obstacles'] = number2
        df.at[i, 'relaxed edges'] = relaxed_edges

        # save each path to file
        if save_path:
            save_to_file(map_info['old_nodes'], path,
                         'output/test0418/path_' + str(i) + '_' + str(from_node) + '-' + str(to_node) +
                         str_append_to_file_name + '_' + today_str)

    # save testing results
    df.to_csv('output/test_result_' + str_append_to_file_name + '_' + str(number_of_obstacles) + '_' +
              heuristic_type + '_' + today_str + '.csv')





def obstacles_save_to_json(obstacle_list):
    final_result = []
    for item in obstacle_list:
        result_path = [[item.get_start_x(), item.get_start_y()], [item.get_end_x(), item.get_end_y()]]
        result_timestep = [item.get_start_time(), item.get_end_time()]
        result = {'vendor': 1, "path": result_path, 'timestamps': result_timestep}
        final_result.append(result)

    with open("obstacles.json", "w") as outfile:
        json.dump(final_result, outfile)


def path_and_obstacle_save_to_json(obstacle_list, nodes_with_coordinates, path, file_name):
    result_path = []
    result_timestep = []
    final_result = []
    # path
    for item in path:
        result_path.append(list(nodes_with_coordinates[item.get_node()]))
        result_timestep.append(item.get_timestep())
    result = {'vendor': 0, "path": result_path, 'timestamps': result_timestep}
    final_result.append(result)
    # obstacles
    for item in obstacle_list:
        result_path = [[item.get_start_x(), item.get_start_y()], [item.get_end_x(), item.get_end_y()]]
        result_timestep = [item.get_start_time(), item.get_end_time()]
        result = {'vendor': 1, "path": result_path, 'timestamps': result_timestep}
        final_result.append(result)

    with open(OUTPUT_ROOT + str(file_name) + ".json", "w") as outfile:
        json.dump(final_result, outfile)


def search_space_save_to_json(nodes_with_coordinates, explored, file_name):
    s = set()
    points = []
    for item in explored:
        s.add(item)
    for item in s:
        point = Point(nodes_with_coordinates[item])
        points.append(Feature(geometry=point))

    feature_collection = FeatureCollection(points)

    with open(OUTPUT_ROOT + file_name + '.geojson', 'w') as f:
        dump(feature_collection, f)
    print('search space points saved!')


if __name__ == "__main__":

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == 'test':
            run_test(str_append_to_file_name='rerun_test', heuristic_type='astar', save_path=False,
                     number_of_obstacles=50)
        if arg == 'test2':
            run_test(str_append_to_file_name='test_50_obstacle_24_landmark', heuristic_type='landmark', save_path=False,
                     number_of_obstacles=50, return_type='detailed')
        else:
            print('Wrong argument')
    else:
        # run a single query and save path to file
        # load data and construct graph
        map_info = pickle.load(open(MAP_PICKLE_FILE_NAME, "rb"))
        nodes_new, nodes_with_coordinates, weights = map_info['nodes'], map_info['coordinates'], map_info['weights']
        landmarks = map_info['landmarks_distances']
        g_2 = MyGraphWithAdjacencyList(nodes_new, nodes_with_coordinates, weights, landmarks)
        # read query and obstacle positions from json
        f = open('data/input.json')
        input_data = json.load(f)
        start_node = input_data['start_node']
        end_node = input_data['end_node']
        obstacles = input_data['obstacles']
        f.close()
        # add obstacles to graph
        obstacle_list = []
        # for item in obstacles:
        #     start = item['obstacle_start_node']
        #     end = item['obstacle_end_node']
        #     start_time = item['obstacle_start_time']
        #     end_time = item['obstacle_end_time']
        #     radius = item['obstacle_radius'] * 111 * 1000
        #     coefficient = item['obstacle_coefficient']
        #     obstacle1 = Obstacle(radius, start[0], start[1],
        #                          end[0], end[1], start_time, end_time, coefficient)
        #     obstacle_list.append(obstacle1)
        # g_2.add_obstacle_by_list(obstacle_list)

        # get query start and end node
        from_coord = tuple(start_node)
        to_coord = tuple(end_node)
        from_node = list(nodes_with_coordinates.values()).index(from_coord)
        to_node = list(nodes_with_coordinates.values()).index(to_coord)

        # do query
        start_time = datetime.datetime.now()
        path, number_of_states, total_obstacles, unaccessible_edges, explored, relaxed_edges = \
            run_dijkstra_and_return_all(g_2, from_node, to_node, 0, heuristic_type='landmark')
        end_time = datetime.datetime.now()
        delta = end_time - start_time

        # output
        today = date.today()
        today_str = today.strftime("%m%d")
        str_append_to_file_name = 'sample'

        print(f'geodesic distance={utils.haversine(from_coord, to_coord)}')
        print(
            f'travel time = {path[-1].get_timestep()}, path length = {len(path)}, time = {round(delta.total_seconds(), 4)} \n'
            f'total states = {number_of_states}, number of relaxed edges={relaxed_edges} \n'
            f'unaccessible/total met obstacles = {unaccessible_edges}/{total_obstacles} \n')

        temp_str = ''
        for item in path:
            temp_str += f'[node = {nodes_with_coordinates[item.get_node()]}, time = {item.get_timestep()}], '
        print(temp_str)

        search_space_save_to_json(nodes_with_coordinates, explored, 'search_space')

        path_and_obstacle_save_to_json(obstacle_list, nodes_with_coordinates, path, str_append_to_file_name + today_str)
        save_to_file(map_info['old_nodes'], path, str_append_to_file_name + today_str)
