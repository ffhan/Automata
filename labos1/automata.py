import collections
import re
import abc

class State:
    def __init__(self, name, value, **rules):
        '''
        Initialises an automata state.

        :param name: name of the state
        :param value: value the state holds (can be used externally to define if a state is accepted or not)
        :param parent: parent automata (any class derived from FA)
        :param rules: transition functions
        '''

        self.name = name
        self.value = value

        self.__transitions = dict()

        if len(rules) > 0:
            self.add_functions(rules)

    def add_function(self, end_state, event):
        '''
        Adds a single transition function.
        :param end_state: a single state or a list of states
        :param event: input value that calls this function
        :return:
        '''
        self.__transitions[event] = end_state

    def add_functions(self, **rules):
        '''
        Adds multiple transition functions.

        Example:
            d = State(...)
            d.add_functions(q1=4, q2=5, q3={2,3})
            ...

        :param rules: transition functions pairs state=value or values
        :return:
        '''
        try:
            for state, value in rules.items():
                if not isinstance(value, collections.Iterable):
                    value = list((value,))
                for single_value in value:
                    self.add_function(state, single_value)
        except IndexError:
            raise IndexError('Transition functions have to be defined with a tuple (end state, transition value)!')

    def __repr__(self):
        result = 'State {} (value {}):\n'.format(self.name, self.value)
        side = ''
        for state, trans_value in self.__transitions.items():
            side += 'on {} -> {}\n'.format(state, trans_value)
        side = side[:-1]
        return result + self.__wrap(side)

    @staticmethod
    def __wrap(state_string):
        return ('{\n' + state_string).replace('\n', '\n\t') + '\n}'

    def forward(self, value):
        try:
            return self.__transitions[value]
        except KeyError:
            raise KeyError('Illegal transition function value {}.'.format(value))

class FA(abc.ABC):
    '''
    Finite automata base abstract class. It isn't aware of transition functions.
    '''
    def __init__(self, states, inputs, start_state, final_states, in_type = int):
        '''
        Initialises a DFA.

        :param states: set of all possible states
        :param inputs: set of all possible inputs
        :param start_state: single starting state
        :param final_states: set of all possible final (accepting) states
        :param in_type: input type (string or int)
        '''
        self.states = dict()
        self.inputs = set()
        self.functions = ''
        #I deliberately include functions although they are not defined in FA class so that __repr__ can be written
        #only in the base class.

        self.type = in_type

        for one_input in inputs:
            self.inputs |= {one_input}

        for state in states:
            self.states[state] = State(state, 1 if state in final_states else 0)

        if self.states.get(start_state, 0):
            self.start_state = start_state
            self.current = self.states[start_state]
        else:
            raise ValueError('State {} not defined in this automata.'.format(start_state))

    @abc.abstractmethod
    def parse_functions_string(self, functions):
        pass

    @staticmethod
    def __wrap_in_braces(string, last_brace_newline=False):
        return '{' + string + ('\n}' if last_brace_newline else '}')

    @staticmethod
    def __tab(string):
        return '\t' + string.replace('\n', '\n\t')

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

        return 'DFA ' + self.__wrap_in_braces(self.__tab(
            self.__newline(states, inputs, funcs, start, final)
        ), True)

    def __contains__(self, item):
        if self.states.get(item, None) is None:
            return False
        return True

    @abc.abstractmethod
    def enter(self, *entry): #I don't want to define the way inputs are passed through the automata
        pass

class DFA(FA): #todo: see if you can utilize class inheritance so that NFA doesn't have to be rewritten.
    '''
    Deterministic finite automata.
    '''
    def __init__(self, states, inputs, functions, start_state, final_states, in_type = int):
        '''
        Initialises a DFA.

        :param states: set of all possible states
        :param inputs: set of all possible inputs
        :param str functions: FIS. see parse_functions_string documentation
        :param start_state: single starting state
        :param final_states: set of all possible final (accepting) states
        :param in_type: input type (string or int)
        '''

        super().__init__(states,inputs,start_state,final_states,in_type)

        self.parse_functions_string(functions)

    def parse_functions_string(self, functions): #todo: improve string handling, maybe completely remove FIS.
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
            start_state:transition_value->end_state

        Example:
            q0:1->q1

        Example of the whole notation system:
            q0:0->q0;
            q0:1->q1;
            q1:0->q1;
            q1:1->q1

        :param str functions: A string defining transition functions for DFA
        :return:
        '''

        funcs = re.sub(r"[\n\t *]", '', functions)
        self.functions = funcs
        try:
            funcs = funcs.split(';')
        except AttributeError:
            raise AttributeError('Invalid function instruction string. Check your function string.')

        functions_added = 0
        for transition_func in funcs:
            try:
                start, valueend = transition_func.split(':')
                value, end = valueend.split('->')
            except (AttributeError, ValueError) as error:
                raise type(error)('Invalid function instruction string. Check your function string.')
            value = self.type(value.strip('"').strip("'")) #sanitizing input
            if start not in self:
                raise ValueError('(starting) State "{}" not defined in this DFA'.format(start))
            if value not in self.inputs:
                raise ValueError('Input "{}" not defined in this DFA'.format(value))
            if end not in self:
                raise ValueError('(ending) State "{}" not defined in this DFA'.format(end))
            self.states[start].add_function(end, value)
            functions_added += 1

        function_check = functions_added - len(self.states) * len(self.inputs)
        if function_check < 0:
            raise AttributeError('Some transition functions were undefined! Check your function instruction string!')
        elif function_check > 0:
            raise AttributeError('You have defined too many transition functions! DFA has to have a function mapped from each state through each input!')

    def enter(self, *entry): #I hate this function. Redo it.
        for inp in entry:
            if isinstance(inp, collections.Iterable):
                for i in inp:
                    self.current = self.states[self.current.forward(self.type(i))]
            else:
                self.current = self.states[self.current.forward(self.type(inp))]
        return self.current

def create_function_string(newline = False, **rules):
    '''
    Creates function string from parameters. This enables the programmer to use both string-type functional input or direct programming.

    Example:
        create_function_string(q0={0:'q0', 1:'q1'}, q1={0:'q0', 1:'q1'})
    :param bool newline: defines if FIS is going to have each function defined in its' own row
    :param dict rules: dictionary with keys (str) being inputs and values (str) being state names
    :return: Function instruction string
    '''
    result = ''

    for start, value_and_end in rules.items():
        for value, end in value_and_end.items():
            result += start + ':' + str(value) + '->' + end + ';' + ('\n' if newline else '')
    return result

has_0_then_1 = DFA({'q0', 'q1', 'q2'}, {0,1},
          '''
          q0:0->q2;
          q0:1->q0;
          q2:1->q1;
          q2:0->q2;
          q1:0->q1;
          q1:1->q1
          ''',
          'q0', {'q1'})

# has_0_then_1.enter('101')

equal01 = DFA({'botheven',
               '1even0odd',
               '1odd0even',
               'bothodd'},
              {'0', '1'},
              '''
              botheven:0->1even0odd;
              botheven:1->1odd0even;
              1even0odd:0->botheven;
              1even0odd:1->bothodd;
              1odd0even:0->bothodd;
              1odd0even:1->botheven;
              bothodd:0->1odd0even;
              bothodd:1->1even0odd
              ''', 'botheven', {'botheven'}, str)

print(equal01.enter('10110010'))

# example of generating the upper function instruction string (FIS):

print(create_function_string(newline=True,
                             q0={0:'q1',1:'q2'},
                             q1={0:'q0',1:'q3'},
                             q2={0:'q3',1:'q0'},
                             q3={0:'q2',1:'q1'}))