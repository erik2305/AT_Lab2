# regex_lib/nfa_builder_visitor.py

from lib.ast_visitor import ASTVisitor
from lib.nfa import NFA
from lib.NFAState import NFAState
from lib.ast_tree import StarNode, ConcatNode, OrNode, EmptyNode, CharNode

class NFABuilderVisitor(ASTVisitor):
    def __init__(self):
        self.id_counter = 0
        self.group_counter = 0
        self.state_map = {}
        self.nfa = None

    def get_nfa(self):
        return self.nfa

    def create_state(self, is_final=False):
        state = NFAState(is_final)
        self.state_map[state.get_id()] = state
        return state

    def visit_char_node(self, char_node):
        print(f"Visiting CharNode with value: {char_node.get_value()}")
        start_state = self.create_state(False)
        end_state = self.create_state(True)
        start_state.add_transition(char_node.get_value(), end_state)
        self.nfa = NFA(start_state, {end_state})
        print(f"Created NFA for CharNode: Start={start_state.get_id()}, End={end_state.get_id()}")

    def visit_group_node(self, group_node):
        inner_visitor = NFABuilderVisitor()
        group_node.get_child().accept(inner_visitor)
        inner_nfa = inner_visitor.get_nfa()

        start_state = self.create_state(False)
        end_state = self.create_state(True)

        start_state.add_epsilon_transition(inner_nfa.get_start_state())

        for state in inner_nfa.get_final_states():
            state.add_epsilon_transition(end_state)
            state.set_final(False)

        self.nfa = NFA(start_state, {end_state})

    def visit_concat_node(self, concat_node):
        left_visitor = NFABuilderVisitor()
        concat_node.get_left().accept(left_visitor)
        left_nfa = left_visitor.get_nfa()

        right_visitor = NFABuilderVisitor()
        concat_node.get_right().accept(right_visitor)
        right_nfa = right_visitor.get_nfa()

        for state in left_nfa.get_final_states():
            state.add_epsilon_transition(right_nfa.get_start_state())
            state.set_final(False)

        self.nfa = NFA(left_nfa.get_start_state(), right_nfa.get_final_states())

    def visit_or_node(self, or_node):
        start_state = self.create_state(False)
        end_state = self.create_state(True)

        left_visitor = NFABuilderVisitor()
        or_node.get_left().accept(left_visitor)
        left_nfa = left_visitor.get_nfa()

        right_visitor = NFABuilderVisitor()
        or_node.get_right().accept(right_visitor)
        right_nfa = right_visitor.get_nfa()

        start_state.add_epsilon_transition(left_nfa.get_start_state())
        start_state.add_epsilon_transition(right_nfa.get_start_state())

        for state in left_nfa.get_final_states():
            state.add_epsilon_transition(end_state)
            state.set_final(False)

        for state in right_nfa.get_final_states():
            state.add_epsilon_transition(end_state)
            state.set_final(False)

        self.nfa = NFA(start_state, {end_state})

    def visit_star_node(self, star_node):
        start_state = self.create_state(False)
        end_state = self.create_state(True)

        inner_visitor = NFABuilderVisitor()
        star_node.get_child().accept(inner_visitor)
        inner_nfa = inner_visitor.get_nfa()

        start_state.add_epsilon_transition(inner_nfa.get_start_state())
        start_state.add_epsilon_transition(end_state)

        for state in inner_nfa.get_final_states():
            state.add_epsilon_transition(end_state)
            state.add_epsilon_transition(inner_nfa.get_start_state())
            state.set_final(False)

        self.nfa = NFA(start_state, {end_state})

    def visit_range_node(self, range_node):
        ranges = range_node.get_ranges()
        or_node = None

        for range_str in ranges:
            if len(range_str) == 1:
                char_node = CharNode(range_str[0])
                if or_node is None:
                    or_node = char_node
                else:
                    or_node = OrNode(or_node, char_node)
            elif len(range_str) == 3 and range_str[1] == '-':
                start_char = range_str[0]
                end_char = range_str[2]
                for char in range(ord(start_char), ord(end_char) + 1):
                    char_node = CharNode(chr(char))
                    if or_node is None:
                        or_node = char_node
                    else:
                        or_node = OrNode(or_node, char_node)

        if or_node:
            or_node.accept(self)

    def visit_repeat_node(self, repeat_node):
        min_repeats = repeat_node.get_min()
        max_repeats = repeat_node.get_max()
        node = repeat_node.get_child()
        result_node = None

        if min_repeats is not None and max_repeats is None:
            # Create 'min' repetitions followed by Kleene star
            result_node = self.create_repetition(node, min_repeats)
            result_node = ConcatNode(result_node, StarNode(node))
        elif min_repeats is None and max_repeats is not None:
            # Create a range of possible repetitions up to 'max'
            result_node = self.create_optional_repetitions(node, max_repeats)
        elif min_repeats is not None and min_repeats == max_repeats:
            # Create exactly 'min' repetitions
            result_node = self.create_repetition(node, min_repeats)
        else:
            # Create a combination of minimum and optional extra repetitions
            result_node = self.create_repetition(node, min_repeats)
            for _ in range(min_repeats, max_repeats):
                result_node = ConcatNode(result_node, OrNode(node, EmptyNode()))

        if result_node:
            result_node.accept(self)

    def create_repetition(self, node, times):
        result_node = None
        for _ in range(times):
            result_node = ConcatNode(result_node, node) if result_node else node
        return result_node

    def create_optional_repetitions(self, node, max_repeats):
        result_node = EmptyNode()
        for _ in range(max_repeats):
            result_node = OrNode(ConcatNode(result_node, node), result_node)
        return result_node

    def visit_lookahead_node(self, lookahead_node):
        main_visitor = NFABuilderVisitor()
        lookahead_node.get_main_expr().accept(main_visitor)
        main_nfa = main_visitor.get_nfa()

        lookahead_visitor = NFABuilderVisitor()
        lookahead_node.get_lookahead_expr().accept(lookahead_visitor)
        lookahead_nfa = lookahead_visitor.get_nfa()

        start_state = self.create_state(False)

        start_state.add_epsilon_transition(main_nfa.get_start_state())

        for state in main_nfa.get_final_states():
            state.add_epsilon_transition(lookahead_nfa.get_start_state())
            state.set_final(False)

        self.nfa = NFA(start_state, lookahead_nfa.get_final_states())

    def visit_empty_node(self, empty_node):
        start_state = self.create_state(True)
        self.nfa = NFA(start_state, {start_state})

    def visit_character_set_node(self, node):
        print(f"Visiting character set node: {node.char_set}")
        """
        Handle the character set node in the NFA builder visitor.
        """
        start_state = self.create_state(False)
        end_state = self.create_state(True)

        for char in node.char_set:
            start_state.add_transition(char, end_state)

        self.nfa = NFA(start_state, {end_state})

    # regex_lib/nfa_builder_visitor.py

def visit_repeat_exact_node(self, node):
    """
    Handle the repeat exact node in the NFA builder visitor.
    """
    start_state = self.create_state(False)
    prev_end_state = None

    # For exact repetitions, create the corresponding NFA states
    for _ in range(node.repeat_value):
        end_state = self.create_state(False)
        if prev_end_state:
            prev_end_state.add_epsilon_transition(end_state)
        prev_end_state = end_state

    if prev_end_state:
        prev_end_state.set_final(True)
    self.nfa = NFA(start_state, {prev_end_state})

