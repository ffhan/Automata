"""
Defines all lexer tests.
"""
import unittest
from grammar.lexers import Token, StandardLexer, UndefinedToken, Lexer
from grammar.regular_expressions import REGEXES

class TestLexer(unittest.TestCase):

    def setUp(self):
        self.lexer = StandardLexer()

    def test_scan(self):
        scanned = self.lexer.scan('_v4R1aB13 = 34.12 (4 == 5. while .123] ! !=')
        self.assertEqual(str(scanned),
                         str([Token(REGEXES['VARIABLE'], '_v4R1aB13'),
                          Token(REGEXES['ASSIGN'], '='),
                          Token(REGEXES['FLOAT'], '34.12'),
                          Token(REGEXES['LPARAM'], '('),
                          Token(REGEXES['INTEGER'], '4'),
                          Token(REGEXES['EQUAL'], '=='),
                          Token(REGEXES['FLOAT'], '5.'),
                          Token(REGEXES['WHILE'], 'while'),
                          Token(REGEXES['FLOAT'], '.123'),
                          Token(REGEXES['RBRACKET'], ']'),
                          UndefinedToken('!'),
                          Token(REGEXES['INEQUAL'], '!=')]))
        scan = self.lexer.scan("""
        A really hard example = this
        *exactly* ((this))!
        is equal == or =?""")
        self.assertEqual(str(scan),
                         str([Token(REGEXES['NEWLINE'], '\n'),
                         Token(REGEXES['VARIABLE'], 'A'),
                         Token(REGEXES['VARIABLE'], 'really'),
                         Token(REGEXES['VARIABLE'], 'hard'),
                         Token(REGEXES['VARIABLE'], 'example'),
                         Token(REGEXES['ASSIGN'], '='),
                         Token(REGEXES['VARIABLE'], 'this'),
                         Token(REGEXES['NEWLINE'], '\n'),
                         Token(REGEXES['ASTERISK'], '*'),
                         Token(REGEXES['VARIABLE'], 'exactly'),
                         Token(REGEXES['ASTERISK'], '*'),
                         Token(REGEXES['LPARAM'], '('),
                         Token(REGEXES['LPARAM'], '('),
                         Token(REGEXES['VARIABLE'], 'this'),
                         Token(REGEXES['RPARAM'], ')'),
                         Token(REGEXES['RPARAM'], ')'),
                         UndefinedToken('!'),
                         Token(REGEXES['NEWLINE'], '\n'),
                         Token(REGEXES['IS'], 'is'),
                         Token(REGEXES['VARIABLE'], 'equal'),
                         Token(REGEXES['EQUAL'], '=='),
                         Token(REGEXES['VARIABLE'], 'or'),
                         Token(REGEXES['ASSIGN'], '='),
                         UndefinedToken('?')]))

        scan2 = Lexer(REGEXES['INTEGER'], REGEXES['FLOAT']).add_ignored_characters(
            ' ').scan('123.1234352436463.56')
        self.assertEqual(str(scan2),
                         str([Token(REGEXES['FLOAT'], '123.1234352436463'),
                          Token(REGEXES['FLOAT'], '.56')]))
        scan3 = Lexer(REGEXES['WHILE'], REGEXES['VARIABLE']).add_ignored_characters(
            ' ').scan('whileab abwhile')
        self.assertEqual(str(scan3),
                         str([Token(REGEXES['VARIABLE'], 'whileab'),
                              Token(REGEXES['VARIABLE'], 'abwhile')]))
        scan4 = Lexer(REGEXES['VARIABLE'], REGEXES['NUMBER']).add_ignored_characters(
            ' ').scan('1234abc123.')
        self.assertEqual(str(scan4),
                         str([Token(REGEXES['NUMBER'], '1234'),
                              Token(REGEXES['VARIABLE'], 'abc123'),
                              UndefinedToken('.')]))
        scan5 = Lexer(REGEXES['VARIABLE'], REGEXES['INTEGER'],
                      REGEXES['FLOAT'], REGEXES['DOT']).add_ignored_characters(
            ' ').scan(
            " 12 . 45   1234..9865 123.56")
        self.assertEqual(str(scan5),
                         str([Token(REGEXES['INTEGER'], '12'),
                              Token(REGEXES['DOT'], '.'),
                              Token(REGEXES['INTEGER'], '45'),
                              Token(REGEXES['FLOAT'], '1234.'),
                              Token(REGEXES['FLOAT'], '.9865'),
                              Token(REGEXES['FLOAT'], '123.56')]))
        scan6 = self.lexer.scan("""while var>=56.65:
        \tprint( 965<)""")
        self.assertEqual(str(scan6),
                         str([Token(REGEXES['WHILE'], 'while'),
                              Token(REGEXES['VARIABLE'], 'var'),
                              Token(REGEXES['GE'], '>='),
                              Token(REGEXES['FLOAT'], '56.65'),
                              Token(REGEXES['COLON'], ':'),
                              Token(REGEXES['NEWLINE'], '\n'),
                              Token(REGEXES['TAB'], '\t'),
                              Token(REGEXES['VARIABLE'], 'print'),
                              Token(REGEXES['LPARAM'], '('),
                              Token(REGEXES['INTEGER'], '965'),
                              Token(REGEXES['LT'], '<'),
                              Token(REGEXES['RPARAM'], ')')]))
