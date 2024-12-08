import ast
from pathlib import Path
from typing import List, Tuple, Set

import pandas as pd
from pix_framework.io.event_log import read_csv_log, DEFAULT_CSV_IDS

from process_running_state.petri_net import PetriNet
from process_running_state.reachability_graph import ReachabilityGraph
from process_running_state.utils import read_petri_net

log_ids = DEFAULT_CSV_IDS
all_techniques = {
    "3-gram-index", "4-gram-index", "5-gram-index",
    "6-gram-index", "10-gram-index", "IAS", "IASR",
    "OCC", "token-replay"
}


def next_activity_accuracy(
        datasets: List[str],
        noise_lvl: str = "",
        discovery_extension: str = "",
):
    # For each dataset
    for dataset in datasets:
        print(f"\n--- Dataset: {dataset} ---\n")
        # Instantiate paths
        if "synthetic" in dataset:
            # Synthetic dataset
            petri_net_path = Path(f"../inputs/synthetic/{dataset}.pnml")
            remaining_cases_path = Path(f"../inputs/synthetic/split/{dataset}_remaining.csv.gz")
            output_file_path = Path(f"../outputs/synthetic_accuracy.csv")
            if noise_lvl == "":
                computed_states_path = Path(f"../results/synthetic/{dataset}_ongoing_states.csv")
                reach_graph_path = Path(f"../results/synthetic/{dataset}_reachability_graph.tgf")
            else:
                computed_states_path = Path(f"../results/synthetic/{dataset}_{noise_lvl}_ongoing_states.csv")
                reach_graph_path = Path(f"../results/synthetic/{dataset}_{noise_lvl}_reachability_graph.tgf")
        else:
            # Real-life log
            petri_net_path = Path(f"../inputs/real-life/{dataset}{discovery_extension}.pnml")
            remaining_cases_path = Path(f"../inputs/real-life/split/{dataset}_remaining.csv.gz")
            computed_states_path = Path(f"../results/real-life/{dataset}{discovery_extension}_ongoing_states.csv")
            reach_graph_path = Path(f"../results/real-life/{dataset}{discovery_extension}_reachability_graph.tgf")
            output_file_path = Path(f"../outputs/real_life_accuracy.csv")
        # Create results file if it doesn't exist
        if not output_file_path.exists():
            with open(output_file_path, "w") as output_file:
                output_file.write("dataset,discovery_algorithm,noise_lvl,technique,"
                                  "num_positives,num_reachable_positives,num_unreachable\n")
        # Read preprocessed event log(s), Petri net, and reachability graph
        remaining_cases = read_csv_log(remaining_cases_path, log_ids, sort=True)
        computed_states = pd.read_csv(computed_states_path)
        num_cases = len(remaining_cases["case_id"].unique())
        petri_net = read_petri_net(petri_net_path)
        with open(reach_graph_path, 'r') as reachability_graph_file:
            reachability_graph = ReachabilityGraph.from_tgf_format(reachability_graph_file.read())
        # Compute reachable markings and initialize results
        print("Computing all reachable markings!")
        reachable_markings = petri_net.compute_reachable_markings()
        petri_net.repair_mixed_decision_points()  # Repair for the "advance_full_marking" operation to work properly
        evaluated_techniques = set(computed_states["technique"].unique()) & all_techniques
        results = {technique: [] for technique in evaluated_techniques}
        # Go over each case ID
        print("Computing accuracy!")
        i = 0
        for case_id, data in computed_states.groupby("case_id"):
            # Retrieve remaining activities of this case
            remaining_case = remaining_cases[remaining_cases[log_ids.case] == case_id]
            # Process techniques
            for technique in evaluated_techniques:
                results[technique] += [
                    evaluate_state_approximation(
                        data,
                        technique,
                        remaining_case,
                        petri_net,
                        reachability_graph,
                        reachable_markings
                    )
                ]
            # Report progress
            if i % 500 == 0:
                print(f"\tComputed {i}/{num_cases}")
            i += 1
        # Write stats to file
        with open(output_file_path, "a") as output_file:
            for technique in evaluated_techniques:
                abs_positives = sum([enabled for enabled, _ in results[technique]])
                abs_reachable_positives = sum([enabled and reachable for enabled, reachable in results[technique]])
                abs_unreachable = sum([not reachable for _, reachable in results[technique]])
                output_file.write(
                    f"{dataset},{discovery_extension},{noise_lvl},{technique},"
                    f"{abs_positives},{abs_reachable_positives},{abs_unreachable}\n"
                )


