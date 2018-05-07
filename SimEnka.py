import sys
from format import preformat

inp = sys.stdin.readlines()

text = ''
for i in inp:
    text += i
# print(text)
preformat.print_output(preformat.parse_e_nfa(text))