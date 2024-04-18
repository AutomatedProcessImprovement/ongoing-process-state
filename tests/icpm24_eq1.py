import ast
from pathlib import Path

import pandas as pd
from pix_framework.io.event_log import read_csv_log, DEFAULT_CSV_IDS

from process_running_state.reachability_graph import ReachabilityGraph

log_ids = DEFAULT_CSV_IDS


def evaluation_question_one():
    # Instantiate datasets
    datasets = ["sepsis_cases"]
    # For each dataset
    for dataset in datasets:
        print(f"\n--- Dataset: {dataset} ---\n")
        # Instantiate paths
        remaining_cases_path = Path(f"../inputs/{dataset}_remaining.csv.gz")
        computed_states_path = Path(f"../inputs/{dataset}_ongoing_states.csv")
        reachability_graph_path = Path(f"../inputs/{dataset}_reachability_graph.tgf")
        # Read preprocessed event log(s)
        remaining_cases = read_csv_log(remaining_cases_path, log_ids, sort=True)
        computed_states = pd.read_csv(computed_states_path)
        with open(reachability_graph_path, "r") as reachability_graph_file:
            reachability_graph = ReachabilityGraph.from_tgf_format(reachability_graph_file.read())
        # Go over each case ID
        iasr, ias, occ, mark3, mark5, mark7, mark9 = [], [], [], [], [], [], []
        for case_id, data in computed_states.groupby("case_id"):
            # Retrieve remaining activities of this case
            remaining_case = remaining_cases[remaining_cases[log_ids.case] == case_id]
            # Process techniques
            iasr += [evaluate_state_approximation(data, "IASR", reachability_graph, remaining_case)]
            ias += [evaluate_state_approximation(data, "IAS", reachability_graph, remaining_case)]
            occ += [evaluate_state_approximation(data, "OCC", reachability_graph, remaining_case)]
            mark3 += [evaluate_state_approximation(data, "marking-3", reachability_graph, remaining_case)]
            mark5 += [evaluate_state_approximation(data, "marking-5", reachability_graph, remaining_case)]
            mark7 += [evaluate_state_approximation(data, "marking-7", reachability_graph, remaining_case)]
            mark9 += [evaluate_state_approximation(data, "marking-9", reachability_graph, remaining_case)]
        # Print stats
        print(f"IASR: {sum(iasr) / len(iasr)}")
        print(f"IAS: {sum(ias) / len(ias)}")
        print(f"OCC: {sum(occ) / len(occ)}")
        print(f"mark-3: {sum(mark3) / len(mark3)}")
        print(f"mark-5: {sum(mark5) / len(mark5)}")
        print(f"mark-7: {sum(mark7) / len(mark7)}")
        print(f"mark-9: {sum(mark9) / len(mark9)}\n")


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


if __name__ == '__main__':
    evaluation_question_one()
