# main.py
from lib.regex_lib import RegexLib

def main():
    try:
        regex1 = RegexLib()
        # regex2 = RegexLib()

        regex1.compile("ab|c")
        # regex2.compile("a+")

        dfa_min = regex1.get_dfa_min()
        if dfa_min is None:
            print("Error: DFA minimization failed.")
            return

        # Augment the DFA
        augmented_dfa = dfa_min.augment()
        print("Augmented DFA created.")
        result = augmented_dfa.match("a")
        print(f"Result of matching 'a' in the augmented DFA: {result}")

        print(f"match : {dfa_min.match('cd')}")
        #print(f"findall: {regex1.findall('a')}") #- уходит в бесконечный луп
        #[] - не проходит dfa
        #{} - не проходит dfa
        

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
