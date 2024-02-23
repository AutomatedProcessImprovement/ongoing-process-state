from process_running_state.bpmn_model import BPMNModel, BPMNNodeType


def _bpmn_model_with_AND_and_XOR() -> BPMNModel:
    bpmn_model = BPMNModel()
    bpmn_model.add_event(BPMNNodeType.START_EVENT, "0", "Start")
    bpmn_model.add_event(BPMNNodeType.END_EVENT, "24", "End")
    bpmn_model.add_task("2", "A")
    bpmn_model.add_task("7", "B")
    bpmn_model.add_task("8", "C")
    bpmn_model.add_task("16", "D")
    bpmn_model.add_task("17", "E")
    bpmn_model.add_task("22", "F")
    bpmn_model.add_gateway(BPMNNodeType.PARALLEL_GATEWAY, "4", "AND-split")
    bpmn_model.add_gateway(BPMNNodeType.PARALLEL_GATEWAY, "11", "AND-join")
    bpmn_model.add_gateway(BPMNNodeType.EXCLUSIVE_GATEWAY, "13", "XOR-split")
    bpmn_model.add_gateway(BPMNNodeType.EXCLUSIVE_GATEWAY, "20", "XOR-join")
    bpmn_model.add_flow("1", "flow", "0", "2")
    bpmn_model.add_flow("3", "flow", "2", "4")
    bpmn_model.add_flow("5", "flow", "4", "7")
    bpmn_model.add_flow("6", "flow", "4", "8")
    bpmn_model.add_flow("9", "flow", "7", "11")
    bpmn_model.add_flow("10", "flow", "8", "11")
    bpmn_model.add_flow("12", "flow", "11", "13")
    bpmn_model.add_flow("14", "flow", "13", "16")
    bpmn_model.add_flow("15", "flow", "13", "17")
    bpmn_model.add_flow("18", "flow", "16", "20")
    bpmn_model.add_flow("19", "flow", "17", "20")
    bpmn_model.add_flow("21", "flow", "20", "22")
    bpmn_model.add_flow("23", "flow", "22", "24")
    return bpmn_model


def _bpmn_model_with_XOR_within_AND() -> BPMNModel:
    bpmn_model = BPMNModel()
    bpmn_model.add_event(BPMNNodeType.START_EVENT, "0", "Start")
    bpmn_model.add_event(BPMNNodeType.END_EVENT, "39", "End")
    bpmn_model.add_task("2", "A")
    bpmn_model.add_task("17", "B")
    bpmn_model.add_task("18", "C")
    bpmn_model.add_task("19", "D")
    bpmn_model.add_task("20", "E")
    bpmn_model.add_task("21", "F")
    bpmn_model.add_task("22", "G")
    bpmn_model.add_task("37", "H")
    bpmn_model.add_gateway(BPMNNodeType.PARALLEL_GATEWAY, "4", "AND-split")
    bpmn_model.add_gateway(BPMNNodeType.PARALLEL_GATEWAY, "35", "AND-join")
    bpmn_model.add_gateway(BPMNNodeType.EXCLUSIVE_GATEWAY, "8", "XOR-split-1")
    bpmn_model.add_gateway(BPMNNodeType.EXCLUSIVE_GATEWAY, "9", "XOR-split-2")
    bpmn_model.add_gateway(BPMNNodeType.EXCLUSIVE_GATEWAY, "10", "XOR-split-3")
    bpmn_model.add_gateway(BPMNNodeType.EXCLUSIVE_GATEWAY, "29", "XOR-join-1")
    bpmn_model.add_gateway(BPMNNodeType.EXCLUSIVE_GATEWAY, "30", "XOR-join-2")
    bpmn_model.add_gateway(BPMNNodeType.EXCLUSIVE_GATEWAY, "31", "XOR-join-3")
    bpmn_model.add_flow("1", "flow", "0", "2")
    bpmn_model.add_flow("3", "flow", "2", "4")
    bpmn_model.add_flow("5", "flow", "4", "8")
    bpmn_model.add_flow("6", "flow", "4", "9")
    bpmn_model.add_flow("7", "flow", "4", "10")
    bpmn_model.add_flow("11", "flow", "8", "17")
    bpmn_model.add_flow("12", "flow", "8", "18")
    bpmn_model.add_flow("13", "flow", "9", "19")
    bpmn_model.add_flow("14", "flow", "9", "20")
    bpmn_model.add_flow("15", "flow", "10", "21")
    bpmn_model.add_flow("16", "flow", "10", "22")
    bpmn_model.add_flow("23", "flow", "17", "29")
    bpmn_model.add_flow("24", "flow", "18", "29")
    bpmn_model.add_flow("25", "flow", "19", "30")
    bpmn_model.add_flow("26", "flow", "20", "30")
    bpmn_model.add_flow("27", "flow", "21", "31")
    bpmn_model.add_flow("28", "flow", "22", "31")
    bpmn_model.add_flow("32", "flow", "29", "35")
    bpmn_model.add_flow("33", "flow", "30", "35")
    bpmn_model.add_flow("34", "flow", "31", "35")
    bpmn_model.add_flow("36", "flow", "35", "37")
    bpmn_model.add_flow("38", "flow", "37", "39")
    return bpmn_model


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


