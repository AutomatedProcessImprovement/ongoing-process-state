import pytest

from test_bpmn_model_fixtures import _bpmn_model_with_AND_and_XOR, _bpmn_model_with_XOR_within_AND, \
    _bpmn_model_with_AND_and_nested_XOR, _bpmn_model_with_loop_inside_AND, \
    _bpmn_model_with_two_loops_inside_AND_followed_by_XOR_within_AND, \
    _bpmn_model_with_three_loops_inside_AND_two_of_them_inside_sub_AND


def test_create_bpmn_model():
    bpmn_model = _bpmn_model_with_AND_and_XOR()
    # Assert general characteristics
    assert len(bpmn_model.nodes) == 12
    assert len(bpmn_model.flows) == 13
    assert sum([len(node.incoming_flows) for node in bpmn_model.nodes]) == 13
    assert sum([len(node.outgoing_flows) for node in bpmn_model.nodes]) == 13
    # Assert some nodes have the expected incoming and outgoing arcs
    assert bpmn_model.id_to_node["4"].incoming_flows == {"3"}
    assert bpmn_model.id_to_node["4"].outgoing_flows == {"5", "6"}
    assert bpmn_model.id_to_node["16"].incoming_flows == {"14"}
    assert bpmn_model.id_to_node["16"].outgoing_flows == {"18"}
    assert bpmn_model.id_to_node["20"].incoming_flows == {"18", "19"}
    assert bpmn_model.id_to_node["20"].outgoing_flows == {"21"}
    assert bpmn_model.id_to_node["24"].incoming_flows == {"23"}
    assert len(bpmn_model.id_to_node["24"].outgoing_flows) == 0


def test_simulate_execution_and_enabled_nodes():
    bpmn_model = _bpmn_model_with_AND_and_XOR()
    # Initialize marking
    marking = bpmn_model.get_initial_marking()
    assert marking == {"1"}
    # Simulate execution
    marking = bpmn_model.simulate_execution("2", marking)[0]
    marking = bpmn_model.simulate_execution("4", marking)[0]
    assert marking == {"5", "6"}
    assert bpmn_model.get_enabled_nodes(marking) == {"7", "8"}
    marking = bpmn_model.simulate_execution("7", marking)[0]
    marking = bpmn_model.simulate_execution("8", marking)[0]
    marking = bpmn_model.simulate_execution("11", marking)[0]
    assert marking == {"12"}
    assert bpmn_model.get_enabled_nodes(marking) == {"13"}
    [marking_one, marking_two] = bpmn_model.simulate_execution("13", marking)
    if "16" in bpmn_model.get_enabled_nodes(marking_one):
        marking_one = bpmn_model.simulate_execution("16", marking_one)[0]
    else:
        marking_one = bpmn_model.simulate_execution("17", marking_one)[0]
    marking_one = bpmn_model.simulate_execution("20", marking_one)[0]
    if "17" in bpmn_model.get_enabled_nodes(marking_two):
        marking_two = bpmn_model.simulate_execution("17", marking_two)[0]
    else:
        marking_two = bpmn_model.simulate_execution("16", marking_two)[0]
    marking_two = bpmn_model.simulate_execution("20", marking_two)[0]
    assert marking_one == {"21"}
    assert marking_one == marking_two
    marking = marking_one
    assert bpmn_model.get_enabled_nodes(marking) == {"22"}
    marking = bpmn_model.simulate_execution("22", marking)[0]
    assert marking == {"23"}
    marking = bpmn_model.simulate_execution("24", marking)[0]
    assert len(marking) == 0


def test_advance_marking_until_decision_point_simple_model():
    bpmn_model = _bpmn_model_with_AND_and_XOR()
    # Advance from state where the AND-split is enabled: it should execute it enabling both branches
    marking = bpmn_model.advance_marking_until_decision_point({"3"})
    assert marking == {"5", "6"}
    # Advance from state where the AND-join is enabled: it should execute only the AND-join
    marking = bpmn_model.advance_marking_until_decision_point({"9", "10"})
    assert marking == {"12"}
    # Advance from state where only one task is enabled: no advance
    marking = bpmn_model.advance_marking_until_decision_point({"21"})
    assert marking == {"21"}


