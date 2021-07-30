"""Defines the default observers included with Gearbox."""

from gearbox_py.core.environments import Action, Outcome
from gearbox_py.core.observers import Observer, ObservedOutcome, \
    ObservedOutcomeWithAction


def full_observer(outcome: Outcome) -> ObservedOutcome:
    """Defines an observer that observes the entire state."""

    return ObservedOutcome.from_outcome(outcome)


def make_action_observer(nested_observer: Observer) -> Observer:
    def action_observer(outcome: Outcome, action: Action, *args, **kwargs) \
            -> ObservedOutcome:
        intermediary = nested_observer(outcome, *args, **kwargs)

        return ObservedOutcomeWithAction \
            .from_observed_outcome(intermediary, action)

    return action_observer


action_observer = make_action_observer(full_observer)
