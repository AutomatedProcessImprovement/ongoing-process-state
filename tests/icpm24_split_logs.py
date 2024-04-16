from pathlib import Path

import pandas as pd
from pix_framework.io.event_log import DEFAULT_CSV_IDS, read_csv_log


def split_logs_into_ongoing_cases():
    """
    Preprocess each event log to split their traces in the middle of their execution. Each event log is split
    into two event logs, one with the ongoing cases (events considered to be already executed), and another
    one with the remaining activities of each case (the events that were left out).
    """
    # Instantiate datasets
    datasets = ["sepsis_cases"]
    log_ids = DEFAULT_CSV_IDS
    # For each dataset
    for dataset in datasets:
        # Instantiate paths
        event_log_path = Path(f"../inputs/{dataset}.csv.gz")
        ongoing_cases_csv = Path(f"../inputs/{dataset}_ongoing.csv.gz")
        ongoing_cases_xes = f"../inputs/{dataset}_ongoing.xes.gz"
        remaining_cases_csv = Path(f"../inputs/{dataset}_remaining.csv.gz")
        remaining_cases_xes = f"../inputs/{dataset}_remaining.xes.gz"
        # Read preprocessed event log(s)
        event_log = read_csv_log(event_log_path, log_ids, sort=True)
        # Create copy with ongoing cases and remaining activities
        ongoing_cases = pd.DataFrame(columns=event_log.columns)
        remaining_cases = pd.DataFrame(columns=event_log.columns)
        for trace_id, events in event_log.groupby(log_ids.case):
            num_to_keep = len(events) - 5 if len(events) > 5 else len(events)  # TODO improve
            ongoing_events = events.head(num_to_keep)
            remaining_events = events.tail(len(events) - num_to_keep)
            assert len(ongoing_events) + len(remaining_events) == len(events)
            ongoing_cases = pd.concat([ongoing_cases, ongoing_events])
            remaining_cases = pd.concat([remaining_cases, remaining_events])
        # Output dataset
        ongoing_cases.to_csv(ongoing_cases_csv, index=False)
        remaining_cases.to_csv(remaining_cases_csv, index=False)
        # dataframe = pm4py.format_dataframe(ongoing_cases, case_id=log_ids.case, activity_key=log_ids.activity,
        #                                   timestamp_key=log_ids.end_time)
        # event_log = pm4py.convert_to_event_log(dataframe)
        # pm4py.write_xes(event_log, ongoing_cases_xes)


if __name__ == '__main__':
    split_logs_into_ongoing_cases()
