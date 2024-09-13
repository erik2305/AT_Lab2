# regex_lib/nfa.py

class NFA:
    def __init__(self, start_state, final_states):
        if not start_state:
            raise ValueError("NFA must have a valid start state.")
        if not final_states:
            raise ValueError("NFA must have at least one final state.")
        self.start_state = start_state
        self.final_states = frozenset(final_states)

    def get_start_state(self):
        return self.start_state

    def get_final_states(self):
        return self.final_states

    def __str__(self, verbose=False):
        sb = []
        sb.append(f"Start State: {self.start_state.get_id()}\n")
        sb.append("Final States: ")
        for state in self.final_states:
            sb.append(f"{state.get_id()} ")
        sb.append("\nTransitions:\n")

        if verbose:
            for state in self.get_all_states():
                sb.append(f"{state}\n")
        else:
            sb.append(f"Total States: {len(self.get_all_states())}\n")
            sb.append("Use verbose=True to see all transitions.\n")

        return ''.join(sb)


    def get_all_states(self):
        all_states = set()
        self.collect_states(self.start_state, all_states)
        return all_states

    def collect_states(self, state, visited):
        if state not in visited:
            visited.add(state)
            for next_states in state.get_transitions().values():
                for next_state in next_states:
                    self.collect_states(next_state, visited)
