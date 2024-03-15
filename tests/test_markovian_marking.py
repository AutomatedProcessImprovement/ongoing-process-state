import pytest

from process_running_state.markovian_marking import MarkovianMarking
from test_bpmn_model_fixtures import _bpmn_model_with_loop_inside_AND, _bpmn_model_with_AND_and_nested_XOR, \
    _bpmn_model_with_XOR_within_AND, _bpmn_model_with_AND_and_XOR


def test_build_simple_size_limit():
    bpmn_model = _bpmn_model_with_AND_and_XOR()
    reachability_graph = bpmn_model.get_reachability_graph()
    markovian_marking = MarkovianMarking(reachability_graph, n_gram_size_limit=1)
    markovian_marking.build()
    # Check the maximum size of the explored n-grams is under the limit
    n_gram_sizes = [len(n_gram) for n_gram in markovian_marking.markings]
    assert max(n_gram_sizes) <= 1
    # Check number of n-grams is the expected (num of labels + trace_start)
    assert len(markovian_marking.markings) == len(reachability_graph.activity_to_edges) + 1
    # Check specific markings
    assert markovian_marking.get_marking_state([MarkovianMarking.TRACE_START]) == [{"1"}]
    assert markovian_marking.get_marking_state(["A"]) == [{"5", "6"}]
    assert markovian_marking.get_marking_state(["B"]) == [{"9", "6"}, {"12"}]
    assert markovian_marking.get_marking_state(["C"]) == [{"5", "10"}, {"12"}]
    assert markovian_marking.get_marking_state(["D"]) == [{"21"}]
    assert markovian_marking.get_marking_state(["E"]) == [{"21"}]
    assert markovian_marking.get_marking_state(["F"]) == [{"23"}]


def test_build_simple():
    bpmn_model = _bpmn_model_with_AND_and_XOR()
    reachability_graph = bpmn_model.get_reachability_graph()
    markovian_marking = MarkovianMarking(reachability_graph, n_gram_size_limit=3)
    markovian_marking.build()
    # Check the maximum size of the explored n-grams is under the limit
    n_gram_sizes = [len(n_gram) for n_gram in markovian_marking.markings]
    assert max(n_gram_sizes) <= 3
    # Check number of n-grams is the expected
    assert len(markovian_marking.markings) == 11
    # Check specific markings
    assert markovian_marking.get_marking_state([MarkovianMarking.TRACE_START]) == [{"1"}]
    assert markovian_marking.get_marking_state(["A"]) == [{"5", "6"}]
    assert markovian_marking.get_marking_state(["B"]) == [{"9", "6"}, {"12"}]
    assert markovian_marking.get_marking_state(["C"]) == [{"5", "10"}, {"12"}]
    assert markovian_marking.get_marking_state(["A", "B"]) == [{"9", "6"}]
    assert markovian_marking.get_marking_state(["C", "B"]) == [{"12"}]
    assert markovian_marking.get_marking_state(["A", "C"]) == [{"5", "10"}]
    assert markovian_marking.get_marking_state(["B", "C"]) == [{"12"}]
    assert markovian_marking.get_marking_state(["D"]) == [{"21"}]
    assert markovian_marking.get_marking_state(["E"]) == [{"21"}]
    assert markovian_marking.get_marking_state(["F"]) == [{"23"}]


@pytest.mark.skip(reason="Test not yest finished")
def test_build_XOR_within_AND():
    bpmn_model = _bpmn_model_with_XOR_within_AND()
    reachability_graph = bpmn_model.get_reachability_graph()
    markovian_marking = MarkovianMarking(reachability_graph, n_gram_size_limit=3)
    markovian_marking.build()
    # Check there is one entry per activity label
    size_1_n_grams = [n_gram for n_gram in markovian_marking.markings if len(n_gram) == 1]
    assert len(size_1_n_grams) == len(reachability_graph.activity_to_edges)
    # Check the maximum size of the explored n-grams is under the limit
    n_gram_sizes = [len(n_gram) for n_gram in markovian_marking.markings]
    assert max(n_gram_sizes) <= 3
    # Check specific markings
    # TODO


@pytest.mark.skip(reason="Test not yest finished")
def test_build_nested_XOR():
    bpmn_model = _bpmn_model_with_AND_and_nested_XOR()
    reachability_graph = bpmn_model.get_reachability_graph()
    markovian_marking = MarkovianMarking(reachability_graph, n_gram_size_limit=3)
    markovian_marking.build()
    # Check there is one entry per activity label
    size_1_n_grams = [n_gram for n_gram in markovian_marking.markings if len(n_gram) == 1]
    assert len(size_1_n_grams) == len(reachability_graph.activity_to_edges)
    # Check the maximum size of the explored n-grams is under the limit
    n_gram_sizes = [len(n_gram) for n_gram in markovian_marking.markings]
    assert max(n_gram_sizes) <= 3
    # Check specific markings
    # TODO


@pytest.mark.skip(reason="Test not yest finished")
def test_build_loop_model():
    bpmn_model = _bpmn_model_with_loop_inside_AND()
    reachability_graph = bpmn_model.get_reachability_graph()
    markovian_marking = MarkovianMarking(reachability_graph, n_gram_size_limit=3)
    markovian_marking.build()
    # Check there is one entry per activity label
    size_1_n_grams = [n_gram for n_gram in markovian_marking.markings if len(n_gram) == 1]
    assert len(size_1_n_grams) == len(reachability_graph.activity_to_edges)
    # Check the maximum size of the explored n-grams is under the limit
    n_gram_sizes = [len(n_gram) for n_gram in markovian_marking.markings]
    assert max(n_gram_sizes) <= 3
    # Check specific markings
    # TODO