def test_advance_full_marking_simple_model():
    bpmn_model = _bpmn_model_with_AND_and_XOR()
    # Advance from state where the AND-split is enabled: it should execute it enabling both branches
    markings = bpmn_model.advance_full_marking({"3"})
    assert markings == [{"5", "6"}]
    # Advance from state where the AND-join is enabled: it should execute both the AND-join and following XOR-split
    markings = bpmn_model.advance_full_marking({"9", "10"})
    assert len(markings) == 2
    assert {"14"} in markings
    assert {"15"} in markings
    # Advance from state where only one task is enabled: no advance
    markings = bpmn_model.advance_full_marking({"21"})
    assert markings == [{"21"}]


def test_advance_marking_until_decision_point_XOR_within_AND_model():
    bpmn_model = _bpmn_model_with_XOR_within_AND()
    # Advance from state where only one task is enabled: no advance
    marking = bpmn_model.advance_marking_until_decision_point({"1"})
    assert marking == {"1"}
    # Advance from state where the AND-split is enabled: it should execute the AND-split
    marking = bpmn_model.advance_marking_until_decision_point({"3"})
    assert marking == {"5", "6", "7"}
    # Advance from state where only the XOR-join of 2 branches are enabled: it should advance until the AND-join
    marking = bpmn_model.advance_marking_until_decision_point({"23", "26", "16"})
    assert marking == {"32", "33", "16"}
    # Advance from state where the three XOR-join are enabled: it should execute the XOR-join and AND-join
    marking = bpmn_model.advance_marking_until_decision_point({"23", "26", "28"})
    assert marking == {"36"}


def test_advance_full_marking_XOR_within_AND_model():
    bpmn_model = _bpmn_model_with_XOR_within_AND()
    # Advance from state where only one task is enabled: no advance
    markings = bpmn_model.advance_full_marking({"1"})
    assert markings == [{"1"}]
    # Advance from state where the AND-split is enabled: it should execute the AND-split and each following XOR-split
    markings = bpmn_model.advance_full_marking({"3"})
    assert len(markings) == 6
    assert {"11", "6", "7"} in markings
    assert {"12", "6", "7"} in markings
    assert {"5", "13", "7"} in markings
    assert {"5", "14", "7"} in markings
    assert {"5", "6", "15"} in markings
    assert {"5", "6", "16"} in markings
    # Advance from state where only the XOR-join of 2 branches are enabled: it should advance until the AND-join
    markings = bpmn_model.advance_full_marking({"23", "26", "16"})
    assert markings == [{"32", "33", "16"}]
    # Advance from state where the three XOR-join are enabled: it should execute the XOR-join and AND-join
    markings = bpmn_model.advance_full_marking({"23", "26", "28"})
    assert markings == [{"36"}]


def test_advance_marking_until_decision_point_nested_XOR_model():
    bpmn_model = _bpmn_model_with_AND_and_nested_XOR()
    # Advance from state where the AND-split is enabled: it should execute it enabling both branches
    marking = bpmn_model.advance_marking_until_decision_point({"3"})
    assert marking == {"4", "6"}
    # Advance from state where one of the upper XOR-join is enabled: it should execute the XOR-join (not the AND-join)
    marking = bpmn_model.advance_marking_until_decision_point({"6", "16"})
    assert marking == {"6", "21"}
    # Advance from state where one of the upper XOR-join is enabled and the lower AND branch: should fully advance
    marking = bpmn_model.advance_marking_until_decision_point({"17", "20"})
    assert marking == {"27"}


def test_advance_full_marking_nested_XOR_model():
    bpmn_model = _bpmn_model_with_AND_and_nested_XOR()
    # Advance from state where the AND-split is enabled: it should execute it enabling both branches
    markings = bpmn_model.advance_full_marking({"3"})
    assert len(markings) == 3
    assert {"6", "8"} in markings
    assert {"6", "12"} in markings
    assert {"6", "13"} in markings
    # Advance from state where one of the upper XOR-join is enabled: it should execute the XOR-join (not the AND-join)
    markings = bpmn_model.advance_full_marking({"6", "16"})
    assert markings == [{"6", "21"}]
    # Advance from state where one of the upper XOR-join is enabled and the lower AND branch: should fully advance
    markings = bpmn_model.advance_full_marking({"17", "20"})
    assert markings == [{"27"}]


