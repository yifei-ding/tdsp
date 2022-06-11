import utils
import geopandas as gpd
import momepy
import networkx as nx
import pandas as pd
import pickle

MAP_FILE_NAME = 'data/selfmade sea grid map3.geojson'


def read_map(file_name=MAP_FILE_NAME):
    df = gpd.read_file(file_name)
    df.to_crs(epsg=4326)
    G = momepy.gdf_to_nx(df, approach="primal")

    # convert to weighted map
    weighted_G = nx.Graph()
    for data in G.edges(data=True):
        weighted_G.add_edge(data[0], data[1], weight=data[2]['length'])

    nodes, edges, W = momepy.nx_to_gdf(weighted_G, spatial_weights=True)

    # add x and y coordinate
    nodes['x'] = nodes['geometry'].x
    nodes['y'] = round(nodes['geometry'].y, 1)

    # connect left most with right most: -180 to 180
    mask1 = nodes[nodes['x'] == 180].sort_values(by=['y']).reset_index()['nodeID']
    mask2 = nodes[nodes['x'] == -180].sort_values(by=['y']).reset_index()['nodeID']

    n1 = mask1.shape[0]
    n2 = mask2.shape[0]
    if n1 == n2:  # check whether the size is same
        new_df = pd.DataFrame()
        new_df['weight'] = pd.Series([0] * n1)  # set weight to 0
        new_df['node_start'] = mask1
        new_df['node_end'] = mask2

    edges_new = pd.concat([edges, new_df], ignore_index=True)

    return nodes, edges_new


def get_neighbouring_nodes(node_id, edges):
    mask = (edges['node_start'] == node_id)
    list1 = list(edges[mask]['node_end'])

    mask = (edges['node_end'] == node_id)
    list2 = list(edges[mask]['node_start'])
    return list1 + list2


def preprocessing_map_to_adjacency_list_and_weight_dict(nodes, edges):
    adjacency_list = create_adjacency_list(nodes, edges)
    nodes_with_coordinates = create_nodes_dict_with_coordinates(nodes)
    weight_dict = create_weight_dict(edges, nodes_with_coordinates)
    return adjacency_list, nodes_with_coordinates, weight_dict


# 1
def create_adjacency_list(nodes, edges):
    result = {}
    nodes_list = nodes['nodeID'].to_list()
    for item in nodes_list:
        result[item] = get_neighbouring_nodes(item, edges)

    return result


# 2
def create_nodes_dict_with_coordinates(nodes):
    result = {}
    for i, row in nodes.iterrows():
        result[row['nodeID']] = (row['x'], row['y'])
    return result


# 3
def create_weight_dict(edges, nodes_with_coordinates):
    result = {}
    for i, row in edges.iterrows():
        # result[(row['node_start'], row['node_end'])] = row['weight']
        result[(row['node_start'], row['node_end'])] = utils.haversine(coord1=nodes_with_coordinates[row['node_start']],
                                                                       coord2=nodes_with_coordinates[row['node_end']])

    return result


# precompute distances between all landmark and all nodes TODO: replace with static Dijkstra
def get_distances_to_landmarks(landmarks, nodes_with_coordinates):
    result_size = len(landmarks)
    result = {k:{} for k in range(result_size)}
    for i, landmark in enumerate(landmarks):
        for node_id in nodes_with_coordinates.keys():
            result[i][node_id] = utils.haversine(landmark, nodes_with_coordinates[node_id])
    return result


if __name__ == "__main__":
    # nodes, edges = read_map()
    # nodes_new, nodes_with_coordinates, weights = preprocessing_map_to_adjacency_list_and_weight_dict(nodes,
    #                                                                                                  edges)
    #
    # dicts = {'nodes': nodes_new,
    #          'coordinates': nodes_with_coordinates,
    #          'weights': weights,
    #          'old_nodes': nodes}  # for storing geometrical path
    # # save
    # pickle.dump(dicts, open("data/map2.p", "wb"))

    map_info = pickle.load(open("data/map.p", "rb"))
    nodes_new, nodes_with_coordinates, weights = map_info['nodes'], map_info['coordinates'], map_info['weights']
    # a = list(nodes_with_coordinates.values()).index((0.0, 0.5))
    # print(a)
    # landmarks = [(90.0, 78.5), (90.0, -78.5), (-90.0, 78.5), (-90.0, -78.5),(180.0, 78.5), (180.0, -78.5),
    #              (45.0, 78.5), (45.0, -78.5), (-45.0, 78.5), (-45.0, -78.5),(0.0, 78.5), (0.0, -78.5),
    #              (90.0, 36.5), (90.0, -36.5), (-90.0, 36.5), (-90.0, -36.5), (180.0, 36.5), (180.0, -36.5),
    #              (45.0, 36.5), (45.0, -36.5), (-45.0, 36.5), (-45.0, -36.5), (0.0, 36.5), (0.0, -36.5),
    #              ]
    # landmarks_distances = get_distances_to_landmarks(landmarks, nodes_with_coordinates)
    # map_info['landmarks'] = landmarks
    # map_info['landmarks_distances'] = landmarks_distances
    # pickle.dump(map_info, open("data/map2_with_landmarks_4.p", "wb"))