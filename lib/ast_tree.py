# lib/ast_tree.py
from abc import ABC, abstractmethod

class ASTTree(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class CharNode(ASTTree):
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def accept(self, visitor):
        visitor.visit_char_node(self)

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

class StarNode(ASTTree):
    def __init__(self, child):
        self.child = child

    def get_child(self):
        return self.child

    def accept(self, visitor):
        visitor.visit_star_node(self)

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

class GroupNode(ASTTree):
    def __init__(self, child, group_num=None, capturing=True):
        self.child = child
        self.group_num = group_num
        self.capturing = capturing

    def get_child(self):
        return self.child

    def get_group_num(self):
        return self.group_num

    def is_capturing(self):
        return self.capturing

    def accept(self, visitor):
        if self.capturing:
            visitor.visit_capture_group_node(self)
        else:
            visitor.visit_non_capturing_group_node(self)

class RepeatNode(ASTTree):
    def __init__(self, child, min_repeats, max_repeats=None):
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

class RangeNode(ASTTree):
    def __init__(self, ranges, negated=False):
        self.ranges = ranges  # List of tuples (start_char, end_char) or single characters
        self.negated = negated

    def get_ranges(self):
        return self.ranges

    def is_negated(self):
        return self.negated

    def accept(self, visitor):
        visitor.visit_range_node(self)

class BackreferenceNode(ASTTree):
    def __init__(self, group_num):
        self.group_num = group_num

    def get_group_num(self):
        return self.group_num

    def accept(self, visitor):
        visitor.visit_backreference_node(self)

class EmptyNode(ASTTree):
    def accept(self, visitor):
        visitor.visit_empty_node(self)

class CharacterSetNode(ASTTree):
    def __init__(self, characters):
        self.characters = characters  # Set of characters

    def get_characters(self):
        return self.characters

    def accept(self, visitor):
        visitor.visit_character_set_node(self)

class RepeatExactNode(ASTTree):
    def __init__(self, child, exact_repeats):
        self.child = child
        self.exact_repeats = exact_repeats

    def get_child(self):
        return self.child

    def get_exact_repeats(self):
        return self.exact_repeats

    def accept(self, visitor):
        visitor.visit_repeat_exact_node(self)
