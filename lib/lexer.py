# regex_lib/lexer.py

from lib.token import Token, TokenType

class Lexer:
    def __init__(self, pattern):
        self.pattern = pattern
        self.position = 0

    def position_inc(self):
        self.position += 1

    def position_dec(self):
        self.position -= 1

    def get_current_char(self):
        if self.position < len(self.pattern):
            return self.pattern[self.position]
        return '\0'

    def skip(self):
        self.position_inc()
        if self.get_current_char() != '\0':
            return Token(TokenType.ESCAPE, self.get_current_char())
        raise SyntaxError(f"Invalid escape character: {self.get_current_char()}")

    def get_token(self):
        ch = self.get_current_char()
        while ch != '\0':
            if ch == '\'':
                return self.skip()
            elif ch == '$':
                self.position_inc()
                return Token(TokenType.EMPTY_STRING, "$")
            elif self.pattern[self.position:self.position + 3] == '...':
                self.position += 3
                return Token(TokenType.KLEENE_STAR, "...")
            elif ch == '|':
                self.position_inc()
                return Token(TokenType.OR, "|")
            elif ch == '[':
                self.position_inc()
                return self.parse_character_set()
            elif ch == ']':
                self.position_inc()
                return Token(TokenType.RANGE_END, "]")
            elif ch == '(':
                self.position_inc()
                return Token(TokenType.GROUP_START, "(")
            elif ch == ')':
                self.position_inc()
                return Token(TokenType.GROUP_END, ")")
            elif ch == '{':
                self.position_inc()
                return self.parse_repeat_expression()
            elif ch == '}':
                self.position_inc()
                return Token(TokenType.REPEAT_END, "}")
            elif ch.isalpha():  # Letters
                self.position_inc()
                return Token(TokenType.LETTER, ch)
            elif ch.isdigit():  # Digits
                self.position_inc()
                return Token(TokenType.DIGIT, ch)
            else:  # Any other symbol
                self.position_inc()
                return Token(TokenType.NOT_SPECIAL_SYMBOL, ch)

        return Token(TokenType.END, "")
    def parse_character_set(self):
        """
        Parse a character set inside [ ] brackets, e.g., [abc...] as individual characters.
        """
        character_set = []
        ch = self.get_current_char()

        while ch != ']' and ch != '\0':  # Continue until you find the closing bracket or EOF
            character_set.append(ch)
            self.position_inc()
            ch = self.get_current_char()
        if ch == ']':
            self.position_inc()  # Skip the closing ]
            return Token(TokenType.CHARACTER_SET, "".join(character_set))  # Return the set as a string or list
        else:
            raise SyntaxError("Unterminated character set")
    def parse_repeat_expression(self):
        """
        Parse the repeat expression of the form {x}.
        """
        self.position_inc()  # Move past the opening '{'
        repeat_value = self.parse_number()  # Extract the number inside the braces

        if self.get_current_char() == '}':
            self.position_inc()  # Move past the closing '}'
            return Token(TokenType.REPEAT_EXACT, str(repeat_value))
        else:
            raise SyntaxError(f"Expected `}}` at position {self.position}")
    
    def parse_number(self):
        """
        Parse a number from the current position.
        """
        num_str = ''
        ch = self.get_current_char()
        
        while ch.isdigit():
            num_str += ch
            self.position_inc()
            ch = self.get_current_char()
        
        return int(num_str) if num_str else None