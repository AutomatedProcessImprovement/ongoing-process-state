import pytest

from test_petri_net_fixtures import _petri_net_with_AND_and_nested_XOR, _petri_net_with_loop_inside_AND, \
    _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND, \
    _petri_net_with_AND_and_nested_XOR_simple, _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND_simple, \
    _petri_net_with_three_loops_inside_AND_two_of_them_inside_sub_AND, \
    _petri_net_with_loop_inside_parallel_and_loop_all_back, _petri_net_with_infinite_loop, \
    _petri_net_with_infinite_loop_and_AND, _petri_net_with_optional_AND_with_skipping_and_loop_branches, \
    _petri_net_with_AND_and_XOR, _petri_net_with_XOR_within_AND


def test_create_petri_net():
    petri_net = _petri_net_with_AND_and_XOR()
    # Assert general characteristics
    assert len(petri_net.transitions) == 7
    assert len(petri_net.places) == 8
    assert sum([len(transition.incoming) for transition in petri_net.transitions]) == 8
    assert sum([len(transition.outgoing) for transition in petri_net.transitions]) == 8
    assert sum([len(place.incoming) for place in petri_net.places]) == 8
    assert sum([len(place.outgoing) for place in petri_net.places]) == 8
    # Assert some nodes have the expected incoming and outgoing arcs
    assert petri_net.id_to_transition["1"].incoming == {"0"}
    assert petri_net.id_to_transition["1"].outgoing == {"2", "3"}
    assert petri_net.id_to_transition["4"].incoming == {"2"}
    assert petri_net.id_to_transition["4"].outgoing == {"6"}
    assert petri_net.id_to_transition["10"].incoming == {"9"}
    assert petri_net.id_to_transition["10"].outgoing == {"12"}
    assert len(petri_net.id_to_place["0"].incoming) == 0
    assert petri_net.id_to_place["0"].outgoing == {"1"}
    assert petri_net.id_to_place["6"].incoming == {"4"}
    assert petri_net.id_to_place["6"].outgoing == {"8"}
    assert petri_net.id_to_place["12"].incoming == {"10", "11"}
    assert petri_net.id_to_place["12"].outgoing == {"13"}


def test_simulate_execution_and_enabled_nodes():
    petri_net = _petri_net_with_AND_and_XOR()
    # Initialize marking
    marking = petri_net.initial_marking
    assert marking == {"0"}
    # Simulate execution
    marking = petri_net.simulate_execution("1", marking)
    assert marking == {"2", "3"}
    assert petri_net.get_enabled_transitions(marking) == {"4", "5"}
    marking = petri_net.simulate_execution("4", marking)
    marking = petri_net.simulate_execution("5", marking)
    marking = petri_net.simulate_execution("8", marking)
    assert marking == {"9"}
    assert petri_net.get_enabled_transitions(marking) == {"10", "11"}
    assert petri_net.simulate_execution("10", marking) == {"12"}
    assert petri_net.simulate_execution("11", marking) == {"12"}
    marking = {"12"}
    assert petri_net.get_enabled_transitions(marking) == {"13"}
    marking = petri_net.simulate_execution("13", marking)
    assert marking == {"14"}
    assert petri_net.is_final_marking(marking)


def test_advance_marking_until_decision_point_XOR_within_AND_model():
    petri_net = _petri_net_with_XOR_within_AND()
    # Advance from state where only one task is enabled: no advance
    marking = petri_net.advance_marking_until_decision_point({"0"})
    assert marking == {"0"}
    # Advance from state where the AND-split is enabled: it should execute the AND-split
    marking = petri_net.advance_marking_until_decision_point({"2"})
    assert marking == {"4", "5", "6"}
    # Advance from state where only the XOR-join of 2 branches are enabled: it should advance until the AND-join
    marking = petri_net.advance_marking_until_decision_point({"25", "5", "30"})
    assert marking == {"37", "5", "39"}
    # Advance from state where the three XOR-join are enabled: it should execute the XOR-join and AND-join
    marking = petri_net.advance_marking_until_decision_point({"25", "38", "29"})
    assert marking == {"41"}


