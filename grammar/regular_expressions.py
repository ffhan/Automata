"""
Defines a regular expression type and all default regular expression checkers.
"""
import grammar.operators as operators
import os
dirname = os.path.dirname(__file__)

class RegEx:
    """
    Defines a class that handles all regular expression needs.
    Currently compiles to epsilon NFA, but that will be bound to change.
    """
    #todo: fix nfa to dfa casting and add compile method that does: operator->e_nfa->nfa->dfa->minimised dfa
    #todo: multiple collation [a-z,A-Z]
    #todo: anchoring
    #todo: {min, max} repetitions
    #todo: advanced collation with ^ (not operator) and . (any character)
    # all these things are going to be implemented when the parser is done.
    # they all require a pretty advanced parser, this structure cannot safely support these features.
    unary_operators = {'+': operators.KleenePlus,
                       '?': operators.QuestionMark,
                       '*': operators.KleeneStar,
                       '': operators.Single}
    binary_operators = {'|': operators.Alternation,
                        '': operators.Concatenation}



    def __init__(self, text: str, name: str = 'placeholder'):
        """
        Initializes a regular expression out of rules defined in a text.

        Rules are as follows:

        Quantification:
            * - 0 or more occurrences
            ? - 0 or 1 occurrence
            + - 1 or more occurrences
        UNION:
            a|b - a or b
        Concatenation:
            ab - a and b

        Collation:
            [a-z] - all characters from a to z (both included)

        Grouping:
            (a|b)c - a or b and then c

            This differs from a|bc because the former accepts ac while the latter does not.

        Escaped character:
            'a\[bc\]' - 'a[bc]'

        :param str name: name that describes a particular regexp
        :param str text: text describing a regular expression
        """

        self._name = name

        self._text = text

        self._groups = self._extract_bracket(text)
        self._groups = self._process(self._groups)
        self.automaton = self._groups.execute()
        # self.compile()

    @property
    def valid_characters(self)->set:
        """
        Returns all valid characters defined in this regex.

        :return set: a set of all valid characters
        """
        return self.automaton.inputs

    @property
    def name(self)->str:
        """
        Property that returns a name

        :return str: regex name
        """
        return self._name

    def __repr__(self):
        return '<' + self.name + '>'

    def create_checker(self):
        """
        Returns a checking function, since the class itself is not needed
        after object creation.

        :return: check function
        """
        return self.check

    def check(self, text)->bool:
        """
        Checks if a particular input is accepted by a regex.

        :param str text: input text
        :return bool: True if accepted, False if not
        """
        #resetting before everything somehow fixed the 't' bug. Don't know how.
        self.automaton.reset()
        for char in text:
            if not char in self.valid_characters:
                return False
            self.automaton.enter(char)
        is_ok = self.automaton.accepted
        # self.automaton.reset()
        return is_ok

    def _process(self, group: list)->operators.Operator:
        """
        Completely processes a text and returns a single Operator
        for a specified list of items.

        :param list group: a list of items
        :return Operator: single operator
        """
        group = self._escape_characters(group)
        group = self._collate(group)
        group = self._process_sublists(group)
        group = self._to_unary_operators(group)
        group = self._concatenate(group)
        group = self._alternate(group)
        group = self._clean(group)

        if len(group) > 1:
            # print(group)
            raise ValueError('Parsing failed.')
        return group[0]

    def _escape_characters(self, group: list)->list:
        """
        Escapes characters after \ symbol to a Single operator.

        :param list group: a list of items
        :return list: a processed list of items
        """

        copied_group = group.copy()
        compressed = 0

        for i, item in enumerate(group):
            if i >= len(group) - compressed:
                break
            if item == '\\':
                copied_group[i - compressed : i + 2 - compressed] = \
                    [operators.Single(copied_group[i + 1 - compressed])]
                compressed += 1
        return copied_group

    def _extract_bracket(self, text: str)->list:
        """
        Extracts all individual brackets in a list.

        :param str text: text to be extracted
        :return list: list of all extracted brackets.
        """
        par_count = 0
        lpar_index = -1
        rpar_index = -1
        result = []
        # print(text)
        for i, char in enumerate(text):
            if char == '(':
                if i > 0:
                    if text[i - 1] == '\\':
                        result.append(char)
                        continue
                par_count += 1
                if lpar_index == -1:
                    lpar_index = i
            elif char == ')':
                if i > 0:
                    if text[i - 1] == '\\':
                        result.append(char)
                        continue
                par_count -= 1
                rpar_index = i
            else:
                if not lpar_index >= 0:
                    result.append(char)
            # print('\t', char, lpar_index, rpar_index, par_count, result, i)
            if par_count == 0 and lpar_index >= 0 and rpar_index >= 0:
                result.append(self._extract_bracket(text[lpar_index+1:rpar_index]))
                lpar_index = -1
                rpar_index = -1
        if par_count != 0:
            raise ValueError('Unbalanced parentheses.')
        # print("exiting", text, result)
        return result

    @staticmethod
    def _collate(group: list)->list:
        """
        Processes all collate operators found within a list (string to operator)

        :param list group: a list of items
        :return list: a list where all string like collates where processed to operators
        """

        copied_groups = group.copy()

        lpar_index = -1 # [ symbol
        dash_index = -1 # - symbol

        compressed = 0

        for i, item in enumerate(group):
            if item == '[':
                lpar_index = i
            elif item == '-':
                dash_index = i
            elif item == ']':
                if dash_index != -1:
                    collation = operators.Collation(*copied_groups[lpar_index+1-compressed:i-compressed:2])
                    copied_groups[lpar_index-compressed:i+1-compressed] = [collation]
                    compressed += 4
                else:
                    raise ValueError('Collation parsing failed, missing "-" character')
        return copied_groups

    def _process_sublists(self, group: list)->list:
        """
        Processes all sublists to operators.

        :param list group: a list of items
        :return list: processed list of items without sublists
        """

        copied_groups = group.copy()

        for i, item in enumerate(group):
            if isinstance(item, list):
                item = self._process(item)
                copied_groups[i] = item
        return copied_groups

    def _to_unary_operators(self, group: list)->list:
        """
        Processes all unary operators from string representation to operator object.

        :param list group: a list of items
        :return list: processed list of items
        """

        copied_groups = group.copy()

        compressed = 0

        for i, item in enumerate(group):
            if isinstance(item, list):
                copied_groups[i - compressed] = self._process(item)
                continue
            elif item in self.unary_operators:
                copied_groups[i - 1 - compressed : i + 1 - compressed] = \
                    [self.unary_operators[item](copied_groups[i - 1 - compressed])]
                compressed += 1
        return copied_groups

    def _concatenate(self, group: list)->list:
        """
        Processes all concatenations to operators.

        :param list group: a list of items
        :return list: processed list of items
        """

        copied_groups = group.copy()

        compressed = 0

        for i, item in enumerate(group):
            next_char = '' if i + 1 >= len(group) else group[i + 1]

            if isinstance(item, list):
                processed = self._process(item)
                copied_groups[i - compressed] = processed
                continue
            elif item not in self.binary_operators and (next_char not in self.binary_operators):
                # print("concatenating", item, next_char)
                copied_groups[i - compressed : i + 2 - compressed] = \
                    [operators.Concatenation(copied_groups[i - compressed],
                                             copied_groups[i + 1 - compressed])]
                compressed += 1

            # print(item, copied_groups)
        return copied_groups

    def _alternate(self, group: list)->list:
        """
        Processes all alternations to operators.

        :param list group: a list of items
        :return list: processed list of items
        """

        copied_groups = group.copy()

        compressed = 0

        for i, item in enumerate(group):

            if isinstance(item, list):
                processed = self._process(item)
                copied_groups[i - compressed] = processed
                continue
            elif item in self.binary_operators:
                copied_groups[i - 1 - compressed: i + 2 - compressed] = \
                    [self.binary_operators[item](copied_groups[i - 1 - compressed],
                                                 copied_groups[i + 1 - compressed])]
                compressed += 2
        return copied_groups

    def _clean(self, group: list)->list:
        """
        Final cleanup, replaces all loose characters with Single operators.

        :param list group: a list of items
        :return list: a processed list of items
        """

        for i, item in enumerate(group):
            if isinstance(item, str):
                group[i] = operators.Single(item)
        return group

    def compile(self):
        """
        Compiles a regex and saves it on a drive.

        :return:
        """
        from misc.helper import save_object
        save_object(self, self.name, 'regex', dirname + '\\compiled_regexes\\')
    @staticmethod
    def load(name: str):
        """
        Loads a regex from compiled_regexes directory.

        :param str name: regex file name
        :return RegEx: loaded regex object
        """
        from misc.helper import load_object
        return load_object(dirname + '\\compiled_regexes\\' + name + '.regex')