def evaluate_state_approximation(
        data: pd.DataFrame,
        technique: str,
        remaining_case: pd.DataFrame,
        petri_net: PetriNet,
        reachability_graph: ReachabilityGraph,
        reachable_markings: Set[Tuple[str]],
) -> Tuple[bool, bool]:
    # Retrieve next activity
    if len(remaining_case) > 0:
        next_activity = remaining_case.head(1)[log_ids.activity].iloc[0]
    else:
        next_activity = None
    # Retrieve estimated marking
    results_technique = data[data["technique"] == technique]
    if len(results_technique) == 1:
        estimated_state = results_technique["marking"].iloc[0]
        if estimated_state.startswith("Error!"):
            is_enabled = False
            is_reachable = False
        else:
            # Marking retrieved, transform to set
            marking = ast.literal_eval(estimated_state)
            marking_key = tuple(sorted(marking))
            is_reachable = marking_key in reachable_markings
            if next_activity is None:
                # End of trace, check marking is final
                is_enabled = petri_net.is_final_marking(marking)
            else:
                # Retrieve enabled activities
                if marking_key in reachability_graph.marking_to_key:
                    # Marking exists in reachability graph, retrieve outgoing edges (labels)
                    marking_id = reachability_graph.marking_to_key[marking_key]
                    enabled_activities = [
                        reachability_graph.edge_to_activity[edge_id]
                        for edge_id in reachability_graph.outgoing_edges[marking_id]
                    ]
                else:
                    # Compute "advance full marking" in petri net to reach all enabled activities from this marking
                    enabled_activities = [
                        petri_net.id_to_transition[enabled_activity].name
                        for enabled_activity, _ in petri_net.advance_full_marking(marking)
                    ]
                # Check if next activity is enabled
                is_enabled = next_activity in enabled_activities
    else:
        is_enabled = False
        is_reachable = False
    # Return if the next activity is enabled or not
    return is_enabled, is_reachable


if __name__ == '__main__':
    # Process results
    next_activity_accuracy([
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
    next_activity_accuracy([
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
    next_activity_accuracy([
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
    next_activity_accuracy([
        "synthetic_and_k3",
        "synthetic_and_k5",
        "synthetic_and_k10",
        "synthetic_and_kinf",
        "synthetic_xor_sequence",
        "synthetic_xor_loop",
        "synthetic_nondeterministic",
    ])
    next_activity_accuracy([
        "synthetic_and_k3",
        "synthetic_and_k5",
        "synthetic_and_k10",
        "synthetic_and_kinf",
        "synthetic_xor_sequence",
        "synthetic_xor_loop",
        "synthetic_nondeterministic",
    ], noise_lvl="noise_1")
    next_activity_accuracy([
        "synthetic_and_k3",
        "synthetic_and_k5",
        "synthetic_and_k10",
        "synthetic_and_kinf",
        "synthetic_xor_sequence",
        "synthetic_xor_loop",
        "synthetic_nondeterministic",
    ], noise_lvl="noise_2")
    next_activity_accuracy([
        "synthetic_and_k3",
        "synthetic_and_k5",
        "synthetic_and_k10",
        "synthetic_and_kinf",
        "synthetic_xor_sequence",
        "synthetic_xor_loop",
        "synthetic_nondeterministic",
    ], noise_lvl="noise_3")