def test_advance_marking_until_decision_point_loop_model():
    bpmn_model = _bpmn_model_with_loop_inside_AND()
    # Advance from state where the AND-split is enabled: should execute it and advance through the XOR-join branch
    marking = bpmn_model.advance_marking_until_decision_point({"3"})
    assert marking == {"9", "6"}
    # Advance from state where the loop XOR is enabled, it should stay in the XOR-split
    marking = bpmn_model.advance_marking_until_decision_point({"11", "6"})
    assert marking == {"11", "6"}
    # Advance from state where the loop XOR is enabled, it should stay in the XOR-split
    marking = bpmn_model.advance_marking_until_decision_point({"11", "15"})
    assert marking == {"11", "15"}


def test_advance_full_marking_loop_model():
    bpmn_model = _bpmn_model_with_loop_inside_AND()
    # Advance from state where the AND-split is enabled: should execute it and advance through the XOR-join branch
    markings = bpmn_model.advance_full_marking({"3"})
    assert markings == [{"9", "6"}]
    # Advance from state where the loop XOR is enabled, it should generate both states going back (loop) and forward
    markings = bpmn_model.advance_full_marking({"11", "6"})
    assert len(markings) == 2
    assert {"9", "6"} in markings
    assert {"14", "6"} in markings
    # Advance from state where the loop XOR is enabled, it should generate both states going back (loop) and forward
    markings = bpmn_model.advance_full_marking({"11", "15"})
    assert len(markings) == 2
    assert {"9", "15"} in markings
    assert {"17"} in markings
    # Advance from state where only one task is enabled: no advance
    markings = bpmn_model.advance_full_marking({"17"})
    assert markings == [{"17"}]


def test_advance_marking_until_decision_point_double_loop_model():
    bpmn_model = _bpmn_model_with_two_loops_inside_AND_followed_by_XOR_within_AND()
    # Advance from state where the AND-split is enabled: should execute it and advance through the XOR-join branch
    marking = bpmn_model.advance_marking_until_decision_point({"3"})
    assert marking == {"9", "10"}
    # Advance from state where the loop XORs are enabled, it should stay in the XOR-splits
    marking = bpmn_model.advance_marking_until_decision_point({"13", "14"})
    assert marking == {"13", "14"}
    # Advance from state where the AND-join is enabled, it should traverse it and the following AND-split
    marking = bpmn_model.advance_marking_until_decision_point({"19", "20"})
    assert marking == {"24", "25"}
    # Advance from state where the two last XOR-join are enabled, it should traverse them and the following AND-join
    marking = bpmn_model.advance_marking_until_decision_point({"36", "39"})
    assert marking == {"43"}


def test_advance_full_marking_double_loop_model():
    bpmn_model = _bpmn_model_with_two_loops_inside_AND_followed_by_XOR_within_AND()
    # Advance from state where the AND-split is enabled: should execute it and advance through the XOR-join branch
    markings = bpmn_model.advance_full_marking({"3"})
    assert markings == [{"9", "10"}]
    # Advance from state where both loop XOR are enabled, it should:
    # - Traverse one of them going back individually (the other does not advance)
    # - Traverse the other going back individually (the first one does not advance)
    # - Traverse them together advancing and traversing the following AND-split, generating:
    #   - First branch of the AND-split advances (two combinations) while the other one holds
    #   - The other branch advances (two combinations) while the first one holds
    markings = bpmn_model.advance_full_marking({"13", "14"})
    assert len(markings) == 6
    assert {"9", "14"} in markings
    assert {"13", "10"} in markings
    assert {"28", "25"} in markings
    assert {"29", "25"} in markings
    assert {"24", "30"} in markings
    assert {"24", "31"} in markings


