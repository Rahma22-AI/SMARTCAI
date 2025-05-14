import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
from data import all_nodes, build_traffic_graph, name_to_id, id_to_name
from algorithms import a_star

def simulation_framework():
    """Simulation Framework module."""
    st.header("Simulation Framework")
    
    vehicle_type = st.selectbox("Vehicle Type", ["Emergency", "Transit"])
    num_vehicles = st.number_input("Number of Vehicles", min_value=1, value=2)
    
    if st.button("Run Simulation"):
        G = build_traffic_graph()
        paths = []
        for _ in range(num_vehicles):
            start_id = name_to_id['Maadi']  # Example
            target_id = name_to_id['El Salam Hospital'] if vehicle_type == "Emergency" else name_to_id['Downtown']
            path_ids, _ = a_star(G, start_id, target_id, priority=(vehicle_type == "Emergency"))
            paths.append([id_to_name[id] for id in path_ids])
        
        # PyDeck animation
        data = []
        for t in range(50):  # 50 time steps
            for i, path in enumerate(paths):
                frac = t / 50
                idx = int(frac * (len(path) - 1))
                if idx < len(path) - 1:
                    start = path[idx]
                    end = path[idx + 1]
                    start_pos = all_nodes[all_nodes['Name'] == start][['X', 'Y']].iloc[0]
                    end_pos = all_nodes[all_nodes['Name'] == end][['X', 'Y']].iloc[0]
                    lon = start_pos['X'] + (end_pos['X'] - start_pos['X']) * (frac * (len(path) - 1) - idx)
                    lat = start_pos['Y'] + (end_pos['Y'] - start_pos['Y']) * (frac * (len(path) - 1) - idx)
                    data.append({"lon": lon, "lat": lat, "color": [255, 0, 0] if vehicle_type == "Emergency" else [0, 255, 0]})
        
        df = pd.DataFrame(data)
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius=100,
            pickable=True
        )
        view_state = pdk.ViewState(latitude=30.0444, longitude=31.2357, zoom=11)
        deck = pdk.Deck(layers=[layer], initial_view_state=view_state)
        st.pydeck_chart(deck)

if __name__ == "__main__":
    simulation_framework()