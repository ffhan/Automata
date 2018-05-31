"""
Defines a regular expression type and all default regular expression checkers.
"""
import grammar.operators as operators

class RegExp:
    """
    Defines a class that handles all regular expression needs.
    Currently compiles to epsilon NFA, but that will be bound to change.
    """
    #todo: fix nfa to dfa casting and add compile method that does: operator->e_nfa->nfa->dfa->minimised dfa
    unary_operators = {'+': operators.KleenePlus,
                       '?': operators.QuestionMark,
                       '*': operators.KleeneStar,
                       '': operators.Single}
    binary_operators = {'|': operators.Alternation,
                        '': operators.Concatenation}

    def __init__(self, text: str):
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

        :param str text: text describing a regular expression
        """
        self._text = text
        self._groups = self._extract_bracket(text)
        self._groups = self._process(self._groups)
        self.automaton = self._groups.execute()

    def check(self, text):
        for char in text:
            self.automaton.enter(char)
        is_ok = self.automaton.accepted
        self.automaton.reset()
        return is_ok

    def _process(self, group: list)->operators.Operator:
        """
        Completely processes a text and returns a single Operator
        for a specified list of items.

        :param list group: a list of items
        :return Operator: single operator
        """

        group = self._collate(group)
        group = self._process_sublists(group)
        group = self._to_unary_operators(group)
        group = self._concatenate(group)
        group = self._alternate(group)

        if len(group) > 1:
            # print(group)
            raise ValueError('Parsing failed.')
        return group[0]

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
                par_count += 1
                if lpar_index == -1:
                    lpar_index = i
            elif char == ')':
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

#todo: enable inputting any character in a dfa. (maybe just a specific type.