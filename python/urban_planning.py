import streamlit as st
import networkx as nx
import heapq
import matplotlib.pyplot as plt
import folium
import pandas as pd  # Added pandas import
from streamlit_folium import folium_static
from data import df_neighborhoods, df_facilities, df_existing, df_potential, df_traffic, all_nodes
from utils import  get_road_name
from algorithms import get_traffic_speed,time_dependent_dijkstra,modified_kruskal,initialize_disjoint_set,find,union

def build_traffic_graph():
    G = nx.Graph()
    for _, row in all_nodes.iterrows():
        G.add_node(row['ID'], pos=(row['X'], row['Y']), name=row['Name'])
    for _, row in df_existing.iterrows():
        G.add_edge(row['FromID'], row['ToID'], distance=row['Distance'])
    return G


def recommend_alternate_route(graph, start_name, end_name, closed_roads, time_of_day, df_traffic, df_existing, name_to_id, id_to_name):
    temp_graph = graph.copy()
    for road in closed_roads:
        u, v = road.split('-')
        u_id, v_id = name_to_id[u], name_to_id[v]
        if temp_graph.has_edge(u_id, v_id):
            temp_graph.remove_edge(u_id, v_id)
    return time_dependent_dijkstra(temp_graph, start_name, end_name, time_of_day, df_traffic, df_existing, name_to_id, id_to_name)

