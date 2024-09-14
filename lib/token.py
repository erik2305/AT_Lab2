# lib/token.py
from enum import Enum, auto

class TokenType(Enum):
    LITERAL = auto()
    ESCAPED_CHAR = auto()
    OR = auto()
    KLEENE_STAR = auto()
    PLUS = auto()
    QUESTION = auto()
    RANGE_START = auto()
    RANGE_END = auto()
    GROUP_START = auto()
    GROUP_END = auto()
    NON_CAPTURING_GROUP_START = auto()
    REPEAT_START = auto()
    REPEAT_END = auto()
    BACKREFERENCE = auto()
    EMPTY_STRING = auto()
    ANY_CHAR = auto()
    COMMA = auto()
    DIGIT = auto()
    END = auto()

class Token:
    def __init__(self, token_type: TokenType, value: str):
        self.type = token_type
        self.value = value     

    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"
