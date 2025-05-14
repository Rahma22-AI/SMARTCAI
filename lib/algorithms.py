import heapq
import math
import pandas as pd
from data import all_nodes, df_existing, df_traffic, transit_routes, df_neighborhoods

route_cache = {}

def a_star(start, goal, graph, priority=False):
    """
    A* algorithm for shortest path with optional priority for emergency vehicles.

    Args:
        start (str): Starting node name.
        goal (str): Destination node name.
        graph (nx.Graph): Weighted graph with 'weight' edge attributes.
        priority (bool): If True, reduces edge weights by 50% for priority mode.

    Returns:
        list: Shortest path from start to goal, or empty list if no path exists.

    Time Complexity: O(E log V) where E is edges, V is vertices.
    """
    open_list = []
    g_costs = {start: 0}
    f_costs = {start: heuristic(start, goal, graph)}
    came_from = {}
    heapq.heappush(open_list, (f_costs[start], start))
    while open_list:
        _, current = heapq.heappop(open_list)
        if current == goal:
            return reconstruct_path(came_from, current)
        for neighbor in graph[current]:
            weight = graph[current][neighbor]["weight"] * (0.5 if priority else 1.0)
            tentative_g_cost = g_costs[current] + weight
            if neighbor not in g_costs or tentative_g_cost < g_costs[neighbor]:
                g_costs[neighbor] = tentative_g_cost
                f_costs[neighbor] = tentative_g_cost + heuristic(neighbor, goal, graph)
                heapq.heappush(open_list, (f_costs[neighbor], neighbor))
                came_from[neighbor] = current
    return []

def heuristic(node, goal, graph):
    """
    Computes Euclidean distance heuristic for A* algorithm.

    Args:
        node (str): Current node name.
        goal (str): Goal node name.
        graph (nx.Graph): Graph with 'x' and 'y' node attributes.

    Returns:
        float: Estimated distance between nodes.
    """
    x1, y1 = graph.nodes[node]["x"], graph.nodes[node]["y"]
    x2, y2 = graph.nodes[goal]["x"], graph.nodes[goal]["y"]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def reconstruct_path(came_from, current):
    """
    Reconstructs the path from A* or Dijkstra's algorithm.

    Args:
        came_from (dict): Parent node mappings.
        current (str): Current node name.

    Returns:
        list: Reconstructed path from start to current node.
    """
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(current)
    path.reverse()
    return path

def initialize_disjoint_set(nodes):
    """
    Initializes a disjoint-set data structure for Kruskal's algorithm.

    Args:
        nodes (pd.Series): Series of node IDs.

    Returns:
        dict: Parent dictionary for disjoint sets.
    """
    return {node: node for node in nodes}

def find(parent, node):
    """
    Finds the root of a node in the disjoint-set with path compression.

    Args:
        parent (dict): Parent dictionary.
        node: Node ID.

    Returns:
        Node ID of the root.
    """
    if parent[node] != node:
        parent[node] = find(parent, parent[node])
    return parent[node]

def union(parent, node1, node2):
    """
    Unites two nodes in the disjoint-set.

    Args:
        parent (dict): Parent dictionary.
        node1: First node ID.
        node2: Second node ID.
    """
    root1 = find(parent, node1)
    root2 = find(parent, node2)
    if root1 != root2:
        parent[root2] = root1

def modified_kruskal(all_edges, all_nodes, mandatory_connections=None):
    """
    Kruskal’s algorithm for Minimum Spanning Tree with mandatory connections.

    Args:
        all_edges (pd.DataFrame): DataFrame with columns ['FromID', 'ToID', 'Cost', 'Type'].
        all_nodes (pd.DataFrame): DataFrame with node IDs and attributes.
        mandatory_connections (list, optional): List of (u, v) tuples for required edges.

    Returns:
        tuple: (mst_edges, total_cost) where mst_edges is a list of (u, v, cost) tuples.

    Time Complexity: O(E log E) due to edge sorting.
    """
    parent = initialize_disjoint_set(all_nodes['ID'])
    mst_edges = []
    total_cost = 0
    all_edges_sorted = all_edges.sort_values(by='Cost')
    if mandatory_connections:
        for u, v in mandatory_connections:
            if find(parent, u) != find(parent, v):
                edge = all_edges[
                    ((all_edges['FromID'] == u) & (all_edges['ToID'] == v)) |
                    ((all_edges['FromID'] == v) & (all_edges['ToID'] == u))
                ]
                if not edge.empty:
                    cost = edge['Cost'].values[0]
                    total_cost += cost
                    mst_edges.append((u, v, cost))
                union(parent, u, v)
    for _, edge in all_edges_sorted.iterrows():
        u, v = edge['FromID'], edge['ToID']
        if find(parent, u) != find(parent, v):
            union(parent, u, v)
            mst_edges.append((u, v, edge['Cost']))
            total_cost += edge['Cost']
    return mst_edges, total_cost