def urban_planning_optimization():
    st.header("Cairo Urban Planning Optimization")
    name_to_id = {row['Name']: row['ID'] for _, row in all_nodes.iterrows()}
    id_to_name = {v: k for k, v in name_to_id.items()}
    location_names = sorted(name_to_id.keys())
    
    # Create MST for the infrastructure network
    df_existing_edges = df_existing[['FromID', 'ToID']].copy()
    df_existing_edges['Cost'] = df_existing['Maintenance_Cost']
    df_existing_edges['Type'] = 'Existing'
    df_potential_edges = df_potential[['FromID', 'ToID']].copy()
    df_potential_edges['Cost'] = df_potential['Cost']
    df_potential_edges['Type'] = 'Potential'
    all_edges = pd.concat([df_existing_edges, df_potential_edges])
    mandatory_connections = [('F9', 3), ('F10', 1)]
    mst_edges, total_cost = modified_kruskal(all_edges, all_nodes, mandatory_connections)
    
    st.subheader(" Infrastructure Network Design")
    
    
    algorithm = st.sidebar.radio(
        "Select Algorithm",
        ("Infrastructure Network Design", "Traffic Flow Optimization", "Road Maintenance"),
        key="urban_algorithm"
    )
    
    if algorithm == "Infrastructure Network Design":

        cairo_map = folium.Map(location=[30.0444, 31.2357], zoom_start=11)
    
    # Add neighborhoods
        for _, row in df_neighborhoods.iterrows():
            folium.CircleMarker(
                location=[row['Y'], row['X']],
                radius=6,
                color='blue',
                fill=True,
                fill_color='blue',
                popup=f"{row['Name']} (Population: {row['Population']})"
            ).add_to(cairo_map)
    
    # Add facilities
        for _, row in df_facilities.iterrows():
            folium.Marker(
                location=[row['Y'], row['X']],
                popup=row['Name'],
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(cairo_map)
    
    # Add MST edges instead of all existing edges
        for u, v, cost in mst_edges:
            from_coord = all_nodes[all_nodes['ID'] == u][['Y', 'X']].values
            to_coord = all_nodes[all_nodes['ID'] == v][['Y', 'X']].values
            if len(from_coord) > 0 and len(to_coord) > 0:
                folium.PolyLine(
                    locations=[from_coord[0], to_coord[0]],
                    color='red' if (u, v) in [(row['FromID'], row['ToID']) for _, row in df_potential.iterrows()] else 'green',
                    weight=3,
                    tooltip=f"Cost: {cost} million EGP"
                ).add_to(cairo_map)
    
        folium_static(cairo_map)
        st.subheader("Optimal Road Network")
        fig, ax = plt.subplots(figsize=(12, 10))
        G = nx.Graph()
        for _, row in all_nodes.iterrows():
            G.add_node(row['ID'], pos=(row['X'], row['Y']))
        for _, row in df_existing.iterrows():
            G.add_edge(row['FromID'], row['ToID'])
        for _, row in df_potential.iterrows():
            G.add_edge(row['FromID'], row['ToID'])
        pos = nx.get_node_attributes(G, 'pos')
        mst_graph = nx.Graph()
        for u, v, cost in mst_edges:
            mst_graph.add_edge(u, v)
        nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=0.5, alpha=0.3, ax=ax)
        nx.draw_networkx_edges(mst_graph, pos, edge_color='red', width=2, ax=ax)
        node_sizes = [row['Population']/5000 for _, row in all_nodes.iterrows()]
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', ax=ax)
        important_nodes = all_nodes[(all_nodes['Population'] > 200000) | (all_nodes['Type'].isin(['Medical', 'Airport']))]
        labels = {row['ID']: row['Name'] for _, row in important_nodes.iterrows()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)
        plt.title("Optimal Road Network (Minimum Spanning Tree)")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True)
        st.pyplot(fig)
        
        st.subheader("Cost Analysis")
        mst_df = pd.DataFrame(mst_edges, columns=['FromID', 'ToID', 'Cost'])
        mst_df = mst_df.merge(all_edges, on=['FromID', 'ToID'], how='left')
        total_cost = mst_df['Cost_x'].sum()
        existing_km = mst_df[mst_df['Type'] == 'Existing']['Cost_x'].count()
        new_km = mst_df[mst_df['Type'] == 'Potential']['Cost_x'].count()
        st.write(f"**Total Network Cost:** {total_cost:,.2f} million EGP")
        st.write(f"**Existing Roads Used:** {existing_km} segments")
        st.write(f"**New Roads Constructed:** {new_km} segments")
    
    elif algorithm == "Traffic Flow Optimization":


        # Visualize the route on a new Folium map
        cairo_map = folium.Map(location=[30.0444, 31.2357], zoom_start=11)
        for _, row in df_neighborhoods.iterrows():
            folium.CircleMarker(
                location=[row['Y'], row['X']],
                radius=6,
                color='blue',
                fill=True,
                fill_color='blue',
                popup=f"{row['Name']} (Population: {row['Population']})"
            ).add_to(cairo_map)
        for _, row in df_facilities.iterrows():
            folium.Marker(
                location=[row['Y'], row['X']],
                popup=row['Name'],
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(cairo_map)
        for _, row in df_existing.iterrows():
            from_id = row['FromID']
            to_id = row['ToID']
            from_coord = all_nodes[all_nodes['ID'] == from_id][['Y', 'X']].values
            to_coord = all_nodes[all_nodes['ID'] == to_id][['Y', 'X']].values
            if len(from_coord) > 0 and len(to_coord) > 0:
                folium.PolyLine(
                    locations=[from_coord[0], to_coord[0]],
                    color='green',
                    weight=2,
                    tooltip=f"Distance: {row['Distance']} km"
                ).add_to(cairo_map)
        folium_static(cairo_map)

        st.subheader("Traffic Flow Optimization")
        col1, col2, col3 = st.columns(3)
        with col1:
            start_location = st.selectbox("Start Location", location_names, key="traffic_start")
        with col2:
            end_location = st.selectbox("End Location", location_names, key="traffic_end")
        with col3:
            time_of_day = st.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"], key="traffic_time")
        closed_roads = st.multiselect("Select roads to close", df_traffic['RoadName'].unique(), key="traffic_roads")
        traffic_graph = build_traffic_graph()
        
        if start_location and end_location and start_location != end_location:
            normal_time, normal_path = time_dependent_dijkstra(traffic_graph, start_location, end_location, time_of_day, df_traffic, df_existing, name_to_id, id_to_name)
            if closed_roads:
                alt_time, alt_path = recommend_alternate_route(traffic_graph, start_location, end_location, closed_roads, time_of_day, df_traffic, df_existing, name_to_id, id_to_name)
            
            st.subheader("Routing Results")
            if not closed_roads:
                st.write(f"**Optimal Route:** {' → '.join(normal_path)}")
                st.write(f"**Estimated Travel Time:** {normal_time:.1f} minutes")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Normal Route**")
                    st.write(f"Path: {' → '.join(normal_path)}")
                    st.write(f"Time: {normal_time:.1f} minutes")
                with col2:
                    st.write("**Alternate Route**")
                    st.write(f"Path: {' → '.join(alt_path)}")
                    st.write(f"Time: {alt_time:.1f} minutes")
            
            st.subheader("Traffic Network Visualization")
            fig, ax = plt.subplots(figsize=(12, 10))
            pos = nx.get_node_attributes(traffic_graph, 'pos')
            for u, v in traffic_graph.edges():
                road_name = get_road_name(u, v, id_to_name)
                congestion = get_traffic_speed(road_name, time_of_day,name_to_id)
                color = 'red' if congestion > 1.5 else 'orange' if congestion > 1.2 else 'green'
                nx.draw_networkx_edges(traffic_graph, pos, edgelist=[(u, v)], edge_color=color, width=1.5, ax=ax)
            route_edges = [(name_to_id[normal_path[i]], name_to_id[normal_path[i+1]]) for i in range(len(normal_path)-1)]
            nx.draw_networkx_edges(traffic_graph, pos, edgelist=route_edges, edge_color='blue', width=3, ax=ax)
            nx.draw_networkx_nodes(traffic_graph, pos, node_size=200, node_color='lightblue', ax=ax)
            labels = {name_to_id[start_location]: start_location, name_to_id[end_location]: end_location}
            nx.draw_networkx_labels(traffic_graph, pos, labels, font_size=10, font_weight='bold', ax=ax)
            plt.title(f"Traffic Conditions ({time_of_day})")
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            plt.grid(True)
            st.pyplot(fig)
    
    else:
        st.subheader("Road Maintenance Optimization")
        budget = st.slider("Maintenance Budget (million EGP)", 0, 1000, 500, key="maintenance_budget")
        if st.button("Optimize Maintenance"):
            improvement, selected_roads = optimize_maintenance(df_existing, budget)
            st.success(f"Total Condition Improvement: {improvement:.2f} units")
            st.write("**Selected Roads for Maintenance:**")
            roads_df = pd.DataFrame(selected_roads, columns=['FromID', 'ToID'])
            roads_df = roads_df.merge(all_nodes[['ID', 'Name']], left_on='FromID', right_on='ID', how='left').rename(columns={'Name': 'From'})
            roads_df = roads_df.merge(all_nodes[['ID', 'Name']], left_on='ToID', right_on='ID', how='left').rename(columns={'Name': 'To'})
            st.table(roads_df[['From', 'To']])
            
            st.subheader("Road Condition Visualization")
            fig, ax = plt.subplots(figsize=(12, 10))
            G = nx.Graph()
            for _, row in all_nodes.iterrows():
                G.add_node(row['ID'], pos=(row['X'], row['Y']))
            for _, row in df_existing.iterrows():
                G.add_edge(row['FromID'], row['ToID'], condition=row['Condition'])
            pos = nx.get_node_attributes(G, 'pos')
            nx.draw_networkx_edges(G, pos, edge_color='lightgray', width=1, alpha=0.5, ax=ax)
            selected_edges = [(row['FromID'], row['ToID']) for _, row in roads_df.iterrows()]
            nx.draw_networkx_edges(G, pos, edgelist=selected_edges, edge_color='red', width=3, ax=ax)
            nx.draw_networkx_nodes(G, pos, node_size=200, node_color='skyblue', ax=ax)
            nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
            plt.title("Roads Selected for Maintenance")
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            plt.grid(True)
            st.pyplot(fig)

def optimize_maintenance(df_existing, budget):
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