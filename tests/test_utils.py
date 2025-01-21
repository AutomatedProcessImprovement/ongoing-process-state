from pathlib import Path

from ongoing_process_state.bpmn_model import BPMNNodeType
from ongoing_process_state.utils import read_bpmn_model, read_petri_net


def test_read_bpmn_model():
    bpmn_path = Path("./tests/assets/bpmn_model_test.bpmn")
    bpmn_model = read_bpmn_model(bpmn_path)
    # Assert number of elements
    assert len(bpmn_model.nodes) == 14
    assert len([node for node in bpmn_model.nodes if node.type == BPMNNodeType.TASK]) == 7
    assert len([node for node in bpmn_model.nodes if node.type == BPMNNodeType.START_EVENT]) == 1
    assert len([node for node in bpmn_model.nodes if node.type == BPMNNodeType.END_EVENT]) == 1
    assert len([node for node in bpmn_model.nodes if node.type == BPMNNodeType.INTERMEDIATE_EVENT]) == 1
    assert len([node for node in bpmn_model.nodes if node.type == BPMNNodeType.EXCLUSIVE_GATEWAY]) == 2
    assert len([node for node in bpmn_model.nodes if node.type == BPMNNodeType.PARALLEL_GATEWAY]) == 2
    assert len([node for node in bpmn_model.nodes if node.type == BPMNNodeType.INCLUSIVE_GATEWAY]) == 0
    assert len(bpmn_model.flows) == 15
    # Check specific node names
    assert bpmn_model.id_to_node["task-10"].name == "C"
    assert bpmn_model.id_to_node["task-21"].name == "E"
    assert bpmn_model.id_to_node["task-26"].name == "G"
    assert bpmn_model.id_to_node["event-0"].name == "Start"
    assert bpmn_model.id_to_node["event-19"].name == "Timer"
    assert bpmn_model.id_to_node["gateway-4"].name == "AND-split"
    assert bpmn_model.id_to_node["gateway-15"].name == "XOR-join"
    # Search for specific flows
    assert bpmn_model.id_to_flow["edge-3"].source == "task-2"
    assert bpmn_model.id_to_flow["edge-3"].target == "gateway-4"
    assert bpmn_model.id_to_flow["edge-6"].source == "gateway-4"
    assert bpmn_model.id_to_flow["edge-6"].target == "task-12"
    assert bpmn_model.id_to_flow["edge-8"].source == "gateway-7"
    assert bpmn_model.id_to_flow["edge-8"].target == "task-10"
    assert bpmn_model.id_to_flow["edge-14"].source == "task-11"
    assert bpmn_model.id_to_flow["edge-14"].target == "gateway-15"
    assert bpmn_model.id_to_flow["edge-18"].source == "gateway-15"
    assert bpmn_model.id_to_flow["edge-18"].target == "event-19"
    assert bpmn_model.id_to_flow["edge-22"].source == "task-21"
    assert bpmn_model.id_to_flow["edge-22"].target == "gateway-24"
    assert bpmn_model.id_to_flow["edge-27"].source == "task-26"
    assert bpmn_model.id_to_flow["edge-27"].target == "event-28"
    # Check replay to ensure structure
    marking = bpmn_model.get_initial_marking()
    assert marking == {"edge-1"}
    marking = bpmn_model.simulate_execution("task-2", marking)[0]
    assert marking == {"edge-3"}
    marking = bpmn_model.simulate_execution("gateway-4", marking)[0]
    assert marking == {"edge-5", "edge-6"}
    markings = bpmn_model.simulate_execution("gateway-7", marking)
    assert {"edge-6", "edge-8"} in markings
    marking = bpmn_model.simulate_execution("task-10", {"edge-6", "edge-8"})[0]
    marking = bpmn_model.simulate_execution("task-12", marking)[0]
    assert marking == {"edge-13", "edge-16"}
    marking = bpmn_model.simulate_execution("gateway-15", marking)[0]
    marking = bpmn_model.simulate_execution("task-17", marking)[0]
    marking = bpmn_model.simulate_execution("event-19", marking)[0]
    marking = bpmn_model.simulate_execution("task-21", marking)[0]
    assert marking == {"edge-22", "edge-23"}
    marking = bpmn_model.simulate_execution("gateway-24", marking)[0]
    marking = bpmn_model.simulate_execution("task-26", marking)[0]
    assert marking == {"edge-27"}


def test_read_petri_net():
    petri_net_path = Path("./tests/assets/petri_net_test.pnml")
    petri_net = read_petri_net(petri_net_path)
    # Assert number of elements
    assert len(petri_net.transitions) == 8
    assert petri_net.id_to_transition["silent-1"].is_invisible()
    assert len(petri_net.places) == 9
    # Check specific transition/place names
    assert petri_net.id_to_transition["task-10"].name == "C"
    assert petri_net.id_to_transition["task-21"].name == "E"
    assert petri_net.id_to_transition["task-26"].name == "G"
    assert petri_net.id_to_place["source"].name == "source"
    assert petri_net.id_to_place["sink"].name == "sink"
    assert petri_net.id_to_place["ent_gateway-15"].name == "ent_gateway-15"
    assert petri_net.id_to_place["ent_task-17"].name == "ent_task-17"
    # Search for specific edges
    # D
    assert petri_net.id_to_transition["task-11"].incoming == {"exi_gateway-7"}
    assert petri_net.id_to_transition["task-11"].outgoing == {"ent_gateway-15"}
    # G
    assert petri_net.id_to_transition["task-26"].incoming == {"edge-22", "edge-23"}
    assert petri_net.id_to_transition["task-26"].outgoing == {"sink"}
    # Place out of XOR split
    assert petri_net.id_to_place["ent_gateway-15"].incoming == {"task-10", "task-11"}
    assert petri_net.id_to_place["ent_gateway-15"].outgoing == {"task-21"}
    # Check replay to ensure structure
    marking = petri_net.initial_marking
    assert marking == {"source"}
    marking = petri_net.simulate_execution("task-2", marking)
    assert marking == {"exi_gateway-7", "ent_task-12"}
    marking = petri_net.simulate_execution("task-10", marking)
    marking = petri_net.simulate_execution("task-21", marking)
    assert marking == {"edge-22", "ent_task-12"}
    marking = petri_net.simulate_execution("task-12", marking)
    assert marking == {"edge-22", "ent_task-17"}
    marking = petri_net.advance_marking_until_decision_point(marking)
    assert marking == {"edge-22", "silent-1-out"}
    marking = petri_net.simulate_execution("task-17", marking)
    marking = petri_net.simulate_execution("task-26", marking)
    assert marking == {"sink"}
    assert petri_net.is_final_marking(marking)