def test_advance_marking_until_decision_point_triple_loop_model():
    bpmn_model = _bpmn_model_with_three_loops_inside_AND_two_of_them_inside_sub_AND()
    # Advance from initial marking: should traverse the AND-split and one XOR-join
    marking = bpmn_model.advance_marking_until_decision_point({"1"})
    assert marking == {"3", "26"}
    # Advance from state where second AND-split is enabled and lower branch is before loop: should traverse all
    marking = bpmn_model.advance_marking_until_decision_point({"7", "4"})
    assert marking == {"13", "14", "26"}
    # Advance from state where the three XOR-split are enabled, no advancement
    marking = bpmn_model.advance_marking_until_decision_point({"17", "18", "28"})
    assert marking == {"17", "18", "28"}


def test_advance_full_marking_triple_loop_model():
    bpmn_model = _bpmn_model_with_three_loops_inside_AND_two_of_them_inside_sub_AND()
    # Advance from initial marking: should traverse the AND-split and one XOR-join
    marking = bpmn_model.advance_marking_until_decision_point({"1"})
    assert marking == {"3", "26"}
    # Advance from state where second AND-split is enabled and lower branch is before loop: should traverse all
    marking = bpmn_model.advance_marking_until_decision_point({"7", "4"})
    assert marking == {"13", "14", "26"}
    # Advance from state where the three loop XOR-split are enabled, it should:
    # - Traverse one of them going back individually (the other two do not advance)
    # - Traverse the second one going back individually (the other two do not advance)
    # - Traverse the third one going back individually (the other two do not advance)
    # - Traverse the two that end in the same AND-join together, and the AND-join too (the other branch holds)
    markings = bpmn_model.advance_full_marking({"17", "18", "28"})
    assert len(markings) == 4
    assert {"13", "18", "28"} in markings
    assert {"17", "14", "28"} in markings
    assert {"17", "18", "26"} in markings
    assert {"31", "28"} in markings


def test_reachability_graph_simple():
    bpmn_model = _bpmn_model_with_AND_and_XOR()
    reachability_graph = bpmn_model.get_reachability_graph()
    # Assert general sizes
    assert len(reachability_graph.markings) == 7
    assert len(reachability_graph.edges) == 8
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 2
    assert len(reachability_graph.activity_to_edges["C"]) == 2
    assert len(reachability_graph.activity_to_edges["D"]) == 1
    assert len(reachability_graph.activity_to_edges["E"]) == 1
    assert len(reachability_graph.activity_to_edges["F"]) == 1
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"5", "6"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "9"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"5", "10"}))],
            reachability_graph.marking_to_key[tuple(sorted({"12"}))]) in edges


@pytest.mark.skip(reason="Skipping until fully refactoring this feature")
def test_reachability_graph_XOR_within_AND():
    bpmn_model = _bpmn_model_with_XOR_within_AND()
    reachability_graph = bpmn_model.get_reachability_graph()
    # Assert general sizes
    assert len(reachability_graph.markings) == 10
    assert len(reachability_graph.edges) == 26
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 4
    assert len(reachability_graph.activity_to_edges["C"]) == 4
    assert len(reachability_graph.activity_to_edges["D"]) == 4
    assert len(reachability_graph.activity_to_edges["E"]) == 4
    assert len(reachability_graph.activity_to_edges["F"]) == 4
    assert len(reachability_graph.activity_to_edges["G"]) == 4
    assert len(reachability_graph.activity_to_edges["H"]) == 1
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"1"}))],
            reachability_graph.marking_to_key[tuple(sorted({"5", "6", "7"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"5", "6", "7"}))],
            reachability_graph.marking_to_key[tuple(sorted({"32", "6", "7"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"5", "33", "7"}))],
            reachability_graph.marking_to_key[tuple(sorted({"32", "33", "7"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"5", "6", "34"}))],
            reachability_graph.marking_to_key[tuple(sorted({"32", "6", "34"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"5", "33", "34"}))],
            reachability_graph.marking_to_key[tuple(sorted({"36"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["F"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"11", "13", "15"}))],
            reachability_graph.marking_to_key[tuple(sorted({"11", "13", "34"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"12", "14", "15"}))],
            reachability_graph.marking_to_key[tuple(sorted({"12", "14", "34"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"32", "33", "15"}))],
            reachability_graph.marking_to_key[tuple(sorted({"36"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["H"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"36"}))],
            reachability_graph.marking_to_key[tuple(sorted({"38"}))]) in edges
