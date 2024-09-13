# regex_lib/nfa_state.py

class NFAState:
    id_counter = 0

    def __init__(self, is_final=False):
        self.id = NFAState.id_counter
        NFAState.id_counter += 1
        self.transitions = {}
        self.is_final = is_final

    def get_id(self):
        return self.id

    def add_transition(self, symbol, next_state):
        if self == next_state:
            print(f"Warning: Adding self-transition on symbol {symbol} for state {self.id}.")
        if symbol not in self.transitions:
            self.transitions[symbol] = set()
        self.transitions[symbol].add(next_state)

    def add_epsilon_transition(self, next_state):
        self.add_transition('\0', next_state)

    def get_transitions(self):
        return self.transitions

    @property
    def is_final(self):
        return self._is_final

    @is_final.setter
    def is_final(self, value):
        self._is_final = value

    def set_final(self, is_final):
        self.is_final = is_final

    def __repr__(self, verbose=False):
        if verbose:
            transitions_repr = ', '.join(f"{k}: {[s.get_id() for s in v]}" for k, v in self.transitions.items())
            return f"State {self.id}, Final: {self.is_final}, Transitions: {transitions_repr}"
        else:
            return f"State {self.id}, Final: {self.is_final}"
