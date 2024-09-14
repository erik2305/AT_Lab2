# lib/nfa_to_dfa_converter.py

from collections import deque
from lib.dfa import DFA
from lib.dfa_state import DFAState
from lib.nfa import NFA, NFAState

class NFAtoDFAConverter:
    def convert(self, nfa: NFA) -> DFA:
        start_closure = self.epsilon_closure({nfa.get_start_state()})
        state_mappings = {}
        dfa_states = set()
        queue = deque()

        # Create start state for DFA
        start_state = DFAState(state_id=0, is_final=any(state.is_final for state in start_closure))
        state_mappings[frozenset(start_closure)] = start_state
        dfa_states.add(start_state)
        queue.append(frozenset(start_closure))
        state_id_counter = 1

        while queue:
            current_set = queue.popleft()
            current_dfa_state = state_mappings[current_set]

            transitions = {}
            for nfa_state in current_set:
                for symbol, target_states in nfa_state.transitions.items():
                    if symbol == '\0':
                        continue  # Epsilon transitions are already handled
                    if symbol not in transitions:
                        transitions[symbol] = set()
                    transitions[symbol].update(target_states)

            for symbol, target_nfa_states in transitions.items():
                closure = self.epsilon_closure(target_nfa_states)
                closure_frozen = frozenset(closure)
                if closure_frozen not in state_mappings:
                    is_final = any(state.is_final for state in closure)
                    new_dfa_state = DFAState(state_id=state_id_counter, is_final=is_final)
                    state_mappings[closure_frozen] = new_dfa_state
                    dfa_states.add(new_dfa_state)
                    queue.append(closure_frozen)
                    state_id_counter += 1
                else:
                    new_dfa_state = state_mappings[closure_frozen]
                current_dfa_state.add_transition(symbol, new_dfa_state)

        return DFA(start_state=start_state, states=dfa_states)

    def epsilon_closure(self, states: set) -> set:
        stack = list(states)
        closure = set(states)
        while stack:
            state = stack.pop()
            for next_state in state.transitions.get('\0', set()):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure
