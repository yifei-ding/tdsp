# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 15:24:04 2022

@author: yifei
"""

import sys
import utils
from model.State import State


class MyGraphWithAdjacencyList(object):
    """new graph with adjacency list"""

    def __init__(self, nodes, nodes_with_coordinates, weights, landmark=None):
        self.nodes = nodes  # in adjacency list
        self.nodes_with_coordinates = nodes_with_coordinates  # {node: (x,y))}
        self.weights = weights
        self.explored_states = 0
        self.relaxed_edges = 0
        self.explored = {}  # for finding if a node is already explored (but not necessarily added to visited)
        self.heuristic_type = 'default'
        self.obstacles = []
        self.number_of_total_obstacles_met = 0
        self.number_of_unaccessible_obstacles_met = 0
        self.landmark = landmark

    def get_neighbouring_nodes(self, node_id):
        return self.nodes[node_id]

    def get_weight(self, u, v):
        """ for undirected graph """
        if (u, v) in self.weights:
            return self.weights[(u, v)]
        elif (v, u) in self.weights:
            return self.weights[(v, u)]
        else:
            return -1

    def set_heuristic_type(self, heuristic_type):
        self.heuristic_type = heuristic_type

    def get_heuristic_type(self):
        return self.heuristic_type

    def get_accessible_states(self, current_state):
        node_id = current_state.get_node()
        timestep = current_state.get_timestep()
        neighbours = self.get_neighbouring_nodes(node_id)
        result = []

        # check if the neighbours are accessible at this timestep
        for item in neighbours:
            time_dependent_weight = self.get_time_dependent_weight(node_id, item, timestep)

            if time_dependent_weight is not None:  # if the neighbour is accessible
                if item in self.explored:
                    result.append(self.explored[item])
                else:
                    result.append(State.from_parent(item, current_state))
            # else:
            #     print(f'edge({node_id}, {item}) is not accessible at timestep {timestep}')

        # print(f'current state = {current_state}, result =  {len(result)}')

        return result

    def get_heuristic(self, u, v):
        if self.heuristic_type == 'astar':
            return utils.haversine(coord1=self.nodes_with_coordinates[u], coord2=self.nodes_with_coordinates[v])
        elif self.heuristic_type == 'landmark':
            max_value = 0
            for i in range(0, 24):
                max_value = max(abs(self.landmark[i][u] - self.landmark[i][v]), max_value)
            return max_value
        else:
            return 0

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def add_obstacle_by_list(self, obstacle_list):
        self.obstacles = obstacle_list

    def get_time_dependent_weight(self, u, v, timestep):
        result = 1  # default coefficient is 1
        for obstacle in self.obstacles:
            if self.cross(u, v, obstacle, timestep):
                self.number_of_total_obstacles_met += 1
                if result < obstacle.get_coefficient():
                    result = obstacle.get_coefficient()  # take the max coefficient in all overlapping obstacles
        if result == 9999:
            self.number_of_unaccessible_obstacles_met += 1
            return None
        else:
            return result * self.get_weight(u, v)

    def cross(self, u, v, obstacle, t):
        """To check if an obstacle is overlapping/crossing the edge(u,v) at timestep t"""
        # TODO: to find a distance between a point and a curve on the sphere
        if obstacle.get_obstacle_location(t):  # if 
            x0, y0 = obstacle.get_obstacle_location(t)
            x1, y1 = self.nodes_with_coordinates[u]
            x2, y2 = self.nodes_with_coordinates[v]

            # calculate the distance between point(x,y) and the edge(u,v)
            line_segment_length = utils.calculate_line_segment_length(x1, y1, x2, y2)
            if line_segment_length < 0.00000001:
                # print('line segment length = 0')
                return utils.calculate_line_segment_length(x1, y1, x0, y0) < obstacle.get_radius()
            else:
                u1 = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1))
                u = u1 / (line_segment_length ** 2)
                if u < 0.00001 or u > 1:
                    distance_to_point1 = utils.calculate_line_segment_length(x1, y1, x0, y0)
                    distance_to_point2 = utils.calculate_line_segment_length(x2, y2, x0, y0)
                    if distance_to_point1 > distance_to_point2:
                        distance = distance_to_point2
                    else:
                        distance = distance_to_point1
                else:
                    projection_point_x = x1 + u * (x2 - x1)
                    projection_point_y = y1 + u * (y2 - y1)
                    distance = utils.calculate_line_segment_length(x0, y0, projection_point_x, projection_point_y)

            return distance < obstacle.get_radius()
        else:
            return False
