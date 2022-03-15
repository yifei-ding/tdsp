# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:59:14 2022

@author: yifei
"""
import numpy as np
from shapely.geometry import LineString
from geojson import Feature, FeatureCollection, dump

import utils
from heapq_modified import *
from State import State
from queue import PriorityQueue


class MyGraph(object):
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.explored_states = 0
        self.edges['time_dependent_weight'] = np.empty((len(self.edges), 0)).tolist()
        self.explored = {}  # for finding if a node is already explored (but not necessarily added to visited)
        self.heuristic_type = 'default'

    def get_neighbouring_nodes(self, node_id):
        mask = (self.edges['node_start'] == node_id)
        list1 = list(self.edges[mask]['node_end'])

        mask = (self.edges['node_end'] == node_id)
        list2 = list(self.edges[mask]['node_start'])

        return list1 + list2

    def get_weight(self, u, v):
        mask = (self.edges['node_start'] == u) & (self.edges['node_end'] == v) | (
                self.edges['node_start'] == v) & (self.edges['node_end'] == u)
        return self.edges[mask].iloc[0]['weight']

    def get_heuristic(self, u, v):
        if self.heuristic_type == 'astar':
            x1, y1 = self.nodes.iloc[u]['x'], self.nodes.iloc[u]['y']
            x2, y2 = self.nodes.iloc[v]['x'], self.nodes.iloc[v]['y']
            return utils.haversine(coord1=(x1, y1), coord2=(x2, y2))
        else:
            return 0

    def get_accessible_states(self, current_state):
        node_id = current_state.get_node()
        timestep = current_state.get_timestep()

        neighbours = self.get_neighbouring_nodes(node_id)
        result = []

        # check if the neighbours are accessible at this timestep
        for item in neighbours:
            edge_index = self.get_edge_by_two_endpoints(node_id, item)
            if self.is_accessible(edge_index, timestep):
                if item in self.explored:
                    result.append(self.explored[item])
                else:
                    result.append(State.from_parent(item, current_state))
        return result

    def is_accessible(self, edge_index, timestep):
        time_intervals = self.edges.iloc[edge_index]['time_dependent_weight']

        for interval in time_intervals:
            start_time = interval[0]
            end_time = interval[1]
            if start_time <= timestep <= end_time:
                print(f'Cannot enter: edge={edge_index}, timestep={timestep}')
                return False

        return True

    def add_moving_obstacle(self, speed, start_vertex, end_vertex, start_time):
        path = pure_dijkstra(self, start_vertex, end_vertex)
        for i, node in enumerate(path):
            if i < len(path) - 1:
                next_node_on_path = path[i + 1]
                travel_time = self.get_weight(node, next_node_on_path) // speed // 2
                # print(f'distance={self.get_distance(node, next_node_on_path)}, travel_time={travel_time}')
                temp = start_time
                end_time = temp + travel_time

                for neighbour in self.get_neighbouring_nodes(node):
                    edge_index = self.get_edge_by_two_endpoints(node, neighbour)
                    self.edges.at[edge_index, 'time_dependent_weight'].append((temp, end_time))

                start_time = end_time
            else:
                for neighbour in self.get_neighbouring_nodes(node):
                    edge_index = self.get_edge_by_two_endpoints(node, neighbour)
                    self.edges.at[edge_index, 'time_dependent_weight'].append((start_time, start_time + travel_time))

    def get_edge_by_two_endpoints(self, u, v):
        mask = (self.edges['node_start'] == u) & (self.edges['node_end'] == v) | (
                self.edges['node_start'] == v) & (self.edges['node_end'] == u)
        return self.edges[mask].index.tolist()[0]  # suppose there's one exact match

    def set_heuristic_type(self, heuristic_type):
        self.heuristic_type = heuristic_type

    def get_heuristic_type(self):
        return self.heuristic_type


# for path finding of the moving obstacle, using dijkstra and no time-dependency
def pure_dijkstra(graph, start_vertex, end_vertex):
    D = {v: float('inf') for v in range(len(graph.nodes))}  # initialize shortest distance for all nodes
    path = {v: -1 for v in range(len(graph.nodes))}  # initialize previous node along shortest path
    D[start_vertex] = 0  # the shortest path to the start vertex is 0
    path[start_vertex] = None  # the previous node of the start_vertex is None
    visited = []
    pq = PriorityQueue()
    pq.put((0, start_vertex))

    while not pq.empty():
        # print('priority queue: {0}'.format(pq.queue))
        (dist, current_vertex) = pq.get()
        if current_vertex == end_vertex:
            result = []
            node = end_vertex

            while node != start_vertex:
                result.append(node)
                node = path[node]

            result.append(start_vertex)
            return list(reversed(result))
        visited.append(current_vertex)
        # print('current vertex: ', current_vertex)
        # print('neighbours: ', graph.getNeighbouringNodes(current_vertex))
        for neighbour in graph.get_neighbouring_nodes(current_vertex):
            if neighbour not in visited:
                # relax
                distance = graph.get_weight(current_vertex,
                                            neighbour)  # get distance between current_vertex and the neighbour
                new_cost = D[current_vertex] + distance
                previous_cost = D[neighbour]

                if new_cost < previous_cost:
                    # if found shorter distance, update cost
                    pq.put((new_cost, neighbour))
                    # print('set ', neighbour,' = ', new_cost)
                    D[neighbour] = new_cost
                    path[neighbour] = current_vertex

    return None


# dijkstra with heap queue
def dijkstra(graph, start_vertex, end_vertex, start_time, heuristic_type):
    graph.explored_states = 0
    graph.explored = {}
    visited = []  # explored states
    speed = 1
    if heuristic_type == 'astar':
        graph.set_heuristic_type('astar')
        print(f'graph.heuristic_type={graph.get_heuristic_type()}')
    else:
        print(f'graph.heuristic_type={graph.get_heuristic_type()}')

    initial_state = State(start_vertex, start_time, 0, None, end_vertex)
    # hq = []
    # heapq.heappush(hq, initial_state)
    initial_state.set_h(graph.get_heuristic(start_vertex, end_vertex))
    hq = modified_heapq()
    hq.add_state(initial_state)
    while len(hq.hq) > 0:
        current_state = hq.pop_state()
        current_vertex = current_state.get_node()
        current_timestep = current_state.get_timestep()
        # print("hq={0}, current_state={1}".format(hq, current_state))      
        # print("current_state: {0}".format(current_state))

        if current_state.is_goal():
            return current_state.extract_path(), graph.explored_states

        visited.append(current_vertex)
        # print('current vertex: ', current_vertex)
        # print('neighbours: ', graph.get_accessible_states(current_state))
        for neighbour in graph.get_accessible_states(current_state):
            if neighbour.get_node() not in visited:
                # relax
                # get distance between current_vertex and the neighbour
                distance = graph.get_weight(current_vertex, neighbour.get_node())
                new_distance = current_state.get_g() + distance
                previous_cost = neighbour.get_g()

                if new_distance < previous_cost:
                    new_timestep = current_timestep + distance // speed
                    neighbour.set_g(new_distance)
                    neighbour.set_timestep(new_timestep)
                    neighbour.set_parent(current_state)
                    neighbour.set_h(graph.get_heuristic(neighbour.get_node(), end_vertex))

                    # heapq.heappush(hq, neighbour) # issue: did not update, it's adding new
                    hq.add_state(neighbour)
                    graph.explored_states += 1
                    graph.explored[neighbour.get_node()] = neighbour
                    # print('Push',neighbour)

    return [], graph.explored_states


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
# print(g2.add_moving_obstacle(1, 0, 6, 2))
#
# path, number_of_states = dijkstra(g2, 0, 8, 0)
#
# print(extract_path(path), number_of_states)
# # %%
# index = 6
# timestep = 3
# time_intervals = df2.iloc[index]['time_dependent_weight']
#
# for interval in time_intervals:
#     start_time = interval[0]
#     end_time = interval[1]
#     if timestep >= start_time and timestep <= end_time:
#         print(True)
#
#     print(False)
