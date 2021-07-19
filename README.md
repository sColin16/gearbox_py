# Overview

Gearbox is a lightweight library intended to organize and unify the APIs of
common reinforcement learning tasks. Unlike Gym, it splits functionality into
different components. This means that rendering and environment logic are handled in
two separate objects. Also, it comes with built-in wrappers to handle common
tasks, providing first-class support for multi-agent environments, and partially
observed states. 

This makes Gearbox just as powerful as other environments like Gym, while being
much more extendable, and providing out-of-the-box standards for common
Reinforcement learning tasks, like multiple agents.

A few goals of Gearbox:
1. Lightweight. A base API that doesn't have too many bells and whistles
2. Modular. Every component defined in the API should have a single
    responsibility, and it should be easy to create new components with these
    responsibilities
3. Feature-rich. The base API will be used to create objects for common
    Reinforcement Learning use cases, that can be used out-of-the box with minimal
    modifications
4. Extendable. All features and components in Gearbox, as well as features or
    components provided by the community should be easy to modify and extend

# Objects

## States

A state is any object that represents the full state of the environment. It could be
as simple as an integer, or as complex as a map of a 3D world

## Observations

An observation is any object that represents an agents observation of the
environment. This may be identical to the state for some environments, and
a small subset of the state in others.

## Actions

An action is any object that represents an action taken on the environment

## AgentActions

An `AgentAction` is any object that represents the action submitted by an agent.
This may be different than the action, in cases such as multi-agent
environments, where the `Action` must also include an identifier for the agent
who took the action

## Rewards

A reward is a number representing the reward signal an agent receives from having taken an action. Note that for multi-agent environments the reward may be an object indicating the rewards for each agent

## Outcomes

An outcome is an object that contains a `state`, a `reward`, a boolean
indicating if the episode is complete (`done`), and an optional dictionary that
contains any additional information (`info`) about the step of the episode

## ObservedOutcome

An observed outcome is identical to an outcome, except that the `state` field is
replaced with an `observation` field. It may also contain additional fields to
provide agents with additional context

# Functions

## Engines 

An engine is a function that accepts a `state` and an `action`, and returns an
`outcome`. Thus, an engine defines the core logic of the environment.

Engines can be built in a variety of different ways. For example, to build a
custom engine, just implement a function with the correct signature:

```python
def nim_engine(state, action):
    new_state = state - action

    return Outcome(
        state = new_state, 
        reward = (1 if new_state == 0 else 0), 
        done = (True if new_state == 0 else 0),
        info = None
    )
```

To customize an existing engine, implement a function with the correct signature
that uses the existing engine:

```python
def custom_nim_engine(state, action):
    outcome = nim_engine(state, action)
    outcome['reward'] *= 100

    return outcome
```

To create a general-purpose wrapper for any number of engines, create a closure
that returns an engine:

```python
def make_reward_multiplier_wrapper(engine, multiplier):
    def reward_multiplier(state, action):
        outcome = engine(state, action)
        outcome['reward'] *= multiplier

        return outcome

    return reward_multiplier
```

As long as the end result is a function that accepts a `state` and `action`, and returns an `outcome`, it really doesn't matter how you create it.

## Observers

An observer is a function that accepts an `Outcome` and any additional context
arguments, and returns an `ObservedOutcome`. The observer is responsible for
creating partially observed states (if applicable), adding fields to the
`ObservedOutcome` (such as the initial state and action taken), and any other
customizations to the outcome returned by the engine, that are necessary before
the outcome is provided to an agent

For example:

```python
def simple_observer(outcome, initial_state, action):
    # Convert the 'state' field to an 'observed' field
    observed_outcome = ObservedOutcome.from_outcome(outcome)

    observed_outcome.initial_state = initial_state
    observed_outcome.action = action

    return observed_outcome
```

Similar to Engines, you can create these observers in many different ways

## ActionTransformer

An `ActionTransformer` is a function that accepts an `AgentAction` and
additional context arguments, and returns an `Action`. Just like an `Engine` or
an `Observer`, they can be freely created in many different ways

# Classes

Gearbox uses a few classes to simplify the API for stateful components

## Environment

An environment combines an engine and state, creating a particular instance of
an environment.

It is very simple to create and use an environment:

```python
my_env = Environment(my_engine, my_initial_state)
my_outcome = my_env.step(my_action)
```

It would also be possible to extend the environment class to create an
environment for a specific engine, with a specific initial state

## Observed Environment

An `ObservedEnvironment` is a specialized object for a set of a particular type
of action transformer and observer, as specified by the context arguments they
require. It is possible to still modify the behavior by wrapping the
`ActionTransfomer` or `Observer`

For example, the following is an `ObservedEnvironment` that leverages some of
the examples above

```python
class SimpleObservedEnv:
    def __init__(self, engine, initial_state, action_transformer, observer):
        self.env = Environment(engine, initial_state)
        self.action_transformer = action_transformer
        self.observer = observer

    def step(self, agent_action, player_num):
        action = self.action_transformer(agent_action, player_num)
        initial_state = self.env.get_state()

        outcome = self.env.step(action)

        observed_outcome = observer(outcome, initial_state, action)

        return observer_outcome
```

# All Together

## Manual Processing

```python
my_env = Environment(my_engine, my_initial_state)

while not outcome.done:
    agent_action = my_agent.get_action()
    action = my_action_transformer(agent_action, player_num)
    initial_state = mv_env.get_state()

    outcome = my_env.step(action)

    observed_outcome = simple_observer(outcome, initial_state, action)
    my_agent.deliver_outcome(observed_outcome)
```

## Observed Environment

```python
my_observed_env = SimpleObservedEnv(my_engine, initial_state, my_action_transformer, my_observer)

while not observed_outcome.done:
    agent_action = my_agent.get_action()

    observed_outcome = my_observed_env.step(action, player_num)

    my_agent.deliver_outcome(observed_outcome)
```

As you can notice, observed environments don't save too many lines of code, and
do constrain access to objects, such as the raw outcome, which may be useful in
many cases. For that reason, they are only recommended to be used in specialized
cases when a particular set of action transformers and observers are being used
repeatedly