import os
import time

from pm4py.algo.conformance.alignments.incremental_a_star.incremental_a_star_approach import \
    apply as incremental_a_star_apply
from pm4py.algo.conformance.alignments.incremental_a_star.occ_approach import \
    apply as incremental_prefix_alignments_apply
from pm4py.objects import petri
from pm4py.objects.log.importer.xes import factory as xes_import_factory

processed_traces = 0
number_traces = 0


def calculate_prefix_alignments_multiprocessing(petri_net_path, log):
    net, im, fm = petri.importer.pnml.import_net(petri_net_path)
    total_runtime = 0
    i = 0
    for trace in log:
        print(f"Iteration {i}")
        i += 1
        start = time.time()
        # Total runtime: 460.53 sec # Average runtime: 0.43 sec
        # result = calculate_prefix_alignment_modified_a_star_with_heuristic(trace, net, im, fm)
        # Total runtime: 237.74 sec # Average runtime: 0.23 sec
        result = calculate_prefix_alignment_modified_a_star_with_heuristic_without_recalculation(trace, net, im, fm)
        # Total runtime: 2831.81 sec # Average runtime: 2.69 sec
        # result = calculate_prefix_alignment_occ(trace, net, im, fm)
        # result = calculate_prefix_alignment_occ(trace, net, im, fm, window_size=1)
        # result = calculate_prefix_alignment_occ(trace, net, im, fm, window_size=2)
        # result = calculate_prefix_alignment_occ(trace, net, im, fm, window_size=5)
        # result = calculate_prefix_alignment_occ(trace, net, im, fm, window_size=10)
        end = time.time()
        total_runtime += end - start
        # print("\n".join([f"{element['label']} -> {element['name']}" for element in result["alignment"]]))
        # model_movements = [
        #     element['label'][1]
        #     for element in result['alignment']
        #     if element['name'][1] != '>>' and element['label'][1] is not None
        # ]
        # print(model_movements)
        print(f"Runtime {end - start} sec")
    print(f"Total runtime: {total_runtime} sec")
    print(f"Average runtime: {total_runtime / i} sec")


def calculate_prefix_alignment_modified_a_star_dijkstra(trace, petri_net, initial_marking, final_marking):
    """
    This method calculates for a trace prefix alignments by starting a* WITHOUT a heurisitc (i.e. dijkstra) and keeps
    open and closed set in memory
    :return:
    """
    res = incremental_a_star_apply(trace, petri_net, initial_marking, final_marking, dijkstra=True)
    return res


def calculate_prefix_alignment_modified_a_star_with_heuristic(trace, petri_net, initial_marking, final_marking):
    """
    This method calculate for a trace prefix alignments by starting a* WITH a heurisitc (i.e. modified state equation)
    and keeps open and closed sset in memory
    :return:
    """
    res = incremental_a_star_apply(trace, petri_net, initial_marking, final_marking)
    return res


def calculate_prefix_alignment_modified_a_star_with_heuristic_without_recalculation(trace, petri_net, initial_marking,
                                                                                    final_marking):
    """
    This method calculates for a trace prefix alignments by starting a* WITH a heurisitc (i.e. modified state equation)
    and keeps open and closed set in memory
    :return:
    """
    res = incremental_a_star_apply(trace, petri_net, initial_marking, final_marking,
                                   recalculate_heuristic_open_set=False)
    return res


def calculate_prefix_alignment_occ(trace, petri_net, initial_marking, final_marking,
                                   window_size=0):
    """
    This methods uses OCC method WITH optimality guarantees (i.e. no partial reverting)
    :return:
    """
    res = incremental_prefix_alignments_apply(trace, petri_net, initial_marking, final_marking, window_size=window_size)
    return res


if __name__ == '__main__':
    # sys.setrecursionlimit(100000)
    dirname = os.path.dirname(__file__)
    path_to_files = os.path.join(dirname, '..', 'inputs')
    calculate_prefix_alignments_multiprocessing(
        petri_net_path=os.path.join(path_to_files, "sepsis-cases.pnml"),
        log=xes_import_factory.apply(os.path.join(path_to_files, "sepsis_cases.xes.gz")),
    )
