from .state import StateName, State
import abc, re, collections

class FiniteAutomaton(abc.ABC):
    """
    Finite automata base abstract class. It isn't aware of transition functions.

    This is not an initialisable class. It serves exclusively as a template for more defined derived classes such as DFA and NFA.
    """

    def __init__(self, text, parser):
        """
        Initialises a finite state automata.

        :param str text: Input text
        :param format.parser.Parser parser: Concrete Parser implementation
        """

        parser.parse(text)

        self.states = parser.states

        self.inputs = set(parser.inputs)

        self.records = []

        if self.states.get(parser.start_state.name, 0):
            self.start_state = parser.start_state
            self.current = {parser.start_state}
        else:
            raise ValueError(self._state_error(parser.start_state.name))

        for name, state in self.states.items():
            try:
                assert isinstance(name, StateName)
            except AssertionError:
                raise TypeError('Type {} is NOT StateName'.format(name.__class__.__name__))
            try:
                assert isinstance(state, State)
            except AssertionError:
                raise TypeError('Type {} is NOT State'.format(state.__class__.__name__))

        assert isinstance(parser.start_state, State)

        self._check_structure()

        self._alias = dict() # used to ensure backwards compatibility after FA minimization.

    @abc.abstractmethod
    def _check_structure(self):
        """
        Checks if inner structure is correct. Raises a ValueError if not correct.

        :return:
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
        if isinstance(alias, State):
            alias = alias.name
        found = self._alias.get(alias, alias)
        if found in self._alias.keys() and found != alias:
            found = self._get_alias(found)
        return found

    def reachable(self):

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
        Method used to follow DRY principle in error reporting. May be moved to custom Error classes.

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

        return '{}{}tate "{}"'.format(prefix, 'S' if prefix == '' else ' s', state,
                                      type(self).__name__) + self._not_defined_substring()

    def _input_error(self, inp):
        """
        Defines an input error string.

        :param str inp: value of the input
        :return str: input error string
        """

        return 'Input "{}"'.format(inp) + self._not_defined_substring()

    def __repr__(self):
        def wrap_in_braces(string, last_brace_newline=False):
            return '{' + string + ('\n}' if last_brace_newline else '}')

        def tab(string):
            return '\t' + string.replace('\n', '\n\t')

        def space(*strings):
            result = ''
            for s in strings:
                result += s + ' '
            return result[:-1]

        def newline(*lines):
            """
            Returns concatenated string composed of all line arguments with newline added between them.

            :param str lines: lines of text that need to be newlined.
            :return: full string composed of individual lines concatenated with newline in-between
            """
            res = '\n'
            for line in lines:
                res += line + '\n'
            return res[:-1]
        states = ''
        final = ''

        for state, state_object in self.states.items():
            states += state + ','
            if state_object.value:
                # print(final, state)
                final += state.name

        final = 'F=' + wrap_in_braces(final)

        states = 'Q=' + wrap_in_braces(states[:-1])

        inputs = ''

        for inp in self.inputs:
            inputs += str(inp) + ','

        inputs = u'\u03A3=' + wrap_in_braces(inputs[:-1])

        funcs = u'\u03B4=' + wrap_in_braces(self.functions)

        start = 'q0=' + self.start_state.name

        return '{} '.format(self.__class__.__name__) + wrap_in_braces(tab(
            newline(states, inputs, funcs, start, final)
        ), True)

    def __contains_helper(self, item):
        """
        Internal wrapper for states dict getter.

        :param StateName item: State name
        :return bool: True if State exists
        """
        if not self.states.get(item, False):
            return False
        return True

    def __contains__(self, item):
        """
        Wrapper allowing 'in self' notation.

        :param item: State name
        :return:
        """
        assert not isinstance(item, str)
        if isinstance(item, StateName):
            return self.__contains_helper(item)
        elif isinstance(item, State):
            return self.__contains_helper(item.name)
        else:
            return False

    def _process(self, *entry): #exists to precisely define how entries are handled. Enter is just interface endpoint
        """
        Processes the entry arguments.

        :param entry: entries that have to be handled.
        :return:
        """

        self.records.append([])
        self.records[-1].append(self.current)
        for inp in entry:
            self._access(inp)
            self.records[-1].append(self.current)

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
        results = self.enter(*entry)
        for result in results:
            if result.value > 0:
                return True
        return False

    def distinguish(self):
        """
        Distinguishes identical states from non-identical and updates the automatum.
        
        :return: 
        """
        raise NotImplementedError()

    def minimize(self):
        raise NotImplementedError()

    @property
    def functions(self):
        """
        Updates functions and start state according to changes made in the automatum.

        :return:
        """

        result = ''

        for state in sorted(self.states.values()):
            for event, end_states in state.transitions.items(): #extremely bad code, but it's a part of an interface
                result += '{},{}->'.format(self._get_alias(state.name), event)
                for end in end_states:
                    # print(end, type(end))
                    result += '{},'.format(self._get_alias(end.name))
                result = result[:-1] + '\n'

        # print(result)

        self.start_state = self._get_alias(self.start_state.name)

        return result.strip()