def time_dependent_dijkstra(graph, start_name, end_name, time_of_day, df_traffic, df_existing, name_to_id, id_to_name):
    """
    Dijkstra’s algorithm with time-varying traffic congestion.

    Args:
        graph (nx.Graph): Graph with 'distance' edge attributes.
        start_name (str): Starting node name.
        end_name (str): Destination node name.
        time_of_day (str): Time period ('Morning', 'Afternoon', 'Evening', 'Night').
        df_traffic (pd.DataFrame): Traffic data.
        df_existing (pd.DataFrame): Existing roads data.
        name_to_id (dict): Name to ID mapping.
        id_to_name (dict): ID to name mapping.

    Returns:
        tuple: (total_time, path_names) or (inf, []) if no path exists.

    Time Complexity: O(E log V).
    """
    start = name_to_id[start_name]
    end = name_to_id[end_name]
    queue = [(0, start, [start_name])]
    visited = set()
    distances = {node: float('inf') for node in graph.nodes()}
    distances[start] = 0
    while queue:
        current_time, node, path_names = heapq.heappop(queue)
        if node == end:
            return current_time, path_names
        if node in visited:
            continue
        visited.add(node)
        for neighbor in graph.neighbors(node):
            road_name = f"{id_to_name[node]}-{id_to_name[neighbor]}"
            distance = graph[node][neighbor]['distance']
            congestion = get_traffic_speed(road_name, time_of_day, name_to_id)
            travel_time = distance * congestion
            if distances[neighbor] > current_time + travel_time:
                distances[neighbor] = current_time + travel_time
                heapq.heappush(queue, (distances[neighbor], neighbor, path_names + [id_to_name[neighbor]]))
    return float('inf'), []

def time_dependent_dijkstra_cached(graph, start_name, end_name, time_of_day, df_traffic, df_existing, name_to_id, id_to_name):
    """
    Cached version of Dijkstra’s for repeated queries.

    Args:
        Same as time_dependent_dijkstra.

    Returns:
        tuple: Cached or computed (total_time, path_names).

    Time Complexity: O(1) for cache hit, O(E log V) for computation.
    """
    key = (start_name, end_name, time_of_day, tuple(sorted(df_traffic['RoadName'])))
    if key in route_cache:
        return route_cache[key]
    result = time_dependent_dijkstra(graph, start_name, end_name, time_of_day, df_traffic, df_existing, name_to_id, id_to_name)
    route_cache[key] = result
    return result

def get_traffic_speed(road_name, time_of_day, name_to_id):
    """
    Computes traffic speed factor based on congestion.

    Args:
        road_name (str): Road name (e.g., 'Maadi-Downtown Cairo').
        time_of_day (str): Time period.
        name_to_id (dict): Name to ID mapping.

    Returns:
        float: Congestion factor (0.5 to 2.0).
    """
    traffic = df_traffic[df_traffic['RoadName'] == road_name]
    if traffic.empty:
        return 1.0
    traffic_volume = traffic[time_of_day].values[0]
    u, v = road_name.split('-')
    u_id, v_id = name_to_id[u], name_to_id[v]
    capacity = df_existing[
        ((df_existing['FromID'] == u_id) & (df_existing['ToID'] == v_id)) |
        ((df_existing['FromID'] == v_id) & (df_existing['ToID'] == u_id))
    ]['Capacity'].values[0]
    return max(0.5, min(2.0, traffic_volume / capacity))

