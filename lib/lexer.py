# lib/lexer.py

from lib.token import Token, TokenType

class Lexer:
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.position = 0
        self.length = len(pattern)

    def get_current_char(self) -> str:
        if self.position < self.length:
            return self.pattern[self.position]
        return '\0'  # End of input

    def advance(self):
        self.position += 1

    def peek(self) -> str:
        if self.position + 1 < self.length:
            return self.pattern[self.position + 1]
        return '\0'

    def get_token(self) -> Token:
        while self.position < self.length:
            ch = self.get_current_char()

            if ch == '\\':
                self.advance()
                next_char = self.get_current_char()
                if next_char.isdigit():
                    # Backreference
                    num_str = ''
                    while self.get_current_char().isdigit():
                        num_str += self.get_current_char()
                        self.advance()
                    return Token(TokenType.BACKREFERENCE, num_str)
                elif next_char in {'\\', '|', '[', ']', '(', ')', '{', '}', '.', '*', '+', '?', '$', ','}:
                    # Escaped special character
                    self.advance()
                    return Token(TokenType.ESCAPED_CHAR, next_char)
                else:
                    # Any other escaped character
                    self.advance()
                    return Token(TokenType.ESCAPED_CHAR, next_char)

            elif ch == '$':
                self.advance()
                return Token(TokenType.EMPTY_STRING, "$")

            elif ch == '|':
                self.advance()
                return Token(TokenType.OR, "|")

            elif ch == '.':
                # Treat '.' as a wildcard (any character)
                self.advance()
                return Token(TokenType.ANY_CHAR, ".")

            elif ch == '*':
                self.advance()
                return Token(TokenType.KLEENE_STAR, "*")

            elif ch == '+':
                self.advance()
                return Token(TokenType.PLUS, "+")

            elif ch == '?':
                self.advance()
                return Token(TokenType.QUESTION, "?")

            elif ch == '[':
                self.advance()
                return Token(TokenType.RANGE_START, "[")

            elif ch == ']':
                self.advance()
                return Token(TokenType.RANGE_END, "]")

            elif ch == '(':
                self.advance()
                if self.get_current_char() == ':':
                    self.advance()
                    return Token(TokenType.NON_CAPTURING_GROUP_START, "(:")
                else:
                    return Token(TokenType.GROUP_START, "(")

            elif ch == ')':
                self.advance()
                return Token(TokenType.GROUP_END, ")")

            elif ch == '{':
                self.advance()
                return Token(TokenType.REPEAT_START, "{")

            elif ch == '}':
                self.advance()
                return Token(TokenType.REPEAT_END, "}")

            elif ch == ',':
                self.advance()
                return Token(TokenType.COMMA, ",")

            elif ch.isdigit():
                # Numbers outside backreferences (if any)
                num_str = ''
                while self.get_current_char().isdigit():
                    num_str += self.get_current_char()
                    self.advance()
                return Token(TokenType.DIGIT, num_str)

            else:
                # Literal characters
                self.advance()
                return Token(TokenType.LITERAL, ch)

        return Token(TokenType.END, "")
