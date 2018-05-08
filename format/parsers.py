import abc
import sys
import format.parser_api as api
from automata.state import State

class Parser(abc.ABC):

    """
    Abstract class that defines the interface for all Parsers.
    Parsers do not have the same interface, which is fine.
    """

    def __init__(self, state_class = State):

        """
        Initialises a Parser.

        :param type state_class: Specific implementation of State interface.
        """

        self.states = dict()
        self.inputs = set()
        self.start_state = ''

        self.state_imp = state_class

    @abc.abstractmethod
    def parse(self, text):
        """
        Internal parser. Used as a central point for parsing a specific text format.
        Passes all parsed data to appropriate containers which are accessible through interface properties.

        :return:
        """
        pass

class StandardFormatParser(Parser):
    """
    Format specification:
    Line 1. states
    Line 2. inputs
    Line 3. accepting states
    Line 4. starting state
    Line 5+ transition functions (each in in its' own row) in format start_state,value->end_state
        If the transition function doesn't produce an end state then use # (start,value->#).
        If the transition function has multiple end states they are separated by a comma. (start,value->s1,s2,s3,s4)
    """
    def _extract_states(self, states, accepted):
        """
        Extracts and packages States from specified lines.

        :param str states: All States
        :param str accepted: All accepted states
        :return:
        """
        accepted_states = api.split_coma_set(accepted)
        for state in api.split_coma_list(states):
            state_obj = self.state_imp(state, 1 if state in accepted_states else 0)
            self.states[state] = state_obj

    def _extract_start_state(self, start_state):
        self.start_state = self.states[start_state]

    def _extract_inputs(self, text):

        for inp in api.split_coma_list(text):
            self.inputs.add(inp)

    def _extract_functions(self, functions):
        for line in functions:
            if line == '':
                continue
            start_value, ends = api.split_factory('->', list)(line)

            start, value = api.split_coma_list(start_value)

            for end in api.split_coma_list(ends):
                if end != '#':
                    self.states[start].add_function(self.states[end], value)

    def parse(self, text):
        lines = api.split_lines_without_removal(text)

        self._extract_states(lines[0], lines[2])
        self._extract_inputs(lines[1])
        self._extract_start_state(lines[3])
        self._extract_functions(lines[4:])

        states = dict()
        for state in self.states.values():
            states[state.name] = state
        self.states = states

class StandardFormatWithInputParser(StandardFormatParser):
    """
    Format specification:
    Line 1. inputs separated with a comma. Multiple input strings are separated with | symbol.
    Line 2. states
    Line 3. inputs
    Line 4. accepting states
    Line 5. starting state
    Line 6+ transition functions (each in in its' own row) in format start_state,value->end_state
        If the transition function doesn't produce an end state then use # (start,value->#).
        If the transition function has multiple end states they are separated by a comma. (start,value->s1,s2,s3,s4)
    """

    def __init__(self, state_class = State):
        super().__init__(state_class)
        self.entries = list()

    def _extract_entries(self, text):

        exact_entries = api.split_factory('|', list)(text)

        for entries in exact_entries:
            self.entries.append([])
            for entry in api.split_coma_list(entries):
                self.entries[-1].append(entry)

    def parse(self, text):
        lines = api.split_newline_list(text)

        self._extract_entries(lines[0])
        self._extract_states(lines[1], lines[3])
        self._extract_inputs(lines[2])
        self._extract_start_state(lines[4])
        self._extract_functions(lines[5:])

        states = dict()

        for state in self.states.values():
            states[state.name] = state

        self.states = states

class PushDownFormatWithInputParser(StandardFormatWithInputParser):

    def __init__(self, state_class = State):

        super().__init__(state_class)

        self.stack_alphabet = set()
        self.start_stack = ''

    def _extract_functions(self, functions):
        for line in functions:
            if line == '':
                continue
            start_value_symbol, ends = api.split_factory('->', list)(line)

            start, value, symbol = api.split_coma_list(start_value_symbol)

            end_state, stack = api.split_coma_list(ends)

            self.states[start].add_function((self.states[end_state], stack), (end_state, symbol))

    def _extract_stack_alphabet(self, symbols):
        """
        Extracts and packages stack alphabet.

        :param str symbols: All stack symbols
        :return:
        """
        for sym in api.split_coma_list(symbols):
            self.stack_alphabet.add(sym)

    def _extract_starting_stack_symbol(self, symbol):
        self.start_stack = symbol

    def parse(self, text):
        lines = api.split_newline_list(text)

        self._extract_entries(lines[0])
        self._extract_states(lines[1], lines[4])
        self._extract_inputs(lines[2])
        self._extract_stack_alphabet(lines[3])
        self._extract_start_state(lines[5])
        self._extract_starting_stack_symbol(lines[6])
        self._extract_functions(lines[7:])

