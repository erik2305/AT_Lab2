# lib/ast_visitor.py

from abc import ABC, abstractmethod

class ASTVisitor(ABC):
    @abstractmethod
    def visit_char_node(self, node):
        pass

    @abstractmethod
    def visit_concat_node(self, node):
        pass

    @abstractmethod
    def visit_star_node(self, node):
        pass

    @abstractmethod
    def visit_or_node(self, node):
        pass

    @abstractmethod
    def visit_capture_group_node(self, node):
        pass

    @abstractmethod
    def visit_non_capturing_group_node(self, node):
        pass

    @abstractmethod
    def visit_repeat_node(self, node):
        pass

    @abstractmethod
    def visit_range_node(self, node):
        pass

    @abstractmethod
    def visit_backreference_node(self, node):
        pass

    @abstractmethod
    def visit_empty_node(self, node):
        pass

    @abstractmethod
    def visit_character_set_node(self, node):
        pass

    @abstractmethod
    def visit_repeat_exact_node(self, node):
        pass
