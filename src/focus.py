#!/usr/bin/env pypy2 -B
import config
from nai.search.state import AISearchState
from nai.search.intelligent import alphabeta

class FocusState(AISearchState):
    def __init__(self, state_string):
        self.state = state_string
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.state == other.state
        return NotImplemented
    def __hash__(self):
        return hash(self.state)
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented
    def get_adjacent_states(self):
        return [self]
    def get_goal(self):
        return self
    def get_transition_cost(self, other):
        if isinstance(other, self.__class__):
            return 1
        return NotImplemented
    def __str__(self):
        return self.state

def main():
    state = FocusState("hello")

if __name__ == "__main__":
    main()
