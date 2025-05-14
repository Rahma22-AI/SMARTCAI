import unittest
import pandas as pd
import networkx as nx
from algorithms import a_star, modified_kruskal, time_dependent_dijkstra, public_transport_dp, optimize_maintenance, greedy_maintenance, get_traffic_speed
from emergency_routing import G_emergency
from urban_planning import build_traffic_graph
from public_transit import create_station_mapping, create_routes, analyze_transfer_points
from data import df_existing, df_potential, all_nodes, df_traffic, transit_routes, df_neighborhoods

class TestTransitSystem(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.name_to_id = {row['Name']: row['ID'] for _, row in all_nodes.iterrows()}
        self.id_to_name = {v: k for k, v in self.name_to_id.items()}
        self.stations = create_station_mapping()
        self.traffic_graph = build_traffic_graph()

    def test_a_star(self):
        """Test A* finds a valid path to a facility."""
        start = "Downtown Cairo"
        goal = "El Salam Hospital"
        path = a_star(start, goal, G_emergency, priority=True)
        self.assertTrue(path, "No path found by A*")
        self.assertEqual(path[0], start, "Path should start at Downtown Cairo")
        self.assertEqual(path[-1], goal, "Path should end at El Salam Hospital")
        normal_path = a_star(start, goal, G_emergency, priority=False)
        normal_weight = sum(G_emergency[path[i]][path[i+1]]['weight'] for i in range(len(normal_path)-1))
        priority_weight = sum(G_emergency[path[i]][path[i+1]]['weight'] * 0.5 for i in range(len(path)-1))
        self.assertLess(priority_weight, normal_weight, "Priority mode should reduce travel time")

    def test_modified_kruskal(self):
        """Test MST includes mandatory connections."""
        df_existing_edges = df_existing[['FromID', 'ToID']].copy()
        df_existing_edges['Cost'] = df_existing['Maintenance_Cost']
        df_existing_edges['Type'] = 'Existing'
        df_potential_edges = df_potential[['FromID', 'ToID']].copy()
        df_potential_edges['Cost'] = df_potential['Cost']
        df_potential_edges['Type'] = 'Potential'
        all_edges = pd.concat([df_existing_edges, df_potential_edges])
        mandatory_connections = [('F9', 3), ('F10', 1)]
        mst_edges, total_cost = modified_kruskal(all_edges, all_nodes, mandatory_connections)
        mandatory_found = [(u, v) for u, v, _ in mst_edges if (u, v) in mandatory_connections or (v, u) in mandatory_connections]
        self.assertEqual(len(mandatory_found), len(mandatory_connections), "Mandatory connections not included")
        self.assertGreater(total_cost, 0, "Total cost should be positive")

    def test_time_dependent_dijkstra(self):
        """Test Dijkstra’s accounts for traffic congestion."""
        start_name = "Maadi"
        end_name = "Downtown Cairo"
        morning_time, morning_path = time_dependent_dijkstra(self.traffic_graph, start_name, end_name, "Morning", df_traffic, df_existing, self.name_to_id, self.id_to_name)
        night_time, night_path = time_dependent_dijkstra(self.traffic_graph, start_name, end_name, "Night", df_traffic, df_existing, self.name_to_id, self.id_to_name)
        self.assertTrue(morning_path, "No path found for morning")
        self.assertTrue(night_path, "No path found for night")
        self.assertGreater(morning_time, night_time, "Morning travel time should be higher due to congestion")

    def test_public_transport_dp(self):
        """Test DP optimizes transit coverage."""
        routes = create_routes("Morning", self.name_to_id)
        time_slots = 6
        max_vehicles = 2
        start_station = "Maadi"
        dp, paths, coverage = public_transport_dp(self.stations, routes, time_slots, start_station, max_vehicles, transit_routes)
        self.assertGreater(coverage, 0, "Coverage score should be positive")
        self.assertLess(coverage, sum(df_neighborhoods['Population']), "Coverage score too high")
        for station in self.stations:
            if station != start_station:
                min_time = min(dp[station])
                if min_time != float('inf'):
                    self.assertGreaterEqual(min_time, 0, f"Travel time to {station} should be non-negative")

    def test_optimize_maintenance(self):
        """Test DP maintenance respects budget."""
        budget = 500
        improvement, selected_roads = optimize_maintenance(df_existing, budget)
        self.assertGreaterEqual(improvement, 0, "Improvement should be non-negative")
        total_cost = sum(df_existing[
            ((df_existing['FromID'] == u) & (df_existing['ToID'] == v)) |
            ((df_existing['FromID'] == v) & (df_existing['ToID'] == u))
        ]['Maintenance_Cost'].iloc[0] for u, v in selected_roads)
        self.assertLessEqual(total_cost, budget, "Selected roads exceed budget")

    def test_greedy_maintenance(self):
        """Test greedy maintenance respects budget."""
        budget = 500
        improvement, selected_roads = greedy_maintenance(df_existing, budget)
        self.assertGreaterEqual(improvement, 0, "Improvement should be non-negative")
        total_cost = sum(df_existing[
            ((df_existing['FromID'] == u) & (df_existing['ToID'] == v)) |
            ((df_existing['FromID'] == v) & (df_existing['ToID'] == u))
        ]['Maintenance_Cost'].iloc[0] for u, v in selected_roads)
        self.assertLessEqual(total_cost, budget, "Selected roads exceed budget")

    def test_analyze_transfer_points(self):
        """Test transfer point analysis identifies hubs."""
        transfer_hubs, transfer_times = analyze_transfer_points(transit_routes, self.stations)
        for hub, count in transfer_hubs.items():
            route_count = sum(1 for route in transit_routes if hub in route['stops'])
            self.assertEqual(count, route_count, f"Incorrect route count for hub {hub}")
            self.assertGreaterEqual(count, 2, f"Hub {hub} should have at least 2 routes")
        for transfer in transfer_times:
            self.assertIn(transfer['Hub'], transfer_hubs, "Transfer time for non-hub")
            self.assertGreater(transfer['Avg_Wait_Time'], 0, "Transfer time should be positive")

if __name__ == '__main__':
    unittest.main()