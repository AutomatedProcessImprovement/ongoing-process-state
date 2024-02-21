from process_running_state.bpmn_model import BPMNModel, BPMNNodeType

if __name__ == '__main__':
    # Example usage
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

    bpmn_model.marking = {"1"}
    bpmn_model.marking = bpmn_model.execute("2")[0]
    bpmn_model.marking = bpmn_model.execute("4")[0]
    bpmn_model.marking = bpmn_model.execute("7")[0]
    bpmn_model.marking = bpmn_model.execute("8")[0]
    bpmn_model.marking = bpmn_model.execute("11")[0]
    (marking_one, marking_two) = bpmn_model.execute("13")
    bpmn_model.marking = marking_one
    bpmn_model.marking = bpmn_model.execute("16")[0]
    marking_one = bpmn_model.execute("20")[0]
    bpmn_model.marking = marking_two
    bpmn_model.marking = bpmn_model.execute("17")[0]
    marking_two = bpmn_model.execute("20")[0]
    assert marking_one == marking_two
    bpmn_model.marking = marking_one
    bpmn_model.marking = bpmn_model.execute("22")[0]
    assert bpmn_model.marking == {"23"}
    print()

