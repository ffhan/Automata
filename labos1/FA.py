from labos1 import abc, re
from labos1.state import State

class FA(abc.ABC):
    '''
    Finite automata base abstract class. It isn't aware of transition functions.

    This is not an initialisable class. It serves exclusively as a template for more defined derived classes such as DFA and NFA.
    '''

    def __init__(self, states, inputs, functions, start_state, final_states, in_type=str):
        '''
        Initialises a finite state automata.

        :param states: set of all possible states
        :param inputs: set of all possible inputs
        :param str functions: Function instruction string.
        :param start_state: single starting state
        :param final_states: set of all possible final (accepting) states
        :param in_type: input type (string or int)
        '''
        self.states = dict()
        self.inputs = set()
        self.functions = ''
        # I deliberately include functions although they are not defined in FA class so that __repr__ can be written
        # only in the base class.

        self.type = in_type

        for one_input in inputs:
            self.inputs |= {self.type(one_input)}

        for state in states:
            self.states[state] = State(state, 1 if state in final_states else 0)

        if self.states.get(start_state, 0):
            self.start_state = start_state
            self.current = self.states[start_state]
        else:
            raise ValueError('State {} not defined in this automata.'.format(start_state))

        self.parse_functions_string(functions)

    def __fis_extract(self, entry):

        '''
        Sanitizes and splits the FIS instructions.
        :param str entry: Function instruction string
        :return list: List that contains individual instructions.
        '''

        funcs = re.sub(r"[\n\t *]", '', entry)
        self.functions = funcs
        try:
            funcs = funcs.split(';')
        except AttributeError:
            raise AttributeError('Invalid function instruction string. Check your function string.')

        return funcs

    @abc.abstractmethod
    def end_state_parser(self, end_state_string):
        '''
        Defines how an end state string is going to be fed to the FA.

        For example DFA returns exclusively one value, not of an iterable type, while NFA returns an iterable.

        :param str end_state_string: Function instruction string
        :return: End state(s) for a particular FIS
        '''
        pass

    def __not_defined_substring(self):
        '''
        Method used to follow DRY principle in error reporting. May be moved to custom Error classes.

        :return str: Returns 'is not defined in this "name of the class"' string for an error.
        '''

        return ' is not defined in this {}.'.format(type(self).__name__)

    def _state_error(self, state, prefix=''):
        '''
        Returns a default error string with a possible prefix.

        Example:
            print(self.__state_error("q0", "Hey, this state"))

        [Out]: Hey, this state "q0" is not defined in this FA.

        :param str state: state name
        :param str prefix: Possible beginning of the error.
        :return str: state error string
        '''

        return '{}{}tate "{}"'.format(prefix, 'S' if prefix == '' else ' s', state,
                                      type(self).__name__) + self.__not_defined_substring()

    def _input_error(self, inp):
        '''
        Defines an input error string
        :param str inp: value of the input
        :return str: input error string
        '''

        return 'Input "{}"'.format(inp) + self.__not_defined_substring()

    def parse_functions_string(self, functions):  # todo: improve string handling, maybe completely remove FIS.
        '''
        Parses the functions instruction string and defines transition functions.

        Each expression of functions string has to be escaped with ; symbol.
        Example: func1;func2;...

        It is advisable to use multiple line string to separate individual transition functions.
        Example:
            func1;
            func2;
            func3;

        Each expression is composed of 3 parts:
            start_state:transition_value->end_state(s)

        Example:
            q0,1->q1

        Multiple end states are separated by a comma. (forbidden in a DFA.)

        Example:
            q0,1->q1,q2

        Example of the whole notation system:
            q0,0->q0;
            q0,1->q1,q0;
            q1,0->q1;
            q1,1->q1

        :param str functions: A string defining transition functions for DFA
        :return:
        '''

        funcs = self.__fis_extract(functions)

        functions_added = 0
        for transition_func in funcs:  # todo: extract FIS parser to a base class (FA) method and pass parsed data to this method.
            try:
                startvalue, end = transition_func.split('->')
                start, value = startvalue.split(',')
                end = self.end_state_parser(end)  # parsing the end state(s).

            except (AttributeError, ValueError) as error:
                raise type(error)('Invalid function instruction string at line {}. Check your function string.'.format(functions_added + 1))
            value = self.type(value.strip('"').strip("'"))  # sanitizing input, removing braces
            if start not in self:
                raise ValueError(self._state_error(end, '(starting)'))
            if value not in self.inputs:
                raise ValueError(self._input_error(value))
            '''
            excluded because this part is handled in the end_state_parser

            if end not in self:
                raise ValueError(self.__state_error(end, '(ending)'))
            '''
            self.states[start].add_function(end, value)
            functions_added += 1

        self.check_fis_output(functions_added)

    @abc.abstractmethod
    def check_fis_output(self, funcs_added):
        '''
        Checks if successfully parsed FA is indeed correct. Raises a suitable error if something is not right.

        :param int funcs_added: how many functions were added.
        :return:
        '''
        pass

    @staticmethod
    def __wrap_in_braces(string, last_brace_newline=False):
        return '{' + string + ('\n}' if last_brace_newline else '}')

    @staticmethod
    def __tab(string):
        return '\t' + string.replace('\n', '\n\t')

    @staticmethod
    def __space(*strings):
        result = ''
        for s in strings:
            result += s + ' '
        return result[:-1]

    @staticmethod
    def __newline(*lines):
        '''
        Returns concatenated string composed of all line arguments with newline added between them.
        :param str lines: lines of text that need to be newlined.
        :return: full string composed of individual lines concatenated with newline in-between
        '''
        res = '\n'
        for line in lines:
            res += line + '\n'
        return res[:-1]

    def __repr__(self):
        states = ''
        final = ''

        for state, state_object in self.states.items():
            states += state + ','
            if state_object.value:
                final += state

        final = 'F=' + self.__wrap_in_braces(final)

        states = 'Q=' + self.__wrap_in_braces(states[:-1])

        inputs = ''

        for inp in self.inputs:
            inputs += str(inp) + ','

        inputs = u'\u03A3=' + self.__wrap_in_braces(inputs[:-1])

        funcs = u'\u03B4=' + self.__wrap_in_braces(self.functions)

        start = 'q0=' + self.start_state

        return '{} '.format(self.__class__.__name__) + self.__wrap_in_braces(self.__tab(
            self.__newline(states, inputs, funcs, start, final)
        ), True)

    def __contains__(self, item):
        if self.states.get(item, None) is None:
            return False
        return True

    @abc.abstractmethod
    def enter(self, *entry):  # I don't want to define the way inputs are passed through automata
        '''
        Reads all inputs from entry and puts them through the FA.
        It's extremely important to specify the correct in_type when initialising.
        For example, creating a finite automata with in type integer (in_type=int) means that any string input '101' will be
        turned into 101 and therefore will not be segmented.

        Entry itself doesn't have to be a singular value. If you opted for string as input type you can easily put everything into one string.

        Example:
            a = NFA(......,in_type = int)
            a.enter(101, 123, 34)
            a.enter('101') #'101' will be turned into a number 101.

            b = NFA(.......,in_type=str)
            b.enter(101, 124) # all numbers will be turned into strings and processed symbol by symbol (1,0,1,...)
            b.enter("example", 123)

        :param entry: All entries.
        :return: result states
        '''
        pass

    def output(self, *entry):
        results = self.enter(*entry)
        for result in results:
            if result.value > 0:
                return True
        return False
