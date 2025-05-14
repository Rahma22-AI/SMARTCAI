import pandas as pd

# Neighborhoods
neighborhoods_data = [
    [1, 'Maadi', 250000, 'Residential', 31.25, 29.96],
    [2, 'Nasr City', 500000, 'Mixed', 31.34, 30.06],
    [3, 'Downtown Cairo', 100000, 'Business', 31.24, 30.04],
    [4, 'New Cairo', 300000, 'Residential', 31.47, 30.03],
    [5, 'Heliopolis', 200000, 'Mixed', 31.32, 30.09],
    [6, 'Zamalek', 50000, 'Residential', 31.22, 30.06],
    [7, '6th October City', 400000, 'Mixed', 30.98, 29.93],
    [8, 'Giza', 550000, 'Mixed', 31.21, 29.99],
    [9, 'Mohandessin', 180000, 'Business', 31.20, 30.05],
    [10, 'Dokki', 220000, 'Mixed', 31.21, 30.03],
    [11, 'Shubra', 450000, 'Residential', 31.24, 30.11],
    [12, 'Helwan', 350000, 'Industrial', 31.33, 29.85],
    [13, 'New Administrative Capital', 50000, 'Government', 31.80, 30.02],
    [14, 'Al Rehab', 120000, 'Residential', 31.49, 30.06],
    [15, 'Sheikh Zayed', 150000, 'Residential', 30.94, 30.01]
]

# Facilities
facilities_data = [
    ['F1', 'Cairo International Airport', 'Airport', 31.41, 30.11],
    ['F2', 'Ramses Railway Station', 'Transit Hub', 31.25, 30.06],
    ['F3', 'Cairo University', 'Education', 31.21, 30.03],
    ['F4', 'Al-Azhar University', 'Education', 31.26, 30.05],
    ['F5', 'Egyptian Museum', 'Tourism', 31.23, 30.05],
    ['F6', 'Cairo International Stadium', 'Sports', 31.30, 30.07],
    ['F7', 'Smart Village', 'Business', 30.97, 30.07],
    ['F8', 'Cairo Festival City', 'Commercial', 31.40, 30.03],
    ['F9', 'Qasr El Aini Hospital', 'Medical', 31.23, 30.03],
    ['F10', 'Maadi Military Hospital', 'Medical', 31.25, 29.95]
]

# Existing roads
existing_roads = [
    [1, 3, 8.5, 3000, 7],
    [1, 8, 6.2, 2500, 6],
    [2, 3, 5.9, 2800, 8],
    [2, 5, 4.0, 3200, 9],
    [3, 5, 6.1, 3500, 7],
    [3, 6, 3.2, 2000, 8],
    [3, 9, 4.5, 2600, 6],
    [3, 10, 3.8, 2400, 7],
    [4, 2, 15.2, 3800, 9],
    [4, 14, 5.3, 3000, 10],
    [5, 11, 7.9, 3100, 7],
    [6, 9, 2.2, 1800, 8],
    [7, 8, 24.5, 3500, 8],
    [7, 15, 9.8, 3000, 9],
    [8, 10, 3.3, 2200, 7],
    [8, 12, 14.8, 2600, 5],
    [9, 10, 2.1, 1900, 7],
    [10, 11, 8.7, 2400, 6],
    [11, 'F2', 3.6, 2200, 7],
    [12, 1, 12.7, 2800, 6],
    [13, 4, 45.0, 4000, 10],
    [14, 13, 35.5, 3800, 9],
    [15, 7, 9.8, 3000, 9],
    ['F1', 5, 7.5, 3500, 9],
    ['F1', 2, 9.2, 3200, 8],
    ['F2', 3, 2.5, 2000, 7],
    ['F7', 15, 8.3, 2800, 8],
    ['F8', 4, 6.1, 3000, 9]
]

# Potential roads
potential_roads = [
    [1, 4, 22.8, 4000, 450],
    [1, 14, 25.3, 3800, 500],
    [2, 13, 48.2, 4500, 950],
    [3, 13, 56.7, 4500, 1100],
    [5, 4, 16.8, 3500, 320],
    [6, 8, 7.5, 2500, 150],
    [7, 13, 82.3, 4000, 1600],
    [9, 11, 6.9, 2800, 140],
    [10, 'F7', 27.4, 3200, 550],
    [11, 13, 62.1, 4200, 1250],
    [12, 14, 30.5, 3600, 610],
    [14, 5, 18.2, 3300, 360],
    [15, 9, 22.7, 3000, 450],
    ['F1', 13, 40.2, 4000, 800],
    ['F7', 9, 26.8, 3200, 540]
]

