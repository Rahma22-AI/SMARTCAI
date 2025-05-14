import streamlit as st
import networkx as nx
import heapq
import math
import matplotlib.pyplot as plt
from pyvis.network import Network
import os
import tempfile
from data import neighborhoods, facilities, roads

# Create emergency graph
G_emergency = nx.Graph()
for neighborhood in neighborhoods.values():
    G_emergency.add_node(neighborhood['name'], location_type="Neighborhood", x=neighborhood['x'], y=neighborhood['y'])
for facility in facilities.values():
    G_emergency.add_node(facility['name'], location_type="Facility", x=facility['x'], y=facility['y'])
for road_id, road_data in roads.items():
    road_weight = road_data["distance"] + (road_data["traffic"] * 0.1)
    if road_data["condition"] == "poor":
        road_weight *= 1.5
    G_emergency.add_edge(road_data["from"], road_data["to"], weight=road_weight, traffic=road_data["traffic"], distance=road_data["distance"], condition=road_data["condition"])

def a_star(start, goal, graph, priority=False):
    open_list = []
    g_costs = {start: 0}
    f_costs = {start: heuristic(start, goal)}
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
                f_costs[neighbor] = tentative_g_cost + heuristic(neighbor, goal)
                heapq.heappush(open_list, (f_costs[neighbor], neighbor))
                came_from[neighbor] = current
    return []

def heuristic(node, goal):
    x1, y1 = G_emergency.nodes[node]["x"], G_emergency.nodes[node]["y"]
    x2, y2 = G_emergency.nodes[goal]["x"], G_emergency.nodes[goal]["y"]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.append(current)
    path.reverse()
    return path

def find_emergency_route(start, facilities, graph, priority=False):
    shortest_path = None
    closest_facility = None
    min_distance = float('inf')
    for facility in facilities.values():
        path = a_star(start, facility['name'], graph, priority)
        if path:
            total_distance = sum(graph[path[i]][path[i + 1]]["weight"] for i in range(len(path) - 1))
            if total_distance < min_distance:
                min_distance = total_distance
                shortest_path = path
                closest_facility = facility
    return shortest_path, closest_facility

def create_interactive_graph(G, shortest_path=None):
    net = Network(height="600px", width="100%", directed=False, notebook=False)
    for node, data in G.nodes(data=True):
        color = "skyblue" if data["location_type"] == "Neighborhood" else "lightcoral"
        size = 15 if data["location_type"] == "Neighborhood" else 20
        net.add_node(node, label=node, color=color, size=size, x=data["x"]*100, y=data["y"]*100)
    for u, v, data in G.edges(data=True):
        color = "red" if data["condition"] == "poor" else "green"
        width = 3 if shortest_path and u in shortest_path and v in shortest_path else 1
        label = f"{data['weight']:.2f} km"
        net.add_edge(u, v, value=width, color=color, title=label)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        output_path = tmp_file.name
        net.save_graph(output_path)
    return output_path

def create_static_graph(G, shortest_path=None):
    plt.figure(figsize=(10, 8))
    pos = {node: (data["x"], data["y"]) for node, data in G.nodes(data=True)}
    nx.draw_networkx_nodes(G, pos, node_color=["skyblue" if G.nodes[n]["location_type"] == "Neighborhood" else "lightcoral" for n in G.nodes], node_size=500)
    nx.draw_networkx_edges(G, pos, edge_color="gray", width=1)
    if shortest_path:
        path_edges = [(shortest_path[i], shortest_path[i+1]) for i in range(len(shortest_path)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="red", width=3)
    nx.draw_networkx_labels(G, pos, font_size=8)
    plt.title("Cairo Transportation Network")
    st.pyplot(plt)

def emergency_vehicle_routing():
    st.header("Cairo Emergency Vehicle Routing")
    start_location = st.selectbox("Select Starting Neighborhood", list(neighborhoods.keys()), key="emergency_start")
    priority_mode = st.checkbox("Enable Emergency Priority at Intersections", key="emergency_priority")
    if st.button("Find Shortest Path"):
        shortest_path, closest_facility = find_emergency_route(start_location, facilities, G_emergency, priority=priority_mode)
        if shortest_path:
            st.success(f"Shortest Path: {' -> '.join(shortest_path)}")
            st.info(f"Closest Facility: {closest_facility['name']}")
            try:
                html_file = create_interactive_graph(G_emergency, shortest_path)
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=600, scrolling=True)
                os.unlink(html_file)
            except Exception as e:
                st.warning(f"Pyvis failed: {e}. Falling back to static graph.")
                create_static_graph(G_emergency, shortest_path)
        else:
            st.error("No path found.")
    st.subheader("Transportation Network")
    try:
        html_file = create_interactive_graph(G_emergency)
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=600, scrolling=True)
        os.unlink(html_file)
    except Exception as e:
        st.warning(f"Pyvis failed: {e}. Falling back to static graph.")
        create_static_graph(G_emergency)