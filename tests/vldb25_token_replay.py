from typing import List, Set, Optional

import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.petri_net.obj import PetriNet, Marking

from process_running_state.reachability_graph import ReachabilityGraph


def custom_replay_prefix_tbr(
        prefix: List[str],
        net: PetriNet,
        im: Marking,
        fm: Marking,
        activity_key: str = "concept:name"
) -> Marking:
    """
    Copy of pm4py.conformance.replay_prefix_tbr() adapted for this evaluation.
    """
    purpose_log = EventLog()
    trace = Trace()
    for act in prefix:
        trace.append(Event({activity_key: act}))
    purpose_log.append(trace)

    from pm4py.algo.conformance.tokenreplay.variants import token_replay
    parameters_tr = {
        token_replay.Parameters.CONSIDER_REMAINING_IN_FITNESS: False,
        token_replay.Parameters.TRY_TO_REACH_FINAL_MARKING_THROUGH_HIDDEN: False,
        token_replay.Parameters.STOP_IMMEDIATELY_UNFIT: False,  # Turn 'false' to continue with replay when unfit
        token_replay.Parameters.WALK_THROUGH_HIDDEN_TRANS: True,
        token_replay.Parameters.ACTIVITY_KEY: activity_key
    }
    res = token_replay.apply(purpose_log, net, im, fm, parameters=parameters_tr)[0]
    return res["reached_marking"]


places_to_flows = {
    "synthetic_and_k3": {
        ("p12", "p6"): {"Flow_0rajtx0"}
    },
    "synthetic_and_k5": {
        ("p17", "p7", "p8"): {"Flow_1mbefht"},
        ("p12", "p19"): {"Flow_0rajtx0"}
    },
    "synthetic_and_k10": {
        ("p13", "p18", "p19", "p7", "p8"): {"Flow_1mbefht"}
    },
    "synthetic_and_kinf": {
        ("XOR-loop-split", "p3"): {"Flow_1279d43", "Flow_1ujr1jr"},
        ("XOR-loop-split", "p4"): {"Flow_0qkv9uj", "Flow_1ujr1jr"},
        ("XOR-loop-split", "p5"): {"Flow_0jtbwl8", "Flow_1ujr1jr"},
    },
    "synthetic_xor_sequence": {},
    "synthetic_xor_loop": {
        ("XOR-join-1",): {"Flow_0a9co7f"}
    },
}


def translate_marking_to_state(
        marking: Marking,
        pnml_model: PetriNet,
        reachability_graph: ReachabilityGraph,
        dataset: str,
) -> Optional[Set[str]]:
    """
    Transform a marking from a Petri net model to its corresponding state (i.e., marking) in the given reachability
    graph. For this, it searches for the marking in the reachability graph that enables the same set of activities.

    Warning! only designed for the synthetic models. Unsure how it will work in the real-life ones.

    :param marking: marking to transform.
    :param pnml_model: Petri net of the corresponding marking.
    :param reachability_graph: reachability graph of the BPMN model to search for the equivalent state.
    :param dataset: name of the dataset for custom translations.
    :return: the state in the reachability graph corresponding to the given marking, if any.
    """
    equivalent_marking = None
    # Get transitions enabled in the Petri net by the given marking
    enabled_transitions = pm4py.analysis.get_enabled_transitions(pnml_model, marking)
    enabled_activities_pnml = {
        str(enabled_transition.label)
        for enabled_transition in enabled_transitions
    }
    # Search for a marking in the reachability graph that enables the same set of activities
    for state_id in reachability_graph.markings:
        # Get activities enabled by current marking
        enabled_activities_bpmn = {
            reachability_graph.edge_to_activity[edge_id]
            for edge_id in reachability_graph.outgoing_edges[state_id]
        }
        # If same activities, same marking
        if enabled_activities_bpmn == enabled_activities_pnml:
            equivalent_marking = reachability_graph.markings[state_id]
    # Try custom translation dict due to silent transitions
    if equivalent_marking is None:
        marking_key = tuple(sorted([place.properties['place_name_tag'] for place in marking]))
        equivalent_marking = places_to_flows[dataset].get(marking_key, None)
    # Return equivalent marking if found
    return equivalent_marking
