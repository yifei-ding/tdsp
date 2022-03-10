# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:59:14 2022

@author: yifei
"""

from shapely.geometry import Point, LineString
from geojson import Point, Feature, FeatureCollection, dump
from heapq_modified import *
from State import State


class MyGraph(object):
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.visited = []

    def get_neighbouring_nodes(self, node_id):
        mask = (self.edges['node_start'] == node_id)
        list1 = list(self.edges[mask]['node_end'])

        mask = (self.edges['node_end'] == node_id)
        list2 = list(self.edges[mask]['node_start'])

        return list1 + list2

    def get_distance(self, u, v):
        mask = (self.edges['node_start'] == u) & (self.edges['node_end'] == v) | (
                self.edges['node_start'] == v) & (self.edges['node_end'] == u)
        return self.edges[mask].iloc[0]['weight']

    def get_accessible_states(self, current_state):

        node_id = current_state.get_node()
        timestep = current_state.get_timestep()

        neighbours = self.get_neighbouring_nodes(node_id)
        result = []

        # check if the neighbours are accessible at this timestep
        for item in neighbours:
            if self.is_accessible(item, timestep):
                if item in entry_finder:
                    result.append(entry_finder[item][2])
                else:
                    result.append(State.from_parent(item, current_state))
        return result

    def is_accessible(self, item, timestep):
        # TODO
        return True

    def add_moving_obstacle(self, radius, speed, start_vertex, end_vertex):
        # TODO
        return None


# dijkstra with heap queue
def dijkstra(graph, start_vertex, end_vertex, start_time):
    visited = []  # explored states
    speed = 1000

    initial_state = State(start_vertex, start_time, 0, None, end_vertex)
    # hq = []
    # heapq.heappush(hq, initial_state)
    add_state(initial_state)
    while len(hq) > 0:
        current_state = pop_state()
        current_vertex = current_state.get_node()
        current_timestep = current_state.get_timestep()
        # print("hq={0}, current_state={1}".format(hq, current_state))      
        # print("current_state: {0}".format(current_state))

        if current_state.is_goal():
            return current_state.extract_path()

        visited.append(current_vertex)
        # print('current vertex: ', current_vertex)
        # print('neighbours: ', graph.getNeighbouringNodes(current_vertex))
        for neighbour in graph.get_accessible_states(current_state):
            if neighbour.get_node() not in visited:
                # relax
                # get distance between current_vertex and the neighbour
                distance = graph.get_distance(current_vertex, neighbour.get_node())
                new_distance = current_state.get_g() + distance
                previous_cost = neighbour.get_g()

                if new_distance < previous_cost:
                    new_timestep = current_timestep + distance // speed
                    neighbour.set_g(new_distance)
                    neighbour.set_timestep(new_timestep)
                    neighbour.set_parent(current_state)
                    # heapq.heappush(hq, neighbour) # issue: did not update, it's adding new
                    add_state(neighbour)
                    # print('Push',neighbour)

    return None


def extract_path(path2):
    result = []
    for item in path2:
        result.append(item.get_node())
    return list(reversed(result))


def save_path(nodes, nodes_on_shortest_path, file_name):
    points = []
    for item in nodes_on_shortest_path:
        mask = nodes['nodeID'] == item
        points.append(nodes[mask].iloc[0]['geometry'])

    linestring_for_export = LineString(points)

    features = [Feature(geometry=linestring_for_export)]
    feature_collection = FeatureCollection(features)
    fileName_str = 'output/my_file_' + file_name + '.geojson'
    with open(fileName_str, 'w') as f:
        dump(feature_collection, f)
    print('Saved!')


# %% test2: use self created graph
# import pandas as pd
# import numpy as np
#
# df2 = pd.DataFrame(np.array([[0, 1, 4],
#                              [0, 6, 7],
#                              [1, 2, 9],
#                              [1, 6, 11],
#                              [1, 7, 20],
#                              [6, 7, 1],
#                              [2, 4, 2],
#                              [2, 3, 6],
#                              [7, 4, 1],
#                              [7, 8, 3],
#                              [4, 3, 10],
#                              [4, 5, 15],
#                              [4, 8, 5],
#                              [3, 5, 5],
#                              [8, 5, 12]
#
#                              ]),
#                    columns=['node_start', 'node_end', 'weight'])
#
# df3 = pd.DataFrame(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8]
#                             ),
#
#                    columns=['nodeID'])
#
# g2 = MyGraph(df3, df2)
#
# path = dijkstra(g2, 0, 8, 0)
#
# print(extract_path(path))
