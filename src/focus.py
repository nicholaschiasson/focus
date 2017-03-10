#!/usr/bin/env pypy2
from copy import deepcopy
import random

from config import *
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
        self.action = "Game start"
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
        ret = []
        possible_move_locations = []
        for i in range(len(self.state)):
            for j in range(len(self.state[i])):
                if self.state[i][j] == None or len(self.state[i][j]) < 1 or self.state[i][j][-1] != self.current_turn:
                    continue
                max_move_distance = len(self.state[i][j])
                for split in range (1, max_move_distance + 1):
                    for k in range(1, split + 1):
                        if i - k >= 0 and self.state[i - k][j] != None:
                            possible_move_locations.append(((i, j), (i - k, j), split))
                        if i + k < 8 and self.state[i + k][j] != None:
                            possible_move_locations.append(((i, j), (i + k, j), split))
                        if j - k >= 0 and self.state[i][j - k] != None:
                            possible_move_locations.append(((i, j), (i, j - k), split))
                        if j + k < 8 and self.state[i][j + k] != None:
                            possible_move_locations.append(((i, j), (i, j + k), split))
        for (i1, j1), (i2, j2), split in possible_move_locations:
            new_state = deepcopy(self)
            old_len = len(new_state.state[i1][j1])
            new_state.state[i2][j2] += new_state.state[i1][j1][old_len-split:]
            new_state.state[i1][j1] = new_state.state[i1][j1][:old_len-split]
            moved_len = len(new_state.state[i2][j2])
            if moved_len > 5:
                captured_pieces = new_state.state[i2][j2][:moved_len-5]
                new_state.state[i2][j2] = new_state.state[i2][j2][moved_len-5:]
                for p in captured_pieces:
                    if p != new_state.current_turn:
                        new_state.PLAYER_X_CAPTURES += 1 if new_state.current_turn == PLAYER_X else 0
                        new_state.PLAYER_O_CAPTURES += 1 if new_state.current_turn == PLAYER_O else 0
            new_state.action = "Move top " + str(split) + " piece" + ("s" if split != 1 else "") + " from ROW-COL" + str((i1+1, j1+1)) + " to ROW-COL" + str((i2+1, j2+1))
            new_state.advance_turn()
            ret.append(new_state)
        return ret
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

def most_control_heuristic(state):
    x_pieces, o_pieces = 0, 0
    for row in state.state:
        for col in row:
            if col != None and len(col) > 0:
                if col[-1] == PLAYER_X:
                    x_pieces += 1
                elif col[-1] == PLAYER_O:
                    o_pieces += 1
    if state.current_turn == PLAYER_X:
        return x_pieces - o_pieces + state.PLAYER_X_CAPTURES - state.PLAYER_O_CAPTURES
    else:
        return o_pieces - x_pieces + state.PLAYER_O_CAPTURES - state.PLAYER_X_CAPTURES

def highest_controlled_stacks(state):
    x_stacks, o_stacks = 0, 0
    for row in state.state:
        for col in row:
            if col != None:
                l = len(col)
                if l > 1:
                    if col[-1] == PLAYER_X:
                        x_stacks += l - 1
                    elif col[-1] == PLAYER_O:
                        o_stacks += l - 1
    if state.current_turn == PLAYER_X:
        return x_stacks - o_stacks + state.PLAYER_X_CAPTURES - state.PLAYER_O_CAPTURES
    else:
        return o_stacks - x_stacks + state.PLAYER_O_CAPTURES - state.PLAYER_X_CAPTURES

def main():
    random.seed()
    state = FocusState.new_game()
    winner = "Unable to determine winner?"
    turn_number = 1
    while True:
        print("Previous action: {}".format(state.action))
        print("Current turn: {}".format(turn_number))
        print("Current Player: {}".format(state.current_turn))
        print("Player X captures: {}".format(state.PLAYER_X_CAPTURES))
        print("Player O captures: {}".format(state.PLAYER_O_CAPTURES))
        print(state)
        print
        if len(state.get_adjacent_states()) < 1 or state.PLAYER_X_CAPTURES >= WIN_CONDITION_CAPTURE_LIMIT or state.PLAYER_O_CAPTURES >= WIN_CONDITION_CAPTURE_LIMIT:
            break
        turn_number += 1
        highest_state = (float("-inf"), state)
        for s in state.get_adjacent_states():
            v = 0
            if state.current_turn == PLAYER_X:
                v = alphabeta(s, (most_control_heuristic,), MIN_MAX_SEARCH_DEPTH-1)
            else:
                v = alphabeta(s, (highest_controlled_stacks,), MIN_MAX_SEARCH_DEPTH-1)
            if v >= highest_state[0]:
                highest_state = (v, s)
        state = highest_state[1]
    if len(state.get_adjacent_states()) < 1:
        print("Player {} is unable to make a valid move".format(state.current_turn))
        state.advance_turn()
        winner = "Player {}".format(state.current_turn)
    elif state.PLAYER_X_CAPTURES >= WIN_CONDITION_CAPTURE_LIMIT:
        print("Player {} has met the winning condition of capturing {} piece{}".format(PLAYER_X, WIN_CONDITION_CAPTURE_LIMIT, "s" if WIN_CONDITION_CAPTURE_LIMIT != 1 else ""))
        winner = "Player X"
    elif state.PLAYER_O_CAPTURES >= WIN_CONDITION_CAPTURE_LIMIT:
        print("Player {} has met the winning condition of capturing {} piece{}".format(PLAYER_O, WIN_CONDITION_CAPTURE_LIMIT, "s" if WIN_CONDITION_CAPTURE_LIMIT != 1 else ""))
        winner = "Player O"
    print("Winner: {}".format(winner))

if __name__ == "__main__":
    main()
