# lib/dfa_state.py

class DFAState:
    def __init__(self, state_id, is_final=False):
        self.id = state_id
        self.is_final = is_final
        self.transitions = {}  # symbol -> DFAState

    def add_transition(self, symbol, state):
        if symbol in self.transitions:
            raise ValueError(f"Transition on '{symbol}' already exists for state {self.id}.")
        self.transitions[symbol] = state

    def get_transition(self, symbol):
        return self.transitions.get(symbol, None)

    def get_transitions(self):
        return self.transitions

    def __repr__(self):
        transitions_repr = {k: v.id for k, v in self.transitions.items()}
        return f"DFAState(id={self.id}, is_final={self.is_final}, transitions={transitions_repr})"