def check_check(rgx, *tests):
    for test in tests:
        print(test, rgx.check(test))

WHILE = RegEx.load('WHILE')
FOR = RegEx.load('FOR')
IN = RegEx.load('IN')
RETURN = RegEx.load('RETURN')
DEFINE = RegEx.load('DEFINE')
CLASS = RegEx.load('CLASS')
# INTEGER = RegEx.load('INTEGER') #todo: pickling this does not work.
# VARIABLE = RegEx.load('VARIABLE')
# FLOAT = RegEx.load('FLOAT')
# NUMBER = RegEx.load('NUMBER')
LPARAM = RegEx.load('LPARAM')
RPARAM = RegEx.load('RPARAM')

LBRACKET = RegEx.load('LBRACKET')
RBRACKET = RegEx.load('RBRACKET')

ASSIGN = RegEx.load('ASSIGN')
EQUAL = RegEx.load('EQUAL')
INEQUAL = RegEx.load('INEQUAL')

LT = RegEx.load('LT')
LE = RegEx.load('LE')

GT = RegEx.load('GT')
GE = RegEx.load('GE')

NEWLINE = RegEx.load('NEWLINE')
TAB = RegEx.load('TAB')

SINGLEQUOTE = RegEx.load('SINGLEQUOTE')
DOUBLEQUOTE = RegEx.load('DOUBLEQUOTE')