# Traffic flow data
traffic_flow_data = [
    ['Maadi-Downtown Cairo', 2800, 1500, 2600, 800],
    ['Maadi-Giza', 2200, 1200, 2100, 600],
    ['Nasr City-Downtown Cairo', 2700, 1400, 2500, 700],
    ['Nasr City-Heliopolis', 3000, 1600, 2800, 650],
    ['Downtown Cairo-Heliopolis', 3200, 1700, 3100, 800],
    ['Downtown Cairo-Zamalek', 1800, 1400, 1900, 500],
    ['Downtown Cairo-Mohandessin', 2400, 1300, 2200, 550],
    ['Downtown Cairo-Dokki', 2300, 1200, 2100, 500],
    ['New Cairo-Nasr City', 3600, 1800, 3300, 750],
    ['New Cairo-Al Rehab', 2800, 1600, 2600, 600],
    ['Heliopolis-Shubra', 2900, 1500, 2700, 650],
    ['Zamalek-Mohandessin', 1700, 1300, 1800, 450],
    ['6th October City-Giza', 3200, 1700, 3000, 700],
    ['6th October City-Sheikh Zayed', 2800, 1500, 2600, 600],
    ['Giza-Dokki', 2000, 1100, 1900, 450],
    ['Giza-Helwan', 2400, 1300, 2200, 500],
    ['Mohandessin-Dokki', 1800, 1200, 1700, 400],
    ['Dokki-Shubra', 2200, 1300, 2100, 500],
    ['Shubra-Ramses Railway Station', 2100, 1200, 2000, 450],
    ['Helwan-Maadi', 2600, 1400, 2400, 550],
    ['New Administrative Capital-New Cairo', 3800, 2000, 3500, 800],
    ['Al Rehab-New Administrative Capital', 3600, 1900, 3300, 750],
    ['Sheikh Zayed-6th October City', 2800, 1500, 2600, 600],
    ['Cairo International Airport-Heliopolis', 3300, 2200, 3100, 1200],
    ['Cairo International Airport-Nasr City', 3000, 2000, 2800, 1100],
    ['Ramses Railway Station-Downtown Cairo', 1900, 1600, 1800, 900],
    ['Smart Village-Sheikh Zayed', 2600, 1500, 2400, 550],
    ['Cairo Festival City-New Cairo', 2800, 1600, 2600, 600],
    ['Qasr El Aini Hospital-Downtown Cairo', 1500, 1000, 1400, 400],
    ['Maadi Military Hospital-Maadi', 1200, 800, 1100, 300]
]

# Emergency routing data
neighborhoods = {
    "Downtown Cairo": {"name": "Downtown Cairo", "x": 0, "y": 0, "type": "Neighborhood"},
    "Zamalek": {"name": "Zamalek", "x": 2, "y": 2, "type": "Neighborhood"},
    "Maadi": {"name": "Maadi", "x": 0, "y": -5, "type": "Neighborhood"},
    "Heliopolis": {"name": "Heliopolis", "x": 5, "y": 2, "type": "Neighborhood"},
    "Nasr City": {"name": "Nasr City", "x": 7, "y": 2, "type": "Neighborhood"},
    "6th of October": {"name": "6th of October", "x": -8, "y": 0, "type": "Neighborhood"},
    "New Cairo": {"name": "New Cairo", "x": 10, "y": 0, "type": "Neighborhood"},
    "Mohandessin": {"name": "Mohandessin", "x": -3, "y": 2, "type": "Neighborhood"},
    "Shubra": {"name": "Shubra", "x": 0, "y": 5, "type": "Neighborhood"},
    "Dokki": {"name": "Dokki", "x": -3, "y": 1, "type": "Neighborhood"},
    "Giza": {"name": "Giza", "x": -5, "y": -2, "type": "Neighborhood"},
    "October City": {"name": "October City", "x": -9, "y": -1, "type": "Neighborhood"},
    "Garden City": {"name": "Garden City", "x": 1, "y": -1, "type": "Neighborhood"},
    "Agouza": {"name": "Agouza", "x": -2, "y": 3, "type": "Neighborhood"}
}

facilities = {
    "F1": {"name": "El Salam Hospital", "x": 6, "y": 3, "type": "Facility", "is_critical": True},
    "F2": {"name": "Maadi Fire Station", "x": 1, "y": -4, "type": "Facility", "is_critical": True},
    "F3": {"name": "Nasr City Police Station", "x": 8, "y": 3, "type": "Facility", "is_critical": True},
    "F4": {"name": "Giza Central Hospital", "x": -4, "y": -3, "type": "Facility", "is_critical": True},
    "F5": {"name": "October Fire Station", "x": -7, "y": -1, "type": "Facility", "is_critical": True},
    "F6": {"name": "6th October Hospital", "x": -7, "y": 1, "type": "Facility", "is_critical": True},
    "F7": {"name": "New Cairo Fire Station", "x": 9, "y": 1, "type": "Facility", "is_critical": True},
    "F8": {"name": "Mohandessin Police Station", "x": -2, "y": 2, "type": "Facility", "is_critical": True},
    "F9": {"name": "Shubra Hospital", "x": 1, "y": 6, "type": "Facility", "is_critical": True},
    "F10": {"name": "Garden City Hospital", "x": 2, "y": -1, "type": "Facility", "is_critical": True}
}

