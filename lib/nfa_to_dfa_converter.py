# regex_lib/nfa_to_dfa_converter.py

from regex_lib.dfa import DFA
from regex_lib.dfa_state import DFAState
from collections import deque

class NFAtoDFAConverter:
    def convert(self, nfa):
        dfa_states_map = {}
        queue = deque()

        # Use frozenset instead of set for the closure to make it hashable
        start_closure = frozenset(self.epsilon_closure({nfa.get_start_state()}))
        start_state = DFAState(start_closure, self.contains_final_state(start_closure, nfa.get_final_states()))
        dfa_states_map[start_closure] = start_state
        queue.append(start_closure)

        final_states = set()
        if start_state.is_final:
            final_states.add(start_state)

        while queue:
            current_closure = queue.popleft()
            current_state = dfa_states_map[current_closure]

            symbols = self.get_all_symbols(current_closure)

            for symbol in symbols:
                move_closure = frozenset(self.epsilon_closure(self.move(current_closure, symbol)))

                #print(f"Type of move_closure: {type(move_closure)}")
                if move_closure not in dfa_states_map:
                    is_final = self.contains_final_state(move_closure, nfa.get_final_states())
                    next_state = DFAState(move_closure, is_final)
                    dfa_states_map[move_closure] = next_state
                    queue.append(move_closure)
                    if is_final:
                        final_states.add(next_state)

                current_state.add_transition(symbol, dfa_states_map[move_closure])

        return DFA(start_state, final_states)


    def epsilon_closure(self, states):
        stack = list(states)
        closure = set(states)

        while stack:
            state = stack.pop()
            for next_state in state.get_transitions().get('\0', set()):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

        return closure

    def move(self, states, symbol):
        move_set = set()
        for state in states:
            move_set.update(state.get_transitions().get(symbol, set()))
        return move_set

    def get_all_symbols(self, states):
        symbols = set()
        for state in states:
            for symbol in state.get_transitions().keys():
                if symbol != '\0':  # Ignore epsilon transitions
                    symbols.add(symbol)
        return symbols

    def contains_final_state(self, states, final_states):
        return any(state in final_states for state in states)