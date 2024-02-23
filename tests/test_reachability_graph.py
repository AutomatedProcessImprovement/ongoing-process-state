from process_running_state.reachability_graph import ReachabilityGraph


def test_reachability_graph_model():
    graph = ReachabilityGraph()
    # Add some markings
    graph.add_marking({"a", "b", "c"})
    graph.add_marking({"a", "b"})
    graph.add_marking({"b", "c"})
    graph.add_marking({"a", "c"})
    # Assert size of stored elements
    assert len(graph.markings) == 4
    assert len(graph.edges) == 0
    assert len(graph.activity_to_edges) == 0
    # Add rest of markings
    graph.add_marking({"a"})
    graph.add_marking({"b"})
    graph.add_marking({"c"})
    graph.add_marking({"d"})
    # Add edges
    graph.add_edge("A", {"a", "b", "c"}, {"b", "c"})
    graph.add_edge("B", {"a", "b", "c"}, {"a", "c"})
    graph.add_edge("C", {"a", "b", "c"}, {"a", "b"})
    graph.add_edge("A", {"a", "b"}, {"b"})
    graph.add_edge("A", {"a", "c"}, {"c"})
    graph.add_edge("B", {"a", "b"}, {"a"})
    graph.add_edge("B", {"b", "c"}, {"c"})
    graph.add_edge("C", {"a", "c"}, {"a"})
    graph.add_edge("C", {"b", "c"}, {"b"})
    graph.add_edge("A", {"a"}, {"d"})
    graph.add_edge("B", {"b"}, {"d"})
    graph.add_edge("C", {"c"}, {"d"})
    # Assert size of stored elements
    assert len(graph.markings) == 8
    assert len(graph.edges) == 12
    assert len(graph.activity_to_edges) == 3
    assert len(graph.activity_to_edges["A"]) == 4
    # Assert incoming and outgoing arcs
    marking_b_key = graph.marking_to_key[tuple(sorted({"b"}))]
    marking_d_key = graph.marking_to_key[tuple(sorted({"d"}))]
    marking_ab_key = graph.marking_to_key[tuple(sorted({"a", "b"}))]
    marking_bc_key = graph.marking_to_key[tuple(sorted({"b", "c"}))]
    assert {
               graph.edges[edge_id]
               for edge_id in graph.incoming_edges[marking_b_key]
           } == {(marking_ab_key, marking_b_key), (marking_bc_key, marking_b_key)}
    assert {
               graph.edges[edge_id]
               for edge_id in graph.outgoing_edges[marking_b_key]
           } == {(marking_b_key, marking_d_key)}
    marking_abc_key = graph.marking_to_key[tuple(sorted({"a", "b", "c"}))]
    marking_c_key = graph.marking_to_key[tuple(sorted({"c"}))]
    assert {
               graph.edges[edge_id]
               for edge_id in graph.incoming_edges[marking_bc_key]
           } == {(marking_abc_key, marking_bc_key)}
    assert {
               graph.edges[edge_id]
               for edge_id in graph.outgoing_edges[marking_bc_key]
           } == {(marking_bc_key, marking_b_key), (marking_bc_key, marking_c_key)}
    # Try to add an existing repeated edge
    graph.add_edge("C", {"b", "c"}, {"b"})
    assert len(graph.edges) == 12
    # Try to add an existing marking
    graph.add_marking({"b", "c"})
    assert len(graph.markings) == 8
