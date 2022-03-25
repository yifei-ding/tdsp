# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 11:20:05 2022

@author: yifei
"""
import pandas as pd
from main import preprocessing_map_to_adjacency_list_and_weight_dict, read_map
from model.Obstacle import Obstacle
from model.mygraph import MyGraphWithAdjacencyList
from tdsp import dijkstra

MAP_FILE_NAME = 'data/selfmade sea grid map2.geojson'

# %%
nodes, edges = read_map(file_name=MAP_FILE_NAME)

# %%
nodes_new, nodes_with_coordinates, weights = preprocessing_map_to_adjacency_list_and_weight_dict(nodes, edges)

# %%
obstacle = Obstacle(100, 40, 40, 70, 70, 0, 2000, 1.2)
obstacle2 = Obstacle(100, -50, -50, -30,-30, 0, 10000, 1.5)

print(obstacle)

#%%
g2 = MyGraphWithAdjacencyList(nodes_new, nodes_with_coordinates, weights)
g2.add_obstacle(obstacle)
g2.add_obstacle(obstacle2)

#%%
print(g2.obstacles)
#%%
import numpy as np
path = dijkstra(g2, 2258, 8261, 0, 'astar')[0]
df2 = pd.DataFrame()
df2['lon'] = [nodes_with_coordinates[x.get_node()][0] for x in path]
df2['lat'] = [nodes_with_coordinates[x.get_node()][1] for x in path]
df2['timestep'] = [int(x.get_timestep()) for x in path]

a = df2['timestep'].min()
b = df2['timestep'].max()

df2.drop_duplicates(subset = ['timestep'], inplace=True)
df2.index = df2['timestep']

time_new = np.linspace(a,b,b-a+1)
df_new = df2.reindex(time_new).interpolate(methond='index')
df_new['type'] = ['path1'] * (b-a+1)
df_new['size'] = [1] * (b-a+1)
#%%
df_new = df_new[df_new['timestep'] % 100 == 0]
df_new.to_csv('test_path4_interpolate.csv')


#%%
path2 = dijkstra(g2, 3363, 5910, 1000, 'astar')[0]

df3 = pd.DataFrame()
df3['lon'] = [nodes_with_coordinates[x.get_node()][0] for x in path2]
df3['lat'] = [nodes_with_coordinates[x.get_node()][1] for x in path2]
df3['timestep'] = [x.get_timestep() for x in path2]
df3['type'] = ['path2'] * len(path2)
df3['size'] = [10] * len(path2)
#%%
result = pd.concat([df2,df3])
#%%
result.to_csv('test_path.csv')

#%% interpolation
import numpy as np

list1 = [x for x in range(40,49,2)]  
list2 = [30]* 5
time = [1,4,6,7,11] 
df4 = pd.DataFrame()
df4['lat'] = list1
df4['lon'] = list2
df4['timestep'] = time
a = df4['timestep'].min()
b = df4['timestep'].max()

df4.index = df4['timestep']

time_new = np.linspace(a,b,b-a+1)
df_new = df4.reindex(time_new).interpolate(methond='index')

