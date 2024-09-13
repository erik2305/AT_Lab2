# regex_lib/ast_tree.py
from abc import ABC, abstractmethod

class ASTTree(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

# regex_lib/ast_tree.py
class CharNode(ASTTree):
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def accept(self, visitor):
        visitor.visit_char_node(self)

# regex_lib/ast_tree.py
class ConcatNode(ASTTree):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def get_left(self):
        return self.left

    def get_right(self):
        return self.right

    def accept(self, visitor):
        visitor.visit_concat_node(self)
# regex_lib/ast_tree.py
class StarNode(ASTTree):
    def __init__(self, child):
        self.child = child

    def get_child(self):
        return self.child

    def accept(self, visitor):
        visitor.visit_star_node(self)

# regex_lib/ast_tree.py
class OrNode(ASTTree):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def get_left(self):
        return self.left

    def get_right(self):
        return self.right

    def accept(self, visitor):
        visitor.visit_or_node(self)
# regex_lib/ast_tree.py
class GroupNode(ASTTree):
    def __init__(self, child):
        self.child = child

    def get_child(self):
        return self.child

    def accept(self, visitor):
        visitor.visit_group_node(self)
# regex_lib/ast_tree.py
class RepeatNode(ASTTree):
    def __init__(self, child, min_repeats, max_repeats):
        self.child = child
        self.min = min_repeats
        self.max = max_repeats

    def get_child(self):
        return self.child

    def get_min(self):
        return self.min

    def get_max(self):
        return self.max

    def accept(self, visitor):
        visitor.visit_repeat_node(self)
# regex_lib/ast_tree.py
class RangeNode(ASTTree):
    def __init__(self, ranges):
        self.ranges = ranges

    def get_ranges(self):
        return self.ranges

    def accept(self, visitor):
        visitor.visit_range_node(self)
# regex_lib/ast_tree.py
class LookaheadNode(ASTTree):
    def __init__(self, main_expr, lookahead_expr):
        self.main_expr = main_expr
        self.lookahead_expr = lookahead_expr

    def get_main_expr(self):
        return self.main_expr

    def get_lookahead_expr(self):
        return self.lookahead_expr

    def accept(self, visitor):
        visitor.visit_lookahead_node(self)
# regex_lib/ast_tree.py
class EmptyNode(ASTTree):
    def accept(self, visitor):
        visitor.visit_empty_node(self)

class CharacterSetNode(ASTTree):
    def __init__(self, char_set):
        self.char_set = char_set

    def accept(self, visitor):
        return visitor.visit_character_set_node(self)
# regex_lib/ast.py

class RepeatExactNode(ASTTree):
    def __init__(self, repeat_value):
        self.repeat_value = repeat_value

    def accept(self, visitor):
        return visitor.visit_repeat_exact_node(self)
