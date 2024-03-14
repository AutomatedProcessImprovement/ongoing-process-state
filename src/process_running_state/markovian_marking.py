from typing import Set, List

from process_running_state.reachability_graph import ReachabilityGraph


class MarkovianMarking:
    TRACE_START = "DEFAULT_TRACE_START_LABEL"

    def __int__(self, graph: ReachabilityGraph, n_gram_size_limit: int = 5):
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

    def build(self):
        # Go over the activity labels in the graph
        for activity_label in self.graph.activity_to_edges:
            # Save target markings
            target_markings = {target_id for (_, target_id) in self.graph.activity_to_edges[activity_label]}
            self.add_associations(activity_label, target_markings)
            # Continue exploring the N-gram backwards until deterministic (only one marking) or limit reached
            if len(target_markings) > 1 and self.n_gram_size_limit > 1:
                # Expand backwards search for each target marking
                for marking_id in target_markings:
                    # Get source markings of the edges [activity_label] having the current one as target
                    source_markings = {
                        source_id
                        for (source_id, target_id) in self.graph.activity_to_edges[activity_label]
                        if target_id == marking_id
                    }
                    # Continue exploration
                    self._explore_backwards(source_markings, marking_id, [activity_label])

    def _explore_backwards(self, source_markings: Set[str], target_marking: str, previous_n_gram: List[str]):
        # Check if initial marking is part of markings
        if self.graph.initial_marking in source_markings:
            current_n_gram = [MarkovianMarking.TRACE_START] + previous_n_gram
            self.add_association(current_n_gram, target_marking)
        # Collect incoming edges for each source marking
        incoming_edge_ids = {
            edge_id
            for edge_id in self.graph.markings[marking_id].incoming_edges
            for marking_id in source_markings
        }
        # Process the incoming edges grouping per activity label
        for activity_label in self.graph.activity_to_edges:
            # Get edges incoming to any marking in [source_markings] with label [activity_label]
            filtered_incoming_edge_ids = incoming_edge_ids & self.graph.activity_to_edges[activity_label]
            # If any arc incoming to a source marking with [activity_label] as label
            if len(filtered_incoming_edge_ids) > 0:
                # Save target marking for grown n-gram
                current_n_gram = [activity_label] + previous_n_gram
                self.add_association(current_n_gram, target_marking)
                # Continue exploring the N-gram backwards until deterministic (only one marking) or limit reached
                if len(target_markings) > 1 and len(current_n_gram) < self.n_gram_size_limit:
                    source_markings = {source_id for (source_id, target_id) in filtered_incoming_edge_ids}
                    self._explore_backwards(current_n_gram, source_markings)
