from typing import List


class ReachabilityGraph:
    def __init__(self):
        self.edges = {}  # Dict with edge ID as key, and tuple source-target marking IDs as value
        self.activity_to_edges = {}  # Dict with activity label as key, and list of edge IDs as value
        self.edge_to_activity = {}  # Dict with edge ID as key, and activity label as value
        self.markings = {}  # Dict with ID as key, and set of place IDs (marking) as value
        self.marking_to_key = {}  # Dict with marking (sorted tuple) as key, and ID as value
        self.incoming_edges = {}  # Dict with marking ID as key, and set of incoming edge IDs as value
        self.outgoing_edges = {}  # Dict with marking ID as key, and set of outgoing edge IDs as value
        self.initial_marking_id = None  # ID of the initial marking

    def add_marking(self, marking: set, is_initial=False):
        marking_key = tuple(sorted(marking))
        if marking_key not in self.marking_to_key:
            marking_id = len(self.markings)
            self.markings[marking_id] = marking
            self.marking_to_key[marking_key] = marking_id
            self.incoming_edges[marking_id] = set()
            self.outgoing_edges[marking_id] = set()
            if is_initial:
                self.initial_marking_id = marking_id

    def add_edge(self, activity: str, source_marking: set, target_marking: set):
        # Get edge components
        edge_id = len(self.edges)
        source_id = self.marking_to_key[tuple(sorted(source_marking))]
        target_id = self.marking_to_key[tuple(sorted(target_marking))]
        # Check if edge already in the graph
        existent_edges = [
            self.edges[existent_edge_id]
            for existent_edge_id in self.activity_to_edges.get(activity, set())
        ]
        if (source_id, target_id) not in existent_edges:
            # Update graph elements
            self.edges[edge_id] = (source_id, target_id)
            self.activity_to_edges[activity] = self.activity_to_edges.get(activity, set()) | {edge_id}
            self.edge_to_activity[edge_id] = activity
            self.incoming_edges[target_id] |= {edge_id}
            self.outgoing_edges[source_id] |= {edge_id}

    def get_marking_from_activity_sequence(self, activity_sequence: List[str]):
        # Initiate search in the initial marking
        current_marking_id = self.initial_marking_id
        # Iterate over the activity sequence advancing in the reachability graph
        for activity in activity_sequence:
            # Retrieve edges leaving current marking with the activity as label
            potential_edges = [
                edge
                for edge in self.outgoing_edges[current_marking_id]
                if self.edge_to_activity[edge] == activity
            ]
            # Advance through this edge if no errors
            if len(potential_edges) == 0:
                # Error, the activity is not enabled in the current marking
                raise RuntimeError(f"Error, '{activity}' is not enabled from marking with ID '{current_marking_id}'")
            elif len(potential_edges) > 1:
                # Error, should not be more than one edge incoming from the same marking with same activity label
                raise RuntimeError(f"Error, multiple edges with same activity and source marking ({potential_edges})")
            else:
                # Correct, advance to target marking of edge
                edge = potential_edges[0]
                current_marking_id = self.edges[edge][1]
        # Return last reached marking
        return self.markings[current_marking_id]