def public_transport_dp(stations, routes, time_slots, start_station, max_vehicles, transit_routes):
    """
    Dynamic Programming for transit travel times and vehicle scheduling.

    Args:
        stations (dict): Station names to coordinates.
        routes (dict): (src, dst) to travel time mappings.
        time_slots (int): Number of time slots (hours).
        start_station (str): Starting station name.
        max_vehicles (int): Maximum number of vehicles.
        transit_routes (list): List of transit route dictionaries.

    Returns:
        tuple: (dp, paths, coverage) where dp is travel times, paths is routes, coverage is population served.

    Time Complexity: O(T * N * E + R * V * T) where T is time slots, N is stations, E is edges, R is routes, V is vehicles.
    """
    dp = {station: [float('inf')] * time_slots for station in stations}
    dp[start_station][0] = 0
    paths = {station: [None] * time_slots for station in stations}
    for time in range(time_slots):
        for station in stations:
            if dp[station][time] < float('inf'):
                for (src, dst), travel_time in routes.items():
                    if src == station and time + 1 < time_slots:
                        transfer_penalty = 5 if paths[src][time] and paths[src][time] in transit_routes else 0
                        new_time = dp[src][time] + travel_time + transfer_penalty
                        if new_time < dp[dst][time + 1]:
                            dp[dst][time + 1] = new_time
                            paths[dst][time + 1] = src
    schedule_dp = {}
    def schedule(route_idx, vehicles_left, time_slot):
        if route_idx >= len(transit_routes) or time_slot >= time_slots:
            return 0
        state = (route_idx, vehicles_left, time_slot)
        if state in schedule_dp:
            return schedule_dp[state]
        max_coverage = schedule(route_idx + 1, vehicles_left, time_slot)
        if vehicles_left > 0:
            route = transit_routes[route_idx]
            pop = sum(df_neighborhoods[df_neighborhoods['Name'].isin(route['stops'])]['Population'])
            if pop <= route['capacity'] * vehicles_left:
                coverage = pop / route['frequency']
                if time_slot + route['frequency'] <= time_slots:
                    max_coverage = max(max_coverage, coverage + schedule(route_idx, vehicles_left - 1, time_slot + route['frequency']))
        schedule_dp[state] = max_coverage
        return max_coverage
    coverage = schedule(0, max_vehicles, 0)
    return dp, paths, coverage

def optimize_maintenance(df_existing, budget):
    """
    Dynamic Programming for road maintenance allocation.

    Args:
        df_existing (pd.DataFrame): Existing roads with maintenance costs and conditions.
        budget (float): Available budget in million EGP.

    Returns:
        tuple: (max_improvement, selected_roads) where selected_roads is a list of (FromID, ToID).

    Time Complexity: O(N * B) where N is roads, B is budget.
    """
    roads = df_existing[["FromID", "ToID", "Maintenance_Cost", "Condition"]].to_dict('records')
    dp = {(0, budget): 0}
    choices = {}
    for i in range(len(roads)):
        for curr_budget in list(dp.keys()):
            idx, budget_left = curr_budget
            if idx != i:
                continue
            dp[(i + 1, budget_left)] = dp.get((i + 1, budget_left), 0)
            cost = roads[i]["Maintenance_Cost"]
            if budget_left >= cost:
                improvement = 10 - roads[i]["Condition"]
                new_state = (i + 1, budget_left - cost)
                new_value = dp[curr_budget] + improvement
                if new_value > dp.get(new_state, 0):
                    dp[new_state] = new_value
                    choices[new_state] = (roads[i]["FromID"], roads[i]["ToID"])
    max_improvement = max(dp.values())
    selected_roads = []
    curr_state = max(dp, key=lambda k: dp[k])
    while curr_state in choices:
        selected_roads.append(choices[curr_state])
        curr_state = (curr_state[0] - 1, curr_state[1] + roads[curr_state[0] - 1]["Maintenance_Cost"])
    return max_improvement, selected_roads

def greedy_maintenance(df_existing, budget):
    """
    Greedy algorithm for road maintenance prioritization.

    Args:
        df_existing (pd.DataFrame): Existing roads with maintenance costs and conditions.
        budget (float): Available budget in million EGP.

    Returns:
        tuple: (total_improvement, selected_roads) where selected_roads is a list of (FromID, ToID).

    Time Complexity: O(N log N) due to sorting.
    """
    roads = df_existing[["FromID", "ToID", "Maintenance_Cost", "Condition"]].to_dict('records')
    roads.sort(key=lambda x: (10 - x["Condition"]) / x["Maintenance_Cost"], reverse=True)
    selected_roads = []
    total_improvement = 0
    remaining_budget = budget
    for road in roads:
        if road["Maintenance_Cost"] <= remaining_budget:
            improvement = 10 - road["Condition"]
            total_improvement += improvement
            remaining_budget -= road["Maintenance_Cost"]
            selected_roads.append((road["FromID"], road["ToID"]))
    return total_improvement, selected_roads