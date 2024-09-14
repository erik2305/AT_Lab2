# main.py

from lib.regex_lib import RegexLib

def main():
    regex = RegexLib()
    pattern = r"(a|b)*c{2,3}"
    print(f"Compiling pattern: {pattern}")
    regex.compile(pattern)

    test_strings = ["aaabcc", "ababc", "c", "abcc", "abccc", "abcccc"]
    for s in test_strings:
        result = regex.match(s)
        print(f"Match('{s}') = {result}")

    # Find all matches in a larger string
    search_string = "aaabccabcccabcccc"
    matches = regex.findall(search_string)
    print(f"Findall in '{search_string}': {matches}")

    # Complement DFA
    complement_dfa = regex.complement()
    if complement_dfa:
        complement_result = complement_dfa.match("abcc")
        print(f"Complement Match('abcc') = {complement_result}")

    # Recover regex from DFA
    recovered_pattern = regex.recover_regex()
    print(f"Recovered Regex: {recovered_pattern}")

if __name__ == "__main__":
    main()
