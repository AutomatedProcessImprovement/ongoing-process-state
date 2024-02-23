from enum import Enum
from itertools import combinations
from typing import List, Set, Dict


class BPMNNodeType(Enum):
    TASK = "TASK"
    START_EVENT = "START-EVENT"
    INTERMEDIATE_EVENT = "INTERMEDIATE-EVENT"
    END_EVENT = "END-EVENT"
    EXCLUSIVE_GATEWAY = "EXCLUSIVE-GATEWAY"
    INCLUSIVE_GATEWAY = "INCLUSIVE-GATEWAY"
    PARALLEL_GATEWAY = "PARALLEL-GATEWAY"
    UNDEFINED = "UNDEFINED"


class Node:
    def __init__(self, node_type: BPMNNodeType, node_id: str, node_name: str):
        self.id: str = node_id
        self.name: str = node_name
        self.type: BPMNNodeType = node_type
        self.incoming_flows: Set[str] = set()
        self.outgoing_flows: Set[str] = set()

    def is_split(self) -> bool:
        return len(self.outgoing_flows) > 1

    def is_join(self) -> bool:
        return len(self.incoming_flows) > 1

    def is_task(self) -> bool:
        return self.type == BPMNNodeType.TASK

    def is_start_event(self) -> bool:
        return self.type == BPMNNodeType.START_EVENT

    def is_end_event(self) -> bool:
        return self.type == BPMNNodeType.END_EVENT

    def is_event(self) -> bool:
        return self.type in [
            BPMNNodeType.START_EVENT,
            BPMNNodeType.INTERMEDIATE_EVENT,
            BPMNNodeType.END_EVENT,
        ]

    def is_gateway(self) -> bool:
        return self.type in [
            BPMNNodeType.EXCLUSIVE_GATEWAY,
            BPMNNodeType.PARALLEL_GATEWAY,
            BPMNNodeType.INCLUSIVE_GATEWAY,
        ]


class Flow:
    def __init__(self, flow_id: str, flow_name: str, source_id: str, target_id: str):
        self.id: str = flow_id
        self.name: str = flow_name
        self.source: str = source_id
        self.target: str = target_id


class BPMNModel:

    def __init__(self):
        self.nodes: Set[Node] = set()
        self.id_to_node: Dict[str, Node] = dict()
        self.flows: Set[Flow] = set()
        self.id_to_flow: Dict[str, Node] = dict()

    def add_task(self, task_id: str, task_name: str):
        if task_id not in self.id_to_node:
            node = Node(BPMNNodeType.TASK, task_id, task_name)
            self.nodes |= {node}
            self.id_to_node[task_id] = node

    def add_event(self, event_type: BPMNNodeType, event_id: str, event_name: str):
        if event_id not in self.id_to_node:
            node = Node(event_type, event_id, event_name)
            if node.is_event():
                self.nodes |= {node}
                self.id_to_node[event_id] = node

    def add_gateway(self, gateway_type: BPMNNodeType, gateway_id: str, gateway_name: str):
        if gateway_type is BPMNNodeType.INCLUSIVE_GATEWAY:
            raise AttributeError("Current implementation does not support Inclusive Gateways!")
        if gateway_id not in self.id_to_node:
            node = Node(gateway_type, gateway_id, gateway_name)
            if node.is_gateway():
                self.nodes |= {node}
                self.id_to_node[gateway_id] = node

    def add_flow(self, flow_id: str, flow_name: str, source_id: str, target_id: str):
        if flow_id not in self.id_to_flow:
            source = self.id_to_node[source_id]
            target = self.id_to_node[target_id]
            # Check correctness
            if (source.is_task() or source.is_event()) and len(source.outgoing_flows) > 0:
                raise RuntimeError(
                    f"Error when adding flow (id: {flow_id}). Tasks and events must have one single outgoing flow arc."
                )
            if target.is_start_event():
                raise RuntimeError(
                    f"Error when adding flow (id: {flow_id}). Start events cannot have incoming flow arcs."
                )
            if source.is_end_event():
                raise RuntimeError(
                    f"Error when adding flow (id: {flow_id}). End events cannot have outgoing flow arcs."
                )
            # Add flow to model
            flow = Flow(flow_id, flow_name, source_id, target_id)
            self.flows |= {flow}
            source.outgoing_flows |= {flow_id}
            target.incoming_flows |= {flow_id}

    def get_initial_marking(self):
        """
        Get initial marking, which corresponds to the execution of the start events of the process model.
        """
        initial_marking = set()
        start_nodes = [node for node in self.nodes if node.is_start_event()]
        for node in start_nodes:
            initial_marking |= node.outgoing_flows  # It always has only one outgoing flow (at most)
        return initial_marking

    def simulate_execution(self, node_id: str, marking: Set[str]) -> List[Set[str]]:
        """
        Simulate the execution of [node_id], if possible, given the current [marking], and return the possible markings
        result of such execution.

        :param node_id: Identifier of the node to execute.
        :param marking: Current marking to simulate the execution over it.
        :return: when it is possible to execute [node_id], list with the different markings result of such execution,
        otherwise, return empty list.
        """
        node = self.id_to_node[node_id]
        if node.is_task() or node.is_event():
            # Task/Event: consume active incoming flow and enable the outgoing flow
            active_incoming_flows = node.incoming_flows & marking
            if len(active_incoming_flows) > 1:
                print(f"Warning! Node '{node_id}' has more than one incoming flow enabled (consuming only one).")
            if len(active_incoming_flows) > 0:
                consumed_flow = active_incoming_flows.pop()
                new_marking = marking - {consumed_flow}
                return [new_marking | node.outgoing_flows]
        elif node.type is BPMNNodeType.EXCLUSIVE_GATEWAY:
            # Exclusive gateway: consume active incoming flow and enable one of the outgoing flows
            active_incoming_flows = node.incoming_flows & marking
            if len(active_incoming_flows) > 1:
                print(f"Warning! ExclGateway '{node_id}' has more than one incoming flow enabled (consuming only one).")
            if len(active_incoming_flows) > 0:
                consumed_flow = active_incoming_flows.pop()
                new_marking = marking - {consumed_flow}
                return [new_marking | {outgoing_flow} for outgoing_flow in node.outgoing_flows]
        elif node.type is BPMNNodeType.PARALLEL_GATEWAY:
            # Parallel gateway: consume all incoming and enable all outgoing
            if node.incoming_flows.issubset(marking):
                new_marking = marking - node.incoming_flows | node.outgoing_flows
                return [new_marking]
        elif node.type is BPMNNodeType.INCLUSIVE_GATEWAY:
            # Inclusive gateway: consume all active incoming edges and enable all combinations of outgoing
            active_incoming_flows = node.incoming_flows & marking
            if len(active_incoming_flows) > 0:
                new_marking = marking - active_incoming_flows
                return [
                    new_marking | outgoing_flows
                    for outgoing_flows in _powerset(node.outgoing_flows)
                    if len(outgoing_flows) > 0
                ]
        # Unknown element or unable to execute
        return []

    def get_enabled_nodes(self, marking: Set[str]) -> Set[str]:
        return {
            node.id
            for node in self.nodes
            if node.incoming_flows.issubset(marking) and not node.is_start_event() and not node.is_end_event()
        }


def _powerset(iterable):
    # powerset({1,2,3}) --> {1} {2} {3} {1,2} {1,3} {2,3} {1,2,3}
    return [
        set(combination)
        for r in range(len(iterable) + 1)
        for combination in combinations(iterable, r)
        if len(combination) > 0
    ]
