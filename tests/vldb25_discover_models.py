import os
import platform
import subprocess
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pm4py
from pm4py.convert import convert_to_petri_net
from pm4py.discovery import discover_bpmn_inductive
from pm4py.read import read_xes
from pm4py.write import write_bpmn, write_pnml

split_miner_jar_path: Path = Path(__file__).parent.parent / "split-miner/split-miner-1.7.1-all.jar"
bpmn_layout_jar_path: Path = Path(__file__).parent.parent / "split-miner/bpmn-layout-1.0.6-jar-with-dependencies.jar"


def discover_with_split_miner(datasets: List[str]):
    """
    Discover the process model with Split Miner.
    """
    # For each dataset
    for dataset in datasets:
        print(f"\n\n----- Processing dataset: {dataset} -----\n")
        # Instantiate paths
        event_log_path = Path(f"../inputs/real-life/{dataset}.xes.gz")
        output_bpmn_path = f"../outputs/{dataset}_SM.bpmn"
        output_petri_path = f"../outputs/{dataset}_SM.pnml"
        # Discover with Split Miner
        args, split_miner_path, input_log_path, model_output_path = _prepare_split_miner_params(
            split_miner_jar_path, event_log_path, Path(output_bpmn_path), strip_output_suffix=False
        )
        args += [
            "-jar", split_miner_path,
            "--logPath", input_log_path,
            "--outputPath", model_output_path,
            "--eta", "0.5",
            "--epsilon", "0.3",
            "--parallelismFirst",
            "--replaceIORs",
        ]
        # args += ["--parallelismFirst"]
        # args += ["--replaceIORs"]
        # args += ["--removeLoopActivityMarkers"]
        print(f"Executing command: {args}")
        execute_external_command(args)
        # Read with PM4PY
        bpmn_model = pm4py.read_bpmn(output_bpmn_path)
        os.remove(output_bpmn_path)
        write_bpmn(bpmn_model, output_bpmn_path)
        petri_net_model, initial_marking, final_marking = convert_to_petri_net(bpmn_model)
        write_pnml(petri_net_model, initial_marking, final_marking, output_petri_path)


def discover_with_inductive_miner(datasets: List[str]):
    """
    Discover the process model with Inductive Miner.
    """
    # For each dataset
    for dataset in datasets:
        print(f"\n\n----- Processing dataset: {dataset} -----\n")
        # Instantiate paths
        event_log_path = f"../inputs/real-life/{dataset}.xes.gz"
        # Read event log
        event_log = read_xes(event_log_path)
        for threshold in [10, 20, 50]:
            print(f"--- Discovering with Inductive Miner ({threshold}) ---")
            # Create path
            output_bpmn_path = f"../outputs/{dataset}_IMf{threshold}.bpmn"
            output_petri_path = f"../outputs/{dataset}_IMf{threshold}.pnml"
            # Discover with Inductive Miner
            print("Discovering...")
            bpmn_model = discover_bpmn_inductive(event_log, noise_threshold=threshold / 100, multi_processing=True)
            print("Exporting to file...")
            write_bpmn(bpmn_model, output_bpmn_path)
            print("Translating to Petri net...")
            petri_net_model, initial_marking, final_marking = convert_to_petri_net(bpmn_model)
            print("Exporting to file...")
            write_pnml(petri_net_model, initial_marking, final_marking, output_petri_path)


def measure_fitness_models(datasets: List[str]):
    """
    Discover the process model with Inductive Miner.
    """
    # For each dataset
    for dataset in datasets:
        print(f"\n\n----- Processing dataset: {dataset} -----\n")
        # Instantiate paths
        event_log_path = f"../inputs/real-life/{dataset}.xes.gz"
        # Read event log
        event_log = read_xes(event_log_path)
        for threshold in [10, 20, 50]:
            print(f"\n--- Assessing fitness for Inductive Miner ({threshold}) ---")
            # Create path
            petri_path = f"../inputs/real-life/{dataset}_IMf{threshold}.pnml"
            # Discover with Inductive Miner
            print("Reading Petri net...")
            petri_net_model, initial_marking, final_marking = pm4py.read_pnml(petri_path)
            and_splits = [
                len(transition.out_arcs)
                for transition in petri_net_model.transitions
                if len(transition.out_arcs) > 1
            ]
            print("Assessing fitness...")
            fitness = pm4py.fitness_alignments(event_log, petri_net_model, initial_marking, final_marking)
            print(f"Fitness: {fitness}")
            print(f"ANDs: {len(and_splits)} ({np.mean(and_splits)})")


def add_bpmn_diagram_to_model(bpmn_model_path: Path):
    """
    Add BPMN diagram to the control flow of the existing BPMN model using the hierarchical layout algorithm.
    This function overwrites the existing BPMN model file.

    :param bpmn_model_path:
    :return: None
    """
    args = ["java", "-jar", '"' + str(bpmn_layout_jar_path) + '"', '"' + str(bpmn_model_path) + '"']
    print(f"Executing command: {args}")
    execute_external_command(args)


def execute_external_command(args):
    if is_windows():
        subprocess.call(" ".join(args))
    else:
        subprocess.call(args)


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def _prepare_split_miner_params(
        split_miner: Path,
        log_path: Path,
        output_model_path: Path,
        strip_output_suffix: bool = True,
        headless: bool = True,
) -> Tuple[List[str], str, str, str]:
    if is_windows():
        # Windows: ';' as separator and escape string with '"'
        args = ["java"]
        if headless:
            args += ["-Djava.awt.headless=true"]
        split_miner_path = '"' + str(split_miner) + '"'
        input_log_path = '"' + str(log_path) + '"'
        if strip_output_suffix:
            model_output_path = '"' + str(output_model_path.with_suffix("")) + '"'
        else:
            if ".bpmn" not in str(output_model_path):
                model_output_path = str(output_model_path.with_suffix(".bpmn"))
            else:
                model_output_path = '"' + str(output_model_path) + '"'
    else:
        # Linux: ':' as separator and add memory specs
        args = ["java", "-Xmx2G", "-Xms1024M"]
        if headless:
            args += ["-Djava.awt.headless=true"]
        split_miner_path = str(split_miner)
        input_log_path = str(log_path)
        if strip_output_suffix:
            model_output_path = str(output_model_path.with_suffix(""))
        else:
            if ".bpmn" not in str(output_model_path):
                model_output_path = str(output_model_path.with_suffix(".bpmn"))
            else:
                model_output_path = str(output_model_path)

    return args, split_miner_path, input_log_path, model_output_path


if __name__ == '__main__':
    discover_with_inductive_miner([
        "BPIC_2012",
        "BPIC_2013_incidents",
        "BPIC_2014_Activity_log_for_incidents",
        # "BPIC_2015_1",
        # "BPIC_2015_2",
        # "BPIC_2015_3",
        # "BPIC_2015_4",
        # "BPIC_2015_5",
        "BPIC_2017",
        "BPIC_2020_DomesticDeclarations",
        "BPIC_2020_InternationalDeclarations",
        "BPIC_2020_PrepaidTravelCost",
        "BPIC_2020_RequestForPayment",
        "BPIC_2020_TravelPermitData",
        "Sepsis_Cases",
        "BPIC_2018",
        "BPIC_2019",
    ])