def test_advance_full_marking_XOR_within_AND_model():
    petri_net = _petri_net_with_XOR_within_AND()
    # Advance from state where only one task is enabled: no advance
    markings = petri_net.advance_full_marking({"0"})
    assert len(markings) == 1
    assert ("1", {"0"}) in markings
    # Advance from state where the AND-split is enabled: it should execute the AND-split and each following XOR-split
    markings = petri_net.advance_full_marking({"2"})
    assert len(markings) == 6
    assert ("19", {"13", "5", "6"}) in markings
    assert ("20", {"14", "5", "6"}) in markings
    assert ("21", {"4", "15", "6"}) in markings
    assert ("22", {"4", "16", "6"}) in markings
    assert ("23", {"4", "5", "17"}) in markings
    assert ("24", {"4", "5", "18"}) in markings
    # Advance from state where only the XOR-join of 2 branches are enabled: it should advance until the AND-join
    markings = petri_net.advance_full_marking({"25", "27", "18"})
    assert len(markings) == 1
    assert ("24", {"37", "38", "18"}) in markings
    # Advance from state where the three XOR-join are enabled: it should execute the XOR-join and AND-join
    markings = petri_net.advance_full_marking({"25", "38", "30"})
    assert len(markings) == 1
    assert ("42", {"41"}) in markings


def test_advance_marking_until_decision_point_nested_XOR_model():
    petri_net = _petri_net_with_AND_and_nested_XOR()
    # Advance from state where the AND-split is enabled: it should execute it enabling both branches
    marking = petri_net.advance_marking_until_decision_point({"2"})
    assert marking == {"4", "5"}
    # Advance from state where one of the upper XOR-join is enabled: it should execute the XOR-join (not the AND-join)
    marking = petri_net.advance_marking_until_decision_point({"18", "5"})
    assert marking == {"23", "5"}
    # Advance from state where one of the upper XOR-join is enabled and the lower AND branch: should fully advance
    marking = petri_net.advance_marking_until_decision_point({"17", "25"})
    assert marking == {"27"}


def test_advance_full_marking_nested_XOR_model():
    petri_net = _petri_net_with_AND_and_nested_XOR()
    # Advance from state where the AND-split is enabled: it should execute it enabling both branches
    markings = petri_net.advance_full_marking({"2"})
    assert len(markings) == 4
    assert ("10", {"8", "5"}) in markings
    assert ("15", {"13", "5"}) in markings
    assert ("16", {"14", "5"}) in markings
    assert ("24", {"4", "5"}) in markings
    # Advance from state where one of the upper XOR-join is enabled: it should execute the XOR-join (not the AND-join)
    markings = petri_net.advance_full_marking({"18", "5"})
    assert len(markings) == 1
    assert ("24", {"23", "5"}) in markings
    # Advance from state where one of the upper XOR-join is enabled and the lower AND branch: should fully advance
    markings = petri_net.advance_full_marking({"17", "25"})
    assert len(markings) == 1
    assert ("28", {"27"}) in markings


def test_advance_marking_until_decision_point_loop_model():
    petri_net = _petri_net_with_loop_inside_AND()
    # Advance from state where the AND-split is enabled: should execute it and advance through the XOR-join branch
    marking = petri_net.advance_marking_until_decision_point({"2"})
    assert marking == {"4", "5"}
    # Advance from state where the loop XOR is enabled, it should stay in the XOR-split
    marking = petri_net.advance_marking_until_decision_point({"8", "5"})
    assert marking == {"8", "5"}
    # Advance from state where the loop XOR is enabled, it should stay in the XOR-split
    marking = petri_net.advance_marking_until_decision_point({"8", "9"})
    assert marking == {"8", "9"}


def test_advance_full_marking_loop_model():
    petri_net = _petri_net_with_loop_inside_AND()
    # Advance from state where the AND-split is enabled: should execute it and advance through the XOR-join branch
    markings = petri_net.advance_full_marking({"2"})
    assert len(markings) == 2
    assert ("6", {"4", "5"}) in markings
    assert ("7", {"4", "5"}) in markings
    # Advance from state where the loop XOR is enabled, it should generate both states going back (loop) and forward
    markings = petri_net.advance_full_marking({"8", "5"})
    assert len(markings) == 2
    assert ("6", {"4", "5"}) in markings
    assert ("7", {"8", "5"}) in markings
    # Advance from state where the loop XOR is enabled, it should generate both states going back (loop) and forward
    markings = petri_net.advance_full_marking({"8", "9"})
    assert len(markings) == 2
    assert ("6", {"4", "9"}) in markings
    assert ("13", {"12"}) in markings
    # Advance from state where only one task is enabled: no advance
    markings = petri_net.advance_full_marking({"12"})
    assert len(markings) == 1
    assert ("13", {"12"}) in markings