SEMICOLON = RegEx.load('SEMICOLON')
COLON = RegEx.load('COLON')
COMMA = RegEx.load('COMMA')
DOT = RegEx.load('DOT')

PLUS = RegEx.load('PLUS')
MINUS = RegEx.load('MINUS')
ASTERISK = RegEx.load('ASTERISK')
SLASH = RegEx.load('SLASH')
BACKSLASH = RegEx.load('BACKSLASH')
DIV = RegEx.load('DIV')

# WHILE = RegEx('while', 'WHILE')
# FOR = RegEx('for', 'FOR')
# IN = RegEx('in', 'IN')
# RETURN = RegEx('return', 'RETURN')
# DEFINE = RegEx('define', 'DEFINE')
# CLASS = RegEx('class', 'CLASS')
#
# #todo: reserved items currently are not being scanned.
#
INTEGER = RegEx('[0-9]+', 'INTEGER')
VARIABLE = RegEx('([a-z]|[A-Z]|_)([a-z]|[A-Z]|[0-9]|_)*', 'VARIABLE')
FLOAT = RegEx('([0-9]+.[0-9]*)|([0-9]*.[0-9]+)', 'FLOAT')
NUMBER = RegEx('([0-9]*.?[0-9]+)|([0-9]+.?[0-9]*)', 'NUMBER')

# FOR REALLY SMALL CHARACTER VOCABULARY LOADING IS 3-4 TIMES SLOWER, FOR BIG VOCABULARY
# LOADING IS ~7.5 TIMES FASTER.
# [a-z][A-Z][0-9] takes about 3 miliseconds to create, while loading it takes about 0.4 miliseconds to load it.
# creating ':' takes about 0.1 miliseconds to create and about 0.4 miliseconds to load it.
# the point is: loading is absolutely necessary. Even for small vocabularies in which loading is slower
# it's still nothing (0.4 miliseconds) compared to the usual lexer scan time (in seconds).
# extensive load tests could give much more precised and nuanced answers though.

# time profiling for lexer turned out two big time consumers: calculating epsilon closures and accepted states
# both are used extremely often and both take a long time to process (as all properties do)
# epsilon closures really can't get much faster without a major redesign, so I should finally write a good
# nfa to dfa caster after writing tests for new modules.

# import time
# t0 = time.clock()
# test = RegEx.load('00test')
# print('{:.100f}'.format(time.clock() - t0))
# test.compile()

# LPARAM = RegEx('\\(', 'LPARAM')
# RPARAM = RegEx('\\)', 'RPARAM')
#
# LBRACKET = RegEx('\\[', 'LBRACKET')
# RBRACKET = RegEx('\\]', 'RBRACKET')
#
# ASSIGN = RegEx('=', 'ASSIGN')
# EQUAL = RegEx('==', 'EQUAL')
# INEQUAL = RegEx('!=', 'INEQUAL')
#
# LT = RegEx('<', 'LT')
# LE = RegEx('<=', 'LE')
#
# GT = RegEx('>', 'GT')
# GE = RegEx('>=', 'GE')
#
# NEWLINE = RegEx('\n', 'NEWLINE')
# TAB = RegEx('\t', 'TAB')
#
# SINGLEQUOTE = RegEx("'", 'SINGLEQUOTE')
# DOUBLEQUOTE = RegEx('"', 'DOUBLEQUOTE')
#
# SEMICOLON = RegEx('\\;', 'SEMICOLON') #todo: fix this in generators.py
# COLON = RegEx(':', 'COLON')
# COMMA = RegEx(',', 'COMMA')
# DOT = RegEx('.', 'DOT')
#
# PLUS = RegEx('\\+', 'PLUS')
# MINUS = RegEx('\\-', 'MINUS')
# ASTERISK = RegEx('\\*', 'ASTERISK')
# SLASH = RegEx('/', 'SLASH')
# BACKSLASH = RegEx('\\\\', 'BACKSLASH')
#
# DIV = RegEx('//', 'DIV')
# print(DIV.check(''))
# print(DIV.check('/'))
# print(DIV.check('//'))
# print(DIV.check('///'))

#todo: consider implementing operator precedence (explicitly, not implicitly)
#todo: implement RegEx precedence (RESERVED and others, also vocabulary size)

# SPACE = RegEx(' ')
# print(SPACE.check(''))
# print(SPACE.check(' '))
# print(SPACE.check('  '))
