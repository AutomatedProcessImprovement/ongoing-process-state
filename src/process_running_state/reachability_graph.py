class ReachabilityGraph:
    def __init__(self):
        self.edges = {}  # Dict with edge ID as key, and tuple source-target marking IDs as value
        self.activity_to_edges = {}  # Dict with activity label as key, and list of edges as value
        self.edge_to_activity = {}  # Dict with edge ID as key, and activity label as value
        self.markings = {}  # Dict with ID as key, and set of place IDs (marking) as value
        self.marking_to_key = {}  # Dict with marking (sorted tuple) as key, and ID as value
        self.incoming_edges = {}  # Dict with marking ID as key, and set of incoming edges as value
        self.outgoing_edges = {}  # Dict with marking ID as key, and set of outgoing edges as value

    def add_marking(self, marking: set):
        marking_key = tuple(sorted(marking))
        if marking_key not in self.marking_to_key:
            marking_id = len(self.markings)
            self.markings[marking_id] = marking
            self.marking_to_key[marking_key] = marking_id

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
            self.incoming_edges[target_id] = self.incoming_edges.get(target_id, set()) | {edge_id}
            self.outgoing_edges[source_id] = self.outgoing_edges.get(source_id, set()) | {edge_id}
