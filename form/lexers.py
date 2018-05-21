"""
Defines a Lexer interface (abstract class) and all used
Lexer implementations.

In other words, defines all output formats.
"""
import abc
import form.lexer_api as api
import automata.state as st
import automata.packs as pk

class Lexer(abc.ABC):
    """
    Abstract class that defines the interface for all Lexers.
    Lexers do not have the same interface, which is fine.
    """

    def __init__(self, state_class=st.State):
        """
        Initialises a Lexer.

        :param type state_class: Specific implementation of State interface.
        """
        self.state_imp = state_class

        self.states = dict()
        self.inputs = set()
        self.start_state = ''

    def reset(self):
        """
        Resets Lexer state so that new scan can be done correctly.

        :return:
        """
        self.states = dict()
        self.inputs = set()
        self.start_state = ''

    @abc.abstractmethod
    def scan(self, text):
        """
        Internal lexer. Used as a central point for parsing a specific text form.
        Passes all compiled data to appropriate containers which are accessible
        through interface properties.

        :return:
        """
        pass

class StandardFormatLexer(Lexer):
    """
    Format specification:
    Line 1. states
    Line 2. inputs
    Line 3. accepting states
    Line 4. starting state
    Line 5+ transition functions (each in in its' own row) in form start_state,value->end_state
        If the transition function doesn't produce an end state then use # (start,value->#).
        If the transition function has multiple end states
        they are separated by a comma. (start,value->s1,s2,s3,s4)
    """

    def _replace_state_keys(self):
        states = dict()
        for state in self.states.values():
            states[state.name] = state
        self.states = states

    def _extract_states(self, states, accepted):
        """
        Extracts and packages States from specified lines.

        :param str states: All States
        :param str accepted: All accepted states
        :return:
        """
        accepted_states = api.SPLIT_COMMA_SET(accepted)
        for state in api.SPLIT_COMMA_LIST(states):
            # epsilon is format-specific so it should be bound to a specific Lexer implementation.
            state_obj = self.state_imp(state, 1 if state in accepted_states else 0)
            self.states[state] = state_obj

    def _extract_start_state(self, start_state):
        self.start_state = self.states[start_state]

    def _extract_inputs(self, text):

        for inp in api.SPLIT_COMMA_LIST(text):
            self.inputs.add(inp)

    def _extract_functions(self, functions):

        for line in functions:
            if line == '':
                continue
            start_value, ends = api.split_factory('->', list)(line)

            start, value = api.SPLIT_COMMA_LIST(start_value)

            for end in api.SPLIT_COMMA_LIST(ends):
                if end != '#':
                    self.states[start].add_function(self.states[end], value)

    def scan(self, text):
        self.reset()

        lines = api.SPLIT_LINES_WITHOUT_REMOVAL(text)

        self._extract_states(lines[0], lines[2])
        self._extract_inputs(lines[1])
        self._extract_start_state(lines[3])
        self._extract_functions(lines[4:])

        self._replace_state_keys()

class StandardFormatWithInputParser(StandardFormatLexer):
    """
    Format specification:
    Line 1. inputs separated with a comma. Multiple input strings are separated with | symbol.
    Line 2. states
    Line 3. inputs
    Line 4. accepting states
    Line 5. starting state
    Line 6+ transition functions (each in in its' own row) in form start_state,value->end_state
        If the transition function doesn't produce an end state then use # (start,value->#).
        If the transition function has multiple end states
        they are separated by a comma. (start,value->s1,s2,s3,s4)
    """

    def __init__(self, state_class=st.State):
        super().__init__(state_class)
        self.entries = list()

    def reset(self):
        super().reset()
        self.entries = list()

    def _extract_entries(self, text):

        exact_entries = api.split_factory('|', list)(text)

        for entries in exact_entries:
            self.entries.append([])
            for entry in api.SPLIT_COMMA_LIST(entries):
                self.entries[-1].append(entry)

    def scan(self, text):
        self.reset()
        lines = api.SPLIT_LINES_WITHOUT_REMOVAL(text)

        self._extract_entries(lines[0])
        self._extract_states(lines[1], lines[3])
        self._extract_inputs(lines[2])
        self._extract_start_state(lines[4])
        self._extract_functions(lines[5:])

        self._replace_state_keys()

class PushDownFormatWithInputParser(StandardFormatWithInputParser):
    """
    Format specification:
    Line 1. inputs separated with a comma. Multiple input strings are separated with | symbol.
    Line 2. states
    Line 3. inputs
    Line 4. stack alphabet
    Line 5. accepting states
    Line 6. starting state
    Line 7+ transition functions (each in in its' own row) in form
    start_state,value,stack->end_state,stack_symbols
    """

    def __init__(self, state_class=st.State, stack=pk.Stack):

        super().__init__(state_class)

        self.stack_imp = stack

        self.stack_alphabet = set()
        self.start_stack = ''

    def reset(self):
        super().reset()
        self.stack_alphabet = set()
        self.start_stack = ''

    def _extract_functions(self, functions):

        for line in functions:
            if line == '':
                continue

            start_value_symbol, ends = api.split_factory('->', list)(line)

            start, value, symbol = api.SPLIT_COMMA_LIST(start_value_symbol)

            end_state, stack = api.SPLIT_COMMA_LIST(ends)

            stck = self.stack_imp()
            for sym in stack:
                stck.push(sym)

            key = pk.InputPack(value, symbol)
            end = self.states[end_state]

            self.states[start].add_function(pk.InputPack(end, stck), key)

    def _extract_stack_alphabet(self, symbols):
        """
        Extracts and packages stack alphabet.

        :param str symbols: All stack symbols
        :return:
        """
        for sym in api.SPLIT_COMMA_LIST(symbols):
            self.stack_alphabet.add(sym)

    def _extract_starting_stack_symbol(self, symbol):
        self.start_stack = symbol

    def scan(self, text):
        lines = api.SPLIT_LINES_WITHOUT_REMOVAL(text)

        # print(text)
        # print(lines)

        self._extract_entries(lines[0])
        self._extract_states(lines[1], lines[4])
        self._extract_inputs(lines[2])
        self._extract_stack_alphabet(lines[3])
        self._extract_start_state(lines[5])
        self._extract_starting_stack_symbol(lines[6])
        self._extract_functions(lines[7:])

        self._replace_state_keys()