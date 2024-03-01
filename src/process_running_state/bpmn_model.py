from enum import Enum
from itertools import combinations
from typing import List, Set, Dict

from process_running_state.reachability_graph import ReachabilityGraph


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

    def is_start_event(self) -> bool:
        return self.type == BPMNNodeType.START_EVENT

    def is_intermediate_event(self) -> bool:
        return self.type == BPMNNodeType.INTERMEDIATE_EVENT

    def is_end_event(self) -> bool:
        return self.type == BPMNNodeType.END_EVENT

    def is_gateway(self) -> bool:
        return self.type in [
            BPMNNodeType.EXCLUSIVE_GATEWAY,
            BPMNNodeType.PARALLEL_GATEWAY,
            BPMNNodeType.INCLUSIVE_GATEWAY,
        ]

    def is_AND(self) -> bool:
        return self.type == BPMNNodeType.PARALLEL_GATEWAY

    def is_OR(self) -> bool:
        return self.type == BPMNNodeType.INCLUSIVE_GATEWAY

    def is_XOR(self) -> bool:
        return self.type == BPMNNodeType.EXCLUSIVE_GATEWAY


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

    def get_initial_marking(self) -> Set[str]:
        """
        Get initial marking, which corresponds to the execution of the start events of the process model.

        :return: marking (set of flows) corresponding to the initial marking of this BPMN model.
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
        elif node.is_XOR():
            # Exclusive gateway: consume active incoming flow and enable one of the outgoing flows
            active_incoming_flows = node.incoming_flows & marking
            if len(active_incoming_flows) > 1:
                print(f"Warning! ExclGateway '{node_id}' has more than one incoming flow enabled (consuming only one).")
            if len(active_incoming_flows) > 0:
                consumed_flow = active_incoming_flows.pop()
                new_marking = marking - {consumed_flow}
                return [new_marking | {outgoing_flow} for outgoing_flow in node.outgoing_flows]
        elif node.is_AND():
            # Parallel gateway: consume all incoming and enable all outgoing
            if node.incoming_flows.issubset(marking):
                new_marking = marking - node.incoming_flows | node.outgoing_flows
                return [new_marking]
        elif node.is_OR():
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
        """
        Compute the set of enabled nodes given the current [marking]. A node (task, gateway, or event) is considered
        to be enabled when it can be fired.
        Warning! the start and end events are filtered out from the result.

        :param marking: marking considered as reference to compute the enabled nodes.
        :return: a set with the IDs of the enabled nodes (no start or end events).
        """
        return {
            node.id
            for node in self.nodes
            if (not node.is_start_event() and not node.is_end_event()) and (
                    (node.is_AND() and node.incoming_flows.issubset(marking)) or
                    (not node.is_AND() and len(node.incoming_flows & marking) > 0)
            )
        }

    def advance_marking_until_decision_point(self, marking: Set[str]) -> Set[str]:
        """
        Advance the current marking (every branch in it) as much as possible without executing any task, event, or
        decision point, i.e., execute AND-split and all join gateways until there are none enabled.

        :param marking: marking to consider as starting point to perform the advance operation.
        :return: marking after (recursively) executing all non-decision-point gateways (AND-split, AND-join, XOR-join,
        OR-join).
        """
        advanced_marking = marking.copy()
        # Get enabled gateways (AND-split, AND-join, XOR-join, OR-join)
        enabled_gateways = [
            node_id
            for node_id in self.get_enabled_nodes(advanced_marking) if
            self.id_to_node[node_id].is_gateway() and
            (self.id_to_node[node_id].is_AND() or not self.id_to_node[node_id].is_split())
        ]
        # Run propagation until no more gateways (AND-split, AND-join, XOR-join, OR-join) can be fired
        while len(enabled_gateways) > 0:
            # Execute one of the enabled gateways and save result for next iteration
            [advanced_marking] = self.simulate_execution(enabled_gateways[0], advanced_marking)
            # Get enabled gateways (exclude XOR-splits & OR-splits)
            enabled_gateways = [
                node_id
                for node_id in self.get_enabled_nodes(advanced_marking) if
                self.id_to_node[node_id].is_gateway() and
                (self.id_to_node[node_id].is_AND() or not self.id_to_node[node_id].is_split())
            ]
        # Return final set
        return advanced_marking

    def advance_marking_per_parallel_branch(self, marking: Set[str]) -> List[Set[str]]:
        """
        Advance each active (parallel) branch on the current marking as much as possible without executing any task,
        i.e., execute gateways until there are none enabled. If there are multiple (parallel) branches, advance each of
        them individually, i.e., each returned marking would correspond to the advancement in one branch. After
        individually advancing each of them, advance the marking until reaching decision points, tasks, or events.

        :param marking: marking to consider as starting point to perform the advance operation.
        :return: list with the different markings result of such advancement.
        """
        # Initialize breath-first search list
        current_markings = [marking]
        explored_markings = set()
        final_markings = []
        # Run propagation until no more gateways can be fired
        while current_markings:
            next_markings = []
            # For each marking
            for current_marking in current_markings:
                # If it hasn't been explored
                marking_key = tuple(sorted(current_marking))
                if marking_key not in explored_markings:
                    # Add it to explored
                    explored_markings.add(marking_key)
                    # Get enabled gateways
                    enabled_gateways = [
                        node_id
                        for node_id in self.get_enabled_nodes(current_marking) if
                        self.id_to_node[node_id].is_gateway()
                    ]
                    # If no enabled gateways, save fully advanced marking
                    if len(enabled_gateways) == 0:
                        final_markings += [current_marking]
                    else:
                        # Otherwise, execute one of the enabled gateways and save result for next iteration
                        next_markings += self.simulate_execution(enabled_gateways[0], current_marking)
            # Update new marking stack
            current_markings = next_markings
        # Return final set
        return final_markings

    def get_reachability_graph(self) -> ReachabilityGraph:
        """
        Storing a marking in the reachability graph, but advancing it in local
        :return:
        """
        # Get initial BPMN marking and instantiate reachability graph
        initial_marking = self.get_initial_marking()
        graph = ReachabilityGraph()
        graph.add_marking(initial_marking)
        # Advance the initial marking (executing enabled gateways) and save them for exploration
        advanced_marking_stack = []
        reference_marking_stack = []
        for advanced_marking in self.advance_marking_per_parallel_branch(initial_marking):
            advanced_marking_stack += [advanced_marking]
            reference_marking_stack += [initial_marking]
        # Start exploration, for each "reference" marking, simulate in its corresponding advanced markings
        explored_markings = set()
        while len(advanced_marking_stack) > 0:
            # Retrieve current markings
            current_marking = advanced_marking_stack.pop()  # The marking to simulate over
            reference_marking = reference_marking_stack.pop()  # Corresponding marking to use in the reachability graph
            # If this marking hasn't been explored (reference marking + advanced marking)
            exploration_key = (tuple(sorted(reference_marking)), tuple(sorted(current_marking)))
            if exploration_key not in explored_markings:
                # Add it to explored
                explored_markings.add(exploration_key)
                # Fire all enabled activity/events and save new markings
                for enabled_node_id in self.get_enabled_nodes(current_marking):
                    enabled_node = self.id_to_node[enabled_node_id]
                    if enabled_node.is_task() or enabled_node.is_event():
                        # Fire task/event (always returns 1 marking)
                        [new_marking] = self.simulate_execution(enabled_node_id, current_marking)
                        # Advance the marking as much as possible without executing decision points (XOR-split/OR-split)
                        new_reference_marking = self.advance_marking_until_decision_point(new_marking)
                        # Advance the marking as much as possible (executing any enabled gateway)
                        new_advanced_markings = self.advance_marking_per_parallel_branch(new_reference_marking)
                        # For each new marking
                        for new_advanced_marking in new_advanced_markings:
                            # Update reachability graph
                            graph.add_marking(new_reference_marking)  # Add reference marking to graph
                            graph.add_edge(enabled_node.name, reference_marking, new_reference_marking)
                            # Save new marking
                            advanced_marking_stack += [new_advanced_marking]
                            reference_marking_stack += [new_reference_marking]
        # Return reachability graph
        return graph


def _powerset(iterable):
    # powerset({1,2,3}) --> {1} {2} {3} {1,2} {1,3} {2,3} {1,2,3}
    return [
        set(combination)
        for r in range(len(iterable) + 1)
        for combination in combinations(iterable, r)
        if len(combination) > 0
    ]
