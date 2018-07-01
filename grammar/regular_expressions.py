"""
Defines a regular expression type and all default regular expression checkers.
"""
import os
import xml.dom.minidom as dom
import os.path as pth
import json
import grammar.operators as operators
import form.generators as generator
import automata.dfa as dfa
import form.compositors as com

dirname = os.path.dirname(__file__)

class RegEx(object):
    """
    Defines a class that handles all regular expression needs.
    Currently compiles to epsilon NFA, but that will be bound to change.
    """
    #todo: fix nfa to dfa casting and add save method that does: operator->e_nfa->nfa->dfa->minimised dfa
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



    def __init__(self, text: str, name: str = 'placeholder', auto_execute: bool = True):
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
        :param bool auto_execute: automatically executes FA from operators
        """

        self._name = name

        self._text = text

        self._groups = self._extract_bracket(text)
        self._groups = self._process(self._groups)
        if auto_execute:
            self.automaton = self._groups.execute()
        # self.save()

    @property
    def min_lookahead(self):
        return self._groups.min_length

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

    def export(self):
        """
        Exports a regex into a JSON file.

        :param regex: regular expression to be exported
        :param file: export destination
        :return:
        """
        inner = dict()
        inner['text'] = self._text
        inner['name'] = self._name
        inner['automaton'] = com.StandardCompositor(self.automaton).composite_automaton()
        with open(dirname + '/compiled_regexes/' + inner['name'].upper() + '.regex', 'w') as file:
            json.dump(inner, file, indent=4)
    @staticmethod
    def load(file):
        """
        Loads a regex.

        :param file: regex filepath
        :return: regex object
        """
        with open(dirname + '/compiled_regexes/' + file + '.regex', 'r') as file:
            data = json.load(file)
            regex = RegEx(data['text'], data['name'], False)
            regex.automaton = dfa.DFA.factory(data['automaton'], generator.StandardFormatGenerator())
        return regex

def check_check(rgx, *tests):
    """
    Enables fast testing whether a regex works as designed.

    :param rgx: regex to test
    :param tests: input characters
    :return:
    """
    for test in tests:
        print(test, rgx.check(test))

REGEXES = dict()
def prepare_regexes():
    """
    Loads and creates all regexes defined in preloaded_regexes.xml

    :return:
    """
    # print("PREPARING REGEXES..")
    doc = dom.parse(dirname + '/' + 'preloaded_regexes.xml')
    rgxs = doc.getElementsByTagName('regex')
    for rgx in rgxs:
        name, expr = rgx.attributes['name'].value, rgx.attributes['expr'].value
        if pth.isfile(dirname + '/' + 'compiled_regexes/{}.regex'.format(name)):
            print('LOADING {}..'.format(name))
            REGEXES[name] = RegEx.load(name)
        else:
            print('CREATING {}..'.format(name))
            REGEXES[name] = RegEx(expr, name)
            REGEXES[name].export()
prepare_regexes()
# print(json.dumps({'%s' % type(NUMBER._groups).__name__ : process_operator(NUMBER._groups)}, indent=4))
# print(process_operator(WHILE))
# # FOR REALLY SMALL CHARACTER VOCABULARY LOADING IS 3-4 TIMES SLOWER, FOR BIG VOCABULARY
# # LOADING IS ~7.5 TIMES FASTER.
# # [a-z][A-Z][0-9] takes about 3 miliseconds to create, while loading it takes about 0.4 miliseconds to load it.
# # creating ':' takes about 0.1 miliseconds to create and about 0.4 miliseconds to load it.
# # the point is: loading is absolutely necessary. Even for small vocabularies in which loading is slower
# # it's still nothing (0.4 miliseconds) compared to the usual lexer scan time (in seconds).
# # extensive load tests could give much more precised and nuanced answers though.
#
# # time profiling for lexer turned out two big time consumers: calculating epsilon closures and accepted states
# # both are used extremely often and both take a long time to process (as all properties do)
# # epsilon closures really can't get much faster without a major redesign, so I should finally write a good
# # nfa to dfa caster after writing tests for new modules. (DONE)
#
# # after creating casts going through 1500 iterations of iteratively increased sequences DFA processes
# # them in less than 3 seconds while it takes ~7-8 seconds for epsilon NFAs'.
# # further minimising the DFAs' would make it a bit faster.
#
# # import time
# # t0 = time.clock()
# # test = RegEx.load('00test')
# # print('{:.100f}'.format(time.clock() - t0))
# # test.save()

# 1.915 seconds to load all regexes.
# 0.677 seconds to create all regexes.
# loading is not going to be used by default. Export is here only to be able to save a regex externally.
# clean version of preparation takes approx. 0.424 seconds which is fine.

# by cutting down the alias dict and shortening all names I got to 0.439 seconds to create all regexes (0.666 when exporting)
# and 0.047 seconds (47 miliseconds) to load all of them. I have successfully solved the export/loading problem.
