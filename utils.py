def haversine(coord1, coord2):
    """the Great-circle distance """
    import math
    # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    R = 6371000  # radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c  # output distance in meters

    return round(meters)

def calculate_line_segment_length(x1, y1, x2, y2):
    # TODO: fix distance calculation
    import math
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def pure_dijkstra(graph, start_vertex, end_vertex):
    """for path finding of the moving obstacle, using dijkstra and no time-dependency"""
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