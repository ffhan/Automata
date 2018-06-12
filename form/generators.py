"""
Defines a Generator interface (abstract class) and all used
Generator implementations.

In other words, defines all output formats.
"""
import abc
import form.generator_api as api
import automata.state as st
import automata.packs as pk
import misc.helper as helper
#todo: refactor the names:
# every format (e.g. standard format) has to have its' own
# subpackage of generators.
class Generator(abc.ABC):
    """
    Abstract class that defines the interface for all generators.
    Generators do not have the same interface, which is fine.
    """

    def __init__(self, state_class=st.State):
        """
        Initialises a Generator.

        :param type state_class: Specific implementation of State interface.
        """
        self.state_imp = state_class

        self.states = dict()
        self.inputs = set()
        self.start_state = ''

    def reset(self):
        """
        Resets Generator state so that new scan can be done correctly.

        :return:
        """
        self.states = dict()
        self.inputs = set()
        self.start_state = ''

    @abc.abstractmethod
    def scan(self, text):
        """
        Internal generator. Used as a central point for parsing a specific text form.
        Passes all compiled data to appropriate containers which are accessible
        through interface properties.

        :return:
        """
        pass

class StandardFormatGenerator(Generator):
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

    If you are using a comma (,) or a newline (\n) anywhere they have to be escaped
    with a backslash (\) in front of the symbol. For more details of escaping
    see form.generator_api.py, specifically split_factory2 method.
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
        accepted_states = api.NEW_SPLIT_COMMA(accepted, remove_empty=True)
        for state in api.NEW_SPLIT_COMMA(states, remove_empty=True):
            state_name = helper.de_escape_string(state)[0]
            # epsilon is format-specific so it should be bound to a specific Generator implementation.
            state_obj = self.state_imp(state_name, 1 if state in accepted_states else 0)
            self.states[state_name] = state_obj

    def _extract_start_state(self, start_state):
        self.start_state = self.states[helper.de_escape_string(start_state)[0]]

    def _extract_inputs(self, text):

        for inp in api.NEW_SPLIT_COMMA(text, remove_empty=True):
            self.inputs.add(*helper.de_escape_string(inp))

    def _extract_functions(self, functions):

        for line in functions:
            if line == '':
                continue
            start_value, ends = api.split_factory2('->')(line)

            start, value = helper.de_escape_string(*api.NEW_SPLIT_COMMA(start_value))

            for end in api.NEW_SPLIT_COMMA(ends):
                end = helper.de_escape_string(end)[0]
                if end != '#':
                    try:
                        self.states[start].add_function(self.states[end], value)
                    except Exception as err:
                        print(self.states, start, end, value)
                        raise err

    def scan(self, text):
        self.reset()

        lines = api.NEW_SPLIT_NEWLINE(text)

        self._extract_states(lines[0], lines[2])
        self._extract_inputs(lines[1])
        self._extract_start_state(lines[3])
        self._extract_functions(lines[4:])

        self._replace_state_keys()

class StandardFormatWithInputGenerator(StandardFormatGenerator):
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

class PushDownFormatWithInputGenerator(StandardFormatWithInputGenerator):
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
        self.reset()

        lines = api.SPLIT_LINES_WITHOUT_REMOVAL(text)

        self._extract_entries(lines[0])
        self._extract_states(lines[1], lines[4])
        self._extract_inputs(lines[2])
        self._extract_stack_alphabet(lines[3])
        self._extract_start_state(lines[5])
        self._extract_starting_stack_symbol(lines[6])
        self._extract_functions(lines[7:])

        self._replace_state_keys()

class StandardTuringMachineFormatGenerator(StandardFormatGenerator):
    """
    This format does NOT allow for explicit rejected state creation.

    Line 1: states
    Line 2: input symbols
    Line 3: alphabet
    Line 4: empty cell symbol
    Line 5: textual representation of a Turing machine tape
    Line 6: acceptable states.
    Line 7: starting state
    Line 8: starting index of turing machine
    Line 9+ transition functions in a format
        currentState,symbol->newState,newSymbol,headMovement
    """

    def __init__(self, state_class = st.State):
        super().__init__(state_class)
        self.alphabet = set()
        self.empty_cell_symbol = None
        self.tape_content = []
        self.head_index = 0

    def reset(self):
        super().reset()
        self.alphabet.clear()
        self.empty_cell_symbol = None
        self.tape_content.clear()
        self.head_index = 0

    def _replace_state_keys(self):
        states = dict()
        for state in self.states.values():
            states[state.name] = state
        self.states = states

    def _extract_start_state(self, start_state):
        self.start_state = self.states[helper.de_escape_string(start_state)[0]]

    def _extract_inputs(self, text):
        for inp in api.NEW_SPLIT_COMMA(text, remove_empty=True):
            self.inputs.add(*helper.de_escape_string(inp))

    def _extract_alphabet(self, text):
        for inp in api.NEW_SPLIT_COMMA(text, remove_empty=True):
            self.alphabet.add(*helper.de_escape_string(inp))

    def _extract_tape(self, text):
        self.tape_content = list(text)

    def _extract_functions(self, functions):

        for line in functions:
            if line == '':
                continue
            start_value, ends = api.split_factory2('->')(line)

            start, value = helper.de_escape_string(*api.NEW_SPLIT_COMMA(start_value))

            end, symbol, movement = helper.de_escape_string(*api.NEW_SPLIT_COMMA(ends))
            end = self.states[end]
            movement = pk.TuringOutputPack.LEFT if movement == 'L' else pk.TuringOutputPack.RIGHT
            self.states[start].add_function(pk.TuringOutputPack(end, symbol, movement), value)

    def scan(self, text):
        self.reset()

        lines = api.NEW_SPLIT_NEWLINE(text)

        self._extract_states(lines[0], lines[5])
        self._extract_inputs(lines[1])
        self._extract_alphabet(lines[2])
        self.empty_cell_symbol = lines[3]
        self._extract_tape(lines[4])
        self._extract_start_state(lines[6])
        self.head_index = int(lines[7])
        self._extract_functions(lines[8:])

        self._replace_state_keys()
