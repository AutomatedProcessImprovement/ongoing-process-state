import ast
from pathlib import Path
from typing import List

import pandas as pd
from pix_framework.io.event_log import read_csv_log, DEFAULT_CSV_IDS

from process_running_state.reachability_graph import ReachabilityGraph

log_ids = DEFAULT_CSV_IDS
output_file_path = Path(f"../outputs/synthetic_accuracy.csv")


def next_activity_accuracy(datasets: List[str], discovery_extension: str = ""):
    # For each dataset
    for dataset in datasets:
        print(f"\n--- Dataset: {dataset} ---\n")
        # Instantiate paths
        remaining_cases_path = Path(f"../inputs/real-life/split/{dataset}_remaining.csv.gz")
        computed_states_path = Path(f"../results/real-life/{dataset}{discovery_extension}_ongoing_states.csv")
        reachability_graph_path = Path(f"../results/real-life/{dataset}{discovery_extension}_reachability_graph.tgf")
        # Read preprocessed event log(s)
        remaining_cases = read_csv_log(remaining_cases_path, log_ids, sort=True)
        computed_states = pd.read_csv(computed_states_path)
        with open(reachability_graph_path, "r") as reachability_graph_file:
            reachability_graph = ReachabilityGraph.from_tgf_format(reachability_graph_file.read())
        # Go over each case ID
        iasr, ias, occ, mark3, mark5, mark10 = [], [], [], [], [], []
        for case_id, data in computed_states.groupby("case_id"):
            # Retrieve remaining activities of this case
            remaining_case = remaining_cases[remaining_cases[log_ids.case] == case_id]
            # Process techniques
            iasr += [evaluate_state_approximation(data, "IASR", reachability_graph, remaining_case)]
            ias += [evaluate_state_approximation(data, "IAS", reachability_graph, remaining_case)]
            occ += [evaluate_state_approximation(data, "OCC", reachability_graph, remaining_case)]
            mark3 += [evaluate_state_approximation(data, "marking-3", reachability_graph, remaining_case)]
            mark5 += [evaluate_state_approximation(data, "marking-5", reachability_graph, remaining_case)]
            mark10 += [evaluate_state_approximation(data, "marking-10", reachability_graph, remaining_case)]
        # Write stats to file
        with open(output_file_path, "a") as output_file:
            output_file.write(f"{dataset},{discovery_extension},IASR,{sum(iasr)},{sum(iasr) / len(iasr)}\n")
            output_file.write(f"{dataset},{discovery_extension},IAS,{sum(ias)},{sum(ias) / len(ias)}\n")
            output_file.write(f"{dataset},{discovery_extension},OCC,{sum(occ)},{sum(occ) / len(occ)}\n")
            output_file.write(f"{dataset},{discovery_extension},mark-3,{sum(mark3)},{sum(mark3) / len(mark3)}\n")
            output_file.write(f"{dataset},{discovery_extension},mark-5,{sum(mark5)},{sum(mark5) / len(mark5)}\n")
            output_file.write(f"{dataset},{discovery_extension},mark-10,{sum(mark10)},{sum(mark10) / len(mark10)}\n")


def evaluate_state_approximation(
        data: pd.DataFrame,
        technique: str,
        reachability_graph: ReachabilityGraph,
        remaining_case: pd.DataFrame
) -> bool:
    # Retrieve next activity
    if len(remaining_case) > 0:
        next_activity = remaining_case.head(1)[log_ids.activity].iloc[0]
    else:
        next_activity = None
    # Retrieve estimated marking
    marking = ast.literal_eval(data[data["technique"] == technique]["state"].iloc[0])
    # Check if the next activity is enabled
    marking_key = reachability_graph.marking_to_key[tuple(sorted(marking))]
    outgoing_edges = reachability_graph.outgoing_edges[marking_key]
    is_enabled = next_activity in [reachability_graph.edge_to_activity[edge] for edge in outgoing_edges]
    # Return if the next activity is enabled or not
    return is_enabled


def _create_output_file():
    with open(output_file_path, "w") as output_file:
        output_file.write("dataset,discovery_algorithm,technique,abs_positives,rel_positives\n")


if __name__ == '__main__':
    # Create output metrics path
    _create_output_file()
    # Process results
    next_activity_accuracy([
        "Sepsis_Cases",
        "BPIC_2012",
        "BPIC_2015_1",
        "BPIC_2015_2",
        "BPIC_2015_3",
        "BPIC_2015_4",
        "BPIC_2015_5",
        "BPIC_2017",
        "BPIC_2018",
        "BPIC_2019",
        "BPIC_2020_DomesticDeclarations",
        "BPIC_2020_InternationalDeclarations",
        "BPIC_2020_PrepaidTravelCost",
        "BPIC_2020_RequestForPayment",
        "BPIC_2020_TravelPermitData",
    ], discovery_extension="_IMf20")
