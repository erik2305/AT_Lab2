# regex_lib/parser.py

from lib.ast_tree import *
from lib.lexer import Lexer
from lib.token import TokenType

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        self.advance()

    def advance(self):
        self.current_token = self.lexer.get_token()
        print(f"Advanced to token: {self.current_token.type} with symbol: {self.current_token.symbol}")

    def match(self, expected_type):
        if self.current_token.type == expected_type:
            self.advance()
        else:
            raise Exception(f"Unexpected token: {self.current_token.type}")

    def parse(self):
        tree = self.regex()
        return tree

    def regex(self):
        print("Entering regex()")
        left = self.term()
        while self.current_token.type == TokenType.OR:
            print("Found OR operator")
            self.advance()
            right = self.term()
            left = OrNode(left, right)  # Ensure this creates an OrNode for the alternation
        print("Exiting regex()")
        return left


    def term(self):
        print("Entering term()")
        node = self.factor()
        while self.is_literal(self.current_token) or self.current_token.type in [TokenType.GROUP_START, TokenType.RANGE_START]:
            print("Concatenating factors")
            next_factor = self.factor()
            node = ConcatNode(node, next_factor)
        print("Exiting term()")
        return node

    def is_literal(self, token):
        return token.type in [TokenType.LETTER, TokenType.DIGIT, TokenType.NOT_SPECIAL_SYMBOL]

    def factor(self):
        node = self.atom()
        if self.current_token.type == TokenType.CHARACTER_SET:
            return self.parse_character_set_node()
        if self.current_token.type == TokenType.REPEAT_EXACT:
            return self.parse_repeat_node()
        while self.current_token.type in [TokenType.KLEENE_STAR, TokenType.REPEAT_START, TokenType.LOOKAHEAD]:
            if self.current_token.type == TokenType.KLEENE_STAR:
                self.advance()
                node = StarNode(node)
            elif self.current_token.type == TokenType.REPEAT_START:
                node = self.parse_repeat(node)
            elif self.current_token.type == TokenType.LOOKAHEAD:
                self.advance()
                lookahead_expr = self.regex()
                node = LookaheadNode(node, lookahead_expr)
        return node

    def atom(self):
        if self.current_token.type == TokenType.GROUP_START:
            print("Starting a group")
            self.advance()
            node = self.regex()
            self.match(TokenType.GROUP_END)
            print("Group parsed successfully")
            return GroupNode(node)
        elif self.current_token.type == TokenType.RANGE_START:
            return self.parse_range()
        elif self.current_token.type == TokenType.ESCAPE:
            self.advance()
            if self.current_token.type in [TokenType.REPEAT_START, TokenType.REPEAT_END, TokenType.GROUP_START, TokenType.GROUP_END,
                                           TokenType.OR, TokenType.RANGE_START, TokenType.RANGE_END, TokenType.LOOKAHEAD]:
                value = self.current_token.symbol
                self.advance()
                return CharNode(value)
            elif self.is_literal(self.current_token):
                value = self.current_token.symbol
                self.advance()
                return CharNode(value)
            else:
                raise (f"Unexpected token after escape: {self.current_token.type}")
        elif self.is_literal(self.current_token):
            value = self.current_token.symbol
            self.advance()
            return CharNode(value)
        elif self.current_token.type == TokenType.EMPTY_STRING:
            self.advance()
            return EmptyNode()
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token.type}, symbol: {self.current_token.symbol}")

    def parse_range(self):
        ranges = []
        self.advance()
        current_range = []
        while self.current_token.type != TokenType.RANGE_END:
            if self.is_literal(self.current_token):
                current_range.append(self.current_token.symbol)
                self.advance()
                if self.current_token.type == TokenType.NOT_SPECIAL_SYMBOL and self.current_token.symbol == '-':
                    current_range.append('-')
                    self.advance()
                    current_range.append(self.current_token.symbol)
                    ranges.append(''.join(current_range))
                    current_range = []
                    self.advance()
                else:
                    ranges.append(''.join(current_range))
                    current_range = []
        self.advance()
        return RangeNode(ranges)

    def parse_repeat(self, child):
        min_repeats = None
        max_repeats = None
        self.advance()

        if self.current_token.type == TokenType.DIGIT:
            min_repeats = int(self.current_token.symbol)
            self.advance()

        if self.current_token.type == TokenType.NOT_SPECIAL_SYMBOL and self.current_token.symbol == ',':
            self.advance()
            if self.current_token.type == TokenType.DIGIT:
                max_repeats = int(self.current_token.symbol)
                self.advance()

        self.match(TokenType.REPEAT_END)

        return RepeatNode(child, min_repeats, max_repeats)
    def parse_character_set_node(self):
        """
        Handle the CHARACTER_SET token by creating a corresponding AST node.
        """
        char_set = self.current_token.symbol  # Get the character set
        self.advance()  # Move to the next token
        return CharacterSetNode(char_set)  # Create a new AST node for the character set
    def parse_repeat_node(self):
        """
        Handle the REPEAT_EXACT token by creating a corresponding AST node.
        """
        repeat_value = int(self.current_token.symbol)  # Get the number of repetitions
        self.advance()  # Move to the next token
        return RepeatExactNode(repeat_value)