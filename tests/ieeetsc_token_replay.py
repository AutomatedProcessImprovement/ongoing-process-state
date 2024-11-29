from typing import List

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.petri_net.obj import PetriNet, Marking


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
