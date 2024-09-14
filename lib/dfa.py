# lib/dfa.py

from collections import deque
from lib.dfa_state import DFAState

class DFA:
    def __init__(self, start_state, states):
        self.start_state = start_state  # DFAState
        self.states = states  # Set of DFAState

    def match(self, input_str):
        current_state = self.start_state
        for symbol in input_str:
            current_state = current_state.get_transition(symbol)
            if current_state is None:
                return False
        return current_state.is_final

    def findall(self, input_str):
        matches = []
        length = len(input_str)
        for i in range(length):
            current_state = self.start_state
            j = i
            while j < length:
                symbol = input_str[j]
                current_state = current_state.get_transition(symbol)
                if current_state is None:
                    break
                if current_state.is_final:
                    matches.append(input_str[i:j+1])
                j += 1
        return matches

    def complement(self):
        # Complement DFA by toggling final states
        new_final_states = set()
        for state in self.states:
            new_final_states.add(DFAState(state.id, not state.is_final))
            new_final_states[-1].transitions = state.transitions.copy()
        return DFA(new_final_states, {state for state in new_final_states if state.is_final})

    def minimize(self):
        # Hopcroft's algorithm for DFA minimization
        partition = [set(), set()]
        for state in self.states:
            if state.is_final:
                partition[0].add(state)
            else:
                partition[1].add(state)
        
        alphabet = self.get_alphabet()
        worklist = deque(partition.copy())

        while worklist:
            current = worklist.popleft()
            for symbol in alphabet:
                # Find states where transition on symbol leads to a state in current
                predecessors = set()
                for state in self.states:
                    target = state.get_transition(symbol)
                    if target and target in current:
                        predecessors.add(state)
                for p in partition.copy():
                    intersection = p.intersection(predecessors)
                    difference = p.difference(predecessors)
                    if intersection and difference:
                        partition.remove(p)
                        partition.append(intersection)
                        partition.append(difference)
                        if p in worklist:
                            worklist.remove(p)
                            worklist.append(intersection)
                            worklist.append(difference)
                        else:
                            if len(intersection) <= len(difference):
                                worklist.append(intersection)
                            else:
                                worklist.append(difference)
        # Create new states
        state_map = {}
        for idx, group in enumerate(partition):
            is_final = any(state.is_final for state in group)
            new_state = DFAState(idx, is_final)
            state_map[frozenset(group)] = new_state

        # Assign transitions
        for group in partition:
            representative = next(iter(group))
            new_state = state_map[frozenset(group)]
            for symbol, target in representative.get_transitions().items():
                for g in partition:
                    if target in g:
                        new_target = state_map[frozenset(g)]
                        new_state.add_transition(symbol, new_target)
                        break

        # Determine new start state
        for group in partition:
            if self.start_state in group:
                new_start_state = state_map[frozenset(group)]
                break

        # Collect all new states
        new_states = set(state_map.values())

        return DFA(new_start_state, new_states)

    def get_alphabet(self):
        alphabet = set()
        for state in self.states:
            alphabet.update(state.get_transitions().keys())
        return alphabet

    def __repr__(self):
        return f"DFA(start_state={self.start_state}, states={self.states})"
