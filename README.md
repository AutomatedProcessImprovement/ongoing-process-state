# Efficient State Computation of Process Ongoing Cases

Approach to, given a process model in BPMN formal, compute the state of ongoing cases in constant time.
The approach consists of, in design time, given a maximum size _n_, create an index that associates each
_n_-gram -- i.e., execution of _n_ consecutive activities -- with the state(s) they lead to in the process model.
Then, at runtime, the state of an ongoing process case can be computed in constant time by searching for the last _n_
executed activities in the index.
For example, for an ongoing case `A-B-F-T-W-S-G-T-D`, after building the 5-gram index, the state would be computed
by searching in the index with the sequence `[W, S, G, T, D]`.

This approach has been submitted as a publication to VLDB 2025 under the title "Efficient Online Computation of Business
Process State From Trace Prefixes via N-Gram Indexing", by David Chapela-Campa and Marlon Dumas.

## Requirements

- Python v3.9.5+
- PIP v23.0+
- Python dependencies: all packages listed in [
  _pyproject.toml_](https://github.com/AutomatedProcessImprovement/process-running-state/blob/main/pyproject.toml)

## Basic Usage

Given a process model in BPMN format, the code to build an _n_-gram index and compute the state given an _n_-gram prefix
is:

```Python
from pathlib import Path

from process_running_state.n_gram_index import NGramIndex
from process_running_state.utils import read_bpmn_model

# Read BPMN model
bpmn_model_path = Path("./inputs/synthetic/synthetic_and_k5.bpmn")
bpmn_model = read_bpmn_model(bpmn_model_path)
# Compute reachability graph
reachability_graph = bpmn_model.get_reachability_graph()
# Build n-gram index
n_gram_index = NGramIndex(reachability_graph, n_gram_size_limit=5)
n_gram_index.build()
# Compute the state of an ongoing case
n_gram = ["B", "E", "F", "C", "G"]
ongoing_state = n_gram_index.get_best_marking_state_for(n_gram)
# Compute the state of an ongoing case with less than N recorded events
n_gram = [NGramIndex.TRACE_START, "A", "B", "F"]
ongoing_state = n_gram_index.get_best_marking_state_for(n_gram)
```

## Evaluation Reproducibility

The scripts with a name starting with `vldb25_` under folder `tests/` contain the necessary code to reproduce the
evaluation presented in the publication.
Most of them are only necessary to preprocess the original datasets.
This data is already available in this [Zenodo repository](doi.org/10.5281/zenodo.11409897).
Unless you want to reproduce also this preprocessing, we advise you to download the content of the folder `inputs` from
there.

### Dependencies

The evaluation scripts depend on two versions of PM4PY:

1. To run the script `vldb25_compute_states.py` where the prefix-alignment technique is used, the requirement is a
   package with a PM4PY fork implemented by Daniel Schuster
   ([repo](https://github.com/fit-daniel-schuster/online_process_monitoring_using_incremental_state-space_expansion_an_exact_algorithm/)).
   Download the project from the corresponding repository and specify its path in the `pyproject.toml` file in the
   line `pm4py = {path = "../schuster-prefix-alignments"}`, then, run `poetry install`.
2. For all the other scripts, the used PM4PY version is 2.7.11.9. Uncomment the line `pm4py = "2.7.11.9"` in the file
   `pyproject.toml` and run `poetry install`.

### Synthetic Evaluation

1. Install the project with the PM4PY version specified in point 1 (see above).
2. Comment the lines in the `main()` function in `vldb25_compute_states.py` that run the state computation for real-life
   logs, leaving only the calls to function `compute_current_states()` for the synthetic datasets.
3. Run the script, obtaining the results with the computed states and runtimes (also the reachability graphs) for each  
   proposal in the folder `outputs`.
4. Reinstall the project with the PM4PY version specified in point 2 (see above).
5. Run the script `vldb25_compute_states_token_replay.py`, adding the token-based replay results to the previous result
   files.
6. Move these files to the folder `results`.
7. Run the script `vldb25_exact_state_accuracy.py`, obtaining the accuracy results in the folder `outputs`.

### Real-life Evaluation

1. Install the project with the PM4PY version specified in point 1 (see above).
2. Comment the lines in the `main()` function in `vldb25_compute_states.py` that run the state computation for synthetic
   logs, leaving only the calls to function `compute_current_states()` for the real-life datasets.
3. Run the script, obtaining the results with the computed states and runtimes for each proposal in the folder
   `outputs`.
4. Move this files to the folder `results`.
5. Run the script `vldb25_next_activity_accuracy.py`, obtaining the accuracy results in the folder `outputs`.