def test_advance_marking_until_decision_point_double_loop_model():
    petri_net = _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND()
    # Advance from state where the AND-split is enabled: should execute it and advance through the XOR-join branch
    marking = petri_net.advance_marking_until_decision_point({"2"})
    assert marking == {"4", "5"}
    # Advance from state where the loop XORs are enabled, it should stay in the XOR-splits
    marking = petri_net.advance_marking_until_decision_point({"8", "9"})
    assert marking == {"8", "9"}
    # Advance from state where the AND-split is enabled, it should traverse it
    marking = petri_net.advance_marking_until_decision_point({"13"})
    assert marking == {"15", "16"}
    # Advance from state where the two last XOR-join are enabled, it should traverse them and the following AND-join
    marking = petri_net.advance_marking_until_decision_point({"29", "32"})
    assert marking == {"40"}


def test_advance_full_marking_double_loop_model():
    petri_net = _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND()
    # Advance from state where the AND-split is enabled: should execute it and advance through the XOR-join branch
    markings = petri_net.advance_full_marking({"2"})
    assert len(markings) == 2
    assert ("6", {"4", "5"}) in markings
    assert ("7", {"4", "5"}) in markings
    # Advance from state where both loop XOR are enabled, it should:
    # - Traverse one of them going back individually (the other does not advance)
    # - Traverse the other going back individually (the first one does not advance)
    # - Traverse them together advancing and traversing the following AND-split, generating:
    #   - First branch of the AND-split advances (two combinations) while the other one holds
    #   - The other branch advances (two combinations) while the first one holds
    markings = petri_net.advance_full_marking({"8", "9"})
    assert len(markings) == 6
    assert ("6", {"4", "9"}) in markings
    assert ("7", {"8", "5"}) in markings
    assert ("25", {"21", "16"}) in markings
    assert ("26", {"22", "16"}) in markings
    assert ("27", {"23", "15"}) in markings
    assert ("28", {"24", "15"}) in markings


def test_advance_marking_until_decision_point_triple_loop_model():
    petri_net = _petri_net_with_three_loops_inside_AND_two_of_them_inside_sub_AND()
    # Advance from initial marking: should traverse the AND-split and one XOR-join
    marking = petri_net.advance_marking_until_decision_point({"0"})
    assert marking == {"2", "18"}
    # Advance from state where second AND-split is enabled and lower branch is before loop: should traverse all
    marking = petri_net.advance_marking_until_decision_point({"4", "18"})
    assert marking == {"6", "7", "18"}
    # Advance from state where the three XOR-split are enabled, no advancement
    marking = petri_net.advance_marking_until_decision_point({"10", "11", "18"})
    assert marking == {"10", "11", "18"}


def test_advance_full_marking_triple_loop_model():
    petri_net = _petri_net_with_three_loops_inside_AND_two_of_them_inside_sub_AND()
    # Advance from initial marking: should traverse the AND-split and one XOR-join
    markings = petri_net.advance_full_marking({"0"})
    assert len(markings) == 2
    assert ("3", {"2", "18"}) in markings
    assert ("19", {"2", "18"}) in markings
    # Advance from state where second AND-split is enabled and lower branch is before loop: should traverse all
    markings = petri_net.advance_full_marking({"4", "18"})
    assert len(markings) == 3
    assert ("8", {"6", "7", "18"}) in markings
    assert ("9", {"6", "7", "18"}) in markings
    assert ("19", {"6", "7", "18"}) in markings
    # Advance from state where the three loop XOR-split are enabled, it should:
    # - Traverse one of them going back individually (the other two do not advance)
    # - Traverse the second one going back individually (the other two do not advance)
    # - Traverse the third one going back individually (the other two do not advance)
    # - Traverse the two that end in the same AND-join together, and the AND-join too (the other branch holds)
    markings = petri_net.advance_full_marking({"10", "11", "20"})
    assert len(markings) == 4
    assert ("8", {"6", "11", "20"}) in markings
    assert ("9", {"10", "7", "20"}) in markings
    assert ("16", {"15", "20"}) in markings
    assert ("19", {"10", "11", "18"}) in markings


