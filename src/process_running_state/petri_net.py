from process_running_state.reachability_graph import ReachabilityGraph


class SafePetriNet:
    def __init__(self):
        self.places = {}  # Maps place names to token presence (0 or 1)
        self.transitions = {}  # Maps transition names to (input_places, output_places)

    def add_place(self, place_name: str, token_present: bool = False):
        self.places[place_name] = 1 if token_present else 0

    def add_transition(self, transition_name: str, input_places: set, output_places: set):
        self.transitions[transition_name] = (input_places, output_places)

    def is_transition_enabled(self, transition_name: str):
        input_places, _ = self.transitions[transition_name]
        return all(self.places[place] == 1 for place in input_places)

    def fire_transition(self, transition_name: str) -> bool:
        is_enabled = self.is_transition_enabled(transition_name)
        if is_enabled:
            # Get input/output places
            input_places, output_places = self.transitions[transition_name]
            # Remove token from input places
            for place in input_places:
                self.places[place] = 0
            # Add token to output place
            for place in output_places:
                self.places[place] = 1
        return is_enabled

    def set_marking(self, marking: set):
        for place in self.places:
            self.places[place] = place in marking

    def get_marking(self) -> set:
        return {place for place in self.places if self.places[place]}

    def get_reachability_graph(self, initial_marking: set) -> ReachabilityGraph:
        graph = ReachabilityGraph()
        graph.add_marking(initial_marking)
        explored_markings = set()
        marking_stack = [initial_marking]

        while marking_stack:
            # Retrieve current marking
            current_marking = marking_stack.pop()
            marking_key = tuple(sorted(current_marking))
            # If it hasn't been explored
            if marking_key not in explored_markings:
                # Add it to explored
                explored_markings.add(marking_key)
                # Initiate Petri net state accordingly
                self.set_marking(current_marking)
                # Fire all enabled transitions and save new markings
                for transition in self.transitions:
                    if self.is_transition_enabled(transition):
                        # Fire transition
                        self.fire_transition(transition)
                        # Get new marking
                        new_marking = self.get_marking()
                        # Update reachability graph
                        graph.add_marking(new_marking)
                        graph.add_edge(transition, current_marking, new_marking)
                        # Save new marking if not explored
                        if new_marking not in explored_markings:
                            marking_stack.append(new_marking)
                        # Reset to original marking before exploring next transition
                        self.set_marking(current_marking)

        return graph
