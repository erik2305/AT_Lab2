from lib.lexer import Lexer
from lib.parser import Parser
from lib.nfa_builder_visitor import NFABuilderVisitor
from lib.nfa_to_dfa_converter import NFAtoDFAConverter
from lib.regex_recovery import RegexRecovery
from lib.dfa import DFA
from lib.nfa import NFA

class RegexLib:
    def __init__(self):
        self.dfa_min: DFA = None

    def compile(self, pattern: str):

        try:
            lexer = Lexer(pattern)
            parser = Parser(lexer)
            ast_tree = parser.parse()

            nfa_builder = NFABuilderVisitor()
            ast_tree.accept(nfa_builder)
            nfa: NFA = nfa_builder.get_nfa()

            converter = NFAtoDFAConverter()
            dfa: DFA = converter.convert(nfa)

            minimized_dfa = dfa.minimize()
            self.dfa_min = minimized_dfa

            print(f"Compilation successful. Minimized DFA has {len(self.dfa_min.states)} states.")

        except Exception as e:
            print(f"Error during compilation: {e}")
            self.dfa_min = None

    def match(self, string: str) -> bool:
        if not self.dfa_min:
            print("Error: No compiled regex. Please compile a pattern first.")
            return False
        return self.dfa_min.match(string)

    def findall(self, string: str) -> list:
        if not self.dfa_min:
            print("Error: No compiled regex. Please compile a pattern first.")
            return []
        return self.dfa_min.findall(string)

    def complement(self) -> DFA:

        if not self.dfa_min:
            print("Error: No compiled regex. Please compile a pattern first.")
            return None
        return self.dfa_min.complement()

    def recover_regex(self) -> str:

        if not self.dfa_min:
            print("Error: No compiled DFA to recover regex from.")
            return None
        recovery = RegexRecovery()
        regex = recovery.recover_regex(self.dfa_min)
        return regex