def test_compute_reachable_markings_AND_and_XOR():
    # Compute reachable markings
    petri_net = _petri_net_with_AND_and_XOR()
    reachable_markings = petri_net.compute_reachable_markings()
    # Assert number of markings
    assert len(reachable_markings) == 8
    # Assert specific markings
    assert tuple(sorted({"0"})) in reachable_markings
    assert tuple(sorted({"2", "3"})) in reachable_markings
    assert tuple(sorted({"2", "7"})) in reachable_markings
    assert tuple(sorted({"3", "6"})) in reachable_markings
    assert tuple(sorted({"6", "7"})) in reachable_markings
    assert tuple(sorted({"9"})) in reachable_markings
    assert tuple(sorted({"12"})) in reachable_markings
    assert tuple(sorted({"14"})) in reachable_markings


def test_compute_reachable_markings_XOR_within_AND():
    # Compute reachable markings
    petri_net = _petri_net_with_XOR_within_AND()
    reachable_markings = petri_net.compute_reachable_markings()
    # Assert number of markings
    assert len(reachable_markings) == 1 + 1 + (6 * 6 * 6) + 1 + 1
    # Assert specific markings
    assert tuple(sorted({"0"})) in reachable_markings
    assert tuple(sorted({"4", "5", "6"})) in reachable_markings
    assert tuple(sorted({"4", "15", "17"})) in reachable_markings
    assert tuple(sorted({"26", "15", "29"})) in reachable_markings
    assert tuple(sorted({"26", "28", "30"})) in reachable_markings
    assert tuple(sorted({"4", "38", "30"})) in reachable_markings
    assert tuple(sorted({"14", "28", "18"})) in reachable_markings
    assert tuple(sorted({"14", "38", "30"})) in reachable_markings
    assert tuple(sorted({"13", "15", "29"})) in reachable_markings
    assert tuple(sorted({"13", "28", "17"})) in reachable_markings
    assert tuple(sorted({"37", "38", "6"})) in reachable_markings
    assert tuple(sorted({"37", "15", "17"})) in reachable_markings
    assert tuple(sorted({"37", "38", "39"})) in reachable_markings
    assert tuple(sorted({"41"})) in reachable_markings


def test_compute_reachable_markings_AND_and_nested_XOR():
    # Compute reachable markings
    petri_net = _petri_net_with_AND_and_nested_XOR()
    reachable_markings = petri_net.compute_reachable_markings()
    # Assert number of markings
    assert len(reachable_markings) == 1 + 1 + (2 * 9) + 1 + 1
    # Assert specific markings
    assert tuple(sorted({"0"})) in reachable_markings
    assert tuple(sorted({"4", "5"})) in reachable_markings
    assert tuple(sorted({"4", "25"})) in reachable_markings
    assert tuple(sorted({"17", "5"})) in reachable_markings
    assert tuple(sorted({"17", "25"})) in reachable_markings
    assert tuple(sorted({"9", "5"})) in reachable_markings
    assert tuple(sorted({"9", "25"})) in reachable_markings
    assert tuple(sorted({"13", "5"})) in reachable_markings
    assert tuple(sorted({"13", "25"})) in reachable_markings
    assert tuple(sorted({"19", "5"})) in reachable_markings
    assert tuple(sorted({"19", "25"})) in reachable_markings
    assert tuple(sorted({"23", "5"})) in reachable_markings
    assert tuple(sorted({"23", "25"})) in reachable_markings
    assert tuple(sorted({"29"})) in reachable_markings


def test_compute_reachable_markings_loop_inside_AND():
    # Compute reachable markings
    petri_net = _petri_net_with_loop_inside_AND()
    reachable_markings = petri_net.compute_reachable_markings()
    # Assert number of markings
    assert len(reachable_markings) == 8
    # Assert specific markings
    assert tuple(sorted({"0"})) in reachable_markings
    assert tuple(sorted({"2"})) in reachable_markings
    assert tuple(sorted({"4", "5"})) in reachable_markings
    assert tuple(sorted({"4", "9"})) in reachable_markings
    assert tuple(sorted({"8", "5"})) in reachable_markings
    assert tuple(sorted({"8", "9"})) in reachable_markings
    assert tuple(sorted({"12"})) in reachable_markings
    assert tuple(sorted({"14"})) in reachable_markings


