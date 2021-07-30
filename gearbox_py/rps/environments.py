from dataclasses import dataclass
import copy
import random

from gearbox_py.core.environments import Outcome, InvalidActionException, \
    Environment


@dataclass
class RPS_Action:
    p1: str
    p2: str


@dataclass
class RPS_state:
    best_of: int
    p1_win: int = 0
    p2_win: int = 0


def rps_engine(state, action):
    values = {
        'rock': 1,
        'paper': 2,
        'scissors': 4
    }

    p1 = values.get(action.p1)
    p2 = values.get(action.p2)

    if not p1:
        raise InvalidActionException(f'{action.p1} is not a valid action. Valid actions are "rock" "paper" and "scissors"')

    if not p2:
        raise InvalidActionException(f'{action.p2} is not a valid action. Valid actions are "rock" "paper" and "scissors"')

    if p1 + p2 == values['rock'] + values['paper']:
        winner = 1 if p1 == values['paper'] else 2

    elif p1 + p2 == values['paper'] + values['scissors']:
        winner = 1 if p1 == values['scissors'] else 2

    elif p1 + p2 == values['scissors'] + values['rock']:
        winner = 1 if p1 == values['rock'] else 2

    elif p1 == p2:
        winner = 0


    if winner == 0:
        reward = [0, 0]
    
    elif winner == 1:
        reward = [1, -1]

    elif winner == 2:
        reward = [-1, 1]


    return Outcome(None, reward, True, {'winner': winner})

# Wraps the rps engine to create a best-of-x game
def multi_rps_engine(state, action):
    outcome = rps_engine(None, action)

    new_state = copy.deepcopy(state)
    new_reward = [0, 0]
    new_done = False
    new_info = {'winner': 0, 'round_winner': outcome.info['winner']}

    if outcome.info['winner'] == 1:
        new_state.p1_win += 1

    elif outcome.info['winner'] == 2:
        new_state.p2_win += 1

    if (new_state.p1_win > (state.best_of // 2)) or (new_state.p2_win > (state.best_of // 2)):
        new_reward = outcome.reward
        new_info['winner'] = outcome.info['winner']
        new_done = True

    elif new_state.p1_win + new_state.p2_win == state.best_of:
        new_done = True

    return Outcome(new_state, new_reward, new_done, new_info)

def main(num):
    env = Environment(RPS_state(num), multi_rps_engine)

    print(f'You\'re playing best of {env.state.best_of}')

    while True:
        human_action = input('ACTION> ')
        computer_action = random.choice(['rock', 'paper', 'scissors'])

        outcome = env.step(RPS_Action(human_action, computer_action))

        print(f'You threw {human_action}')
        print(f'The computer threw {computer_action}')

        if outcome.info['round_winner'] == 1:
            print('You win!')

        elif outcome.info['round_winner'] == 2:
            print('You lose!')

        else:
            print('It\'s a draw!')

        print(f'You: {outcome.state.p1_win} | Computer: {outcome.state.p2_win}')

        print()

        if outcome.done:
            break

    if outcome.info['winner'] == 1:
        print('You win it all!')

    elif outcome.info['winner'] == 2:
        print('You lost it all!')

    else:
        print('It\'s a draw!')
