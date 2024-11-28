import pytest

from test_petri_net_fixtures import _petri_net_with_AND_and_nested_XOR, _petri_net_with_loop_inside_AND, \
    _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND, \
    _petri_net_with_AND_and_nested_XOR_simple, _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND_simple, \
    _petri_net_with_three_loops_inside_AND_two_of_them_inside_sub_AND, \
    _petri_net_with_loop_inside_parallel_and_loop_all_back, _petri_net_with_infinite_loop, \
    _petri_net_with_infinite_loop_and_AND


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


def test_reachability_graph_double_loop_model():
    petri_net = _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    # Assert general sizes
    assert len(reachability_graph.markings) == 9
    assert len(reachability_graph.edges) == 18
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 4
    assert len(reachability_graph.activity_to_edges["C"]) == 4
    assert len(reachability_graph.activity_to_edges["D"]) == 2
    assert len(reachability_graph.activity_to_edges["E"]) == 2
    assert len(reachability_graph.activity_to_edges["F"]) == 2
    assert len(reachability_graph.activity_to_edges["G"]) == 2
    assert len(reachability_graph.activity_to_edges["H"]) == 1
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
            reachability_graph.marking_to_key[tuple(sorted({"37", "16"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"15", "38"}))],
            reachability_graph.marking_to_key[tuple(sorted({"40"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["G"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"8", "9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"15", "38"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"37", "16"}))],
            reachability_graph.marking_to_key[tuple(sorted({"40"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["H"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"40"}))],
            reachability_graph.marking_to_key[tuple(sorted({"42"}))]) in edges
    # # # # # # # # # # # # # # # # #
    # Same test on simple Petri net #
    # # # # # # # # # # # # # # # # #
    petri_net = _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND_simple()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    assert len(reachability_graph.markings) == 9
    assert len(reachability_graph.edges) == 18
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 4
    assert len(reachability_graph.activity_to_edges["C"]) == 4
    assert len(reachability_graph.activity_to_edges["D"]) == 2
    assert len(reachability_graph.activity_to_edges["E"]) == 2
    assert len(reachability_graph.activity_to_edges["F"]) == 2
    assert len(reachability_graph.activity_to_edges["G"]) == 2
    assert len(reachability_graph.activity_to_edges["H"]) == 1
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"0"}))],
            reachability_graph.marking_to_key[tuple(sorted({"2", "3"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "3"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "3"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "3"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "3"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "7"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "7"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "7"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "7"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["D"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "7"}))],
            reachability_graph.marking_to_key[tuple(sorted({"17", "12"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"11", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"17", "18"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["G"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "7"}))],
            reachability_graph.marking_to_key[tuple(sorted({"11", "18"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"17", "12"}))],
            reachability_graph.marking_to_key[tuple(sorted({"17", "18"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["H"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"17", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"20"}))]) in edges


def test_reachability_graph_triple_loop_model():
    petri_net = _petri_net_with_three_loops_inside_AND_two_of_them_inside_sub_AND()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    # Assert general sizes
    assert len(reachability_graph.markings) == 13
    assert len(reachability_graph.edges) == 33
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 2
    assert len(reachability_graph.activity_to_edges["B"]) == 8
    assert len(reachability_graph.activity_to_edges["C"]) == 8
    assert len(reachability_graph.activity_to_edges["D"]) == 12
    assert len(reachability_graph.activity_to_edges["E"]) == 2
    assert len(reachability_graph.activity_to_edges["F"]) == 1
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "7", "18"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "7", "20"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "7", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "7", "18"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"10", "7", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "7", "18"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "7", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "7", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"10", "7", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "7", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "11", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "11", "18"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"10", "11", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "11", "18"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "11", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "11", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"10", "11", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "11", "20"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["D"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"2", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"2", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "7", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "7", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "7", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "7", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"10", "7", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "7", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"10", "7", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "7", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "11", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "11", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "11", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "11", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"10", "11", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "11", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"10", "11", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"10", "11", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"17", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"17", "20"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"17", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"17", "20"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["E"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"10", "11", "18"}))],
            reachability_graph.marking_to_key[tuple(sorted({"17", "18"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"10", "11", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"17", "20"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["F"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"17", "20"}))],
            reachability_graph.marking_to_key[tuple(sorted({"25"}))]) in edges


def test_reachability_graph_loop_inside_parallel_and_loop_all_back():
    petri_net = _petri_net_with_loop_inside_parallel_and_loop_all_back()
    # Check incorrect format raises error
    with pytest.raises(RuntimeError) as e_info:
        petri_net.get_reachability_graph(cached_search=False)
        assert e_info == "Incorrect model structure! Check logged info."
    # Repair and continue with correct format
    petri_net.add_transition("14_it", "14_incoming_transition", invisible=True)
    petri_net.add_place("14_ip", "14_incoming_place")
    petri_net.id_to_place["12"].outgoing = {"13"}
    petri_net.id_to_transition["14"].incoming = set()
    petri_net.add_edge("12", "14_it")
    petri_net.add_edge("14_it", "14_ip")
    petri_net.add_edge("14_ip", "14")
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    # Assert general sizes
    assert len(reachability_graph.markings) == 6
    assert len(reachability_graph.edges) == 10
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"0"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "8"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "8"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "8"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "8"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "8"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "10"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "10"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "10"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "10"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "10"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "8"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["C"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "8"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "10"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "8"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "10"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "10"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "10"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["D"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "10"}))],
            reachability_graph.marking_to_key[tuple(sorted({"15"}))]) in edges


def test_reachability_graph_infinite_loop():
    petri_net = _petri_net_with_infinite_loop()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    # Assert general sizes
    assert len(reachability_graph.markings) == 4
    assert len(reachability_graph.edges) == 5
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"0"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4"}))],
            reachability_graph.marking_to_key[tuple(sorted({"11"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"11"}))],
            reachability_graph.marking_to_key[tuple(sorted({"11"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["C"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4"}))],
            reachability_graph.marking_to_key[tuple(sorted({"16"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"11"}))],
            reachability_graph.marking_to_key[tuple(sorted({"16"}))]) in edges


def test_reachability_graph_infinite_loop_and_AND():
    petri_net = _petri_net_with_infinite_loop_and_AND()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    # Assert general sizes
    assert len(reachability_graph.markings) == 6
    assert len(reachability_graph.edges) == 15
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"0"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4"}))],
            reachability_graph.marking_to_key[tuple(sorted({"11", "12"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "17"}))],
            reachability_graph.marking_to_key[tuple(sorted({"11", "12"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"11", "12"}))],
            reachability_graph.marking_to_key[tuple(sorted({"11", "12"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"22"}))],
            reachability_graph.marking_to_key[tuple(sorted({"11", "12"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "17"}))],
            reachability_graph.marking_to_key[tuple(sorted({"22"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["D"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4"}))],
            reachability_graph.marking_to_key[tuple(sorted({"27"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"11", "12"}))],
            reachability_graph.marking_to_key[tuple(sorted({"27"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"6", "17"}))],
            reachability_graph.marking_to_key[tuple(sorted({"27"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"22"}))],
            reachability_graph.marking_to_key[tuple(sorted({"27"}))]) in edges
