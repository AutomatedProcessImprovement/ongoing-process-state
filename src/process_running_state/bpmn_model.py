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
        self.marking: Set[str] = set()

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
        if gateway_id not in self.id_to_node:
            node = Node(gateway_type, gateway_id, gateway_name)
            if node.is_gateway():
                self.nodes |= {node}
                self.id_to_node[gateway_id] = node

    def add_flow(self, flow_id: str, flow_name: str, source_id: str, target_id: str):
        if flow_id not in self.id_to_flow:
            flow = Flow(flow_id, flow_name, source_id, target_id)
            self.flows |= {flow}
            source = self.id_to_node[source_id]
            target = self.id_to_node[target_id]
            source.outgoing_flows |= {flow_id}
            target.incoming_flows |= {flow_id}

    def execute(self, node_id: str) -> List[Set[str]]:
        node = self.id_to_node[node_id]
        if node.is_task() or node.is_event() or node.type is BPMNNodeType.EXCLUSIVE_GATEWAY:
            # Task/Event/ExclusiveGateway: consume one incoming flow and enable one outgoing flow
            active_incoming_flows = node.incoming_flows & self.marking
            if len(active_incoming_flows) > 0:
                consumed_flow = active_incoming_flows.pop()
                new_marking = self.marking - {consumed_flow}
                return [new_marking | {outgoing_flow} for outgoing_flow in node.outgoing_flows]
        elif node.type is BPMNNodeType.PARALLEL_GATEWAY:
            # Parallel gateway: consume all incoming and enable all outgoing
            if node.incoming_flows.issubset(self.marking):
                new_marking = self.marking - node.incoming_flows | node.outgoing_flows
                return [new_marking]
        elif node.type is BPMNNodeType.INCLUSIVE_GATEWAY:
            # Inclusive gateway: consume all active incoming edges and enable all combinations of outgoing
            active_incoming_flows = node.incoming_flows & self.marking
            if len(active_incoming_flows) > 0:
                new_marking = self.marking - active_incoming_flows
                return [
                    new_marking | outgoing_flows
                    for outgoing_flows in _powerset(node.outgoing_flows)
                    if len(outgoing_flows) > 0
                ]
            pass
        else:
            # Unknown element
            return []

    def get_enabled_nodes(self) -> Set[Node]:
        return {
            node.id
            for node in self.nodes
            if node.incoming_flows.issubset(self.marking)
        }


def _powerset(iterable):
    # powerset({1,2,3}) --> {1} {2} {3} {1,2} {1,3} {2,3} {1,2,3}
    return [
        set(combination)
        for r in range(len(iterable) + 1)
        for combination in combinations(iterable, r)
        if len(combination) > 0
    ]
