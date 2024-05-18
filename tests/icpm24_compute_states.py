import time
from enum import Enum
from pathlib import Path
from typing import Tuple, List, Set

import numpy as np
from pix_framework.io.event_log import read_csv_log, DEFAULT_CSV_IDS
from pm4py.objects import petri
from pm4py.objects.log.importer.xes import factory as xes_import_factory
from scipy.stats import t

from icpm24_prefix_alignment import calculate_prefix_alignment_modified_a_star_with_heuristic, \
    calculate_prefix_alignment_modified_a_star_with_heuristic_without_recalculation, calculate_prefix_alignment_occ
from process_running_state.bpmn_model import BPMNModel
from process_running_state.markovian_marking import MarkovianMarking
from process_running_state.reachability_graph import ReachabilityGraph
from process_running_state.utils import read_bpmn_model

number_of_runs = 3
log_ids = DEFAULT_CSV_IDS


class AlignmentType(str, Enum):
    IASR = "IASR"
    IAS = "IAS"
    OCC = "OCC"


def _n_gram_sizes(dataset: str, threshold: str) -> List[int]:
    """ N-gram size to evaluate depending on the dataset. """
    sizes = []
    if "synthetic" in dataset:
        # Synthetic tested with 3, 5, and 10
        sizes = [3, 5, 10]
    elif "BPIC_2018" in dataset:
        # BPIC 2018
        if "IMf50" in threshold or "IMf20" in threshold:
            sizes = [3, 4, 5]
        elif "IMf10" in threshold:
            sizes = [3, 4]
    elif "BPIC_2019" in dataset:
        # BPIC 2019
        if "IMf50" in threshold:
            sizes = [3, 4, 5]
        elif "IMf20" in threshold or "IMf10" in threshold:
            sizes = [3, 4]
    elif "TravelPermitData" in dataset or "BPIC_2014" in dataset:
        # BPIC_2020_TravelPermitData and BPIC_2014_Activity_log_for_incidents
        if "IMf50" in threshold or "IMf20" in threshold:
            sizes = [3, 4, 5, 6]
        elif "IMf10" in threshold:
            sizes = [3, 4, 5]
    else:
        # Other real-life logs
        sizes = [3, 4, 5, 6]
    # Return sizes
    return sizes


