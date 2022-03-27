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
import sys
# obstacle = Obstacle(100, 40, 40, 70, 70, 0, 2000, 1)
# obstacle2 = Obstacle(100, -50, -50, -30,-30, 0, 10000, 1)
obstacle3 = Obstacle(1000000,160, 25, 160, 22,2800, 4400, 9999)
#%%
g2 = MyGraphWithAdjacencyList(nodes_new, nodes_with_coordinates, weights)
# g2.add_obstacle(obstacle)
# g2.add_obstacle(obstacle2)
g2.add_obstacle(obstacle3)
print(g2.obstacles)

#%%
import numpy as np
path = dijkstra(g2, 2258, 8261, 0, 'astar')[0]
print(path)
# path2 = dijkstra(g2, 3363, 5910, 1000, 'astar')[0]


#%% transform into time series for animation

import numpy as np

def interpolate_df(df):
    a = df['timestep'].min()
    b = df['timestep'].max()
    
    df.index = df['timestep']
    time_new = np.linspace(a,b,b-a+1)
    df_new = df.reindex(time_new).interpolate(methond='index')
    return df_new
    
def get_obstalce_moving_df(obstacle, name='obstacle'):
    # for visualizing an obstacle
    df2 = pd.DataFrame()
    df2['lon'] = [obstacle.get_start_x(), obstacle.get_end_x()]
    df2['lat'] = [obstacle.get_start_y(), obstacle.get_end_y()]
    df2['timestep'] = [obstacle.get_start_time(), obstacle.get_end_time()]
    
    a = df2['timestep'].min()
    b = df2['timestep'].max()
    
    df2.drop_duplicates(subset = ['timestep'], inplace=True)
    df2.index = df2['timestep']
    
    time_new = np.linspace(a,b,b-a+1)
    df_new = df2.reindex(time_new).interpolate(methond='index')
    df_new['type'] = [name] * (b-a+1)
    # df_new['size'] = [obstacle.get_radius() // 100] * (b-a+1)
    df_new['size'] = [10] * (b-a+1)

    df_new = df_new[df_new['timestep'] % 100 == 0]
    return df_new

def get_path_moving_df(nodes_with_coordinates, path, name = 'path'):
    # for visualizing a path
    df2 = pd.DataFrame()
    df2['lon'] = [nodes_with_coordinates[x.get_node()][0] for x in path]
    df2['lat'] = [nodes_with_coordinates[y.get_node()][1] for y in path]
    df2['timestep'] = [int(x.get_timestep()) for x in path]    
    duplicate_mask = df2['timestep'].duplicated
    c = df2[duplicate_mask()].index
    if c.shape[0] == 1:
        print('has duplicate. path cross +- 180 longitude')
        split_point = c[0]
        temp_df1 = interpolate_df(df2[:split_point])
        temp_df2 = interpolate_df(df2[split_point:])
        df_new = pd.concat([temp_df1,temp_df2]).drop_duplicates(
            subset = ['timestep'])    
        df_new = df_new[df_new['timestep'] % 100 == 0]         
    elif c.shape[0] ==0:
        print('no duplicate')    
        df_new = interpolate_df(df2)
        df_new = df_new[df_new['timestep'] % 100 == 0]
    else:
        print('multiple duplicates')
        
    n = df_new.shape[0]

    df_new['type'] = [name] * n
    df_new['size'] = [5] * n 
    # df_new.to_csv('test_path4_interpolate.csv')
    return df_new



#%%
# a = get_obstalce_moving_df(obstacle, name = 'obstacle1')
# b = get_obstalce_moving_df(obstacle2, name = 'obstacle2')
# b_1 = get_obstalce_moving_df(obstacle3, name = 'obstacle3')
c = get_path_moving_df(nodes_with_coordinates, path, name = 'path1')
# d = get_path_moving_df(nodes_with_coordinates, path2, name = 'path2')

    
# result = pd.concat([b_1,c])

c.to_csv('test_path_with_obstacle_5.csv')
#%% interpolation
# import numpy as np

# list1 = [x for x in range(40,49,2)]  
# list2 = [30]* 5
# time = [1,4,6,7,11] 
# df4 = pd.DataFrame()
# df4['lat'] = list1
# df4['lon'] = list2
# df4['timestep'] = time
# a = df4['timestep'].min()
# b = df4['timestep'].max()

# df4.index = df4['timestep']

# time_new = np.linspace(a,b,b-a+1)
# df_new = df4.reindex(time_new).interpolate(methond='index')


#%%
df1 = pd.read_csv('test_path_no_obstacle.csv')
df2 = pd.read_csv('test_path_with_obstacle_5.csv')


df1['type'] = 'path1_no_obstacle'
result = pd.concat([df1,df2])
result.to_csv('comparison.csv')
