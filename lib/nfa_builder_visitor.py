# lib/nfa_builder_visitor.py

from lib.ast_visitor import ASTVisitor
from lib.nfa import NFA, NFAState
from lib.ast_tree import (
    CharNode, ConcatNode, StarNode, OrNode, GroupNode,
    BackreferenceNode, RangeNode, RepeatNode, EmptyNode,
    CharacterSetNode, RepeatExactNode
)

class NFABuilderVisitor(ASTVisitor):
    def __init__(self):
        self.group_map = {}  # Maps group numbers to (start_state, end_state)
        self.nfa = None
        self.current_group = None

    def get_nfa(self):
        return self.nfa

    def visit_char_node(self, node):
        start = NFAState(False)
        end = NFAState(True)
        start.add_transition(node.get_value(), end)
        self.nfa = NFA(start, {end})

    def visit_concat_node(self, node):
        left_visitor = NFABuilderVisitor()
        node.get_left().accept(left_visitor)
        left_nfa = left_visitor.get_nfa()

        right_visitor = NFABuilderVisitor()
        node.get_right().accept(right_visitor)
        right_nfa = right_visitor.get_nfa()

        for state in left_nfa.get_final_states():
            state.is_final = False
            state.add_epsilon_transition(right_nfa.get_start_state())

        self.nfa = NFA(left_nfa.get_start_state(), right_nfa.get_final_states())

    def visit_star_node(self, node):
        inner_visitor = NFABuilderVisitor()
        node.get_child().accept(inner_visitor)
        inner_nfa = inner_visitor.get_nfa()

        start = NFAState(False)
        end = NFAState(True)

        start.add_epsilon_transition(inner_nfa.get_start_state())
        start.add_epsilon_transition(end)

        for state in inner_nfa.get_final_states():
            state.is_final = False
            state.add_epsilon_transition(inner_nfa.get_start_state())
            state.add_epsilon_transition(end)

        self.nfa = NFA(start, {end})

    def visit_or_node(self, node):
        left_visitor = NFABuilderVisitor()
        node.get_left().accept(left_visitor)
        left_nfa = left_visitor.get_nfa()

        right_visitor = NFABuilderVisitor()
        node.get_right().accept(right_visitor)
        right_nfa = right_visitor.get_nfa()

        start = NFAState(False)
        end = NFAState(True)

        start.add_epsilon_transition(left_nfa.get_start_state())
        start.add_epsilon_transition(right_nfa.get_start_state())

        for state in left_nfa.get_final_states():
            state.is_final = False
            state.add_epsilon_transition(end)

        for state in right_nfa.get_final_states():
            state.is_final = False
            state.add_epsilon_transition(end)

        self.nfa = NFA(start, {end})

    def visit_capture_group_node(self, node):
        group_num = node.get_group_num()
        inner_visitor = NFABuilderVisitor()
        node.get_child().accept(inner_visitor)
        inner_nfa = inner_visitor.get_nfa()

        start = NFAState(False)
        end = NFAState(True)

        start.add_epsilon_transition(inner_nfa.get_start_state())
        for state in inner_nfa.get_final_states():
            state.is_final = False
            state.add_epsilon_transition(end)

        self.group_map[group_num] = (start, end)
        self.nfa = NFA(start, {end})

    def visit_non_capturing_group_node(self, node):
        inner_visitor = NFABuilderVisitor()
        node.get_child().accept(inner_visitor)
        self.nfa = inner_visitor.get_nfa()

    def visit_backreference_node(self, node):
        group_num = node.get_group_num()
        if group_num not in self.group_map:
            raise ValueError(f"Undefined backreference to group {group_num}")

        start, end = self.group_map[group_num]
        self.nfa = NFA(start, {end})

    def visit_repeat_node(self, node):
        min_repeats = node.get_min()
        max_repeats = node.get_max()
        child = node.get_child()

        if max_repeats is not None and min_repeats > max_repeats:
            raise ValueError("Minimum repeats cannot exceed maximum repeats.")

        # Build NFA for child
        child_visitor = NFABuilderVisitor()
        child.accept(child_visitor)
        child_nfa = child_visitor.get_nfa()

        if min_repeats == 0 and max_repeats == 0:
            # Equivalent to empty string
            start = NFAState(False)
            end = NFAState(True)
            start.add_epsilon_transition(end)
            self.nfa = NFA(start, {end})
            return

        nfa = None
        previous_end_states = set()

        for _ in range(min_repeats):
            if nfa is None:
                nfa = child_nfa
            else:
                for state in previous_end_states:
                    state.is_final = False
                    state.add_epsilon_transition(child_nfa.get_start_state())
                nfa = NFA(nfa.get_start_state(), child_nfa.get_final_states())
            previous_end_states = child_nfa.get_final_states()

        if max_repeats is None:
            # Unlimited repetitions after min_repeats
            star_visitor = NFABuilderVisitor()
            star_node = StarNode(child)
            star_node.accept(star_visitor)
            star_nfa = star_visitor.get_nfa()

            if nfa is None:
                nfa = star_nfa
            else:
                for state in previous_end_states:
                    state.is_final = False
                    state.add_epsilon_transition(star_nfa.get_start_state())
                nfa = NFA(nfa.get_start_state(), star_nfa.get_final_states())
        elif max_repeats > min_repeats:
            # Limited repetitions
            optional_part = max_repeats - min_repeats
            for _ in range(optional_part):
                optional_visitor = NFABuilderVisitor()
                optional_nfa = child.accept(optional_visitor) or child_visitor.get_nfa()

                start = NFAState(False)
                end = NFAState(True)
                start.add_epsilon_transition(optional_nfa.get_start_state())
                start.add_epsilon_transition(end)

                for state in optional_nfa.get_final_states():
                    state.is_final = False
                    state.add_epsilon_transition(end)

                if nfa is None:
                    nfa = NFA(start, {end})
                else:
                    for state in previous_end_states:
                        state.is_final = False
                        state.add_epsilon_transition(start)
                    nfa = NFA(nfa.get_start_state(), {end})

        self.nfa = nfa

    def visit_range_node(self, node):
        ranges = node.get_ranges()
        negated = node.is_negated()
        start = NFAState(False)
        end = NFAState(True)

        if negated:
            # Assuming printable ASCII for negation
            import string
            all_chars = set(string.printable)
            range_chars = set()
            for r in ranges:
                if len(r) == 2:
                    range_chars.update(chr(c) for c in range(ord(r[0]), ord(r[1]) + 1))
                else:
                    range_chars.add(r[0])
            complement_chars = all_chars - range_chars
            for ch in complement_chars:
                start.add_transition(ch, end)
        else:
            for r in ranges:
                if len(r) == 2:
                    for c in range(ord(r[0]), ord(r[1]) + 1):
                        start.add_transition(chr(c), end)
                else:
                    start.add_transition(r[0], end)

        self.nfa = NFA(start, {end})

    def visit_empty_node(self, node):
        start = NFAState(False)
        end = NFAState(True)
        start.add_epsilon_transition(end)
        self.nfa = NFA(start, {end})

    def visit_character_set_node(self, node):
        # Similar to RangeNode but with explicit characters
        characters = node.get_characters()
        start = NFAState(False)
        end = NFAState(True)
        for ch in characters:
            start.add_transition(ch, end)
        self.nfa = NFA(start, {end})

    def visit_repeat_exact_node(self, node):
        exact = node.get_exact_repeats()
        child = node.get_child()

        if exact < 0:
            raise ValueError("Exact repeats cannot be negative.")

        if exact == 0:
            # Equivalent to empty string
            start = NFAState(False)
            end = NFAState(True)
            start.add_epsilon_transition(end)
            self.nfa = NFA(start, {end})
            return

        nfa = None
        previous_end_states = set()

        for _ in range(exact):
            child_visitor = NFABuilderVisitor()
            child.accept(child_visitor)
            child_nfa = child_visitor.get_nfa()

            if nfa is None:
                nfa = child_nfa
            else:
                for state in previous_end_states:
                    state.is_final = False
                    state.add_epsilon_transition(child_nfa.get_start_state())
                nfa = NFA(nfa.get_start_state(), child_nfa.get_final_states())

            previous_end_states = child_nfa.get_final_states()

        self.nfa = nfa