def test_compute_reachable_markings_two_loops_inside_AND_followed_by_XOR_within_AND():
    # Compute reachable markings
    petri_net = _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND()
    reachable_markings = petri_net.compute_reachable_markings()
    # Assert number of markings
    assert len(reachable_markings) == 1 + 1 + (2 * 2) + 1 + (6 * 6) + 1 + 1
    # Assert specific markings
    assert tuple(sorted({"0"})) in reachable_markings
    assert tuple(sorted({"4", "5"})) in reachable_markings
    assert tuple(sorted({"4", "9"})) in reachable_markings
    assert tuple(sorted({"8", "5"})) in reachable_markings
    assert tuple(sorted({"8", "9"})) in reachable_markings
    assert tuple(sorted({"13"})) in reachable_markings
    assert tuple(sorted({"15", "16"})) in reachable_markings
    assert tuple(sorted({"15", "23"})) in reachable_markings
    assert tuple(sorted({"15", "32"})) in reachable_markings
    assert tuple(sorted({"21", "16"})) in reachable_markings
    assert tuple(sorted({"21", "24"})) in reachable_markings
    assert tuple(sorted({"21", "31"})) in reachable_markings
    assert tuple(sorted({"21", "38"})) in reachable_markings
    assert tuple(sorted({"29", "23"})) in reachable_markings
    assert tuple(sorted({"29", "32"})) in reachable_markings
    assert tuple(sorted({"30", "16"})) in reachable_markings
    assert tuple(sorted({"30", "38"})) in reachable_markings
    assert tuple(sorted({"37", "24"})) in reachable_markings
    assert tuple(sorted({"37", "31"})) in reachable_markings
    assert tuple(sorted({"37", "38"})) in reachable_markings
    assert tuple(sorted({"42"})) in reachable_markings


def test_compute_reachable_markings_three_loops_inside_AND_two_of_them_inside_sub_AND():
    # Compute reachable markings
    petri_net = _petri_net_with_three_loops_inside_AND_two_of_them_inside_sub_AND()
    reachable_markings = petri_net.compute_reachable_markings()
    # Assert number of markings
    assert len(reachable_markings) == 1 + (2 * 8) + 1 + 1
    # Assert specific markings
    assert tuple(sorted({"0"})) in reachable_markings
    assert tuple(sorted({"2", "18"})) in reachable_markings
    assert tuple(sorted({"2", "20"})) in reachable_markings
    assert tuple(sorted({"4", "18"})) in reachable_markings
    assert tuple(sorted({"6", "7", "18"})) in reachable_markings
    assert tuple(sorted({"6", "11", "20"})) in reachable_markings
    assert tuple(sorted({"10", "7", "20"})) in reachable_markings
    assert tuple(sorted({"10", "11", "18"})) in reachable_markings
    assert tuple(sorted({"15", "20"})) in reachable_markings
    assert tuple(sorted({"17", "18"})) in reachable_markings
    assert tuple(sorted({"25"})) in reachable_markings


def test_compute_reachable_markings_loop_inside_parallel_and_loop_all_back():
    # Compute reachable markings
    petri_net = _petri_net_with_loop_inside_parallel_and_loop_all_back()
    reachable_markings = petri_net.compute_reachable_markings()
    # Assert number of markings
    assert len(reachable_markings) == 8
    # Assert specific markings
    assert tuple(sorted({"0"})) in reachable_markings
    assert tuple(sorted({"2"})) in reachable_markings
    assert tuple(sorted({"4", "8"})) in reachable_markings
    assert tuple(sorted({"4", "10"})) in reachable_markings
    assert tuple(sorted({"6", "8"})) in reachable_markings
    assert tuple(sorted({"6", "10"})) in reachable_markings
    assert tuple(sorted({"12"})) in reachable_markings
    assert tuple(sorted({"15"})) in reachable_markings


