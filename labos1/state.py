from labos1 import collections
from labos1 import DFA, NFA, FA

class State:
    def __init__(self, name, value, state_type = DFA, **rules):
        '''
        Initialises an automata state.

        :param name: name of the state
        :param value: value the state holds (can be used externally to define if a state is accepted or not)
        :param parent: parent automata (any class derived from FA)
        :param rules: transition functions
        '''

        self.name = name
        self.value = value

        def get_parent(cls):
            '''
            Determines if state type class is FA (finite automata).

            :param cls: metaclass provided as state_type on State initialisation.
            :return: base class type
            '''
            if not cls.__base__ is object:
                return get_parent(cls.__base__)
            return cls

        if not get_parent(state_type) is FA:
            raise TypeError('Automata type {} provided in state_type is not derived from FA class.'.format(state_type.__name__))
        self.state_type = state_type

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

        if self.state_type is DFA:
            self.__transitions[end_state] = event
        elif self.state_type is NFA:
            if self.__transitions.get(end_state, -1) == -1:
                self.__transitions[end_state] = {event}
            else:
                self.__transitions[end_state] |= {event}


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

    def forward(self, value): #todo: fix forwarding when using NFA.
        try:
            return self.__transitions[value]
        except KeyError:
            raise KeyError('Illegal transition function value {}.'.format(value))