import streamlit as st
from emergency_routing import emergency_vehicle_routing
from urban_planning import urban_planning_optimization
from public_transit import public_transit_optimization
import matplotlib
matplotlib.use('Agg')

def main():
    st.title("SMARTCAI : Cairo Transportation and Urban Planning")
    module = st.sidebar.selectbox("Select Module", ["Urban Planning Optimization" , "Emergency Vehicle Routing" , "Public Transit Optimization"])
    if module == "Emergency Vehicle Routing":
        emergency_vehicle_routing()
    elif module == "Urban Planning Optimization":
        urban_planning_optimization()
    else:
        public_transit_optimization()

if __name__ == "__main__":
    main()