from lib.dfa import DFA
from lib.dfa_state import DFAState
from collections import deque

class RegexRecovery:
    def recover_regex(self, dfa: DFA) -> str:
        """
        Attempts to recover the regex pattern from the minimized DFA using state elimination.
        """
        # Create a mapping from state ID to state
        state_map = {state.id: state for state in dfa.states}
        final_states = {state.id for state in dfa.states if state.is_final}
        start_state_id = dfa.start_state.id

        # Remove unreachable states
        reachable = self.get_reachable_states(dfa)
        state_map = {sid: state_map[sid] for sid in reachable}

        # Initialize regex expressions between states
        regex_matrix = {}
        for i in state_map:
            regex_matrix[i] = {}
            for j in state_map:
                regex_matrix[i][j] = set()

        # Populate initial transitions
        for state in state_map.values():
            for symbol, target in state.transitions.items():
                regex_matrix[state.id][target.id].add(self.escape_regex(symbol))

        # State elimination
        states = set(state_map.keys())
        states.remove(start_state_id)
        states -= final_states

        for elim_state in list(states):
            for i in list(state_map.keys()):
                for j in list(state_map.keys()):
                    if regex_matrix[i][elim_state] and regex_matrix[elim_state][j]:
                        part1 = regex_matrix[i][j]
                        part2 = set()
                        for r1 in regex_matrix[i][elim_state]:
                            for r2 in regex_matrix[elim_state][elim_state]:
                                part2.add(f"({r1})({self.union_regex(regex_matrix[elim_state][elim_state])})*")
                            for r3 in regex_matrix[elim_state][j]:
                                part2.add(f"({r1})({self.union_regex(regex_matrix[elim_state][elim_state])})*({r3})")
                        regex_matrix[i][j].update(part2)
            # Remove elim_state from the matrix
            for i in regex_matrix:
                if elim_state in regex_matrix[i]:
                    del regex_matrix[i][elim_state]
            for j in regex_matrix:
                if elim_state in regex_matrix[j]:
                    del regex_matrix[j][elim_state]
            states.remove(elim_state)

        # Combine regex from start state to all final states
        recovered_regex = set()
        for final_state in final_states:
            if regex_matrix[start_state_id][final_state]:
                recovered_regex.update(regex_matrix[start_state_id][final_state])

        if not recovered_regex:
            return ""
        elif len(recovered_regex) == 1:
            return next(iter(recovered_regex))
        else:
            return "(" + "|".join(recovered_regex) + ")"

    def get_reachable_states(self, dfa: DFA) -> set:
        """
        Returns a set of reachable state IDs from the start state.
        """
        reachable = set()
        queue = deque()
        queue.append(dfa.start_state.id)
        reachable.add(dfa.start_state.id)

        while queue:
            current = queue.popleft()
            state = next((s for s in dfa.states if s.id == current), None)
            if state:
                for target in state.transitions.values():
                    if target.id not in reachable:
                        reachable.add(target.id)
                        queue.append(target.id)
        return reachable

    def escape_regex(self, symbol: str) -> str:
        special_chars = set(".^$*+?{}[]\\|()")
        if symbol in special_chars:
            return f"\\{symbol}"
        else:
            return symbol

    def union_regex(self, regex_set: set) -> str:
        if not regex_set:
            return ""
        elif len(regex_set) == 1:
            return next(iter(regex_set))
        else:
            return "(" + "|".join(regex_set) + ")"
