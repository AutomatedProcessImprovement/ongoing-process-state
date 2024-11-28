from itertools import combinations
from typing import List, Set, Dict, Tuple, Optional

from process_running_state.reachability_graph import ReachabilityGraph


class Transition:
    def __init__(self, transition_id: str, transition_name: str, invisible=False):
        self.id: str = transition_id
        self.name: str = transition_name
        self.invisible: bool = invisible
        self.incoming: Set[str] = set()  # Set of IDs of incoming places
        self.outgoing: Set[str] = set()  # Set of IDs of outgoing places

    def is_task(self) -> bool:
        return not self.invisible

    def is_invisible(self) -> bool:
        return self.invisible

    def is_split(self) -> bool:
        return len(self.outgoing) > 1

    def is_join(self) -> bool:
        return len(self.incoming) > 1

    def is_enabled(self, marking: Set[str]) -> bool:
        return self.incoming <= marking


class Place:
    def __init__(self, place_id: str, place_name: str):
        self.id: str = place_id
        self.name: str = place_name
        self.incoming: Set[str] = set()
        self.outgoing: Set[str] = set()

    def is_split(self) -> bool:
        return len(self.outgoing) > 1

    def is_join(self) -> bool:
        return len(self.incoming) > 1


class PetriNet:

    def __init__(self):
        self.initial_marking = set()
        self.final_marking = set()
        self.transitions: Set[Transition] = set()
        self.id_to_transition: Dict[str, Transition] = dict()
        self.places: Set[Place] = set()
        self.id_to_place: Dict[str, Place] = dict()
        # Params for cached reachability graph search
        self._cached_search: bool = True
        self._advance_marking_cache = dict()
        self._advance_combination_cache = dict()

    def add_transition(self, transition_id: str, transition_name: str, invisible: bool = False):
        if transition_id not in self.id_to_transition and transition_id not in self.id_to_place:
            transition = Transition(transition_id, transition_name, invisible)
            self.transitions |= {transition}
            self.id_to_transition[transition_id] = transition

    def add_place(self, place_id: str, place_name: str):
        if place_id not in self.id_to_place and place_id not in self.id_to_transition:
            place = Place(place_id, place_name)
            self.places |= {place}
            self.id_to_place[place_id] = place

    def add_edge(self, source_id: str, target_id: str):
        # Check correctness
        if source_id in self.id_to_transition and target_id in self.id_to_transition:
            raise RuntimeError(f"Error when adding edge '{source_id} to {target_id}' (transition to transition).")
        elif source_id in self.id_to_place and target_id in self.id_to_place:
            raise RuntimeError(f"Error when adding edge '{source_id} to {target_id}' (place to place).")
        elif source_id not in self.id_to_transition and source_id not in self.id_to_place:
            raise RuntimeError(f"Error when adding edge '{source_id} to {target_id}' (unknown source).")
        elif target_id not in self.id_to_transition and target_id not in self.id_to_place:
            raise RuntimeError(f"Error when adding edge '{source_id} to {target_id}' (unknown target).")
        # Retrieve nodes
        source = self.id_to_place[source_id] if source_id in self.id_to_place else self.id_to_transition[source_id]
        target = self.id_to_place[target_id] if target_id in self.id_to_place else self.id_to_transition[target_id]
        # Add edge to petri net
        source.outgoing |= {target_id}
        target.incoming |= {source_id}

    def fulfills_preconditions(self) -> bool:
        """
        Checks correctness of Petri net according to the restrictions needed to compute the reachability graph. This
        implies that all the outgoing transitions of a place must be either invisible transitions or tasks, not mixed.

        :return: boolean whether the Petri net is correct for reachability graph analysis or not.
        """
        fulfills = True
        # Check that all places are connected either to all invisible or all tasks
        for place in self.places:
            if fulfills:
                # Update flag variable for this place
                all_invisible = all([self.id_to_transition[outgoing_id].is_invisible()
                                     for outgoing_id in place.outgoing
                                     ])
                all_task = all([self.id_to_transition[outgoing_id].is_task()
                                for outgoing_id in place.outgoing
                                ])
                if not all_invisible and not all_task:
                    print(f"Error! Place '{place.id}' is connected to both invisible transitions and tasks.")
                    fulfills = False
        # Return result
        return fulfills

    def simulate_execution(self, transition_id: str, marking: Set[str]) -> Set[str]:
        """
        Simulate the execution of [node_id], if possible, given the current [marking], and return the possible markings
        result of such execution.

        :param transition_id: Identifier of the transition to execute.
        :param marking: Current marking to simulate the execution over it.
        :return: when it is possible to execute [transition_id], marking result of such execution, otherwise, return
        empty set.
        """
        transition = self.id_to_transition[transition_id]
        if transition.is_enabled(marking):
            # All incoming places have a token, simulate
            return marking - transition.incoming | transition.outgoing
        else:
            # Transition is not enabled
            return set()

    def get_enabled_transitions(self, marking: Set[str]) -> Set[str]:
        """
        Compute the set of enabled transitions given the current [marking]. A transition is considered to be enabled
        when all its incoming places have a token, i.e., it can be fired.

        :param marking: marking considered as reference to compute the enabled transitions.
        :return: a set with the IDs of the enabled transitions.
        """
        return {
            transition.id
            for transition in self.transitions
            if transition.is_enabled(marking)
        }

    def get_enabled_tasks(self, marking: Set[str]) -> Set[str]:
        """
        Compute the set of enabled tasks (i.e., visible transitions) given the current [marking].

        :param marking: marking considered as reference to compute the enabled tasks.
        :return: a set with the IDs of the enabled tasks.
        """
        return {
            transition.id
            for transition in self.transitions
            if transition.is_enabled(marking) and transition.is_task()
        }

    def get_enabled_invisible_transitions(self, marking: Set[str]) -> Set[str]:
        """
        Compute the set of enabled invisible transitions given the current [marking].

        :param marking: marking considered as reference to compute the enabled transitions.
        :return: a set with the IDs of the enabled invisible transitions.
        """
        return {
            transition.id
            for transition in self.transitions
            if transition.is_enabled(marking) and transition.is_invisible()
        }

    def get_enabled_invisible_non_decision_point_transitions(self, marking: Set[str]) -> Set[str]:
        """
        Compute the set of enabled invisible transitions that are not part of a decision point, given the current
        [marking]. An invisible transition is considered to be part of a decision point when one of its incoming
        places have more than one outgoing arc (i.e., XOR-split).

        :param marking: marking considered as reference to compute the enabled transitions.
        :return: a set with the IDs of the enabled invisible transitions that are not part of a decision point.
        """
        return {
            transition_id
            for transition_id in self.get_enabled_invisible_transitions(marking)
            if all(  # All its incoming places have one single outgoing transition (not decision point).
                [
                    not self.id_to_place[place_id].is_split()
                    for place_id in self.id_to_transition[transition_id].incoming
                ]
            )
        }

    def advance_full_marking(
            self,
            marking: Set[str],
            explored_markings: Optional[Set[Tuple[str]]] = None,
    ) -> List[Tuple[str, Set[str]]]:
        """
        Advance the current marking as much as possible without executing any task, i.e., execute gateways until there
        are none enabled. If there are multiple (parallel) branches, first advance in each of them individually, and
        only advance in more than one branch if needed to trigger an AND-join and advance further. For example, if the
        marking contains three enabled branches, but one of them cannot advance to close the AND-join, the result will
        be the markings after individually advancing each branch.

        :param marking: marking to consider as starting point to perform the advance operation.
        :param explored_markings: if recursive call, set of previously explored markings to avoid infinite loop.
        :return: list of tuples with the ID of an enabled task as first element and the advanced marking that
        enabled it as second element.
        """
        # Instantiate list for advanced markings
        tuples_final_markings = set()
        # First advance all branches at the same time until tasks, events, or decision points (XOR-split/OR-split)
        advanced_marking = self.advance_marking_until_decision_point(marking)
        # Advance all branches together (getting all combinations of advancements)
        tuples_fully_advanced_markings = self._advance_marking(advanced_marking, explored_markings)
        # Save only advanced marking that enabled new tasks/events
        for enabled_task_id, fully_advanced_marking in tuples_fully_advanced_markings:
            # Try to rollback the advancements in other branches as much as possible
            rollbacked_marking = self._try_rollback(fully_advanced_marking, advanced_marking, enabled_task_id)
            # Save rollbacked marking
            tuples_final_markings |= {(enabled_task_id, tuple(sorted(rollbacked_marking)))}
        # Return final markings (if none of them enabled any new tasks/events return original marking)
        return [(enabled_task_id, set(final_marking)) for enabled_task_id, final_marking in tuples_final_markings]

    def advance_marking_until_decision_point(self, marking: Set[str]) -> Set[str]:
        """
        Advance the current marking (every branch in it) as much as possible by executing invisible transitions except
        in decision points (i.e., places with more than one outgoing edge).

        :param marking: marking to consider as starting point to perform the advance operation.
        :return: marking after (recursively) executing all non-decision-point invisible transitions (i.e., invisible
        transitions which incoming places only have one outgoing edge).
        """
        advanced_marking = marking.copy()
        # Get enabled invisible transitions discarding those part of decision points
        enabled_transitions = self.get_enabled_invisible_non_decision_point_transitions(advanced_marking)
        # Run propagation until no more invisible transitions (not in decision points) can be fired
        while len(enabled_transitions) > 0:
            # Execute one of the enabled gateways and save result for next iteration
            advanced_marking = self.simulate_execution(enabled_transitions.pop(), advanced_marking)
            # Get enabled gateways (exclude XOR-splits & OR-splits)
            enabled_transitions = self.get_enabled_invisible_non_decision_point_transitions(advanced_marking)
        # Return final set
        return advanced_marking

    def _advance_marking(
            self,
            marking: Set[str],
            explored_markings: Optional[Set[Tuple[str]]] = None,
    ) -> List[Tuple[str, Set[str]]]:
        """
        Advance the current marking as much as possible without executing any task, i.e., execute invisible transitions
        until there are none enabled.

        When traversing split transitions (i.e., AND-splits), the process has to start again (recursion) to consider the
        chance of many branches with decision points (we do not want to traverse all of them creating all
        possible combinations, but branch by branch).

        :param marking: marking to consider as starting point to perform the advance operation.
        :param explored_markings: if recursive call, set of previously explored markings to avoid infinite loop.
        :return: list of tuples with the ID of the enabled tasks as first element, and the advanced marking that
        enabled it as second element.
        """
        # If result in cache, retrieve, otherwise compute
        marking_key = tuple(sorted(marking))
        if self._cached_search and marking_key in self._advance_marking_cache:
            tuples_final_markings = self._advance_marking_cache[marking_key]
        else:
            # Initialize breath-first search list
            current_marking_stack = [marking]
            explored_markings = set() if explored_markings is None else explored_markings
            set_tuples_final_markings = set()
            # Run propagation until no more gateways can be fired
            while current_marking_stack:
                next_marking_stack = []
                # For each marking
                for current_marking in current_marking_stack:
                    # If it hasn't been explored
                    current_marking_key = tuple(sorted(current_marking))
                    if current_marking_key not in explored_markings:
                        # Add it to explored
                        explored_markings.add(current_marking_key)
                        # Get enabled invisible transitions
                        enabled_invisible_transition_ids = self.get_enabled_invisible_transitions(current_marking)
                        # If there are no enabled invisible transitions
                        if len(enabled_invisible_transition_ids) == 0:
                            # Save fully advanced marking
                            set_tuples_final_markings |= {
                                (enabled_task_id, current_marking_key)
                                for enabled_task_id in self.get_enabled_tasks(current_marking)
                            }
                        else:
                            # Get one invisible transition and its incoming place(s)
                            selected_transition_id = enabled_invisible_transition_ids.pop()
                            selected_transition = self.id_to_transition[selected_transition_id]
                            to_be_consumed_place_ids = selected_transition.incoming
                            # Create set with this invisible transition + all others sharing any of its incoming places
                            invisible_transitions_to_fire = {
                                transition_id
                                for transition_id in enabled_invisible_transition_ids
                                if len(
                                    self.id_to_transition[transition_id].incoming & to_be_consumed_place_ids) > 0
                            } | {selected_transition_id}
                            # Fire invisible transitions sharing incoming place(s) (i.e., XOR-split)
                            for invisible_transition_id in invisible_transitions_to_fire:
                                invisible_transition = self.id_to_transition[invisible_transition_id]
                                # If it is a parallel split
                                if invisible_transition.is_split():
                                    # Fire it
                                    advanced_marking = self.simulate_execution(invisible_transition_id, current_marking)
                                    # Save advancements that were needed to enable new activities (recursive)
                                    set_tuples_final_markings |= {
                                        (enabled_task_id, tuple(sorted(fully_advanced_marking)))
                                        for enabled_task_id, fully_advanced_marking
                                        in self.advance_full_marking(advanced_marking, explored_markings)
                                    }
                                else:
                                    # One outgoing edge transition, execute and continue with advancement
                                    next_marking_stack += [
                                        self.simulate_execution(invisible_transition_id, current_marking)
                                    ]
                # Update new marking stack
                current_marking_stack = next_marking_stack
            # Transform to tuples with sets (str, Set[str])
            tuples_final_markings = [
                (task_id, set(final_marking))
                for task_id, final_marking in set_tuples_final_markings
            ]
            # Save if using cache
            if self._cached_search:
                self._advance_marking_cache[marking_key] = tuples_final_markings
        # Return final set
        return tuples_final_markings

    def _try_rollback(self, advanced_marking: Set[str], marking: Set[str], enabled_task_id: str) -> Set[str]:
        """
        Given an advanced marking and the task for which it advanced, try to rollback the advancement of as much
        branches as possible while keeping the task enabled. In this way, the marking still enables the desired node,
        and all the other branches remain as if they did not advance, only the required ones to enabled the desired
        task remain advanced.

        For example, imagine marking={p1,p2}, {p1} advances to {p3} and {p4}, and {p2} advances to {p5} and {p6}.
        Then, advanced_markings=[{p3,p5},{p3,p6},{p4,p5},{p4,p6}], and the objective is to rollback first the
        advancements of {p1}, and then of {p2}, so the result is [{p1,p5},{p1,p6},{p3,p2},{p4,p2}].

        For this, the method has to find the smaller combination of branches that, when advanced isolated, enable the
        desired task. Then, identify the remaining branches, advance them individually, and rollback such advancement.
        In this way, we ensure that when many parallel branches need to join (in an AND-join), they are advanced
        together.

        :param advanced_marking: advanced marking result of advancing the branches in [marking] as much as possible.
        :param marking: marking considered as starting point.
        :param enabled_task_id: identifier of the task that is enabled and must remain enabled.
        :return: rollbacked marking.
        """
        rollbacked_marking = set()
        # Retrieve place enabling current task
        enabling_places = self.id_to_transition[enabled_task_id].incoming & advanced_marking
        # Generate all possible branch combinations to explore individually
        branch_combinations = [
            combination
            for combination in _powerset(marking)
            if combination != marking
        ]
        branch_combinations.sort(key=len)  # Sort ascending to find the smaller one first
        # Identify the combination of branches needed for the enabling branch to advance
        advanced_combination = set(marking)  # If no other smaller combination found, all branches were needed
        found = False
        for branch_combination in branch_combinations:
            if not found:
                # Advance with this branch combination
                for _, advanced_marking_with_branch_combination in self._advance_marking(branch_combination):
                    # If the advancement reached the enabling place(s)
                    reached_enabling_place = enabling_places <= advanced_marking_with_branch_combination
                    # and the advanced marking with these branch combination is all in the advanced marking
                    advanced_is_subset = advanced_marking_with_branch_combination <= advanced_marking
                    if not found and reached_enabling_place and advanced_is_subset:
                        # All these branches were needed to advance current one, save to not rollback them
                        found = True
                        advanced_combination = branch_combination
        # Rollback the advancements that were also reached when advancing the other branches
        other_branches = marking - advanced_combination
        rollbacked = False
        if len(other_branches) > 0:
            for _, advanced_marking_other_branches in self._advance_marking(other_branches):
                if not rollbacked and advanced_marking_other_branches <= advanced_marking:
                    # This advancement is independent of the current branch, rollback it
                    rollbacked = True
                    rollbacked_marking = advanced_marking - advanced_marking_other_branches | other_branches
            if not rollbacked:
                rollbacked_marking = advanced_marking
        else:
            # If it was not rollbacked (i.e., all branches needed to advance until that point), keep it
            rollbacked_marking = advanced_marking
        # Return final markings
        return rollbacked_marking

    def get_reachability_graph(self, cached_search: bool = True) -> ReachabilityGraph:
        """
        Compute the reachability graph of this Petri net. Each marking in the reachability graph contains the enabled
        places of that state, and corresponds to a state of the process where the only enabled elements are tasks and
        decision points (invisible transitions).

        :return: the reachability graph of this BPMN model.
        """
        # Check correctness of Petri net
        if not self.fulfills_preconditions():
            raise RuntimeError("Incorrect model structure! Check logged info.")
        # Initialize caches
        self._cached_search = cached_search
        self._advance_marking_cache = dict()
        self._advance_combination_cache = dict()
        # Assert initial marking and instantiate reachability graph
        assert len(self.initial_marking) > 0, "Error! No initial marking defined."
        initial_advanced_marking = self.advance_marking_until_decision_point(self.initial_marking)
        graph = ReachabilityGraph()
        graph.add_marking(initial_advanced_marking, is_initial=True)
        # Start exploration, for each "reference" marking, simulate in its corresponding advanced markings
        marking_stack = [initial_advanced_marking]
        explored_markings = set()
        while len(marking_stack) > 0:
            # Retrieve current markings
            current_marking = marking_stack.pop()  # This marking is already advanced to decision points
            # If this marking hasn't been explored (reference marking + advanced marking)
            exploration_key = tuple(sorted(current_marking))
            if exploration_key not in explored_markings:
                # Add it to explored
                explored_markings.add(exploration_key)
                # Advance the current marking, executing enabled gateways, obtaining:
                #   An activity enabled by the advancement
                #   The advanced marking needed to execute the activity
                tuples_advanced_markings = self.advance_full_marking(current_marking)
                # For each pair of enabled activity and advanced marking that enables it
                for enabled_node_id, advanced_marking in tuples_advanced_markings:
                    enabled_node = self.id_to_transition[enabled_node_id]
                    # Fire task/event (always returns 1 marking)
                    new_marking = self.simulate_execution(enabled_node_id, advanced_marking)
                    # Advance the marking as much as possible without executing decision points (XOR-split/OR-split)
                    new_advanced_marking = self.advance_marking_until_decision_point(new_marking)
                    # Update reachability graph
                    graph.add_marking(new_advanced_marking)  # Add reference marking to graph
                    graph.add_edge(enabled_node.name, current_marking, new_advanced_marking)
                    # Save to continue exploring it
                    marking_stack += [new_advanced_marking]
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
