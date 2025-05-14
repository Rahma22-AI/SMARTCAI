import pytest
from data import build_traffic_graph, all_nodes, df_existing, df_potential, name_to_id
from algorithms import a_star, dijkstra, kruskal_mst, optimize_maintenance, greedy_maintenance

def test_a_star():
    G = build_traffic_graph()
    path, distance = a_star(G, name_to_id['Maadi'], name_to_id['El Salam Hospital'], False)
    assert len(path) > 1
    assert distance > 0

def test_dijkstra():
    G = build_traffic_graph()
    path, distance = dijkstra(G, name_to_id['Downtown'], name_to_id['Nasr City'], "Morning")
    assert len(path) > 1
    assert distance > 0

def test_kruskal_mst():
    G = build_traffic_graph()
    mst_edges, total_cost = kruskal_mst(G, df_existing, df_potential, [('F9', 1)])
    assert len(mst_edges) >= 1
    assert total_cost > 0

def test_optimize_maintenance():
    selected_roads, improvement = optimize_maintenance(df_existing, 500)
    assert len(selected_roads) >= 0
    assert improvement >= 0

def test_greedy_maintenance():
    selected_roads, improvement = greedy_maintenance(df_existing, 500)
    assert len(selected_roads) >= 0
    assert improvement >= 0