from test_petri_net_fixtures import _petri_net_with_AND_and_nested_XOR, _petri_net_with_AND_and_nested_XOR_simple


def test_reachability_graph_nested_XOR():
    # # # # # # # # # # # # # # # # # # # # #
    # Complex Petri net with many invisible #
    # # # # # # # # # # # # # # # # # # # # #
    petri_net = _petri_net_with_AND_and_nested_XOR()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    # Assert general sizes
    assert len(reachability_graph.markings) == 6
    assert len(reachability_graph.edges) == 10
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 2
    assert len(reachability_graph.activity_to_edges["C"]) == 2
    assert len(reachability_graph.activity_to_edges["D"]) == 2
    assert len(reachability_graph.activity_to_edges["E"]) == 2
    assert len(reachability_graph.activity_to_edges["F"]) == 1
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"0"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "5"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["C"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "5"}))],
            reachability_graph.marking_to_key[tuple(sorted({"23", "5"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "25"}))],
            reachability_graph.marking_to_key[tuple(sorted({"27"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["E"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "5"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "25"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"23", "5"}))],
            reachability_graph.marking_to_key[tuple(sorted({"27"}))]) in edges
    # # # # # # # # # # # # # # # # #
    # Same test on simple Petri net #
    # # # # # # # # # # # # # # # # #
    petri_net = _petri_net_with_AND_and_nested_XOR_simple()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    # Assert general sizes
    assert len(reachability_graph.markings) == 6
    assert len(reachability_graph.edges) == 10
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 2
    assert len(reachability_graph.activity_to_edges["C"]) == 2
    assert len(reachability_graph.activity_to_edges["D"]) == 2
    assert len(reachability_graph.activity_to_edges["E"]) == 2
    assert len(reachability_graph.activity_to_edges["F"]) == 1
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"0"}))],
            reachability_graph.marking_to_key[tuple(sorted({"2", "3"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["C"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "3"}))],
            reachability_graph.marking_to_key[tuple(sorted({"8", "3"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"8", "9"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["E"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "3"}))],
            reachability_graph.marking_to_key[tuple(sorted({"2", "9"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"8", "3"}))],
            reachability_graph.marking_to_key[tuple(sorted({"8", "9"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["F"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"8", "9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"11"}))]) in edges


def test_reachability_graph_loop_model():
    petri_net = _petri_net_with_loop_inside_AND()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    # Assert general sizes
    assert len(reachability_graph.markings) == 6
    assert len(reachability_graph.edges) == 8
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 4
    assert len(reachability_graph.activity_to_edges["C"]) == 2
    assert len(reachability_graph.activity_to_edges["D"]) == 1
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"0"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "5"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "5"}))],
            reachability_graph.marking_to_key[tuple(sorted({"8", "5"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"8", "5"}))],
            reachability_graph.marking_to_key[tuple(sorted({"8", "5"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"8", "9"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"8", "9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"8", "9"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["D"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"8", "9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"14"}))]) in edges
