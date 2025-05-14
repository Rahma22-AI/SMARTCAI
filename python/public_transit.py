import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk
from algorithms import public_transport_dp, get_traffic_speed
from data import df_neighborhoods, df_facilities, df_existing, df_traffic, all_nodes, transit_routes

def create_station_mapping():
    """
    Creates a mapping of station names to coordinates.

    Returns:
        dict: Station names to (longitude, latitude) coordinate tuples.
    """
    stations = {}
    for _, row in df_neighborhoods.iterrows():
        stations[row['Name']] = (row['X'], row['Y'])  # X=longitude, Y=latitude
    for _, row in df_facilities.iterrows():
        stations[row['Name']] = (row['X'], row['Y'])
    return stations

def create_routes(time_of_day, name_to_id):
    """
    Creates a dictionary of routes with travel times based on traffic.

    Args:
        time_of_day (str): Time period ('Morning', 'Afternoon', 'Evening', 'Night').
        name_to_id (dict): Name to ID mapping.

    Returns:
        dict: (src, dst) tuples to travel times.
    """
    routes = {}
    id_to_name = {v: k for k, v in name_to_id.items()}
    for _, row in df_existing.iterrows():
        from_name = id_to_name.get(row['FromID'], row['FromID'])
        to_name = id_to_name.get(row['ToID'], row['ToID'])
        if isinstance(from_name, str) and from_name.startswith('F'):
            from_name = id_to_name.get(from_name, from_name)
        if isinstance(to_name, str) and to_name.startswith('F'):
            to_name = id_to_name.get(to_name, to_name)
        road_name = f"{from_name}-{to_name}"
        congestion = get_traffic_speed(road_name, time_of_day, name_to_id)
        travel_time = row['Distance'] * congestion
        routes[(from_name, to_name)] = travel_time
        routes[(to_name, from_name)] = travel_time  # Bidirectional
    return routes

def analyze_transfer_points(transit_routes, stations):
    """
    Analyzes transfer points by identifying shared stations and computing transfer times.

    Args:
        transit_routes (list): List of transit route dictionaries.
        stations (dict): Station names to coordinates.

    Returns:
        tuple: (transfer_hubs, transfer_times) where transfer_hubs is a dict of stations with route counts,
               transfer_times is a list of transfer time data.
    """
    station_route_count = {}
    for route in transit_routes:
        for stop in route['stops']:
            station_route_count[stop] = station_route_count.get(stop, 0) + 1
    
    transfer_hubs = {station: count for station, count in station_route_count.items() if count >= 2}
    
    transfer_times = []
    for hub in transfer_hubs:
        hub_routes = [r for r in transit_routes if hub in r['stops']]
        for i in range(len(hub_routes)):
            for j in range(i + 1, len(hub_routes)):
                route1 = hub_routes[i]
                route2 = hub_routes[j]
                avg_wait_time = route2['frequency'] / 2  # Average waiting time
                transfer_times.append({
                    'Hub': hub,
                    'From_Route': f"Route {route1['route_id']} ({route1['type']})",
                    'To_Route': f"Route {route2['route_id']} ({route2['type']})",
                    'Avg_Wait_Time': avg_wait_time
                })
    
    return transfer_hubs, transfer_times