def compute_current_states(
        datasets: List[str],
        noise_lvl: str = "",
        discovery_extension: str = ""
):
    """
    - Run both techniques, "our proposal" and "prefix-alignments", to compute the state of each ongoing process case.
    - Save the results in an intermediate CSV file storing the case ID, technique, ongoing state, avg runtime
    - In this way, the states can be reused later to evaluate any of the RQs.
    """
    # For each dataset
    for dataset in datasets:
        print(f"\n\n----- Processing dataset: {dataset} -----\n")
        # Instantiate paths
        #  - For synthetic logs, adapt "input" paths for each of the noise levels (e.g., '/inputs/synthetic/original/')
        if noise_lvl == "":
            ongoing_cases_csv = Path(f"../inputs/real-life/split/{dataset}_ongoing.csv.gz")
            ongoing_cases_xes = f"../inputs/real-life/split/{dataset}_ongoing.xes.gz"
            output_filename = Path(f"../outputs/{dataset}{discovery_extension}_ongoing_states.csv")
            reachability_graph_path = Path(f"../outputs/{dataset}{discovery_extension}_reachability_graph.tgf")
        else:
            ongoing_cases_csv = Path(f"../inputs/synthetic/{noise_lvl}/{dataset}_ongoing_{noise_lvl}.csv.gz")
            ongoing_cases_xes = f"../inputs/synthetic/{noise_lvl}/{dataset}_ongoing_{noise_lvl}.xes.gz"
            output_filename = Path(f"../outputs/{dataset}_{noise_lvl}_ongoing_states.csv")
            reachability_graph_path = Path(f"../outputs/{dataset}_{noise_lvl}_reachability_graph.tgf")
        bpmn_model_path = Path(f"../inputs/real-life/{dataset}{discovery_extension}.bpmn")
        pnml_model_path = Path(f"../inputs/real-life/{dataset}{discovery_extension}.pnml")
        # Read preprocessed event log(s)
        event_log_xes = xes_import_factory.apply(ongoing_cases_xes)
        event_log_csv = read_csv_log(ongoing_cases_csv, log_ids, sort=True)
        log_size = len(event_log_xes)
        # Read proces model(s)
        bpmn_model = read_bpmn_model(bpmn_model_path)
        pnml_model, initial_marking, final_marking = petri.importer.pnml.import_net(pnml_model_path)

        # Compute and export reachability graph
        print("--- Computing Reachability Graph ---\n")
        reachability_graph, runtime_avg, runtime_cnf = compute_reachability_graph(bpmn_model)
        with open(output_filename, 'a') as output_file:
            output_file.write("technique,case_id,state,runtime_avg,runtime_cnf\n")
            output_file.write(f"\"compute-reachability-graph\",,,{runtime_avg},{runtime_cnf}\n")
        with open(reachability_graph_path, 'w') as output_file:
            output_file.write(reachability_graph.to_tgf_format())

        # Compute n-gram indexes
        print("\n--- Computing N-Gram indexes ---\n")
        for n_size in _n_gram_sizes(dataset, discovery_extension):
            # Compute n-gram index
            print(f"- Building {n_size}-gram index -")
            markovian_marking, runtime_avg, runtime_cnf = compute_markovian_marking(reachability_graph, n_size)
            with open(output_filename, 'a') as output_file:
                output_file.write(f"\"build-marking-{n_size}\",,,{runtime_avg},{runtime_cnf}\n")
            # Estimate states
            print(f"- Estimating states with {n_size}-gram index -")
            total_runtime = 0
            with open(output_filename, 'a') as output_file:
                i = 0
                for trace_id, events in event_log_csv.groupby(log_ids.case):
                    # Get n-gram
                    n_gram = list(events.tail(min(len(events), n_size))[log_ids.activity])
                    # Estimate with n-gram index
                    state, runtime_avg, runtime_cnf = get_state_markovian_marking(markovian_marking, n_gram)
                    total_runtime += runtime_avg
                    # Output to file
                    output_file.write(f"\"marking-{n_size}\",\"{trace_id}\",\"{state}\",{runtime_avg},{runtime_cnf}\n")
                    # Keep progress counter
                    i += 1
                    if i % 500 == 0 or i == log_size:
                        print(f"\tProcessed {i}/{log_size}")
                # Write total runtime
                output_file.write(f"\"total-runtime-marking-{n_size}\",,,{total_runtime},\n")

        # Process prefix alignments
        print("\n--- Computing with Prefix-Alignments ---\n")
        prefix_types = [AlignmentType.IASR, AlignmentType.IAS, AlignmentType.OCC]
        for prefix_type in prefix_types:
            print(f"- Estimating with {prefix_type} -")
            total_runtime = 0
            with open(output_filename, 'a') as output_file:
                i = 0
                for trace in event_log_xes:
                    trace_id = trace.attributes['concept:name']
                    # Estimate with prefix-alignment
                    try:
                        state, runtime_avg, runtime_cnf = get_state_prefix_alignment(trace, pnml_model, initial_marking,
                                                                                     final_marking, prefix_type,
                                                                                     reachability_graph)
                    except TypeError as e:
                        state = f"Error! {str(e).replace(',', '.')}"
                        runtime_avg, runtime_cnf = 0, 0
                    total_runtime += runtime_avg
                    # Output to file
                    output_file.write(f"\"{prefix_type}\",\"{trace_id}\",\"{state}\",{runtime_avg}, {runtime_cnf}\n")
                    # Keep progress counter
                    i += 1
                    if i % 10 == 0 or i == log_size:
                        print(f"\tProcessed {i}/{log_size}")
                # Print total runtimes
                output_file.write(f"\"total-runtime-{prefix_type}\",,,{total_runtime},\n")


def compute_reachability_graph(bpmn_model: BPMNModel) -> Tuple[ReachabilityGraph, float, float]:
    """Compute the reachability graph of the given BPMN model"""
    runtimes = []
    final_reachability_graph = None
    # Compute state number_of_runs times
    for i in range(number_of_runs):
        start = time.time()
        reachability_graph = bpmn_model.get_reachability_graph()
        end = time.time()
        runtimes += [end - start]
        if i == number_of_runs - 1:
            final_reachability_graph = reachability_graph
    # Compute runtime confidence interval
    runtime_avg, runtime_cnf = compute_mean_conf_interval(runtimes)
    return final_reachability_graph, runtime_avg, runtime_cnf


def compute_markovian_marking(
        reachability_graph: ReachabilityGraph,
        n_gram_size_limit: int
) -> Tuple[MarkovianMarking, float, float]:
    """Compute the n-gram indexing of the given BPMN model"""
    runtimes = []
    final_markovian_marking = None
    # Compute state number_of_runs times
    for i in range(number_of_runs):
        start = time.time()
        markovian_marking = MarkovianMarking(reachability_graph, n_gram_size_limit)
        markovian_marking.build()
        end = time.time()
        runtimes += [end - start]
        if i == number_of_runs - 1:
            final_markovian_marking = markovian_marking
    # Compute runtime confidence interval
    runtime_avg, runtime_cnf = compute_mean_conf_interval(runtimes)
    return final_markovian_marking, runtime_avg, runtime_cnf