def test_advance_marking_simple_model():
    bpmn_model = _bpmn_model_with_AND_and_XOR()
    # Advance from state where the AND-split is enabled: it should execute it enabling both branches
    marking = bpmn_model.advance_marking({"3"})
    assert marking == [{"5", "6"}]
    # Advance from state where the AND-join is enabled: it should execute both the AND-join and following XOR-split
    markings = bpmn_model.advance_marking({"9", "10"})
    assert len(markings) == 2
    assert {"14"} in markings
    assert {"15"} in markings
    # Advance from state where only one task is enabled: no advance
    marking = bpmn_model.advance_marking({"21"})
    assert marking == [{"21"}]


def test_advance_marking_complex_model():
    bpmn_model = _bpmn_model_with_XOR_within_AND()
    # Advance from state where only one task is enabled: no advance
    marking = bpmn_model.advance_marking({"1"})
    assert marking == [{"1"}]
    # Advance from state where the AND-split is enabled: it should execute the AND-split and each following XOR-split
    markings = bpmn_model.advance_marking({"3"})
    assert len(markings) == 8
    assert {"11", "13", "15"} in markings
    assert {"11", "13", "16"} in markings
    assert {"11", "14", "15"} in markings
    assert {"11", "14", "16"} in markings
    assert {"12", "13", "15"} in markings
    assert {"12", "13", "16"} in markings
    assert {"12", "14", "15"} in markings
    assert {"12", "14", "16"} in markings
    # Advance from state where only the XOR-join of 2 branches are enabled: it should advance until the AND-join
    markings = bpmn_model.advance_marking({"23", "26", "16"})
    assert markings == [{"32", "33", "16"}]
    # Advance from state where the three XOR-join are enabled: it should execute the XOR-join and AND-join
    markings = bpmn_model.advance_marking({"23", "26", "28"})
    assert markings == [{"36"}]


def test_reachability_graph():
    bpmn_model = _bpmn_model_with_AND_and_XOR()
    reachability_graph = bpmn_model.get_reachability_graph()
    # Assert general sizes
    assert len(reachability_graph.markings) == 8
    assert len(reachability_graph.edges) == 10
    # Assert size of edges per activity
    assert len(reachability_graph.activity_to_edges["A"]) == 1
    assert len(reachability_graph.activity_to_edges["B"]) == 3
    assert len(reachability_graph.activity_to_edges["C"]) == 3
    assert len(reachability_graph.activity_to_edges["D"]) == 1
    assert len(reachability_graph.activity_to_edges["E"]) == 1
    assert len(reachability_graph.activity_to_edges["F"]) == 1
    # Assert specific edges
    edges = {reachability_graph.edges[edge_id] for edge_id in reachability_graph.activity_to_edges["B"]}
    assert (reachability_graph.marking_to_key[tuple(sorted({"5", "6"}))],
            reachability_graph.marking_to_key[tuple(sorted({"6", "9"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"5", "10"}))],
            reachability_graph.marking_to_key[tuple(sorted({"14"}))]) in edges
    assert (reachability_graph.marking_to_key[tuple(sorted({"5", "10"}))],
            reachability_graph.marking_to_key[tuple(sorted({"15"}))]) in edges
