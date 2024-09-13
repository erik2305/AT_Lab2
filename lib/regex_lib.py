# regex_lib/regex_lib.py

from regex_lib.lexer import Lexer
from regex_lib.parser import Parser
from regex_lib.nfa_builder_visitor import NFABuilderVisitor
from regex_lib.nfa_to_dfa_converter import NFAtoDFAConverter

class RegexLib:
    def __init__(self):
        self.dfa_min = None

    def get_dfa_min(self):
        return self.dfa_min

    def set_dfa_min(self, dfa_min):
        self.dfa_min = dfa_min

    def compile(self, pattern):
        try:
            lexer = Lexer(pattern)
            parser = Parser(lexer)
            ast_tree = parser.parse()
    
            nfa_builder = NFABuilderVisitor()
            ast_tree.accept(nfa_builder)
    
            nfa = nfa_builder.get_nfa()
            print(f"Generated NFA: {nfa}")
    
            # Convert NFA to DFA
            converter = NFAtoDFAConverter()
            dfa = converter.convert(nfa)
            if dfa is None:
                raise ValueError("DFA conversion failed")
            print(f"Generated DFA: {dfa}")
    
            # Minimize the DFA
            self.dfa_min = dfa.minimize()
            if self.dfa_min is None:
                raise ValueError("DFA minimization failed")
            print(f"Minimized DFA: {self.dfa_min}")
    
        except Exception as e:
            print(f"Error during compile: {e}")
            self.dfa_min = None

    def match(self, string):
        if self.dfa_min is None:
            print("DFA Min is not initialized.")
            return False
        return self.dfa_min.match(string)

    def match_with_dfa(self, dfa, string):
        return dfa.match(string)

    def findall(self, string):
        if self.dfa_min is None:
            print("DFA Min is not initialized.")
            return []
        return self.dfa_min.findall(string)

    def findall_with_dfa(self, dfa, string):
        return dfa.findall(string)

    def inverse(self):
        if self.dfa_min is None:
            print("Cannot perform inverse: DFA is None")
            return None
        return self.dfa_min.inverse()