def public_transit_optimization():
    """
    Streamlit interface for public transit optimization and transfer point analysis.
    """
    st.header("Cairo Public Transit Optimization")
    name_to_id = {row['Name']: row['ID'] for _, row in all_nodes.iterrows()}
    stations = create_station_mapping()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        start_station = st.selectbox("Select Start Station", sorted(stations.keys()), key="transit_start")
    with col2:
        time_slots = st.slider("Number of Time Slots (hours)", 6, 24, 6, key="transit_slots")
    with col3:
        max_vehicles = st.slider("Max Vehicles", 1, 50, 10, key="transit_vehicles")
    time_of_day = st.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"], key="transit_time")
    
    if st.button("Optimize Transit"):
        routes = create_routes(time_of_day, name_to_id)
        dp, paths, coverage = public_transport_dp(stations, routes, time_slots, start_station, max_vehicles, transit_routes)
        
        # Display travel times
        st.subheader("Minimal Travel Times")
        results = []
        for station in stations:
            min_time = min(dp[station])
            if min_time != float('inf'):
                results.append({"Destination": station, "Minimal Time": min_time, "Route": f"{start_station} → {station}"})
        df_results = pd.DataFrame(results).sort_values('Minimal Time')
        st.dataframe(df_results)
        st.write(f"**Coverage Score:** {coverage:.2f} (population served per minute)")
        
        # Transfer point analysis
        st.subheader("Transfer Point Analysis")
        transfer_hubs, transfer_times = analyze_transfer_points(transit_routes, stations)
        if transfer_hubs:
            st.write("**Key Transfer Hubs (Stations with Multiple Routes):**")
            hub_df = pd.DataFrame(list(transfer_hubs.items()), columns=['Station', 'Route Count'])
            st.table(hub_df)
            st.write("**Average Transfer Waiting Times at Hubs:**")
            transfer_df = pd.DataFrame(transfer_times)
            if not transfer_df.empty:
                st.table(transfer_df)
            else:
                st.write("No transfer times calculated (single-route hubs).")
        else:
            st.write("No transfer hubs found.")
        
        # Transit network map
        st.subheader("Transit Network Map")
        route_data = []
        for (src, dst), _ in routes.items():
            if src in stations and dst in stations:  # Ensure valid stations
                route_data.append({
                    'from': src, 'to': dst,
                    'from_lat': stations[src][1], 'from_lon': stations[src][0],  # Y=latitude, X=longitude
                    'to_lat': stations[dst][1], 'to_lon': stations[dst][0]
                })
        df_routes = pd.DataFrame(route_data)
        station_data = [
            {
                'name': k,
                'lat': v[1],  # Y=latitude
                'lon': v[0],  # X=longitude
                'is_hub': k in transfer_hubs,
                'color': [255, 0, 0, 160] if k in transfer_hubs else [165, 42, 42, 160],
                'radius': 1000 if k in transfer_hubs else 500
            }
            for k, v in stations.items()
        ]
        df_stations = pd.DataFrame(station_data)
        
        # Debug: Display raw data
        if df_routes.empty:
            st.warning("No routes available to display. Check if 'routes' dictionary is populated.")
        if df_stations.empty:
            st.warning("No stations available to display. Check 'stations' mapping.")
        else:
            st.write(f"Number of stations: {len(df_stations)}")
            st.write(f"Number of routes: {len(df_routes)}")
        
        stations_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_stations,
            get_position='[lon, lat]',
            get_fill_color='color',
            get_radius='radius',
            pickable=True
        )
        routes_layer = pdk.Layer(
            "LineLayer",
            data=df_routes,
            get_source_position='[from_lon, from_lat]',
            get_target_position='[to_lon, to_lat]',
            get_width=3,
            get_color=[0, 0, 255, 160],
            pickable=True
        )
        optimal_routes = []
        for station in stations:
            if station != start_station and min(dp[station]) != float('inf'):
                optimal_routes.append({
                    'from': start_station, 'to': station,
                    'from_lat': stations[start_station][1], 'from_lon': stations[start_station][0],
                    'to_lat': stations[station][1], 'to_lon': stations[station][0]
                })
        df_optimal_routes = pd.DataFrame(optimal_routes)
        optimal_layer = pdk.Layer(
            "LineLayer",
            data=df_optimal_routes,
            get_source_position='[from_lon, from_lat]',
            get_target_position='[to_lon, to_lat]',
            get_width=5,
            get_color=[0, 255, 0, 200],
            pickable=True
        )
        
        # Compute centroid for view state
        if not df_stations.empty:
            avg_lat = df_stations['lat'].mean()
            avg_lon = df_stations['lon'].mean()
        else:
            avg_lat, avg_lon = 30.0444, 31.2357  # Fallback to Cairo center
        
        view_state = pdk.ViewState(
            latitude=avg_lat,
            longitude=avg_lon,
            zoom=10,
            pitch=0
        )
        r = pdk.Deck(
            layers=[routes_layer, stations_layer, optimal_layer],
            initial_view_state=view_state,
            tooltip={
                'html': '<b>{name}</b>' if 'name' in df_stations.columns else '<b>{from}</b> to <b>{to}</b>',
                'style': {'color': 'white'}
            }
        )
        try:
            st.pydeck_chart(r)
        except Exception as e:
            st.error(f"Failed to render map: {e}")
            st.write("Stations Data:", df_stations[['name', 'lat', 'lon', 'is_hub']])
            st.write("Routes Data:", df_routes[['from', 'to', 'from_lat', 'from_lon', 'to_lat', 'to_lon']])
        
        # Travel time matrix
        st.subheader("Travel Time Matrix")
        fig, ax = plt.subplots(figsize=(12, 8))
        station_names = sorted(stations.keys())
        heatmap_data = [dp[station] for station in station_names]
        im = ax.imshow(heatmap_data, cmap='viridis', aspect='auto')
        ax.set_xticks(np.arange(time_slots))
        ax.set_yticks(np.arange(len(station_names)))
        ax.set_xticklabels([f"Hour {i}" for i in range(time_slots)])
        ax.set_yticklabels(station_names)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        plt.colorbar(im, ax=ax, label='Travel Time (minutes)')
        ax.set_title("Travel Time Matrix")
        st.pyplot(fig)
        
        # Transit route coverage
        st.subheader("Transit Route Coverage")
        fig, ax = plt.subplots(figsize=(10, 6))
        coverage_data = []
        for route in transit_routes:
            pop = sum(df_neighborhoods[df_neighborhoods['Name'].isin(route['stops'])]['Population'])
            coverage_data.append({'Route': f"Route {route['route_id']} ({route['type']})", 'Population': pop})
        df_coverage = pd.DataFrame(coverage_data)
        ax.bar(df_coverage['Route'], df_coverage['Population'], color='skyblue')
        ax.set_xlabel("Transit Routes")
        ax.set_ylabel("Population Covered")
        ax.set_title("Population Coverage by Transit Routes")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)