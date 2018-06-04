"""
Defines all lexer tests.
"""
import unittest
import grammar.lexers as lex

class TestLexer(unittest.TestCase):

    def setUp(self):
        self.lexer = lex.StandardLexer()

    def test_scan(self):
        self.assertEqual(self.lexer.scan('_v4R1aB13 = 34.12 (4 == 5. while .123] ! !='),
                         [lex.Token('VARIABLE', '_v4R1aB13'),
                          lex.Token('ASSIGN', '='),
                          lex.Token('FLOAT', '34.12'),
                          lex.Token('LPARAM', '('),
                          lex.Token('INTEGER', '4'),
                          lex.Token('EQUAL', '=='),
                          lex.Token('FLOAT', '5.'),
                          lex.Token('WHILE', 'while'),
                          lex.Token('FLOAT', '.123'),
                          lex.Token('RBRACKET', ']'),
                          lex.UndefinedToken('!'),
                          lex.Token('INEQUAL', '!=')])
