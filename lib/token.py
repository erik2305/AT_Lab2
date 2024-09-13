# regex_lib/token.py
from enum import Enum

class TokenType(Enum):
    LETTER = "LETTER"
    DIGIT = "DIGIT"
    OR = "OR"
    KLEENE_STAR = "KLEENE_STAR"
    GROUP_START = "GROUP_START"
    GROUP_END = "GROUP_END"
    RANGE_START = "RANGE_START"
    RANGE_END = "RANGE_END"
    ESCAPE = "ESCAPE"
    EMPTY_STRING = "EMPTY_STRING"
    REPEAT_START = "REPEAT_START"
    REPEAT_END = "REPEAT_END"
    NOT_SPECIAL_SYMBOL = "NOT_SPECIAL_SYMBOL"
    LOOKAHEAD = "LOOKAHEAD"
    END = "END"
    CHARACTER_SET = "CHARACTER_SET"
    REPEAT_EXACT = "REPEAT_EXACT"

class Token:
    def __init__(self, token_type, symbol):
        self.type = token_type  # TokenType instance
        self.symbol = symbol    # The actual character or string

    def __repr__(self):
        return f"Token({self.type}, '{self.symbol}')"
