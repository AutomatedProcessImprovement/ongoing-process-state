from process_running_state.petri_net import SafePetriNet

if __name__ == '__main__':
    # Example usage
    petri_net = SafePetriNet()
    petri_net.add_place('P1', True)
    petri_net.add_place('P2', False)
    petri_net.add_place('P3', False)
    petri_net.add_place('P4', False)
    petri_net.add_place('P5', False)
    petri_net.add_place('P6', False)
    petri_net.add_transition('A', {'P1'}, {'P2', 'P3'})
    petri_net.add_transition('B', {'P2'}, {'P4'})
    petri_net.add_transition('C', {'P3'}, {'P5'})
    petri_net.add_transition('D', {'P4', 'P5'}, {'P6'})
    initial_marking = {'P1'}

    reachability_graph = petri_net.get_reachability_graph(initial_marking)
    print(reachability_graph)
