# regex_lib/ast_visitor.py

from abc import abstractmethod

class ASTVisitor:
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
    def visit_group_node(self, node):
        pass

    @abstractmethod
    def visit_repeat_node(self, node):
        pass

    @abstractmethod
    def visit_range_node(self, node):
        pass

    @abstractmethod
    def visit_lookahead_node(self, node):
        pass

    @abstractmethod
    def visit_empty_node(self, node):
        pass
