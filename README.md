# State Computation of Process Ongoing Cases

Technique to build, given the BPMN model of a process, a function that computes the marking state (current state of the
execution of the process) given the N last executed activities (n-gram) in a running case.

### Dependencies

All dependencies are managed by Poetry and can be found in `pyproject.toml`.

In order to run the baseline prefix-alignment technique to compare its performance w.r.t. the proposed method, a local
dependency is needed: `pm4py = {path = "../schuster-prefix-alignments"}`. This package corresponds to the PM4PY fork
implemented by Daniel
Schuster ([repo](https://github.com/fit-daniel-schuster/online_process_monitoring_using_incremental_state-space_expansion_an_exact_algorithm/)).
Download the project from the corresponding repository and specify its path in the `pyproject.toml` file.

