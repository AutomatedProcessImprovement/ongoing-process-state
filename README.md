# Efficient State Computation of Process Ongoing Cases

Approach to, given a process model in BPMN formal, compute the state of ongoing cases in constant time.
The approach consists of, in design time, given a maximum size _n_, create an index that associates each
_n_-gram -- i.e., execution of _n_ consecutive activities -- with the state(s) they lead to in the process model.
Then, at runtime, the state of an ongoing process case can be computed in constant time by searching for the last _n_
executed activities in the index.
For example, for an ongoing case `A-B-F-T-W-S-G-T-D`, after building the 5-gram index, the state would be computed
by searching in the index with the sequence `[W, S, G, T, D]`.

This approach has been submitted as a publication to ICPM 2024 under the title "Efficient State Computation for Log
Animation and Short-Term Simulation Using N-Gram Indexing", by David Chapela-Campa and Marlon Dumas.

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

The scripts with a name starting with `icpm24_` under folder `tests/` contain the necessary code to reproduce the
evaluation presented in the publication.
Most of them are only necessary to preprocess the original datasets.
This data is already available in this [Zenodo repository](doi.org/10.5281/zenodo.11409897).
Unless you want to reproduce also this preprocessing, we advise you to download the content of the folder `inputs` from
there.

### Dependencies

The evaluation scripts depend on two versions of PM4PY.

1. To discover the process models and measure their fitness, uncomment the line `pm4py = "2.7.11.9"` in the
   file `pyproject.toml` and run `poetry install`. This is unnecessary if you downloaded the input files from Zenodo (
   see above).
2. For the other scripts where the prefix-alignment technique is used, the requirement is a package with a PM4PY fork
   implemented by Daniel
   Schuster ([repo](https://github.com/fit-daniel-schuster/online_process_monitoring_using_incremental_state-space_expansion_an_exact_algorithm/)).
   Download the project from the corresponding repository and specify its path in the `pyproject.toml` file in the
   line `pm4py = {path = "../schuster-prefix-alignments"}`, then, run `poetry install`.

### Synthetic Evaluation

1. Adapt the log routes in the file `icpm24_compute_states.py` as said in the comments, and the IDs passed by the `main`
   function to `compute_current_states()` so the executed datasets are the synthetic ones.
2. Run the script, obtaining the results with the computed states and runtimes for each proposal in the
   folder `outputs`.
3. Move this files to the folder `results`.
4. Run the script `icpm24_exact_state_accuracy.py`, obtaining the accuracy results in the folder `outputs`.

### Real-life Evaluation

1. Adapt the log routes in the file `icpm24_compute_states.py` as said in the comments, and the IDs passed by the `main`
   function to `compute_current_states()` so the executed datasets are the real-life ones.
2. Run the script, obtaining the results with the computed states and runtimes for each proposal in the
   folder `outputs`.
3. Move this files to the folder `results`.
4. Run the script `icpm24_next_activity_accuracy.py`, obtaining the accuracy results in the folder `outputs`.

