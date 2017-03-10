#!/usr/bin/env pypy2 -B
import random

import config
from nai.search.state import AISearchState
from nai.search.intelligent import alphabeta

EMPTY_SPACE = "-"
PLAYER_X      = "X"
PLAYER_O      = "O"

class FocusState(AISearchState):
    def __init__(self, state_string):
        state_split = state_string.split("\n")
        if len(state_split) != 8:
            raise ValueError("focus board must have height dimension of 8")
        self.current_turn = PLAYER_X
        self.PLAYER_X_CAPTURES = 0
        self.PLAYER_O_CAPTURES = 0
        self.state = []
        skip_indices = set([(0, 0), (0, 1), (0, 6), (0, 7), (1, 0), (1, 7), (6, 0), (6, 7), (7, 0), (7, 1), (7, 6), (7, 7)])
        for i, s in enumerate(state_split):
            s_trimmed = s.strip()
            if len(s_trimmed) != 8:
                raise ValueError("focus board row {} must have width dimension of 8".format(i + 1))
            self.state.append([])
            for j, c in enumerate(s_trimmed):
                if (i, j) in skip_indices:
                    self.state[i].append(None)
                else:
                    self.state[i].append([])
                    if c != EMPTY_SPACE:
                        self.state[i][j].append(c)
    @classmethod
    def new_game(cls):
        '''Generates new shuffled game state'''
        remaining_x, remaining_o = 18, 18
        state_str = ""
        for i in range(8):
            if i > 0:
                state_str += "\n"
            for j in range(8):
                if i < 1 or i > 6 or j < 1 or j > 6:
                    state_str += EMPTY_SPACE
                else:
                    if remaining_x > 0 and remaining_o > 0:
                        if random.getrandbits(1) == 0:
                            state_str += PLAYER_X
                            remaining_x -= 1
                        else:
                            state_str += PLAYER_O
                            remaining_o -= 1
                    elif remaining_x > 0:
                        state_str += PLAYER_X
                        remaining_x -= 1
                    elif remaining_o > 0:
                        state_str += PLAYER_O
                        remaining_o -= 1
                    else:
                        state_str += EMPTY_SPACE
        return cls(state_str)
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.state == other.state
        return NotImplemented
    def __hash__(self):
        return hash(str(self))
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented
    def get_adjacent_states(self):
        return []
    def get_goal(self):
        return self
    def get_transition_cost(self, other):
        if isinstance(other, self.__class__):
            return 1
        return NotImplemented
    def __str__(self):
        ret = ""
        for i, row in enumerate(self.state):
            if i > 0:
                ret += "\n"
            for j, col in enumerate(row):
                if j > 0:
                    ret += " "
                if col == None:
                    ret += " "
                else:
                    if len(col) > 0:
                        ret += col[-1]
                    else:
                        ret += EMPTY_SPACE
        return ret
    def advance_turn(self):
        self.current_turn = PLAYER_X if self.current_turn == PLAYER_O else PLAYER_O

def main():
    random.seed()
    state = FocusState.new_game()
    winner = "Unable to determine winner?"
    while True:
        print("Current turn: {}".format(state.current_turn))
        print("Player X captures: {}".format(state.PLAYER_X_CAPTURES))
        print("Player O captures: {}".format(state.PLAYER_O_CAPTURES))
        print(state)
        print
        if len(state.get_adjacent_states()) < 1 or state.PLAYER_X_CAPTURES >= WIN_CONDITION_CAPTURE_LIMIT or state.PLAYER_O_CAPTURES >= WIN_CONDITION_CAPTURE_LIMIT:
            break
        state = alphabeta(state, (), MIN_MAX_SEARCH_DEPTH)
    if len(state.get_adjacent_states()) < 1:
        print("Player {} is unable to make a valid move".format(state.current_turn))
        state.advance_turn()
        winner = "Player {}".format(state.current_turn)
    elif state.PLAYER_X_CAPTURES >= WIN_CONDITION_CAPTURE_LIMIT:
        print("Player {} has met the win condition of capturing {} pieces".format(PLAYER_X, WIN_CONDITION_CAPTURE_LIMIT))
        winner = "Player X"
    elif state.PLAYER_O_CAPTURES >= WIN_CONDITION_CAPTURE_LIMIT:
        print("Player {} has met the win condition of capturing {} pieces".format(PLAYER_O, WIN_CONDITION_CAPTURE_LIMIT))
        winner = "Player O"
    print("Winner: {}".format(winner))

if __name__ == "__main__":
    main()
