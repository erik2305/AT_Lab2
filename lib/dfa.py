from collections import deque
from lib.dfa_state import DFAState

# regex_lib/pair.py

class Pair:
    def __init__(self, first, second):
        """
        Initialize a pair object to hold two values.
        :param first: The first value in the pair.
        :param second: The second value in the pair.
        """
        self.first = first
        self.second = second

    def __eq__(self, other):
        """
        Compare this pair to another pair for equality.
        :param other: The other pair to compare to.
        :return: True if both pairs have the same first and second values.
        """
        if isinstance(other, Pair):
            return self.first == other.first and self.second == other.second
        return False

    def __hash__(self):
        """
        Compute a hash value for this pair so it can be used in sets or as dictionary keys.
        :return: The hash value based on the first and second values.
        """
        return hash((self.first, self.second))

    def __repr__(self):
        """
        Provide a string representation of the pair.
        :return: A string that represents the pair.
        """
        return f"Pair({self.first}, {self.second})"


class DFA:
    def __init__(self, start_state, final_states):
        self.start_state = start_state
        self.final_states = final_states

    def match(self, input_str):
        """
        Match the entire input string against the DFA.
        :param input_str: The input string to be matched.
        :return: True if the entire string matches, otherwise False.
        """
        if not input_str:
            return self.start_state.is_final
        current_state = self.start_state
        for symbol in input_str:
            next_state = current_state.get_transition(symbol)
            if next_state is None:
                return False
            current_state = next_state

        return current_state.is_final

    def minimize(self):
        """
        Minimize the DFA by partitioning states into equivalent groups.
        """
        non_final_states = {state for state in self.get_all_states() if not state.is_final}
        partitions = [self.final_states, non_final_states]
    
        partition_changed = True
        iteration_count = 0  # Debugging: track number of iterations
    
        while partition_changed:
            iteration_count += 1  # Debugging: increment iteration count
            print(f"Iteration {iteration_count}, current partitions: {partitions}")
            partition_changed = False
            new_partitions = []
    
            for group in partitions:
                partition_map = {}
                for state in group:
                    transition_map = {}
                    for symbol in self.get_alphabet():
                        target_state = state.get_transition(symbol)
                        if target_state is None:
                            #print(f"No transition for state {state} on symbol '{symbol}', skipping.")
                            continue  # Safely skip states without transitions for this symbol
                        
                        # Convert partition to frozenset to ensure it is hashable
                        partition = frozenset(self.get_state_partition(target_state, partitions))
                        transition_map[symbol] = partition
    
                    # Group states by their transition patterns
                    transition_map_key = frozenset(transition_map.items())  # Debugging: track transition map
                    print(f"State {state}, Transition map: {transition_map_key}")  # Debugging
                    partition_map.setdefault(transition_map_key, []).append(state)
    
                # Add new partitions
                for new_group in partition_map.values():
                    new_partitions.append(new_group)
                    if len(new_group) > 1:
                        partition_changed = True
            
            if not partition_changed:
                print(f"Partition stabilized after {iteration_count} iterations.")  # Debugging: when partitions stabilize
                break
            
            # Check if partitions are actually different from the previous iteration
            if new_partitions == partitions:
                print("Partitions didn't change, breaking the loop.")  # Debugging: exit if no actual change
                break
            
            partitions = new_partitions
            print(f"Updated partitions: {partitions}")
    
        print(f"Minimization completed in {iteration_count} iterations.")  # Debugging: track completion
        # Ensure partition is a frozenset when used as a dictionary key
        new_states_map = {frozenset(partition): DFAState(frozenset(partition), any(state.is_final for state in partition)) for partition in partitions}

        # Create transitions in minimized DFA
        for partition in partitions:
            new_state = new_states_map[frozenset(partition)]
            for symbol in self.get_alphabet():
                target_state = next(iter(partition)).get_transition(symbol)
                if target_state is not None:
                    target_partition = self.get_state_partition(target_state, partitions)
                    new_state.add_transition(symbol, new_states_map[frozenset(target_partition)])

        new_start_state = new_states_map[frozenset(self.get_state_partition(self.start_state, partitions))]
        new_final_states = {new_states_map[frozenset(partition)] for partition in partitions if any(state.is_final for state in partition)}

        print("Minimization complete")
        return DFA(new_start_state, new_final_states)
    
    def findall(self, input_str):
        """
        Find all non-overlapping occurrences of substrings in the input string that match the DFA.
        :param input_str: The string to search.
        :return: A list of start indices of all matching substrings.
        """
        matches = []
        i = 0

        while i < len(input_str):
            current_state = self.start_state
            j = i

            while j < len(input_str):
                symbol = input_str[j]
                next_state = current_state.get_transition(symbol)

                if next_state is None:
                    break

                current_state = next_state
                j += 1

                if current_state.is_final:
                    matches.append(i)  # Record the start index of the match
                    i = j  # Move the starting point to the end of the current match to prevent overlapping
                    break

            # If no match is found, increment i
            if i == j:  # If no match was found starting from this position
                i += 1

        return matches

    def inverse (self):
        """
        Compute the inverse  of the DFA.
        :return: A new DFA representing the inverse.
        """
        all_states = self.get_all_states()
        new_final_states = {state for state in all_states if not state.is_final}
        return DFA(self.start_state, new_final_states)

    def get_alphabet(self):
        """
        Get all symbols (alphabet) from the DFA.
        :return: A set of symbols (characters).
        """
        alphabet = set()
        for state in self.get_all_states():
            alphabet.update(state.get_transitions().keys())
        return alphabet

    def get_all_states(self):
        """
        Get all states in the DFA.
        :return: A set of all DFA states.
        """
        visited = set()
        queue = deque([self.start_state])

        while queue:
            current_state = queue.pop()
            if current_state not in visited:
                visited.add(current_state)
                # Add all transitions to the queue
                for next_state in current_state.get_transitions().values():
                    if next_state not in visited:
                        queue.append(next_state)

        return visited
    

    def augment(self):
        """
        Construct the augmentation of the current DFA.
        :return: A new DFA that represents the augmentation of the current DFA.
        """
        # Get all states of the DFA
        all_states = self.get_all_states()

        # New final states will be the non-final states in the original DFA
        new_final_states = set(state for state in all_states if state not in self.final_states)

        # Return a new DFA with the same transitions but flipped final states
        return DFA(self.start_state, new_final_states)

    def get_state_partition(self, state, partitions):
        """
        Find the partition containing the given state.
        :param state: The DFA state to find.
        :param partitions: The partitions of DFA states.
        :return: The partition that contains the state.
        """
        if state is None:
            return None
        for partition in partitions:
            if state in partition:
                return partition
        return None

    def get_pair_state(self, pair, state_map, final_states, other_dfa):
        """
        Get or create a new state for the pair of states from two DFAs.
        :param pair: The pair of DFA states (one from each DFA).
        :param state_map: The map of pairs to new DFA states.
        :param final_states: Set of final states for the new DFA.
        :return: A new DFAState corresponding to the pair.
        """
        if pair not in state_map:
            combined_nfa_states = set(pair.first.get_nfa_states()).union(pair.second.get_nfa_states())
            is_final = pair.first.is_final and not pair.second.is_final
            new_state = DFAState(combined_nfa_states, is_final)
            state_map[pair] = new_state
            if is_final:
                final_states.add(new_state)
        return state_map[pair]
