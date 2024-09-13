# regex_lib/dfa_state.py

class DFAState:
    def __init__(self, nfa_states, is_final=False):
        """
        Initialize a DFA state from a set of NFA states and whether it's final or not.
        :param nfa_states: The set of NFA states represented by this DFA state.
        :param is_final: Boolean indicating if this DFA state is a final state.
        """
        self.nfa_states = frozenset(nfa_states)  # Ensure nfa_states is a frozenset
        self._is_final = is_final
        self.transitions = {}

    def add_transition(self, symbol, state):
        """
        Add a transition from this state to another DFA state on the given symbol.
        :param symbol: Character input for the transition.
        :param state: DFAState to transition to.
        """
        if symbol in self.transitions:
            raise ValueError(f"Transition on '{symbol}' already exists.")
        self.transitions[symbol] = state

    def get_transition(self, symbol):
        """
        Get the state this DFA state transitions to on the given symbol.
        :param symbol: Character input for the transition.
        :return: The DFAState transitioned to, or None if no transition exists.
        """
        return self.transitions.get(symbol)

    def get_nfa_states(self):
        """
        Get the set of NFA states this DFA state represents.
        :return: Set of NFA states.
        """
        return self.nfa_states

    @property
    def is_final(self):
        """
        Check if this DFA state is a final state.
        :return: Boolean indicating if this is a final state.
        """
        return self._is_final

    def get_transitions(self):
        """
        Get all transitions from this DFA state.
        :return: Dictionary of transitions (symbol -> DFAState).
        """
        return self.transitions

    def __eq__(self, other):
        """
        Check equality of two DFA states based on the set of NFA states.
        :param other: Another DFAState.
        :return: True if the NFA states are the same, otherwise False.
        """
        if isinstance(other, DFAState):
            return self.nfa_states == other.nfa_states
        return False

    def __hash__(self):
        """
        Generate a hash based on the set of NFA states for use in collections.
        :return: Hash of the set of NFA states.
        """
        return hash(frozenset(self.nfa_states))

    def __repr__(self):
        """
        Provide a string representation of the DFA state, including transitions and finality.
        :return: String representation of the DFAState.
        """
        transitions_repr = {k: v.nfa_states for k, v in self.transitions.items()}
        return f"DFAState(nfa_states={list(self.nfa_states)}, transitions={transitions_repr}, is_final={self._is_final})"