def test_compute_reachable_markings_infinite_loop():
    # Compute reachable markings
    petri_net = _petri_net_with_infinite_loop()
    reachable_markings = petri_net.compute_reachable_markings()
    # Assert number of markings
    assert len(reachable_markings) == 8
    # Assert specific markings
    assert tuple(sorted({"0"})) in reachable_markings
    assert tuple(sorted({"2"})) in reachable_markings
    assert tuple(sorted({"4"})) in reachable_markings
    assert tuple(sorted({"6"})) in reachable_markings
    assert tuple(sorted({"9"})) in reachable_markings
    assert tuple(sorted({"11"})) in reachable_markings
    assert tuple(sorted({"14"})) in reachable_markings
    assert tuple(sorted({"16"})) in reachable_markings


def test_compute_reachable_markings_infinite_loop_and_AND():
    # Compute reachable markings
    petri_net = _petri_net_with_infinite_loop_and_AND()
    reachable_markings = petri_net.compute_reachable_markings()
    # Assert number of markings
    assert len(reachable_markings) == 1 + 1 + 1 + (3 * 3) + 1 + 1 + 1 + 1
    # Assert specific markings
    assert tuple(sorted({"0"})) in reachable_markings
    assert tuple(sorted({"2"})) in reachable_markings
    assert tuple(sorted({"6", "12"})) in reachable_markings
    assert tuple(sorted({"6", "14"})) in reachable_markings
    assert tuple(sorted({"6", "17"})) in reachable_markings
    assert tuple(sorted({"8", "12"})) in reachable_markings
    assert tuple(sorted({"8", "14"})) in reachable_markings
    assert tuple(sorted({"8", "17"})) in reachable_markings
    assert tuple(sorted({"11", "12"})) in reachable_markings
    assert tuple(sorted({"11", "14"})) in reachable_markings
    assert tuple(sorted({"11", "17"})) in reachable_markings
    assert tuple(sorted({"22"})) in reachable_markings
    assert tuple(sorted({"27"})) in reachable_markings


def test_compute_reachable_markings_optional_AND_with_skipping_and_loop_branches():
    # Compute reachable markings
    petri_net = _petri_net_with_optional_AND_with_skipping_and_loop_branches()
    reachable_markings = petri_net.compute_reachable_markings()
    # Assert number of markings
    assert len(reachable_markings) == 1 + 1 + (3 * 2) + 1 + 1
    # Assert specific markings
    assert tuple(sorted({"0"})) in reachable_markings
    assert tuple(sorted({"2"})) in reachable_markings
    assert tuple(sorted({"4", "5"})) in reachable_markings
    assert tuple(sorted({"4", "9"})) in reachable_markings
    assert tuple(sorted({"8", "5"})) in reachable_markings
    assert tuple(sorted({"8", "9"})) in reachable_markings
    assert tuple(sorted({"12", "5"})) in reachable_markings
    assert tuple(sorted({"12", "9"})) in reachable_markings
    assert tuple(sorted({"18"})) in reachable_markings


