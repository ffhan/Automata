"""
Defines a regular expression type and all default regular expression checkers.
"""
import grammar.operators as operators

class RegExp:
    operators = {'+', '?', '*', '|'}
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
        self._collate()

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
        subtext = ''
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

    def _collate(self):

        copied_groups = self._groups.copy()

        lpar_index = -1 # [ symbol
        dash_index = -1 # - symbol
        # rpar_index = -1 # ] symbol

        for i, item in enumerate(self._groups):

            if item == '[':
                lpar_index = i
            elif item == '-':
                dash_index = i
            elif item == ']':
                collation = operators.Collation(*self._groups[lpar_index+1:i:2])
                copied_groups[lpar_index:i+1] = [collation]
        self._groups = copied_groups

d = RegExp("[a-z](a|b)*((bc+)|(b+c))")
print(d._groups)

#todo: enable inputting any character in a dfa. (maybe just a specific type.