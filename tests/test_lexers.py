"""
Defines all lexer tests.
"""
import unittest
from grammar.lexers import Token, StandardLexer, UndefinedToken, Lexer
import grammar.regular_expressions as regex

class TestLexer(unittest.TestCase):

    def setUp(self):
        self.lexer = StandardLexer()

    def test_scan(self):
        scanned = self.lexer.scan('_v4R1aB13 = 34.12 (4 == 5. while .123] ! !=')
        self.assertEqual(str(scanned),
                         str([Token(regex.VARIABLE, '_v4R1aB13'),
                          Token(regex.ASSIGN, '='),
                          Token(regex.FLOAT, '34.12'),
                          Token(regex.LPARAM, '('),
                          Token(regex.INTEGER, '4'),
                          Token(regex.EQUAL, '=='),
                          Token(regex.FLOAT, '5.'),
                          Token(regex.WHILE, 'while'),
                          Token(regex.FLOAT, '.123'),
                          Token(regex.RBRACKET, ']'),
                          UndefinedToken('!'),
                          Token(regex.INEQUAL, '!=')]))
        scan = self.lexer.scan("""
        A really hard example = this
        *exactly* ((this))!
        is equal == or =?""")
        self.assertEqual(str(scan),
                         str([Token(regex.NEWLINE, '\n'),
                         Token(regex.VARIABLE, 'A'),
                         Token(regex.VARIABLE, 'really'),
                         Token(regex.VARIABLE, 'hard'),
                         Token(regex.VARIABLE, 'example'),
                         Token(regex.ASSIGN, '='),
                         Token(regex.VARIABLE, 'this'),
                         Token(regex.NEWLINE, '\n'),
                         Token(regex.ASTERISK, '*'),
                         Token(regex.VARIABLE, 'exactly'),
                         Token(regex.ASTERISK, '*'),
                         Token(regex.LPARAM, '('),
                         Token(regex.LPARAM, '('),
                         Token(regex.VARIABLE, 'this'),
                         Token(regex.RPARAM, ')'),
                         Token(regex.RPARAM, ')'),
                         UndefinedToken('!'),
                         Token(regex.NEWLINE, '\n'),
                         Token(regex.VARIABLE, 'is'),
                         Token(regex.VARIABLE, 'equal'),
                         Token(regex.EQUAL, '=='),
                         Token(regex.VARIABLE, 'or'),
                         Token(regex.ASSIGN, '='),
                         UndefinedToken('?')]))

        scan2 = Lexer(regex.INTEGER, regex.FLOAT).scan('123.1234352436463.56')
        self.assertEqual(str(scan2),
                         str([Token(regex.FLOAT, '123.1234352436463'),
                          Token(regex.FLOAT, '.56')]))
        scan3 = Lexer(regex.WHILE, regex.VARIABLE).scan('whileab abwhile')
        self.assertEqual(str(scan3),
                         str([Token(regex.VARIABLE, 'whileab'),
                              Token(regex.VARIABLE, 'abwhile')]))
        scan4 = Lexer(regex.VARIABLE, regex.NUMBER).scan('1234abc123.')
        self.assertEqual(str(scan4),
                         str([Token(regex.NUMBER, '1234'),
                              Token(regex.VARIABLE, 'abc123'),
                              UndefinedToken('.')]))
        scan5 = Lexer(regex.VARIABLE, regex.INTEGER, regex.FLOAT, regex.DOT).scan(
            " 12 . 45   1234..9865 123.56")
        self.assertEqual(str(scan5),
                         str([Token(regex.INTEGER, '12'),
                              Token(regex.DOT, '.'),
                              Token(regex.INTEGER, '45'),
                              Token(regex.FLOAT, '1234.'),
                              Token(regex.FLOAT, '.9865'),
                              Token(regex.FLOAT, '123.56')]))
        scan6 = self.lexer.scan("""while var>=56.65:
        \tprint( 965<)""")
        self.assertEqual(str(scan6),
                         str([Token(regex.WHILE, 'while'),
                              Token(regex.VARIABLE, 'var'),
                              Token(regex.GE, '>='),
                              Token(regex.FLOAT, '56.65'),
                              Token(regex.COLON, ':'),
                              Token(regex.NEWLINE, '\n'),
                              Token(regex.TAB, '\t'),
                              Token(regex.VARIABLE, 'print'),
                              Token(regex.LPARAM, '('),
                              Token(regex.INTEGER, '965'),
                              Token(regex.LT, '<'),
                              Token(regex.RPARAM, ')')]))
