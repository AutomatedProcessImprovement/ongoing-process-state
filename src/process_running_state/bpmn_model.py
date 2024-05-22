from enum import Enum
from itertools import combinations
from typing import List, Set, Dict, Tuple, Optional

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
        self.id_to_flow: Dict[str, Flow] = dict()
        # Params for cached reachability graph search
        self._cached_search: bool = True
        self._advance_marking_cache = dict()

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
            self.id_to_flow[flow_id] = flow
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
        Compute the set of enabled nodes (excluding start/end events) given the current [marking]. A node (task,
        gateway, or event) is considered to be enabled when it can be fired.

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

    def get_enabled_tasks_events(self, marking: Set[str]) -> Set[str]:
        """
        Compute the set of enabled tasks or events (excluding start/end events) given the current [marking].

        :param marking: marking considered as reference to compute the enabled nodes.
        :return: a set with the IDs of the enabled tasks/events (no start or end events).
        """
        return {
            node.id
            for node in self.nodes
            if ((node.is_task() or node.is_event()) and
                (not node.is_start_event() and not node.is_end_event()) and
                len(node.incoming_flows & marking) > 0)
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

    def advance_full_marking(
            self,
            marking: Set[str],
            explored_markings: Optional[Set[Tuple[str]]] = None,
    ) -> List[Set[str]]:
        """
        Advance the current marking as much as possible without executing any task, i.e., execute gateways until there
        are none enabled. If there are multiple (parallel) branches, first advance in each of them individually, and
        only advance in more than one branch if needed to trigger an AND-join and advance further. For example, if the
        marking contains three enabled branches, but one of them cannot advance to close the AND-join, the result will
        be the markings after individually advancing each branch.

        :param marking: marking to consider as starting point to perform the advance operation.
        :param explored_markings: if recursive call, set of previously explored markings to avoid infinite loop.
        :return: list with the different markings result of such advancement.
        """
        # First advance all branches at the same time until tasks, events, or decision points (XOR-split/OR-split)
        advanced_marking = self.advance_marking_until_decision_point(marking)
        # Advance all branches together (getting all combinations of advancements)
        fully_advanced_markings = self._advance_marking(advanced_marking, explored_markings)
        # For each branch, try to rollback the advancements in other branches as much as possible
        if fully_advanced_markings == [advanced_marking] or len(advanced_marking) == 1:
            # If the marking did not advance, or there is only one branch, no need to try to rollback other branches
            final_markings = fully_advanced_markings
        else:
            final_markings = self._try_rollback(advanced_marking, fully_advanced_markings)
        # Keep only final markings that enabled new tasks/events, otherwise the advancement is useless
        filtered_final_markings = []
        enabled_in_marking = self.get_enabled_tasks_events(advanced_marking)
        for final_marking in final_markings:
            enabled_in_final_marking = self.get_enabled_tasks_events(final_marking)
            if enabled_in_marking != enabled_in_final_marking:
                filtered_final_markings += [final_marking]
        # Return final markings (if none of them enabled any new tasks/events return original marking)
        return filtered_final_markings if len(filtered_final_markings) > 0 else [advanced_marking]

    def _advance_marking(
            self,
            marking: Set[str],
            explored_markings: Optional[Set[Tuple[str]]] = None,
    ) -> List[Set[str]]:
        """
        Advance the current marking as much as possible without executing any task, i.e., execute gateways until there
        are none enabled.

        When traversing AND-split or OR-split gateways, the process has to start again (recursion) to consider the
        possibility of many branches with decision points (we do not want to traverse all of them creating all
        possible combinations, but branch by branch).

        :param marking: marking to consider as starting point to perform the advance operation.
        :param explored_markings: if recursive call, set of previously explored markings to avoid infinite loop.
        :return: list with the different markings result of such advancement.
        """
        # If result in cache, retrieve, otherwise compute
        marking_key = tuple(sorted(marking))
        if self._cached_search and marking_key in self._advance_marking_cache:
            final_markings = self._advance_marking_cache[marking_key]
        else:
            # Initialize breath-first search list
            current_markings = [marking]
            explored_markings = set() if explored_markings is None else explored_markings
            final_markings = []
            # Run propagation until no more gateways can be fired
            while current_markings:
                next_markings = []
                # For each marking
                for current_marking in current_markings:
                    # If it hasn't been explored
                    current_marking_key = tuple(sorted(current_marking))
                    if current_marking_key not in explored_markings:
                        # Add it to explored
                        explored_markings.add(current_marking_key)
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
                            gateway_id = enabled_gateways.pop()
                            gateway = self.id_to_node[gateway_id]
                            if (gateway.is_AND() or gateway.is_OR()) and gateway.is_split():
                                # AND-split/OR-split: traverse it
                                advanced_markings = self.simulate_execution(gateway_id, current_marking)
                                # For each advanced markings (after gateway split)
                                for advanced_marking in advanced_markings:
                                    final_markings += self.advance_full_marking(advanced_marking, explored_markings)
                            else:
                                # JOINs or XOR-split, execute and continue with advancement
                                next_markings += self.simulate_execution(gateway_id, current_marking)
                # Update new marking stack
                current_markings = next_markings
            # Save if using cache
            if self._cached_search:
                self._advance_marking_cache[marking_key] = final_markings
        # Return final set
        return final_markings

    def _try_rollback(self, marking: Set[str], advanced_markings: List[Set[str]]) -> List[Set[str]]:
        """
        For each of the advanced markings in [advanced_markings], leaving the advancement result of one of the original
        branches (from [marking]) untouched, rollback the independent advancements of other branches as much as
        possible.

        For example, imagine marking={1,2}, {1} advances to {3} and {4}, and {2} advances to {5} and {6}.
        Then, advanced_markings=[{3,5},{3,6},{4,5},{4,6}], and the objective is to rollback first the advancements of
        {1}, and then of {2}, so the result is [{1,5},{1,6},{3,2},{4,2}].

        For this, the method has to, for each branch, advance as much as possible in all combinations of the others,
        and rollback when one of the combinations (the one involving more branches) is part of the fully advanced
        marking. In this way we ensure that when many branches join (AND-join), they are advanced together.

        :param marking: marking considered as starting point.
        :param advanced_markings: list of markings result of advancing all branches in [marking] as much as possible.
        :return: list of rollbacked markings.
        """
        final_markings_keys = set()
        # Generate all possible branch combinations to explore individually
        branch_combinations = [
            combination
            for combination in _powerset(marking)
            if combination != marking
        ]
        # For each branch in the non-advanced marking
        for branch_flow_id in marking:
            # Get combinations that include own branch
            own_branch_combinations = [
                combination
                for combination in branch_combinations
                if branch_flow_id in combination
            ]
            own_branch_combinations.sort(key=len)  # Sort ascending to find the smaller one first
            # Get advanced markings where this branch advanced (if it didn't advance, no need to rollback the others)
            filtered_advanced_markings = [
                advanced_marking
                for advanced_marking in advanced_markings if
                branch_flow_id not in advanced_marking
            ]
            # From each advanced marking (where this branch also advanced)
            for advanced_marking in filtered_advanced_markings:
                # Identify the combination of branches needed for this branch to advance in this advanced marking
                advanced_combination = set(marking)  # If no other smaller combination found, all branches were needed
                found = False
                for own_branch_combination in own_branch_combinations:
                    if not found:
                        advanced_markings_with_own_branch = self._advance_marking(own_branch_combination)
                        for advanced_marking_with_own_branch in advanced_markings_with_own_branch:
                            if not found and advanced_marking_with_own_branch.issubset(advanced_marking):
                                # All these branches were needed to advance current one, save to not rollback them
                                found = True
                                advanced_combination = own_branch_combination
                # Try to rollback the advancements that were also reached when advancing the other branches
                other_branches = marking - advanced_combination
                rollbacked = False
                if len(other_branches) > 0:
                    advanced_markings_other_branches = self._advance_marking(other_branches)
                    for advanced_marking_other_branch in advanced_markings_other_branches:
                        if not rollbacked and advanced_marking_other_branch.issubset(advanced_marking):
                            # This advancement is independent of the current branch, rollback it
                            rollbacked = True
                            rollbacked_marking = advanced_marking - advanced_marking_other_branch | other_branches
                            final_markings_keys |= {tuple(sorted(rollbacked_marking))}
                else:
                    # If it was not rollbacked (i.e., all branches needed to advance until that point), keep it
                    final_markings_keys |= {tuple(sorted(advanced_marking))}
        # Return final markings
        return [set(final_marking) for final_marking in final_markings_keys]

    def get_reachability_graph(self, cached_search: bool = True) -> ReachabilityGraph:
        """
        Compute the reachability graph of this BPMN model. Each marking in the reachability graph contains the enabled
        flows of that state, and corresponds to a state of the process where the only enabled elements are tasks,
        events, and decision points (XOR-split/OR-split).

        :return: the reachability graph of this BPMN model.
        """
        self._cached_search = cached_search
        self._advance_marking_cache = dict()
        # Get initial BPMN marking and instantiate reachability graph
        initial_marking = self.get_initial_marking()
        initial_reference_marking = self.advance_marking_until_decision_point(initial_marking)
        graph = ReachabilityGraph()
        graph.add_marking(initial_reference_marking, is_initial=True)
        # Advance the initial marking (executing enabled gateways) and save them for exploration
        advanced_marking_stack = []
        reference_marking_stack = []
        for advanced_marking in self.advance_full_marking(initial_reference_marking):
            advanced_marking_stack += [advanced_marking]
            reference_marking_stack += [initial_reference_marking]
        # Start exploration, for each "reference" marking, simulate in its corresponding advanced markings
        explored_markings = set()
        explored_reference_markings = set()
        while len(advanced_marking_stack) > 0:
            # Retrieve current markings
            current_marking = advanced_marking_stack.pop()  # The marking to simulate over
            reference_marking = reference_marking_stack.pop()  # Corresponding marking to use in the reachability graph
            advanced_branches = current_marking - reference_marking
            original_branches = reference_marking - current_marking
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
                        if len(advanced_branches) > 0 and advanced_branches.issubset(new_reference_marking):
                            new_reference_marking = new_reference_marking - advanced_branches | original_branches
                        # Update reachability graph
                        graph.add_marking(new_reference_marking)  # Add reference marking to graph
                        graph.add_edge(enabled_node.name, reference_marking, new_reference_marking)
                        # If the new_reference_marking was already advanced, no need to repeat
                        new_reference_marking_key = tuple(sorted(new_reference_marking))
                        if new_reference_marking_key not in explored_reference_markings:
                            # Add it to explored
                            explored_reference_markings.add(new_reference_marking_key)
                            # Advance the marking as much as possible (executing any enabled gateway)
                            new_advanced_markings = self.advance_full_marking(new_reference_marking)
                            # For each new marking
                            for new_advanced_marking in new_advanced_markings:
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
