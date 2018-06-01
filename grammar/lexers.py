"""
Defines all Lexer implementations.
"""
import abc
import grammar.regular_expressions as rgx

class Token:
    """
    Defines a Token, a result of a Lexer scan.
    """
    def __init__(self, token_type: str, token_value: str):
        """
        Initialises a Token. A token contains a token type (for example a variable, an integer..)
        and a value or an alias, what it's changing (token type: variable, token value: example_of_a_variable)

        :param str token_type: token type
        :param str token_value: token value
        """
        self.token_type = token_type
        self.token_value = token_value

    def __repr__(self):
        return '<' + self.token_type + ', ' + self.token_value + '>'

class Lexer:
    """
    Bare bones Lexer implementation.
    """
    def __init__(self, *regexes):
        """
        Creates a Lexer defined with regular expressions.

        :param regexes: regex class
        """
        self._regexes: list = regexes

    def scan(self, text):

        start_index = -1
        # end_index = -1

        current_regex = None
        tokens = []
        # print(text)
        for i, char in enumerate(text):
            # print(i, char, "'{}'".format(text[start_index:i + 1]), current_regex, tokens)
            if start_index == -1:
                for regex in self._regexes:
                    result = regex.check(char)
                    #todo: fix a bug where if this is removed it doesn't see t in this
                    if regex.check(char):
                        start_index = i
                        current_regex = regex
                        break
            else:
                continue_flag = False
                for regex in self._regexes:
                    if regex.check(text[start_index:i + 1]) and regex != current_regex:
                        continue_flag = True
                        current_regex = regex
                    elif current_regex.check(text[start_index:i + 1]):
                        continue_flag = True
                    if continue_flag:
                        break
                if not continue_flag:
                    tokens.append(Token(current_regex.name, text[start_index:i]))
                    # start_index = -1
                    # current_regex = None
                    tokens += self.scan(text[i:])
                    return tokens
        if start_index != -1 and current_regex:
            tokens.append(Token(current_regex.name, text[start_index:]))
        return tokens

class StandardLexer(Lexer):
    """
    Defines a standard lexer, sufficient for a default wide-range use.
    """

    def __init__(self):
        super().__init__(rgx.VARIABLE, rgx.FLOAT, rgx.INTEGER, rgx.LPARAM,
                         rgx.RPARAM, rgx.LBRACKET, rgx.RBRACKET, rgx.ASSIGN,
                         rgx.EQUALITY)