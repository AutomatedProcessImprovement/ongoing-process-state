from typing import List, Set, Tuple

import pytest

from process_running_state.markovian_marking import MarkovianMarking
from test_bpmn_model_fixtures import _bpmn_model_with_loop_inside_AND, _bpmn_model_with_AND_and_nested_XOR, \
    _bpmn_model_with_XOR_within_AND, _bpmn_model_with_AND_and_XOR


def _prepare(markings: List[Set[str]]) -> Set[Tuple[str]]:
    return {tuple(sorted(marking)) for marking in markings}


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


def test_build_XOR_within_AND():
    bpmn_model = _bpmn_model_with_XOR_within_AND()
    reachability_graph = bpmn_model.get_reachability_graph()
    markovian_marking = MarkovianMarking(reachability_graph, n_gram_size_limit=3)
    markovian_marking.build()
    # Check the maximum size of the explored n-grams is under the limit
    n_gram_sizes = [len(n_gram) for n_gram in markovian_marking.markings]
    assert max(n_gram_sizes) <= 3
    # Check number of n-grams is the expected
    assert len(markovian_marking.markings) == 9 + 6 + 24 + 24 + 48
    # Check 1-grams (9)
    assert markovian_marking.get_marking_state([MarkovianMarking.TRACE_START]) == [{"1"}]
    assert markovian_marking.get_marking_state(["A"]) == [{"5", "6", "7"}]
    assert _prepare(
        markovian_marking.get_marking_state(["B"])
    ) == _prepare([{"32", "6", "7"}, {"32", "33", "7"}, {"32", "6", "34"}, {"36"}])
    assert _prepare(
        markovian_marking.get_marking_state(["C"])
    ) == _prepare([{"32", "6", "7"}, {"32", "33", "7"}, {"32", "6", "34"}, {"36"}])
    assert _prepare(
        markovian_marking.get_marking_state(["D"])
    ) == _prepare([{"5", "33", "7"}, {"32", "33", "7"}, {"5", "33", "34"}, {"36"}])
    assert _prepare(
        markovian_marking.get_marking_state(["E"])
    ) == _prepare([{"5", "33", "7"}, {"32", "33", "7"}, {"5", "33", "34"}, {"36"}])
    assert _prepare(
        markovian_marking.get_marking_state(["F"])
    ) == _prepare([{"5", "6", "34"}, {"32", "6", "34"}, {"5", "33", "34"}, {"36"}])
    assert _prepare(
        markovian_marking.get_marking_state(["G"])
    ) == _prepare([{"5", "6", "34"}, {"32", "6", "34"}, {"5", "33", "34"}, {"36"}])
    assert markovian_marking.get_marking_state(["H"]) == [{"38"}]
    # 2-gram at the start of the trace (6)
    assert markovian_marking.get_marking_state(["A", "B"]) == [{"32", "6", "7"}]
    assert markovian_marking.get_marking_state(["A", "C"]) == [{"32", "6", "7"}]
    assert markovian_marking.get_marking_state(["A", "D"]) == [{"5", "33", "7"}]
    assert markovian_marking.get_marking_state(["A", "E"]) == [{"5", "33", "7"}]
    assert markovian_marking.get_marking_state(["A", "F"]) == [{"5", "6", "34"}]
    assert markovian_marking.get_marking_state(["A", "G"]) == [{"5", "6", "34"}]
    # 2-gram in the middle of the AND execution (24)
    assert _prepare(markovian_marking.get_marking_state(["B", "E"])) == _prepare([{"32", "33", "7"}, {"36"}])
    assert _prepare(markovian_marking.get_marking_state(["C", "F"])) == _prepare([{"32", "6", "34"}, {"36"}])
    assert _prepare(markovian_marking.get_marking_state(["D", "B"])) == _prepare([{"32", "33", "7"}, {"36"}])
    assert _prepare(markovian_marking.get_marking_state(["E", "G"])) == _prepare([{"5", "33", "34"}, {"36"}])
    assert _prepare(markovian_marking.get_marking_state(["F", "C"])) == _prepare([{"32", "6", "34"}, {"36"}])
    assert _prepare(markovian_marking.get_marking_state(["G", "D"])) == _prepare([{"5", "33", "34"}, {"36"}])
    # 3-gram at the start of the trace (24)
    assert markovian_marking.get_marking_state(["A", "B", "E"]) == [{"32", "33", "7"}]
    assert markovian_marking.get_marking_state(["A", "C", "F"]) == [{"32", "6", "34"}]
    assert markovian_marking.get_marking_state(["A", "D", "B"]) == [{"32", "33", "7"}]
    assert markovian_marking.get_marking_state(["A", "E", "G"]) == [{"5", "33", "34"}]
    assert markovian_marking.get_marking_state(["A", "F", "C"]) == [{"32", "6", "34"}]
    assert markovian_marking.get_marking_state(["A", "G", "D"]) == [{"5", "33", "34"}]
    # 3-gram in the middle of the AND execution (48)
    assert markovian_marking.get_marking_state(["F", "B", "E"]) == [{"36"}]
    assert markovian_marking.get_marking_state(["D", "C", "F"]) == [{"36"}]
    assert markovian_marking.get_marking_state(["F", "D", "B"]) == [{"36"}]
    assert markovian_marking.get_marking_state(["C", "E", "G"]) == [{"36"}]
    assert markovian_marking.get_marking_state(["D", "F", "C"]) == [{"36"}]
    assert markovian_marking.get_marking_state(["B", "G", "D"]) == [{"36"}]


