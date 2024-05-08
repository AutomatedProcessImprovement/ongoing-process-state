import ast
from pathlib import Path
from typing import List, Set

import pandas as pd
from pix_framework.io.event_log import read_csv_log, DEFAULT_CSV_IDS

from process_running_state.reachability_graph import ReachabilityGraph

log_ids = DEFAULT_CSV_IDS


def exact_state_accuracy(datasets: List[str]):
    # For each dataset
    for dataset in datasets:
        print(f"\n--- Dataset: {dataset} ---\n")
        # Instantiate paths
        ongoing_cases_path = Path(f"../inputs/synthetic/original/{dataset}_ongoing.csv.gz")
        computed_states_path = Path(f"../results/{dataset}_ongoing_states.csv")
        reachability_graph_path = Path(f"../results/{dataset}_reachability_graph.tgf")
        # Read event log, computed states, and reachability graph
        ongoing_cases = read_csv_log(ongoing_cases_path, log_ids, sort=True)
        computed_states = pd.read_csv(computed_states_path, quotechar="\"")
        with open(reachability_graph_path, "r") as reachability_graph_file:
            reachability_graph = ReachabilityGraph.from_tgf_format(reachability_graph_file.read())
        # Go over each case ID
        iasr, ias, occ, mark3, mark5, mark7, mark9 = [], [], [], [], [], [], []
        for case_id, data in computed_states.groupby("case_id"):
            # Compute real state(s)
            real_states = reachability_graph.get_markings_from_activity_sequence(
                ongoing_cases[ongoing_cases[log_ids.case] == case_id][log_ids.activity]
            )
            assert len(real_states) == 1, "Multi-state marking found!!!"  # Shouldn't be any in our test logs
            real_state = real_states[0]
            # Process each technique estimation
            iasr += [evaluate_state_approximation(data, "IASR", real_state)]
            ias += [evaluate_state_approximation(data, "IAS", real_state)]
            occ += [evaluate_state_approximation(data, "OCC", real_state)]
            mark3 += [evaluate_state_approximation(data, "marking-3", real_state)]
            mark5 += [evaluate_state_approximation(data, "marking-5", real_state)]
            mark7 += [evaluate_state_approximation(data, "marking-7", real_state)]
            mark9 += [evaluate_state_approximation(data, "marking-9", real_state)]
        # Print stats
        print("IASR:   {:.2f} ({:.2f})".format(
            sum(iasr) / len(iasr),
            sum([value for value in iasr if value == 1.0]) / len(iasr)
        ))
        print("IAS:    {:.2f} ({:.2f})".format(
            sum(ias) / len(ias),
            sum([value for value in ias if value == 1.0]) / len(ias)
        ))
        print("OCC:    {:.2f} ({:.2f})".format(
            sum(occ) / len(occ),
            sum([value for value in occ if value == 1.0]) / len(occ)
        ))
        print("mark-3: {:.2f} ({:.2f})".format(
            sum(mark3) / len(mark3),
            sum([value for value in mark3 if value == 1.0]) / len(mark3)
        ))
        print("mark-5: {:.2f} ({:.2f})".format(
            sum(mark5) / len(mark5),
            sum([value for value in mark5 if value == 1.0]) / len(mark5)
        ))
        print("mark-7: {:.2f} ({:.2f})".format(
            sum(mark7) / len(mark7),
            sum([value for value in mark7 if value == 1.0]) / len(mark7)
        ))
        print("mark-9: {:.2f} ({:.2f})\n".format(
            sum(mark9) / len(mark9),
            sum([value for value in mark9 if value == 1.0]) / len(mark9)
        ))


def evaluate_state_approximation(
        data: pd.DataFrame,
        technique: str,
        real_marking: Set[str]
) -> float:
    # Retrieve estimated marking
    marking = ast.literal_eval(data[data["technique"] == technique]["state"].iloc[0])
    # Return
    return len(marking & real_marking) / max(len(marking), len(real_marking))


if __name__ == '__main__':
    exact_state_accuracy([
        "synthetic_and_k3",
        "synthetic_and_k5",
        "synthetic_and_k7",
        "synthetic_and_kinf",
        "synthetic_xor",
        "synthetic_xor_loop",
    ])
