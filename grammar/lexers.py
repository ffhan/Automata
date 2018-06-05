"""
Defines all Lexer implementations.
"""
import abc
import grammar.regular_expressions as rgx

class BasicToken:
    """
    Defines a interface that all tokens have to follow.
    Does not contain a value (used for keywords)
    """
    def __init__(self, token_type):
        self.token_type = token_type
    def __repr__(self):
        return '<' + (self.token_type.name if isinstance(self.token_type, rgx.RegEx)
                      else self.token_type) + '>'

class BoundToken(BasicToken):
    """
    Defines a token that delimits other tokens in a list.
    """
    def __init__(self):
        super().__init__('_delimit_')

class Token(BasicToken):
    """
    Defines a Token, a result of a Lexer scan.
    """
    def __init__(self, token_type, token_value: str):
        """
        Initialises a Token. A token contains a token type (for example a variable, an integer..)
        and a value or an alias, what it's changing (token type: variable, token value: example_of_a_variable)

        :param str token_type: token type
        :param str token_value: token value
        """
        super().__init__(token_type)
        self.token_value = token_value

    def __repr__(self):
        return '<' + (self.token_type.name if isinstance(self.token_type, rgx.RegEx)
                      else self.token_type) + ", '{}'".format(self.token_value) + '>'

class UndefinedToken(Token):
    """
    Defines a Token that has not been matched by a lexer but isn't a whitespace.
    """
    def __init__(self, token_value: str):
        super().__init__('UNDEFINED', token_value)

class Lexer:
    """
    Bare bones Lexer implementation.
    """
    def __init__(self, *regexes): #todo: maybe design a container for regexes (because of precedence)
        """
        Creates a Lexer defined with regular expressions.

        :param regexes: regex class
        """
        self._regexes: list = regexes
        self._ignored = set()

    def add_ignored_characters(self, *ignored):
        """
        Adds all ignored characters

        :param ignored: all ignored characters
        :return:
        """
        self._ignored |= set(filter(lambda t : isinstance(t, str), ignored))

    # def scan(self, text: str)->list:
    #     """
    #     Scans the text and returns a list of found tokens.
    #
    #     :param str text: string of text
    #     :return list: a list containing tokens
    #     """
    #     start_index = -1
    #     # end_index = -1
    #
    #     current_regex = None
    #     tokens = []
    #     # print("entered", text)
    #     for i, char in enumerate(text):
    #         # print(i, char, "'{}'".format(text[start_index:i + 1]), current_regex, tokens)
    #         if start_index == -1:
    #             continue_flag = False
    #             for regex in self._regexes:
    #                 result = regex.check(char)
    #                 # print("'{}' {}".format(char, result), rgx.INEQUAL.check(char))
    #                 if result:
    #                     start_index = i
    #                     current_regex = regex
    #                     continue_flag = True
    #                     break
    #             if not continue_flag and char != ' ':
    #                 tokens.append(UndefinedToken(char))
    #         else:
    #             continue_flag = False
    #             for regex in self._regexes:
    #                 if current_regex.check(text[start_index:i + 1]):
    #                     continue_flag = True
    #                 elif regex.check(text[start_index:i + 1]) and regex != current_regex:
    #                     continue_flag = True
    #                     current_regex = regex
    #
    #                 if continue_flag:
    #                     break
    #             if not continue_flag:
    #                 tokens.append(Token(current_regex.name, text[start_index:i]))
    #                 # start_index = -1
    #                 # current_regex = None
    #                 tokens += self.scan(text[i:])
    #                 return tokens
    #     if start_index != -1 and current_regex:
    #         tokens.append(Token(current_regex.name, text[start_index:]))
    #     return tokens

    def _backtrack(self, tokens):
        """
        Backtracks through tokens and tries to merge them together.

        :param tokens:
        :return:
        """
        if len(tokens) > 1:
            value = tokens[-2].token_value + tokens[-1].token_value
            for rgx in self._regexes:
                if rgx.check(value):
                    tokens[-2:] = [Token(rgx, value)]
                    return self._backtrack(tokens)
        return tokens

    def _clean_ignored(self, tokens):
        """
        Removes all individual undefined variables that contain whitespace.
        This is wrong and should not be a thing.

        :param tokens:
        :return:
        """
        return list(filter(lambda t : t.token_value not in self._ignored, tokens))

    def scan(self, text: str)->list:
        """
        Scans the text and returns a list of found tokens.

        :param str text: string of text
        :return list: a list containing tokens
        """
        return self._clean_ignored(self._internal_scan(text))

    def _internal_scan(self, text: str)->list:
        """
        Scans the text and returns a list of found tokens.

        :param str text: string of text
        :return list: a list containing tokens
        """
        start_index = -1
        # end_index = -1

        current_regex = None
        tokens = []
        # print("entered", text)
        i = -1
        while i - 1 < len(text):
            # print(i, char, "'{}'".format(text[start_index:i + 1]), current_regex, tokens)
            i += 1
            if i >= len(text):
                break
            char = text[i]
            if start_index == -1:
                continue_flag = False
                for regex in self._regexes:
                    result = regex.check(text[i: i + regex.min_lookahead])
                    if result:
                        start_index = i
                        i += regex.min_lookahead - 1
                        # print('found', "'"+text[start_index:i + 1]+"'")
                        current_regex = regex
                        continue_flag = True
                        break
                if not continue_flag:
                    tokens.append(UndefinedToken(char))
            else:
                continue_flag = False
                # print('check', "'" + text[start_index:i+1] + "'", tokens)
                if current_regex.check(text[start_index:i + 1]):
                    continue_flag = True
                else:
                    for regex in self._regexes:
                        if regex.check(text[start_index:i + 1]) and regex != current_regex:
                            continue_flag = True
                            current_regex = regex

                        if continue_flag:
                            break
                if not continue_flag:
                    tokens.append(Token(current_regex, text[start_index:i]))
                    # start_index = -1
                    # current_regex = None
                    # print(tokens, "'{}'".format(text[start_index:i]))
                    tokens2 = self._internal_scan(text[i:])
                    if tokens2:
                        tokens += self._backtrack(tokens2)
                    return tokens
        if start_index != -1 and current_regex:
            tokens.append(Token(current_regex, text[start_index:]))
        # tokens = self._backtrack(tokens)

        return tokens

class StandardLexer(Lexer):
    """
    Defines a standard lexer, sufficient for a default wide-range use.
    """

    def __init__(self):
        super().__init__(rgx.WHILE, rgx.FOR, rgx.IN, rgx.RETURN, rgx.DEFINE,
                         rgx.CLASS, rgx.VARIABLE, rgx.FLOAT, rgx.INTEGER,
                         rgx.LPARAM, rgx.RPARAM, rgx.LBRACKET, rgx.RBRACKET,
                         rgx.ASSIGN, rgx.EQUAL, rgx.INEQUAL, rgx.LE, rgx.GE,
                         rgx.LT, rgx.GT, rgx.NEWLINE, rgx.TAB, rgx.SINGLEQUOTE,
                         rgx.DOUBLEQUOTE, rgx.ASTERISK, rgx.COMMA, rgx.DOT,
                         rgx.SLASH, rgx.BACKSLASH, rgx.SEMICOLON, rgx.COLON,
                         rgx.PLUS, rgx.MINUS, rgx.DIV)
        self.add_ignored_characters(' ')