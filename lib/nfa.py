# lib/nfa.py

from collections import deque

class NFAState:
    id_counter = 0

    def __init__(self, is_final=False):
        self.id = NFAState.id_counter
        NFAState.id_counter += 1
        self.transitions = {}  # symbol -> set of NFAState
        self.is_final = is_final

    def add_transition(self, symbol, state):
        if symbol not in self.transitions:
            self.transitions[symbol] = set()
        self.transitions[symbol].add(state)

    def add_epsilon_transition(self, state):
        self.add_transition('\0', state)  # '\0' represents epsilon

    def get_transitions(self):
        return self.transitions

    def __repr__(self):
        transitions_repr = {k: [s.id for s in v] for k, v in self.transitions.items()}
        return f"NFAState(id={self.id}, is_final={self.is_final}, transitions={transitions_repr})"

class NFA:
    def __init__(self, start_state, final_states):
        self.start_state = start_state  # NFAState
        self.final_states = final_states  # Set of NFAState

    def get_start_state(self):
        return self.start_state

    def get_final_states(self):
        return self.final_states

    def __repr__(self):
        return f"NFA(start_state={self.start_state.id}, final_states={[s.id for s in self.final_states]})"

    def get_all_states(self):
        all_states = set()
        queue = deque([self.start_state])

        while queue:
            current = queue.popleft()
            if current not in all_states:
                all_states.add(current)
                for states in current.get_transitions().values():
                    queue.extend(states)
        return all_states
