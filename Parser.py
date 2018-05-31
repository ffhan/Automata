import Parser_implementation
import sys

read = sys.stdin.readlines()

text = ''
for line in read:
    text += line
print(Parser_implementation.parser(text))