"""Defines the base Observer data classes and types."""

from dataclasses import dataclass
from typing import Any, Union, Iterable, Callable

from gearbox_py.core.environments import Action, Outcome


@dataclass
class Observation:
    """The base class that all observations are suggested to extend."""

    @classmethod
    def from_state(cls, state):
        """Convert a state to an identical observation instance
        for cases when states and observations are identical.
        """

        return cls(vars(state))


@dataclass
class ObservedOutcome:
    """The base outcome returned by observers.

    Attributes:
        observation: Observation(s) of the state available to agents
        reward: Reward for each agent
        done: Whether or not the episode is complete
        info: Information not captured by other fields
    """

    observation: Observation
    reward: Union[int, Iterable[int]]
    done: bool
    info: Any

    @classmethod
    def from_outcome(cls, outcome: Outcome):
        """Create a new ObservedOutcome instance from an Outcome,
        converting the state field to the observation field.
        """

        dict_repr = vars(outcome)
        dict_repr['observation'] = dict_repr['state']
        dict_repr.pop('state')

        return cls(**dict_repr)


@dataclass
class ObservedOutcomeWithAction(ObservedOutcome):
    """An extension of the ObservedOutcome class that stores an action in addition.

    Attributes:
        action: The action that was taken to result in the provided outcome
    """

    action: Action

    @classmethod
    def from_outcome(cls, outcome, action):
        """Create an ObservedOutcomeWithAction from an Outcome."""

        return cls.from_observed_outcome(super().from_outcome(outcome), action)

    @classmethod
    def from_observed_outcome(cls, observed_outcome, action):
        """Create an ObservedOutcomeWithAction from an ObservedOutcome."""

        return cls(**vars(observed_outcome), action=action)


Observer = Callable[[Outcome], ObservedOutcome]
