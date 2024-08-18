import time
from pathlib import Path
from typing import Tuple, List

import numpy as np
import pm4py
from pix_framework.io.event_log import read_csv_log, DEFAULT_CSV_IDS
from pm4py import Marking
from scipy.stats import t

from process_running_state.reachability_graph import ReachabilityGraph
from vldb25_token_replay import translate_marking_to_state, custom_replay_prefix_tbr

number_of_runs = 3
log_ids = DEFAULT_CSV_IDS


def compute_current_states(
        datasets: List[str],
        noise_lvl: str = "",
):
    """
    - Run the "token-replay" technique to compute the state of each ongoing process case.
    - Save the results in an intermediate CSV file storing the case ID, technique, ongoing state, avg runtime
    - In this way, the states can be reused later to evaluate any of the RQs.
    """
    # For each dataset
    for dataset in datasets:
        print(f"\n\n----- Processing dataset: {dataset} -----\n")
        # Instantiate paths
        pnml_model_path = f"../inputs/synthetic/{dataset}.pnml"
        if noise_lvl == "":
            # No noise
            ongoing_cases_csv = Path(f"../inputs/synthetic/split/{dataset}_ongoing.csv.gz")
            output_filename = Path(f"../outputs/{dataset}_ongoing_states.csv")
            reachability_graph_path = Path(f"../outputs/{dataset}_reachability_graph.tgf")
        else:
            # With noise
            ongoing_cases_csv = Path(f"../inputs/synthetic/{noise_lvl}/{dataset}_ongoing_{noise_lvl}.csv.gz")
            output_filename = Path(f"../outputs/{dataset}_{noise_lvl}_ongoing_states.csv")
            reachability_graph_path = Path(f"../outputs/{dataset}_{noise_lvl}_reachability_graph.tgf")
        # Read preprocessed event log(s)
        event_log_csv = read_csv_log(ongoing_cases_csv, log_ids, sort=True)
        log_size = len(event_log_csv[log_ids.case].unique())
        # Read Petri net
        pnml_model, initial_marking, final_marking = pm4py.read_pnml(pnml_model_path)

        # Read reachability graph
        print("--- Reading Reachability Graph ---\n")
        with open(reachability_graph_path, 'r') as reachability_graph_file:
            reachability_graph = ReachabilityGraph.from_tgf_format(reachability_graph_file.read())

        # Compute token-replay
        print("\n--- Computing with Token-Replay ---\n")
        total_runtime = 0
        with open(output_filename, 'a') as output_file:
            # output_file.write("technique,case_id,state,runtime_avg,runtime_cnf\n")  # Appending to old result files
            i = 0
            for trace_id, events in event_log_csv.groupby(log_ids.case):
                # Get sequence of activities
                prefix_activities = list(events[log_ids.activity])
                # Estimate with token-replay
                marking, runtime_avg, runtime_cnf = get_marking_token_replay(prefix_activities, pnml_model,
                                                                             initial_marking, final_marking)
                total_runtime += runtime_avg
                # Translate for exporting
                state = translate_marking_to_state(marking, pnml_model, reachability_graph, dataset)
                if state is None:
                    state = set()
                # Output to file
                output_file.write(f"\"token-replay\",\"{trace_id}\",\"{state}\",{runtime_avg},{runtime_cnf}\n")
                # Keep progress counter
                i += 1
                if i % 500 == 0 or i == log_size:
                    print(f"\tProcessed {i}/{log_size}")
            # Write total runtime
            output_file.write(f"\"total-runtime-token-replay\",,,{total_runtime},\n")


def get_marking_token_replay(
        prefix_activities,
        pnml_model,
        initial_marking,
        final_marking,
) -> Tuple[Marking, float, float]:
    """
    Compute the Petri net marking of an ongoing case with a token-replay technique.
    """
    runtimes = []
    marking = None
    # Compute state number_of_runs times
    for i in range(number_of_runs):
        start = time.time()
        result = custom_replay_prefix_tbr(prefix_activities, pnml_model, initial_marking, final_marking)
        end = time.time()
        runtimes += [end - start]
        if i == number_of_runs - 1:
            marking = result
    # Compute runtime confidence interval
    runtime_avg, runtime_cnf = compute_mean_conf_interval(runtimes)
    return marking, runtime_avg, runtime_cnf


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
    # compute_current_states([
    #     "BPIC_2012",
    #     "BPIC_2013_incidents",
    #     "BPIC_2014_Activity_log_for_incidents",
    #     "BPIC_2017",
    #     "BPIC_2018",
    #     "BPIC_2019",
    #     "BPIC_2020_DomesticDeclarations",
    #     "BPIC_2020_InternationalDeclarations",
    #     "BPIC_2020_PrepaidTravelCost",
    #     "BPIC_2020_RequestForPayment",
    #     "BPIC_2020_TravelPermitData",
    #     "Sepsis_Cases",
    # ], discovery_extension="_IMf50")
    # compute_current_states([
    #     "BPIC_2012",
    #     "BPIC_2013_incidents",
    #     "BPIC_2014_Activity_log_for_incidents",
    #     "BPIC_2017",
    #     "BPIC_2018",
    #     "BPIC_2019",
    #     "BPIC_2020_DomesticDeclarations",
    #     "BPIC_2020_InternationalDeclarations",
    #     "BPIC_2020_PrepaidTravelCost",
    #     "BPIC_2020_RequestForPayment",
    #     "BPIC_2020_TravelPermitData",
    #     "Sepsis_Cases",
    # ], discovery_extension="_IMf20")
    # compute_current_states([
    #     "BPIC_2012",
    #     "BPIC_2013_incidents",
    #     "BPIC_2014_Activity_log_for_incidents",
    #     "BPIC_2017",
    #     "BPIC_2018",
    #     "BPIC_2019",
    #     "BPIC_2020_DomesticDeclarations",
    #     "BPIC_2020_InternationalDeclarations",
    #     "BPIC_2020_PrepaidTravelCost",
    #     "BPIC_2020_RequestForPayment",
    #     "BPIC_2020_TravelPermitData",
    #     "Sepsis_Cases",
    # ], discovery_extension="_IMf10")
    # run_ambiguous_model_test()
    compute_current_states([
        "synthetic_and_k3",
        "synthetic_and_k5",
        "synthetic_and_k10",
        "synthetic_and_kinf",
        "synthetic_xor_sequence",
        "synthetic_xor_loop",
        "synthetic_nondeterministic",
    ])
    compute_current_states([
        "synthetic_and_k3",
        "synthetic_and_k5",
        "synthetic_and_k10",
        "synthetic_and_kinf",
        "synthetic_xor_sequence",
        "synthetic_xor_loop",
    ], noise_lvl="noise_1")
    compute_current_states([
        "synthetic_and_k3",
        "synthetic_and_k5",
        "synthetic_and_k10",
        "synthetic_and_kinf",
        "synthetic_xor_sequence",
        "synthetic_xor_loop",
    ], noise_lvl="noise_2")
    compute_current_states([
        "synthetic_and_k3",
        "synthetic_and_k5",
        "synthetic_and_k10",
        "synthetic_and_kinf",
        "synthetic_xor_sequence",
        "synthetic_xor_loop",
    ], noise_lvl="noise_3")
