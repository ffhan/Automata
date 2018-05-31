"""
Defines finite automata abstract class.
In other words, it defines an interface that all derived classes have to follow.
"""
import abc, copy
import automata.state as st
import automata.packs as pk

class FiniteAutomaton(abc.ABC):
    """
    Finite automata base abstract class. It isn't aware of transition functions.

    This is not an initialisable class.
    It serves exclusively as a template for more defined derived classes such as DFA and NFA.
    """

    def __init__(self, states, inputs, start_state):
        """
        Initialises a finite state automaton.
        Direct use is highly discouraged. Use factory method instead.

        :param states: all State objects
        :param inputs: all inputs
        :param State start_state: starting State object
        """

        self.states = states

        self.inputs = set(inputs)

        self.records = pk.Records()

        if self.states.get(start_state.name, 0):
            self.start_state = start_state
            assert isinstance(self.start_state, st.State)
            self.current = {start_state}
        else:
            raise ValueError(self._state_error(start_state.name))

        for name, state in self.states.items():
            try:
                assert isinstance(name, st.StateName)
            except AssertionError:
                raise TypeError('Type {} is NOT StateName (Name: {})'.format(name.__class__.__name__, name))
            try:
                assert isinstance(state, st.State)
            except AssertionError:
                raise TypeError('Type {} is NOT State (Object {})'.format(state.__class__.__name__, state))

        assert isinstance(start_state, st.State)
        assert isinstance(self.start_state, st.State)

        self._check_structure()

        self._alias = dict() # used to ensure backwards compatibility after FA minimization.

    @abc.abstractmethod
    def _check_structure(self) -> bool:
        """
        Checks if inner structure is correct. Raises a ValueError if not correct.

        :return bool: True
        """
        pass

    @property
    @abc.abstractmethod
    def accepted(self) -> bool:
        """
        Defines if current automaton state is defined

        :return bool: True if accepted, False if not
        """
        pass

    @property
    def accepted_states(self):
        """
        Returns states that contain value different than 0.

        :return: Accepted States
        """
        final = set()

        for state in self.states.values():

            if state.accepted:
                final.add(state)

        return final

    def _set_alias(self, state, alias):
        """
        Stores an alias for a removed State.

        :param StateName state: State that has replaced a state
        :param StateName alias: The replaced State
        :return:
        """
        self._alias[alias] = state

    def _get_alias(self, alias):
        """
        Find current State associated with a removed State.

        Returns the same State if it doesn't exist (case when State hasn't been removed from FA.

        :param StateName alias: Removed State
        :return StateName: Current State identical to the old State
        """
        # print(alias, type(alias))
        # assert isinstance(alias, StateName)
        if isinstance(alias, st.State):
            alias = alias.name
        found = self._alias.get(alias, alias)
        if found in self._alias.keys() and found != alias:
            found = self._get_alias(found)
        return found

    def reachable(self):

        """
        Removes all unreachable states.

        :return:
        """

        visited = self.start_state.indirect_reach

        states = dict()

        for state in visited:

            states[state.name] = state

        self.states = states

    def reset(self):
        """
        Resets the current FA state and clears step records.

        :return:
        """
        # self.records.clear()
        self.current = {self.start_state}

    def _not_defined_substring(self):
        """
        Method used to follow DRY principle in error reporting.
        May be moved to custom Error classes.

        :return str: Returns 'is not defined in this "name of the class"' string for an error.
        """

        return ' is not defined in this {}.'.format(type(self).__name__)

    def _state_error(self, state, prefix=''):
        """
        Returns a default error string with a possible prefix.

        Example:
            print(self.__state_error("q0", "Hey, this state"))

        [Out]: Hey, this state "q0" is not defined in this FA.

        :param str state: state name
        :param str prefix: Possible beginning of the error.
        :return str: state error string
        """
        start_prefix = 'S' if prefix == '' else ' s'
        return '{}{}tate "{}" {}'.format(prefix, start_prefix, state,
                                         type(self).__name__) + self._not_defined_substring()

    def _input_error(self, inp):
        """
        Defines an input error string.

        :param str inp: value of the input
        :return str: input error string
        """

        return 'Input "{}"'.format(inp) + self._not_defined_substring()

    def __repr__(self):
        assert isinstance(self.start_state, st.State)
        def wrap_in_braces(string, last_brace_newline=False):
            """
            Wraps up a string in {}.

            :param str string: string to be wrapped
            :param bool last_brace_newline: defines if newline will be put after braces
            :return str: wrapped string
            """
            return '{' + string + ('\n}' if last_brace_newline else '}')

        def tab(string):
            """
            Puts tabs in front of all lines in a string.

            Example:
            -------------
            For example,
            this becomes:
            -------------
                For example,
                this becomes:
            -------------

            :param str string: input string
            :return str: tabbed strings
            """
            return '\t' + string.replace('\n', '\n\t')

        def newline(*lines):
            """
            Returns string composed of all line arguments with newline added between them.

            :param str lines: lines of text that need to be newlined.
            :return: full string composed of individual lines concatenated with newline in-between
            """
            res = '\n'
            for line in lines:
                res += line + '\n'
            return res[:-1]

        states = ''
        final = ''

        for state, state_object in sorted(self.states.items(), key=lambda t : t[0]):
            states += str(state) + ','
            if state_object.value:
                # print(final, state)
                final += str(state.name) + ','

        final = 'F=' + wrap_in_braces(final[:-1])

        states = 'Q=' + wrap_in_braces(states[:-1])

        inputs = ''

        for inp in sorted(self.inputs):
            inputs += str(inp) + ','

        inputs = u'\u03A3=' + wrap_in_braces(inputs[:-1])

        funcs = u'\u03B4=' + wrap_in_braces(self.functions)

        try:
            assert isinstance(self.start_state, st.State)
        except AssertionError as error:
            print("Start state is not state, it's {}".format(type(self.start_state)), error)
            raise AssertionError
        start = 'q0=' + str(self.start_state.name)
        try:
            assert isinstance(self.start_state, st.State)
        except AssertionError as error:
            print("Start state is not state, it's {}".format(type(self.start_state)), error)
            raise AssertionError
        return '{} '.format(self.__class__.__name__) + wrap_in_braces(tab(
            newline(states, inputs, funcs, start, final)
        ), True)

    def __contains_helper(self, item):
        """
        Internal wrapper for states dict getter.

        :param StateName item: State name
        :return bool: True if State exists
        """
        assert type(item) is st.StateName

        return item in self.states

    def __contains__(self, item):
        """
        Wrapper allowing 'in self' notation.

        :param item: State name
        :return:
        """

        assert not isinstance(item, str)
        if isinstance(item, st.StateName):
            return self.__contains_helper(item)
        elif isinstance(item, st.State):
            return self.__contains_helper(item.name)
        return False

    # exists to precisely define how entries are handled. Enter is just interface endpoint
    def _process(self, *entry):
        """
        Processes the entry arguments.

        :param entry: entries that have to be handled.
        :return:
        """
        records = pk.Records()
        records.add_record(pk.RecordPack(self.current, self.accepted))
        for inp in entry:
            self._access(inp)
            records.add_record(pk.RecordPack(self.current, self.accepted))

        self.records.add_record(records)

    @abc.abstractmethod
    def _access(self, value):
        """
        A method that handles the individual input passing through FA.

        :param value: input
        :return:
        """
        pass

    def enter(self, *entry):
        """
        Reads all inputs from entry and puts them through the FA.

        :param entry: All entries.
        :return: result states
        """
        self._process(*entry)
        return self.current

    def record(self, *entry):
        """
        See entry method.

        :param entry: All entries.
        :return:
        """
        self._process(*entry)
        return self.records

    def output(self, *entry):
        """
        Outputs end state acceptance.

        :param entry: Inputs
        :return bool: Outputs True if end state is acceptable, False if not
        """
        self.enter(*entry)
        return self.accepted

    def distinguish(self):
        """
        Distinguishes identical states from non-identical and updates the automatum.

        :return:
        """
        raise NotImplementedError()

    def minimize(self):
        """
        Minimizes an automaton.

        :return:
        """
        raise NotImplementedError()

    @property
    def functions(self) -> str:
        """
        Returns functions for repr() function.

        :return str: string representation of transition functions
        """

        result = ''

        for state in sorted(self.states.values()):
            for event, end_states in state.transitions.items():
                # extremely bad code, but it's a part of an interface
                result += '{},{}->'.format(self._get_alias(state.name), event)
                for end in end_states:
                    # print(end, type(end))
                    result += '{},'.format(self._get_alias(end.name))
                result = result[:-1] + '\n'

        return result.strip()

    @staticmethod
    def factory(input_text, lexer):
        """
        Encapsulates FA object creation through a string and a lexer.
        Use this method for FA object creation instead of direct __init__

        :param type class_type: class type that has to be created
        :param str input_text: text that defines the FA
        :param Generator lexer: a conecrete Generator implementation
        :return FA: a concrete FA object
        """
        lexer.scan(input_text)
        return __class__(lexer.states, lexer.inputs, lexer.start_state)

    def _create_copy(self, *args):
        """
        Handles copy creation. Enables easy extension of deepcopy.
        Internal method. Do not use directly.

        :param args: arguments for creation.
        :return: FA object
        """
        return self.__class__(*args)

    def _create_state(self, *args):
        """
        Creates a State object.
        Exists solely for easy deepcopy extensions.

        Do NOT use directly.

        :param args: arguments for State creation.
        :return State: a State object
        """
        return st.State(*args)

    def deepcopy(self):
        """
        Deep copies an instance of FA.

        :return: FA object not bound by any references to the original object
        """
        # copying states has to be done inside FAs' because references have to be the same.
        copied_states = set()
        for state in self.states.values():
            name = copy.deepcopy(state.name)
            copied_states.add(self._create_state(name.name, copy.deepcopy(state.value)))
        inputs = copy.deepcopy(self.inputs)

        states = dict()
        for state in copied_states:
            states[state.name] = state

        for name, state in self.states.items():
            for event, transition_states in state.transitions.items():
                transitions = set()
                for transition_state in transition_states:
                    transitions.add(states[transition_state.name])
                states[name].transitions[event] = transitions
        start_state = states[self.start_state.name]

        return self._create_copy(states, inputs, start_state)

    def rename_state(self, old_name: st.StateName, new_name: str):
        """
        Renames a state inside the FA.

        It's critical to use this method to rename a state.

        If renaming states through iterator contain the keys in a list or a set,
        otherwise renaming will be incorrect (the dictionary changes size
        during iteration).
        For example:
        for name in list(automaton.states):
            ...
            automaton.rename_state(name, 'new_name')
            ...
        and NOT
        for name in automaton.states:
            ...

        :param StateName old_name: state name to be renamed
        :param str new_name: new state name
        :return:
        """

        state = self.states.pop(old_name)
        state.name.name = new_name
        self.states[state.name] = state
