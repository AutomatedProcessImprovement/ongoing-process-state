import ast
from pathlib import Path
from typing import List

import pandas as pd
from pix_framework.io.event_log import read_csv_log, DEFAULT_CSV_IDS

from process_running_state.petri_net import PetriNet
from process_running_state.utils import read_petri_net

log_ids = DEFAULT_CSV_IDS


def next_activity_accuracy(
        datasets: List[str],
        noise_lvl: str = "",
        discovery_extension: str = ""
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
            else:
                computed_states_path = Path(f"../results/synthetic/{dataset}_{noise_lvl}_ongoing_states.csv")
        else:
            # Real-life log
            petri_net_path = Path(f"../inputs/real-life/{dataset}{discovery_extension}.pnml")
            remaining_cases_path = Path(f"../inputs/real-life/split/{dataset}_remaining.csv.gz")
            computed_states_path = Path(f"../results/real-life/{dataset}{discovery_extension}_ongoing_states.csv")
            output_file_path = Path(f"../outputs/real_life_accuracy.csv")
        # Create results file if it doesn't exist
        if not output_file_path.exists():
            with open(output_file_path, "w") as output_file:
                output_file.write("dataset,discovery_algorithm,technique,abs_positives,rel_positives\n")
        # Read preprocessed event log(s) and Petri net
        remaining_cases = read_csv_log(remaining_cases_path, log_ids, sort=True)
        computed_states = pd.read_csv(computed_states_path)
        petri_net = read_petri_net(petri_net_path)
        # Go over each case ID
        evaluated_techniques = computed_states["technique"].unique()
        results = {technique: [] for technique in evaluated_techniques}
        for case_id, data in computed_states.groupby("case_id"):
            # Retrieve remaining activities of this case
            remaining_case = remaining_cases[remaining_cases[log_ids.case] == case_id]
            # Process techniques
            for technique in evaluated_techniques:
                results[technique] += [
                    evaluate_state_approximation(data, results[technique], remaining_case, petri_net)
                ]
        # Write stats to file
        with open(output_file_path, "a") as output_file:
            for technique in evaluated_techniques:
                total_accuracy = sum(results[technique])
                partial_accuracy = sum(results[technique]) / len(results[technique])
                output_file.write(f"{dataset},{discovery_extension},{technique},{total_accuracy},{partial_accuracy}\n")


def evaluate_state_approximation(
        data: pd.DataFrame,
        technique: str,
        remaining_case: pd.DataFrame,
        petri_net: PetriNet
) -> bool:
    # Retrieve next activity
    if len(remaining_case) > 0:
        next_activity = remaining_case.head(1)[log_ids.activity].iloc[0]
    else:
        next_activity = None
    # Retrieve estimated marking
    results_technique = data[data["technique"] == technique]
    if len(results_technique) == 1:
        estimated_state = results_technique["state"].iloc[0]
        if estimated_state.startswith("Error!"):
            is_enabled = False
        else:
            marking = ast.literal_eval(estimated_state)
            # Check if the next activity is enabled
            enabled_activities = [enabled_activity for enabled_activity, _ in petri_net.advance_full_marking(marking)]
            is_enabled = next_activity in enabled_activities
    else:
        is_enabled = False
    # Return if the next activity is enabled or not
    return is_enabled


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