def test_reachability_graph_AND_and_XOR():
    petri_net = _petri_net_with_AND_and_XOR()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
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
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"0"}))],
            reachability_graph.marking_to_key[tuple(sorted({"2", "3"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "3"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "3"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"2", "7"}))],
            reachability_graph.marking_to_key[tuple(sorted({"9"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["D"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"12"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["F"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"12"}))],
            reachability_graph.marking_to_key[tuple(sorted({"14"}))]) in edges


def test_reachability_graph_XOR_within_AND():
    petri_net = _petri_net_with_XOR_within_AND()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
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
    assert (reachability_graph.marking_to_key[tuple(sorted({"0"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "5", "6"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "5", "6"}))],
            reachability_graph.marking_to_key[tuple(sorted({"37", "5", "6"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "38", "6"}))],
            reachability_graph.marking_to_key[tuple(sorted({"37", "38", "6"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "5", "39"}))],
            reachability_graph.marking_to_key[tuple(sorted({"37", "5", "39"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "38", "39"}))],
            reachability_graph.marking_to_key[tuple(sorted({"41"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["F"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "5", "6"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "5", "39"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "38", "6"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "38", "39"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"37", "5", "6"}))],
            reachability_graph.marking_to_key[tuple(sorted({"37", "5", "39"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"37", "38", "6"}))],
            reachability_graph.marking_to_key[tuple(sorted({"41"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["H"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"41"}))],
            reachability_graph.marking_to_key[tuple(sorted({"43"}))]) in edges


def test_reachability_graph_AND_nested_XOR():
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
    petri_net.repair_mixed_decision_points()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    # Assert general sizes
    assert len(reachability_graph.markings) == 6
    assert len(reachability_graph.edges) == 10
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 5
    assert len(reachability_graph.activity_to_edges["C"]) == 3
    assert len(reachability_graph.activity_to_edges["D"]) == 1
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
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 2
    assert len(reachability_graph.activity_to_edges["C"]) == 2
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
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 5
    assert len(reachability_graph.activity_to_edges["C"]) == 5
    assert len(reachability_graph.activity_to_edges["D"]) == 4
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


def test_reachability_graph_optional_AND_with_skipping_and_loop_branches():
    petri_net = _petri_net_with_optional_AND_with_skipping_and_loop_branches()
    reachability_graph = petri_net.get_reachability_graph(cached_search=False)
    # Assert general sizes
    assert len(reachability_graph.markings) == 6
    assert len(reachability_graph.edges) == 10
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 2
    assert len(reachability_graph.activity_to_edges["C"]) == 4
    assert len(reachability_graph.activity_to_edges["D"]) == 3
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["A"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"0"}))],
            reachability_graph.marking_to_key[tuple(sorted({"2"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["C"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"2"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "9"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"4", "9"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"12", "5"}))],
            reachability_graph.marking_to_key[tuple(sorted({"12", "9"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"12", "9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"12", "9"}))]) in edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["D"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"2"}))],
            reachability_graph.marking_to_key[tuple(sorted({"18"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"4", "9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"18"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"12", "9"}))],
            reachability_graph.marking_to_key[tuple(sorted({"18"}))]) in edges


def test_reachability_graphs_with_cache():
    petri_net = _petri_net_with_AND_and_XOR()
    reachability_graph_no_cache = petri_net.get_reachability_graph(cached_search=False)
    reachability_graph_cache = petri_net.get_reachability_graph(cached_search=True)
    assert reachability_graph_cache == reachability_graph_no_cache

    petri_net = _petri_net_with_XOR_within_AND()
    reachability_graph_no_cache = petri_net.get_reachability_graph(cached_search=False)
    reachability_graph_cache = petri_net.get_reachability_graph(cached_search=True)
    assert reachability_graph_cache == reachability_graph_no_cache

    petri_net = _petri_net_with_AND_and_nested_XOR()
    reachability_graph_no_cache = petri_net.get_reachability_graph(cached_search=False)
    reachability_graph_cache = petri_net.get_reachability_graph(cached_search=True)
    assert reachability_graph_cache == reachability_graph_no_cache

    petri_net = _petri_net_with_loop_inside_AND()
    reachability_graph_no_cache = petri_net.get_reachability_graph(cached_search=False)
    reachability_graph_cache = petri_net.get_reachability_graph(cached_search=True)
    assert reachability_graph_cache == reachability_graph_no_cache

    petri_net = _petri_net_with_two_loops_inside_AND_followed_by_XOR_within_AND()
    reachability_graph_no_cache = petri_net.get_reachability_graph(cached_search=False)
    reachability_graph_cache = petri_net.get_reachability_graph(cached_search=True)
    assert reachability_graph_cache == reachability_graph_no_cache

    petri_net = _petri_net_with_three_loops_inside_AND_two_of_them_inside_sub_AND()
    reachability_graph_no_cache = petri_net.get_reachability_graph(cached_search=False)
    reachability_graph_cache = petri_net.get_reachability_graph(cached_search=True)
    assert reachability_graph_cache == reachability_graph_no_cache

    petri_net = _petri_net_with_loop_inside_parallel_and_loop_all_back()
    petri_net.repair_mixed_decision_points()
    reachability_graph_no_cache = petri_net.get_reachability_graph(cached_search=False)
    reachability_graph_cache = petri_net.get_reachability_graph(cached_search=True)
    assert reachability_graph_cache == reachability_graph_no_cache

    petri_net = _petri_net_with_infinite_loop()
    reachability_graph_no_cache = petri_net.get_reachability_graph(cached_search=False)
    reachability_graph_cache = petri_net.get_reachability_graph(cached_search=True)
    assert reachability_graph_cache == reachability_graph_no_cache
