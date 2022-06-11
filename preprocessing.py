import utils
import geopandas as gpd
import momepy
import networkx as nx
import pandas as pd
import pickle
import composition

map_file_1 = 'data/map.p'
map_file_2 = 'data/map2.p'




# 1. read map (L0 graph)
map_info = pickle.load(open(map_file_1, "rb"))
nodes_new, nodes_with_coordinates, weights = map_info['nodes'], map_info['coordinates'], map_info['weights']
coordinate_to_node = {v: k for k, v in nodes_with_coordinates.items()}

## preprocessing
#2. read obstacles
#3. add time-dependent weight to L0 graph


#4. for number of layers, add layer from bottom to top
density = 2 # depending on the input map: 1 for map.p; 2 for map2.p

step = density * 2 # depending on which layer, L1 - *2, L2 - *4, L3 - *8, etc

count = 0
for i in range(-180,181,step):
    for j_prime in range(-76,77,step):   
        j = j_prime +0.5 
        if (i,j) in coordinate_to_node:
            node1 = coordinate_to_node[(i,j)]
            # do the same for eight directions 
            if (i+step//2,j) in coordinate_to_node:
                temp =  coordinate_to_node[(i+step//2,j)]
            if (i+step,j) in coordinate_to_node:
                node1_right =  coordinate_to_node[(i+step,j)]
            if (node1,temp) in weights and (temp,node1_right) in weights:             
                count +=1
                nodes_new[node1].append(node1_right) #add to adjacency list
                weights[(node1,node1_right)] = weights[(node1,temp)] + weights[(temp,node1_right)]  #add to weight new d(u,v)
                
                weight1, weight2 = time_dependent_weight[(node1,temp)], time_dependent_weight[(temp,node1_right)]
                merged_time_dependent_weight = composition.merge(weight1,weight2) # time-depedent function merge
                time_dependent_weight[(node1,node1_right)] = merged_time_dependent_weight # add to time dependent weight
                
            
            # if (i,j+step//2) in coordinate_to_node and (i,j+step) in coordinate_to_node:
            #     count +=1
            #     nodes_new[coordinate_to_node[(i,j)]].append(coordinate_to_node[(i,j+step)])
            
            # if (i+step//2,j+step//2) in coordinate_to_node and (i+step,j+step) in coordinate_to_node:
            #     count +=1
            #     nodes_new[coordinate_to_node[(i,j)]].append(coordinate_to_node[(i+step,j+step)])
            # if (i+step//2,j-step//2) in coordinate_to_node and  (i+step,j-step) in coordinate_to_node:
            #     count +=1
            #     nodes_new[coordinate_to_node[(i,j)]].append(coordinate_to_node[(i+step,j-step)])
print(count)