def test_build_nested_XOR():
    bpmn_model = _bpmn_model_with_AND_and_nested_XOR()
    reachability_graph = bpmn_model.get_reachability_graph()
    markovian_marking = MarkovianMarking(reachability_graph, n_gram_size_limit=3)
    markovian_marking.build()
    # Check the maximum size of the explored n-grams is under the needed one
    n_gram_sizes = [len(n_gram) for n_gram in markovian_marking.markings]
    assert max(n_gram_sizes) <= 2
    # Check number of n-grams is the expected
    assert len(markovian_marking.markings) == 7 + 10
    # Check 1-gram markings (7)
    assert markovian_marking.get_marking_state([MarkovianMarking.TRACE_START]) == [{"1"}]
    assert markovian_marking.get_marking_state(["A"]) == [{"4", "6"}]
    assert _prepare(markovian_marking.get_marking_state(["B"])) == _prepare([{"21", "6"}, {"27"}])
    assert _prepare(markovian_marking.get_marking_state(["C"])) == _prepare([{"21", "6"}, {"27"}])
    assert _prepare(markovian_marking.get_marking_state(["D"])) == _prepare([{"21", "6"}, {"27"}])
    assert _prepare(markovian_marking.get_marking_state(["E"])) == _prepare([{"4", "20"}, {"27"}])
    assert markovian_marking.get_marking_state(["F"]) == [{"24"}]
    # Check 2-gram markings (10)
    assert markovian_marking.get_marking_state(["A", "B"]) == [{"21", "6"}]
    assert markovian_marking.get_marking_state(["A", "C"]) == [{"21", "6"}]
    assert markovian_marking.get_marking_state(["A", "D"]) == [{"21", "6"}]
    assert markovian_marking.get_marking_state(["A", "E"]) == [{"4", "20"}]
    assert markovian_marking.get_marking_state(["B", "E"]) == [{"27"}]
    assert markovian_marking.get_marking_state(["C", "E"]) == [{"27"}]
    assert markovian_marking.get_marking_state(["D", "E"]) == [{"27"}]
    assert markovian_marking.get_marking_state(["E", "B"]) == [{"27"}]
    assert markovian_marking.get_marking_state(["E", "C"]) == [{"27"}]
    assert markovian_marking.get_marking_state(["E", "D"]) == [{"27"}]


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