def get_state_prefix_alignment(
        trace,
        pnml_model,
        initial_marking,
        final_marking,
        alignment_type: AlignmentType,
        reachability_graph: ReachabilityGraph
) -> Tuple[Set[str], float, float]:
    """Compute the state of an ongoing case with a prefix-alignment technique."""
    runtimes = []
    state = None
    # Compute state number_of_runs times
    for i in range(number_of_runs):
        start = time.time()
        if alignment_type == AlignmentType.IASR:
            result = calculate_prefix_alignment_modified_a_star_with_heuristic(trace, pnml_model,
                                                                               initial_marking,
                                                                               final_marking)
        elif alignment_type == AlignmentType.IAS:
            result = calculate_prefix_alignment_modified_a_star_with_heuristic_without_recalculation(trace, pnml_model,
                                                                                                     initial_marking,
                                                                                                     final_marking)
        else:
            result = calculate_prefix_alignment_occ(trace, pnml_model,
                                                    initial_marking,
                                                    final_marking)
        end = time.time()
        runtimes += [end - start]
        if i == number_of_runs - 1:
            model_movements = [
                element['label'][1]
                for element in result['alignment']
                if element['name'][1] != '>>' and element['label'][1] is not None
            ]
            states = reachability_graph.get_markings_from_activity_sequence(model_movements)
            state = np.random.choice(states, 1)[0]  # If non-deterministic process, then random state
    # Compute runtime confidence interval
    runtime_avg, runtime_cnf = compute_mean_conf_interval(runtimes)
    return state, runtime_avg, runtime_cnf


def get_state_markovian_marking(
        markovian_marking: MarkovianMarking,
        n_gram: List[str]
) -> Tuple[Set[str], float, float]:
    """Compute the state of an ongoing case with the n-gram indexing technique (our proposal)."""
    runtimes = []
    state = None
    # Compute state number_of_runs times
    for i in range(number_of_runs):
        start = time.time()
        result = markovian_marking.get_best_marking_state_for(n_gram)
        end = time.time()
        runtimes += [end - start]
        if i == number_of_runs - 1:
            state = result
    # Compute runtime confidence interval
    runtime_avg, runtime_cnf = compute_mean_conf_interval(runtimes)
    return state, runtime_avg, runtime_cnf


def compute_mean_conf_interval(data: list, confidence: float = 0.95) -> Tuple[float, float]:
    # Compute the sample mean and standard deviation
    sample_mean = float(np.mean(data))
    sample_std = np.std(data, ddof=1)  # ddof=1 calculates the sample standard deviation
    # Compute the degrees of freedom
    df = len(data) - 1
    # Compute the t-value for the confidence level
    t_value = t.ppf(1 - (1 - confidence) / 2, df)
    # Compute the standard error of the mean
    std_error = sample_std / np.sqrt(len(data))
    conf_interval = t_value * std_error
    # Compute the confidence interval
    return sample_mean, conf_interval


if __name__ == '__main__':
    compute_current_states([
        "BPIC_2012",
        "BPIC_2013_incidents",
        "BPIC_2014_Activity_log_for_incidents",
        "BPIC_2017",
        "BPIC_2018",
        "BPIC_2019",
        "BPIC_2020_DomesticDeclarations",
        "BPIC_2020_InternationalDeclarations",
        "BPIC_2020_PrepaidTravelCost",
        "BPIC_2020_RequestForPayment",
        "BPIC_2020_TravelPermitData",
        "Sepsis_Cases",
    ], discovery_extension="_IMf50")
    compute_current_states([
        "BPIC_2012",
        "BPIC_2013_incidents",
        "BPIC_2014_Activity_log_for_incidents",
        "BPIC_2017",
        "BPIC_2018",
        "BPIC_2019",
        "BPIC_2020_DomesticDeclarations",
        "BPIC_2020_InternationalDeclarations",
        "BPIC_2020_PrepaidTravelCost",
        "BPIC_2020_RequestForPayment",
        "BPIC_2020_TravelPermitData",
        "Sepsis_Cases",
    ], discovery_extension="_IMf20")
    compute_current_states([
        "BPIC_2012",
        "BPIC_2013_incidents",
        "BPIC_2014_Activity_log_for_incidents",
        "BPIC_2017",
        "BPIC_2018",
        "BPIC_2019",
        "BPIC_2020_DomesticDeclarations",
        "BPIC_2020_InternationalDeclarations",
        "BPIC_2020_PrepaidTravelCost",
        "BPIC_2020_RequestForPayment",
        "BPIC_2020_TravelPermitData",
        "Sepsis_Cases",
    ], discovery_extension="_IMf10")
    # compute_current_states([
    #     "synthetic_and_k3",
    #     "synthetic_and_k5",
    #     "synthetic_and_k10",
    #     "synthetic_and_kinf",
    #     "synthetic_xor_sequence",
    #     "synthetic_xor_loop",
    # ])
    # compute_current_states([
    #     "synthetic_and_k3",
    #     "synthetic_and_k5",
    #     "synthetic_and_k10",
    #     "synthetic_and_kinf",
    #     "synthetic_xor_sequence",
    #     "synthetic_xor_loop",
    # ], noise_lvl="noise_1")
    # compute_current_states([
    #     "synthetic_and_k3",
    #     "synthetic_and_k5",
    #     "synthetic_and_k10",
    #     "synthetic_and_kinf",
    #     "synthetic_xor_sequence",
    #     "synthetic_xor_loop",
    # ], noise_lvl="noise_2")
    # compute_current_states([
    #     "synthetic_and_k3",
    #     "synthetic_and_k5",
    #     "synthetic_and_k10",
    #     "synthetic_and_kinf",
    #     "synthetic_xor_sequence",
    #     "synthetic_xor_loop",
    # ], noise_lvl="noise_3")
