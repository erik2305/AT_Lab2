# lib/parser.py

from lib.ast_tree import (
    ASTTree, CharNode, ConcatNode, OrNode, StarNode, GroupNode,
    RepeatNode, RangeNode, BackreferenceNode, EmptyNode, CharacterSetNode, RepeatExactNode
)
from lib.lexer import Lexer
from lib.token import TokenType, Token

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token: Token = self.lexer.get_token()
        self.group_num = 1  # Start numbering groups from 1

    def parse(self) -> ASTTree:
        return self.regex()

    def consume(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_token()
        else:
            raise SyntaxError(f"Expected token {token_type}, got {self.current_token.type}")

    def regex(self) -> ASTTree:
        """
        regex := term ('|' term)*
        """
        node = self.term()
        while self.current_token.type == TokenType.OR:
            self.consume(TokenType.OR)
            right = self.term()
            node = OrNode(node, right)
        return node

    def term(self) -> ASTTree:
        """
        term := factor+
        """
        nodes = []
        while self.current_token.type in (
            TokenType.LETTER , TokenType.ESCAPED_CHAR, TokenType.GROUP_START,
            TokenType.NON_CAPTURING_GROUP_START, TokenType.RANGE_START, TokenType.NOT_SPECIAL_SYMBOL, TokenType.EMPTY_STRING
        ):
            nodes.append(self.factor())
        if not nodes:
            return EmptyNode()
        node = nodes[0]
        for next_node in nodes[1:]:
            node = ConcatNode(node, next_node)
        return node

    def factor(self) -> ASTTree:
        """
        factor := atom ('*' | '+' | '?' | '{' number [',' number] '}')*
        """
        node = self.atom()
        while self.current_token.type in (
            TokenType.KLEENE_STAR, TokenType.PLUS, TokenType.QUESTION, TokenType.REPEAT_START
        ):
            if self.current_token.type == TokenType.KLEENE_STAR:
                self.consume(TokenType.KLEENE_STAR)
                node = StarNode(node)
            elif self.current_token.type == TokenType.PLUS:
                self.consume(TokenType.PLUS)
                node = RepeatNode(child=node, min_repeats=1, max_repeats=None)
            elif self.current_token.type == TokenType.QUESTION:
                self.consume(TokenType.QUESTION)
                node = RepeatNode(child=node, min_repeats=0, max_repeats=1)
            elif self.current_token.type == TokenType.REPEAT_START:
                node = self.repeat(node)
        return node

    def atom(self) -> ASTTree:
        """
        atom := LETTER | ESCAPED_CHAR | '.' | '(' regex ')' | '(?:' regex ')' | '[' range ']' | '$' | '\\' number
        """
        token = self.current_token
        if token.type == TokenType.LETTER:
            self.consume(TokenType.LETTER)
            return CharNode(token.value)
        elif token.type == TokenType.ESCAPED_CHAR:
            self.consume(TokenType.ESCAPED_CHAR)
            return CharNode(token.value)
        elif token.type == TokenType.NOT_SPECIAL_SYMBOL:
            self.consume(TokenType.NOT_SPECIAL_SYMBOL)
            # Represent '.' as a character set of all printable characters except newline
            import string
            characters = set(string.printable) - {'\n', '\r'}
            return CharacterSetNode(characters)
        elif token.type == TokenType.GROUP_START:
            self.consume(TokenType.GROUP_START)
            node = self.regex()
            self.consume(TokenType.GROUP_END)
            group_node = GroupNode(child=node, group_num=self.group_num, capturing=True)
            self.group_num += 1
            return group_node
        elif token.type == TokenType.NON_CAPTURING_GROUP_START:
            self.consume(TokenType.NON_CAPTURING_GROUP_START)
            node = self.regex()
            self.consume(TokenType.GROUP_END)
            return GroupNode(child=node, capturing=False)
        elif token.type == TokenType.RANGE_START:
            return self.character_set()
        elif token.type == TokenType.EMPTY_STRING:
            self.consume(TokenType.EMPTY_STRING)
            return EmptyNode()
        elif token.type == TokenType.BACKREFERENCE:
            self.consume(TokenType.BACKREFERENCE)
            group_num = int(token.value)
            return BackreferenceNode(group_num=group_num)
        else:
            raise SyntaxError(f"Unexpected token: {token.type}")

    def character_set(self) -> ASTTree:
        """
        character_set := '[' '^'? range ']'
        range := ... (to be implemented)
        """
        self.consume(TokenType.RANGE_START)
        negated = False
        if self.current_token.type == TokenType.ESCAPED_CHAR and self.current_token.value == '^':
            negated = True
            self.consume(TokenType.ESCAPED_CHAR)
        ranges = []
        while self.current_token.type != TokenType.RANGE_END:
            if self.current_token.type == TokenType.LETTER or self.current_token.type == TokenType.ESCAPED_CHAR:
                first_char = self.current_token.value
                self.consume(self.current_token.type)
                if self.current_token.type == TokenType.ESCAPED_CHAR and self.current_token.value == '-':
                    self.consume(TokenType.ESCAPED_CHAR)
                    if self.current_token.type in (TokenType.LETTER, TokenType.ESCAPED_CHAR):
                        second_char = self.current_token.value
                        self.consume(self.current_token.type)
                        ranges.append((first_char, second_char))
                    else:
                        raise SyntaxError("Invalid range in character set")
                else:
                    ranges.append((first_char, first_char))
            else:
                raise SyntaxError("Invalid character in character set")
        self.consume(TokenType.RANGE_END)
        return RangeNode(ranges=ranges, negated=negated)

    def repeat(self, node: ASTTree) -> ASTTree:
        """
        Handles repetition constructs like {x}, {x,}, {x,y}
        """
        self.consume(TokenType.REPEAT_START)
        min_repeats = self.number()
        max_repeats = min_repeats
        if self.current_token.type == TokenType.COMMA:
            self.consume(TokenType.COMMA)
            if self.current_token.type == TokenType.DIGIT:
                max_repeats = self.number()
            else:
                max_repeats = None  # No upper limit
        self.consume(TokenType.REPEAT_END)
        return RepeatNode(child=node, min_repeats=min_repeats, max_repeats=max_repeats)

    def number(self) -> int:
        """
        Parses a number (one or more digits)
        """
        token = self.current_token
        if token.type == TokenType.DIGIT:
            num = int(token.value)
            self.consume(TokenType.DIGIT)
            return num
        else:
            raise SyntaxError(f"Expected number, got {token.type}")
