import ast
from pathlib import Path
from typing import List, Set, Optional

import pandas as pd
from pix_framework.io.event_log import read_csv_log, DEFAULT_CSV_IDS

from process_running_state.reachability_graph import ReachabilityGraph

log_ids = DEFAULT_CSV_IDS
output_file_path = Path(f"../outputs/synthetic_accuracy.csv")


def compute_state_accuracy(datasets: List[str], noise: Optional[str] = None):
    # For each dataset
    for dataset in datasets:
        # Instantiate paths
        ongoing_cases_path = Path(f"../inputs/synthetic/split/{dataset}_ongoing.csv.gz")
        if noise is None:
            print(f"\n--- Dataset: {dataset} ---\n")
            computed_states_path = Path(f"../results/synthetic/{dataset}_ongoing_states.csv")
            reachability_graph_path = Path(f"../results/synthetic/{dataset}_reachability_graph.tgf")
        else:
            print(f"\n--- Dataset: {dataset} ({noise}) ---\n")
            computed_states_path = Path(f"../results/synthetic/{dataset}_{noise}_ongoing_states.csv")
            reachability_graph_path = Path(f"../results/synthetic/{dataset}_{noise}_reachability_graph.tgf")
        # Read event log, computed states, and reachability graph
        ongoing_cases = read_csv_log(ongoing_cases_path, log_ids, sort=True)
        computed_states = pd.read_csv(computed_states_path, quotechar="\"")
        with open(reachability_graph_path, "r") as reachability_graph_file:
            reachability_graph = ReachabilityGraph.from_tgf_format(reachability_graph_file.read())
        # Go over each case ID
        ias, tbr, mark3, mark5, mark10 = [], [], [], [], []
        for case_id, data in computed_states.groupby("case_id"):
            # Compute real state(s)
            real_states = reachability_graph.get_markings_from_activity_sequence(
                ongoing_cases[ongoing_cases[log_ids.case] == case_id][log_ids.activity]
            )
            if len(real_states) == 1:
                # Evaluate deterministic models (or deterministic case of nondeterministic model)
                real_state = real_states[0]
                # Process each technique estimation
                ias += [evaluate_state_approximation(data, "IAS", real_state)]
                tbr += [evaluate_state_approximation(data, "token-replay", real_state)]
                mark3 += [evaluate_state_approximation(data, "3-gram-index", real_state)]
                mark5 += [evaluate_state_approximation(data, "5-gram-index", real_state)]
                mark10 += [evaluate_state_approximation(data, "10-gram-index", real_state)]
            else:
                # More than one state, only allowed in non-deterministic model
                assert "nondeterministic" in dataset, "Multi-state marking found in deterministic model!!!"
                # Process each technique estimation
                ias += [max([
                    evaluate_state_approximation(data, "IAS", real_state)
                    for real_state in real_states
                ])]
                tbr += [max([
                    evaluate_state_approximation(data, "token-replay", real_state)
                    for real_state in real_states
                ])]
                mark3 += [max([
                    evaluate_state_approximation(data, "3-gram-index", real_state)
                    for real_state in real_states
                ])]
                mark5 += [max([
                    evaluate_state_approximation(data, "5-gram-index", real_state)
                    for real_state in real_states
                ])]
                mark10 += [max([
                    evaluate_state_approximation(data, "10-gram-index", real_state)
                    for real_state in real_states
                ])]
        # Print stats
        full_dataset_name = dataset if noise is None else f"{dataset}_{noise}"
        _output_summarized_results(full_dataset_name, "IAS", ias)
        _output_summarized_results(full_dataset_name, "token-replay", tbr)
        _output_summarized_results(full_dataset_name, "3-gram-index", mark3)
        _output_summarized_results(full_dataset_name, "5-gram-index", mark5)
        _output_summarized_results(full_dataset_name, "10-gram-index", mark10)


def _output_summarized_results(dataset: str, technique: str, results: List[float]):
    with open(output_file_path, "a") as output_file:
        output_file.write(
            f"{dataset},"
            f"{technique},"
            f"{len([value for value in results if value == 1.0])},"
            f"{len(results)},"
            f"{sum([value for value in results if value == 1.0]) / len(results)},"
            f"{sum(results) / len(results)}\n"
        )


def evaluate_state_approximation(
        data: pd.DataFrame,
        technique: str,
        real_marking: Set[str]
) -> float:
    # Retrieve estimated marking
    marking = ast.literal_eval(data[data["technique"] == technique]["state"].iloc[0])
    # Return
    return len(marking & real_marking) / max(len(marking), len(real_marking))


def _create_output_file():
    with open(output_file_path, "w") as output_file:
        output_file.write("dataset,technique,abs_full_matches,num_cases,rel_full_matches,abs_partial_matches\n")


if __name__ == '__main__':
    # Create output metrics path
    _create_output_file()
    # Process results without noise
    compute_state_accuracy(
        ["synthetic_and_k3", "synthetic_and_k5", "synthetic_and_k10",
         "synthetic_and_kinf", "synthetic_xor_sequence", "synthetic_xor_loop",
         "synthetic_nondeterministic"]
    )
    # Process results with noise lvl 1
    compute_state_accuracy(
        ["synthetic_and_k3", "synthetic_and_k5", "synthetic_and_k10",
         "synthetic_and_kinf", "synthetic_xor_sequence", "synthetic_xor_loop",
         "synthetic_nondeterministic"],
        "noise_1"
    )
    # Process results with noise lvl 2
    compute_state_accuracy(
        ["synthetic_and_k3", "synthetic_and_k5", "synthetic_and_k10",
         "synthetic_and_kinf", "synthetic_xor_sequence", "synthetic_xor_loop",
         "synthetic_nondeterministic"],
        "noise_2"
    )
    # Process results with noise lvl 3
    compute_state_accuracy(
        ["synthetic_and_k3", "synthetic_and_k5", "synthetic_and_k10",
         "synthetic_and_kinf", "synthetic_xor_sequence", "synthetic_xor_loop",
         "synthetic_nondeterministic"],
        "noise_3"
    )
