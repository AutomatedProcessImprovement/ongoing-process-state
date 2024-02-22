from process_running_state.bpmn_model import BPMNModel, BPMNNodeType


def _bpmn_model_with_and_and_xor() -> BPMNModel:
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


def test_create_bpmn_model():
    bpmn_model = _bpmn_model_with_and_and_xor()
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
    bpmn_model = _bpmn_model_with_and_and_xor()
    # Initialize marking
    bpmn_model.initialize_marking()
    assert bpmn_model.marking == {"1"}
    # Simulate execution
    bpmn_model.marking = bpmn_model.simulate_execution("2")[0]
    bpmn_model.marking = bpmn_model.simulate_execution("4")[0]
    assert bpmn_model.marking == {"5", "6"}
    assert bpmn_model.get_enabled_nodes() == {"7", "8"}
    bpmn_model.marking = bpmn_model.simulate_execution("7")[0]
    bpmn_model.marking = bpmn_model.simulate_execution("8")[0]
    bpmn_model.marking = bpmn_model.simulate_execution("11")[0]
    assert bpmn_model.marking == {"12"}
    assert bpmn_model.get_enabled_nodes() == {"13"}
    (marking_one, marking_two) = bpmn_model.simulate_execution("13")
    bpmn_model.marking = marking_one
    if "16" in bpmn_model.get_enabled_nodes():
        bpmn_model.marking = bpmn_model.simulate_execution("16")[0]
    else:
        bpmn_model.marking = bpmn_model.simulate_execution("17")[0]
    marking_one = bpmn_model.simulate_execution("20")[0]
    bpmn_model.marking = marking_two
    if "17" in bpmn_model.get_enabled_nodes():
        bpmn_model.marking = bpmn_model.simulate_execution("17")[0]
    else:
        bpmn_model.marking = bpmn_model.simulate_execution("16")[0]
    marking_two = bpmn_model.simulate_execution("20")[0]
    assert marking_one == {"21"}
    assert marking_one == marking_two
    bpmn_model.marking = marking_one
    assert bpmn_model.get_enabled_nodes() == {"22"}
    bpmn_model.marking = bpmn_model.simulate_execution("22")[0]
    assert bpmn_model.marking == {"23"}
    bpmn_model.marking = bpmn_model.simulate_execution("24")[0]
    assert len(bpmn_model.marking) == 0
