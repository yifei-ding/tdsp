# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:59:14 2022

@author: youyang
"""


from shapely.geometry import Point, LineString
from geojson import Point, Feature, FeatureCollection, dump
from heapq_modified import *

import sys

class MyGraph(object):
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.visited = []

    def getNeighbouringNodes(self, node_id):
        mask = (self.edges['node_start'] == node_id)
        list1 = list(self.edges[mask]['node_end'])

        mask = (self.edges['node_end'] == node_id)
        list2 = list(self.edges[mask]['node_start'])

        return list1+list2

    def getDistance(self, u, v):
        mask = (self.edges['node_start'] == u) & (self.edges['node_end'] == v) | (
            self.edges['node_start'] == v) & (self.edges['node_end'] == u)
        return self.edges[mask].iloc[0]['weight']

    def getAccessibleStates(self, current_state):
        
        node_id = current_state.getNode()
        timestep = current_state.getTimestep()
        
        neighbours = self.getNeighbouringNodes(node_id)
        result = []

        # check if the neighbours are accessible at this timestep
        for item in neighbours:
            if self.isAccessible(item,timestep):
                if item in entry_finder:
                    result.append(entry_finder[item][2])
                else:
                    result.append(State.from_parent(item,current_state)) 
        return result
    
    def isAccessible(self, item, timestep):
        #TODO
        return True

    def addMovingObstacle(self, radius, speed, start_vertex, end_vertex):
        # TODO
        return None


class State(object):
    def __init__(self, node, timestep, cost, parent):
        self.node = node
        self.timestep = timestep
        self.cost = cost
        self.parent = parent
    
    @classmethod
    def from_parent(cls, node, parent):
        return cls(node=node, timestep=None, cost=sys.maxsize, parent=parent)
    
    
    
    def setTimestep(self, timestep):
        self.timestep = timestep

    def setCost(self, cost):
        self.cost = cost
        
    def setParent(self, parent):
        self.parent = parent
        
    def getNode(self):
        return self.node

    def getTimestep(self):
        return self.timestep
    
    def getCost(self):
        return self.cost

    def extractPath(self):
        state = self
        path = []
        path.append(state)
        while (state.parent is not None):    
            state = state.parent
            path.append(state)
        return path

    def __lt__(self, other):
        return self.cost < other.cost

    def __gt__(self, other):
        return self.cost > other.cost

    def __eq__(self, other):
        # and self.timestep == other.timestep and self.cost == other.cost
        return self.node == other.node and self.timestep == other.timestep
    
    def __repr__(self):
        return "node={0}, timestep={1}, cost={2}".format(self.node, self.timestep, self.cost)
    
    
    

# dijkstra with heap queue
def dijkstra(graph, start_vertex, end_vertex, start_time):

    visited = [] # explored states
    speed = 1000

    initial_state = State(start_vertex, start_time, 0, None)
    # hq = []
    # heapq.heappush(hq, initial_state)
    add_state(initial_state)
    while len(hq) > 0:   
        current_state = pop_state()
        current_vertex = current_state.getNode()
        current_timestep = current_state.getTimestep()
        # print("hq={0}, current_state={1}".format(hq, current_state))      
        # print("current_state: {0}".format(current_state))

        if current_vertex == end_vertex:
            return current_state.extractPath()

        visited.append(current_vertex)
        # print('current vertex: ', current_vertex)
        # print('neighbours: ', graph.getNeighbouringNodes(current_vertex))
        for neighbour in graph.getAccessibleStates(current_state):
            if neighbour.getNode() not in visited:
                # relax
                # get distance between current_vertex and the neighbour
                distance = graph.getDistance(current_vertex, neighbour.getNode())
                new_cost = current_state.getCost() + distance
                previous_cost = neighbour.getCost()

                if (new_cost < previous_cost):
                    new_timestep = current_timestep + distance // speed                   
                    neighbour.setCost(new_cost)
                    neighbour.setTimestep(new_timestep)
                    neighbour.setParent(current_state)
                    # heapq.heappush(hq, neighbour) # issue: did not update, it's adding new
                    add_state(neighbour)
                    # print('Push',neighbour)

    return None


def extractPath(path):
    result = []
    for item in path:
        result.append(item.getNode())
    return list(reversed(result))


def savePath(nodes, nodes_on_shortest_path, fileName):
    points = []
    for item in nodes_on_shortest_path:
        mask = nodes['nodeID'] == item
        points.append(nodes[mask].iloc[0]['geometry'])

    linestring_for_export = LineString(points)

    features = []
    features.append(Feature(geometry=linestring_for_export))
    feature_collection = FeatureCollection(features)
    fileName_str = 'myfile-'+fileName+'.geojson'
    with open(fileName_str, 'w') as f:
        dump(feature_collection, f)
    print('Saved!')
        


#%% test2: use self created graph
# import pandas as pd
# import numpy as np
# df2 = pd.DataFrame(np.array([[0, 1, 4], 
#                               [0, 6, 7], 
#                               [1, 2, 9],
#                               [1, 6, 11],
#                               [1, 7, 20],
#                               [6, 7, 1],
#                               [2, 4, 2],
#                               [2, 3, 6],
#                               [7, 4, 1],
#                               [7, 8, 3],
#                               [4, 3, 10], 
#                               [4, 5, 15],
#                               [4, 8, 5],
#                               [3, 5, 5],
#                               [8, 5, 12]    
                             
#                               ]),
#                     columns=['node_start', 'node_end', 'weight'])

# df3 = pd.DataFrame(np.array([0, 1,2,3,4,5,6,7,8]
#                           ),                    
    
#                     columns=['nodeID'])

# g2 = MyGraph(df3,df2)

# path = dijkstra(g2,0,8,0)

# print(extractPath(path))

