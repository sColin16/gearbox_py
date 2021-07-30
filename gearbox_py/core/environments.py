"""Defines the core data classes and types for Gearbox environments."""

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Union


@dataclass
class Action:
    """Base class that all actions are suggested to extend."""


@dataclass
class State:
    """Base class that all states are suggested to extend."""


@dataclass
class Outcome:
    """Ground-truth outcome returned by engines.

    Attributes:
        state: Ground-truth state of the environment.
        reward: Reward for each agent.
        done: Whether or not the episode is complete.
        info: Information not captured by other fields.
    """

    state: State
    reward: Union[int, Iterable[int]]
    done: bool
    info: Any


Engine = Callable[[State, Action], Outcome]


class InvalidActionException(Exception):
    """Exception engines are suggested to raise if an action is invalid."""


@dataclass
class Environment:
    """Stateful wrapper for engines that persists the state.

    Attributes:
        state: State of the environment persisted after each step.
        engine: Engine defining the environment logic.
    """

    state: State
    engine: Engine

    def step(self, action: Action) -> Outcome:
        """Advance the environment a step forward with the provided action.

        Args:
            action: Action to take on the environment

        Returns:
            Outcome defining result of the action on the environment.
        """

        outcome = self.engine(self.state, action)
        self.state = outcome.state

        return outcome
