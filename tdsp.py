# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:59:14 2022

@author: yifei
"""

from heapq_modified import *
from model.State import State


# dijkstra with heap queue
def dijkstra(graph, start_vertex, end_vertex, start_time, heuristic_type, return_type='default'):
    graph.explored_states = 0
    graph.relaxed_edges = 0
    graph.explored = {}
    graph.number_of_total_obstacles_met = 0
    graph.number_of_unaccessible_obstacles_met = 0
    visited = []  # explored states
    speed = 1000 * 10
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
    while hq.hq:
        # try:
        current_state = hq.pop_state()
        # except KeyError as e:
        #     print('KeyError')
        #     return [], graph.explored_states

        current_vertex = current_state.get_node()
        current_timestep = current_state.get_timestep()
        # print("hq={0}, current_state={1}".format(hq, current_state))      
        # print("current_state: {0}".format(current_state))

        if current_state.is_goal():
            if return_type == 'detailed':
                return current_state.extract_path(), graph.explored_states, graph.number_of_total_obstacles_met, \
                       graph.number_of_unaccessible_obstacles_met, graph.explored, graph.relaxed_edges
            else:
                return current_state.extract_path()

        visited.append(current_vertex)
        # print('current vertex: ', current_vertex)
        # print('neighbours: ', graph.get_accessible_states(current_state))
        for neighbour in graph.get_accessible_states(current_state):
            graph.explored_states += 1

            if neighbour.get_node() not in visited:
                # relax
                # get distance between current_vertex and the neighbour
                # distance = graph.get_weight(current_vertex, neighbour.get_node())
                # new_distance = current_state.get_g() + distance
                # 0321 replace with time-dependent weight
                distance = graph.get_time_dependent_weight(current_vertex, neighbour.get_node(), current_timestep)
                new_distance = current_state.get_g() + distance
                previous_cost = neighbour.get_g()

                if new_distance < previous_cost:
                    new_timestep = current_timestep + distance // speed
                    neighbour.set_g(new_distance)
                    neighbour.set_timestep(new_timestep)
                    neighbour.set_parent(current_state)
                    neighbour.set_h(graph.get_heuristic(neighbour.get_node(), end_vertex))
                    graph.relaxed_edges += 1
                    # heapq.heappush(hq, neighbour) # issue: did not update, it's adding new
                    hq.add_state(neighbour)
                    graph.explored[neighbour.get_node()] = neighbour
                    # print('Push', neighbour)

    if return_type == 'detailed':
        return [], graph.explored_states, graph.number_of_total_obstacles_met, \
               graph.number_of_unaccessible_obstacles_met, graph.explored, graph.relaxed_edges
    else:
        return []