roads = {
    1: {"from": "Downtown Cairo", "to": "Zamalek", "distance": 2, "capacity": 50, "traffic": 10, "condition": "good"},
    2: {"from": "Zamalek", "to": "Maadi", "distance": 3, "capacity": 40, "traffic": 20, "condition": "average"},
    3: {"from": "Maadi", "to": "El Salam Hospital", "distance": 5, "capacity": 20, "traffic": 30, "condition": "poor"},
    4: {"from": "Heliopolis", "to": "Nasr City", "distance": 4, "capacity": 60, "traffic": 15, "condition": "good"},
    5: {"from": "Nasr City", "to": "New Cairo", "distance": 7, "capacity": 30, "traffic": 25, "condition": "average"},
    6: {"from": "6th of October", "to": "Heliopolis", "distance": 10, "capacity": 40, "traffic": 35, "condition": "poor"},
    7: {"from": "Zamalek", "to": "Maadi Fire Station", "distance": 3, "capacity": 40, "traffic": 5, "condition": "good"},
    8: {"from": "Nasr City", "to": "Nasr City Police Station", "distance": 3, "capacity": 50, "traffic": 10, "condition": "good"},
    9: {"from": "New Cairo", "to": "6th of October", "distance": 12, "capacity": 25, "traffic": 40, "condition": "poor"},
    10: {"from": "Mohandessin", "to": "Shubra", "distance": 7, "capacity": 45, "traffic": 25, "condition": "average"},
    11: {"from": "Heliopolis", "to": "Dokki", "distance": 8, "capacity": 35, "traffic": 30, "condition": "good"},
    12: {"from": "Dokki", "to": "Giza", "distance": 6, "capacity": 50, "traffic": 20, "condition": "good"},
    13: {"from": "Giza", "to": "Giza Central Hospital", "distance": 5, "capacity": 30, "traffic": 40, "condition": "poor"},
    14: {"from": "Maadi", "to": "October Fire Station", "distance": 4, "capacity": 40, "traffic": 20, "condition": "average"},
    15: {"from": "Nasr City", "to": "El Salam Hospital", "distance": 4, "capacity": 55, "traffic": 12, "condition": "good"},
    16: {"from": "6th of October", "to": "6th October Hospital", "distance": 9, "capacity": 25, "traffic": 30, "condition": "average"},
    17: {"from": "New Cairo", "to": "New Cairo Fire Station", "distance": 5, "capacity": 40, "traffic": 20, "condition": "good"},
    18: {"from": "Mohandessin", "to": "Mohandessin Police Station", "distance": 6, "capacity": 35, "traffic": 15, "condition": "good"},
    19: {"from": "Shubra", "to": "Shubra Hospital", "distance": 8, "capacity": 45, "traffic": 25, "condition": "average"},
    20: {"from": "Giza", "to": "New Cairo Fire Station", "distance": 5, "capacity": 40, "traffic": 30, "condition": "poor"}
}

# Transit routes
transit_routes = [
    {"route_id": 1, "type": "Metro", "stops": ["Maadi", "Downtown Cairo", "Zamalek"], "frequency": 10, "capacity": 500},
    {"route_id": 2, "type": "Bus", "stops": ["Nasr City", "Heliopolis", "New Cairo"], "frequency": 15, "capacity": 50},
    {"route_id": 3, "type": "Metro", "stops": ["Giza", "Dokki", "Downtown Cairo"], "frequency": 12, "capacity": 400},
    {"route_id": 4, "type": "Bus", "stops": ["6th October City", "Sheikh Zayed", "Giza"], "frequency": 20, "capacity": 60}
]

# DataFrames
df_neighborhoods = pd.DataFrame(neighborhoods_data, columns=['ID', 'Name', 'Population', 'Type', 'X', 'Y'])
df_facilities = pd.DataFrame(facilities_data, columns=['ID', 'Name', 'Type', 'X', 'Y'])
df_existing = pd.DataFrame(existing_roads, columns=['FromID', 'ToID', 'Distance', 'Capacity', 'Condition'])
df_potential = pd.DataFrame(potential_roads, columns=['FromID', 'ToID', 'Distance', 'Capacity', 'Cost'])
df_traffic = pd.DataFrame(traffic_flow_data, columns=['RoadName', 'Morning', 'Afternoon', 'Evening', 'Night'])
all_nodes = pd.concat([
    df_neighborhoods[['ID', 'Name', 'Type', 'X', 'Y', 'Population']],
    df_facilities[['ID', 'Name', 'Type', 'X', 'Y']].assign(Population=0)
])
df_existing['Maintenance_Cost'] = (10 - df_existing['Condition']) * df_existing['Distance'] * 10