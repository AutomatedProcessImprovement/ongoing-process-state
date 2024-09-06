from pathlib import Path
from random import randrange
from typing import List

import pandas as pd
import pm4py
from pix_framework.io.event_log import DEFAULT_CSV_IDS, read_csv_log, DEFAULT_XES_IDS

log_ids = DEFAULT_CSV_IDS


def split_logs_into_ongoing_cases(datasets: List[str]):
    """
    Preprocess each event log to split their traces in the middle of their execution. Each event log is split
    into two event logs, one with the ongoing cases (events considered to be already executed), and another
    one with the remaining activities of each case (the events that were left out).
    """
    # For each dataset
    for dataset in datasets:
        # Instantiate paths
        event_log_path = Path(f"../inputs/real-life/{dataset}.csv.gz")
        # event_log_path = Path(f"../inputs/synthetic/{dataset}.csv.gz")
        ongoing_cases_csv = Path(f"../outputs/{dataset}_ongoing.csv.gz")
        ongoing_cases_xes = f"../outputs/{dataset}_ongoing.xes"
        remaining_cases_csv = Path(f"../outputs/{dataset}_remaining.csv.gz")
        # Read preprocessed event log(s)
        event_log = read_csv_log(event_log_path, log_ids, sort=True)
        # Create copy with ongoing cases and remaining activities
        ongoing_cases = pd.DataFrame(columns=event_log.columns)
        remaining_cases = pd.DataFrame(columns=event_log.columns)
        for trace_id, events in event_log.groupby(log_ids.case):
            num_to_keep = compute_number_of_events_to_retain(events)
            ongoing_events = events.head(num_to_keep)
            remaining_events = events.tail(len(events) - num_to_keep)
            assert len(ongoing_events) + len(remaining_events) == len(events)
            ongoing_cases = pd.concat([ongoing_cases, ongoing_events])
            remaining_cases = pd.concat([remaining_cases, remaining_events])
        # Output datasets
        export_as_csv(ongoing_cases, ongoing_cases_csv)
        export_as_xes(ongoing_cases, ongoing_cases_xes)
        export_as_csv(remaining_cases, remaining_cases_csv)


def compute_number_of_events_to_retain(events: pd.DataFrame) -> int:
    """
    Return the number of events from a trace to retain as executed ones. The remaining
    ones will be considered as future events.

    (left_padding=3, right_padding=0) for synthetic logs for the noise edits to be
    possible (REMOVE - SWAP requires at least 3 events to be performed).

    (left_padding=1, right_padding=1) for real-life logs because it would be trivial
    to estimate the state for an empty start (initial marking), and one remaining
    activity needed to evaluate the estimation (is next activity enabled?).
    """
    left_padding = 1
    right_padding = 1
    start = min(len(events), left_padding)
    stop = max(start, len(events) - right_padding)
    return randrange(start, stop + 1)  # randrange returns in [start, stop)


def export_as_csv(event_log: pd.DataFrame, file_path: Path):
    event_log.to_csv(file_path, index=False)


def export_as_xes(event_log: pd.DataFrame, file_path: str):
    event_log.rename(columns={
        log_ids.case: DEFAULT_XES_IDS.case,
        log_ids.activity: DEFAULT_XES_IDS.activity,
        log_ids.end_time: DEFAULT_XES_IDS.end_time,
        log_ids.resource: DEFAULT_XES_IDS.resource,
    }, inplace=True)
    event_log = pm4py.convert_to_event_log(event_log)
    pm4py.write_xes(event_log, file_path, parameters={"compress": True})


if __name__ == '__main__':
    split_logs_into_ongoing_cases([
        "BPIC_2012",
        "BPIC_2013_incidents",
        "BPIC_2014_Activity_log_for_incidents",
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
        "Sepsis_Cases",
    ])
    # split_logs_into_ongoing_cases([
    #     "synthetic_and_k3",
    #     "synthetic_and_k5",
    #     "synthetic_and_k10",
    #     "synthetic_and_kinf",
    #     "synthetic_xor_loop",
    #     "synthetic_xor_sequence",
    #     "synthetic_nondeterministic",
    # ])
