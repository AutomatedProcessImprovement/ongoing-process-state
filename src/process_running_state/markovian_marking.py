from typing import Set, List

from process_running_state.reachability_graph import ReachabilityGraph


class MarkovianMarking:
    TRACE_START = "DEFAULT_TRACE_START_LABEL"

    def __init__(self, graph: ReachabilityGraph, n_gram_size_limit: int = 5):
        self.graph = graph
        self.n_gram_size_limit = n_gram_size_limit
        self.markings = {}  # Dict with the N-Gram (tuple) as key and list with marking(s) as value

    def add_associations(self, n_gram: List[str], markings: Set[str]):
        n_gram_key = tuple(n_gram)
        if n_gram_key in self.markings:
            self.markings[n_gram_key] |= markings
        else:
            self.markings[n_gram_key] = markings

    def add_association(self, n_gram: List[str], marking: str):
        n_gram_key = tuple(n_gram)
        if n_gram_key in self.markings:
            self.markings[n_gram_key] |= {marking}
        else:
            self.markings[n_gram_key] = {marking}

    def get_marking_state(self, n_gram: List[str]) -> List[Set[str]]:
        """
        Retrieve, given an n-gram representing the last N activities executed in a trace, the list of markings (set of
        enabled flows) associated to that state.

        :param n_gram: list of activity labels representing the last N activities recorded in the trace.
        :return: a list with the marking(s) corresponding to the state of the process.
        """
        n_gram_key = tuple(n_gram)
        markings = {}
        # If present, retrieve marking IDs associated to this n-gram
        if n_gram_key in self.markings:
            markings = self.markings[n_gram_key]
        # Return set of markings
        return [self.graph.markings[marking] for marking in markings]

    def build(self):
        """
        Build the markovian marking mapping for the reachability graph in [self.graph] and with the n-limit stored in
        [self.n_gram_size_limit].
        """
        # Initialize stacks
        marking_stack = list(self.graph.markings)  # Stack of markings to explore (incoming edges)
        n_gram_stack = [[] for _ in marking_stack]  # n-gram (list of str) explored to reach each marking in the stack
        target_marking_stack = marking_stack.copy()  # List of marking that each n-gram points to
        # Continue with expansion while there are markings in the stack
        while len(marking_stack) > 0:
            # Initialize lists for next iteration
            next_marking_stack = []
            next_n_gram_stack = []
            next_target_marking_stack = []
            # Expand each of the markings in the stack backwards
            while len(marking_stack) > 0:
                # Retrieve marking to explore, n-gram that led (backwards) to it, and marking at the end of the n-gram
                marking_id = marking_stack.pop()
                previous_n_gram = n_gram_stack.pop()
                target_marking = target_marking_stack.pop()
                # If this marking is the initial marking, save corresponding association
                if marking_id == self.graph.initial_marking_id:
                    current_n_gram = [MarkovianMarking.TRACE_START] + previous_n_gram
                    self.add_association(current_n_gram, target_marking)
                # Grow n-gram with each incoming edge
                for edge_id in self.graph.incoming_edges[marking_id]:
                    # Add association
                    current_n_gram = [self.graph.edge_to_activity[edge_id]] + previous_n_gram
                    self.add_association(current_n_gram, target_marking)
                    # Save source marking for exploration if necessary
                    if len(current_n_gram) < self.n_gram_size_limit:
                        (source_marking_id, _) = self.graph.edges[edge_id]
                        next_marking_stack += [source_marking_id]
                        next_n_gram_stack += [current_n_gram]
                        next_target_marking_stack += [target_marking]
            # Update search stacks when necessary to keep expanding backwards
            while len(next_marking_stack) > 0:
                # Retrieve marking to explore, n-gram that led (backwards) to it, and marking at the end of the n-gram
                marking_id = next_marking_stack.pop()
                previous_n_gram = next_n_gram_stack.pop()
                target_marking = next_target_marking_stack.pop()
                # If the n-gram is not deterministic, add it to search further
                markings = self.get_marking_state(previous_n_gram)
                if len(markings) > 1:
                    marking_stack += [marking_id]
                    n_gram_stack += [previous_n_gram]
                    target_marking_stack += [target_marking]
