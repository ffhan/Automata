from labos1 import collections

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

    @staticmethod
    def __clean(value):

        if not isinstance(value, collections.Iterable) or isinstance(value, str):
            value = {value}
        return value

    def add_function(self, end_state, event):
        '''
        Adds a single transition function.
        :param end_state: a single state or a list of states
        :param event: input value that calls this function
        :return:
        '''

        end_state = self.__clean(end_state)
        event = self.__clean(event)

        for state in end_state:
            for ev in event:
                if self.__transitions.get(ev, -1) == -1:
                    self.__transitions[ev] = {state}
                else:
                    self.__transitions[ev] |= {state}


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
                value = self.__clean(value)
                state = self.__clean(state)
                for single_value in value:
                    self.add_function(state, single_value)
        except IndexError:
            raise IndexError('Transition functions have to be defined with a tuple (end state, transition value)!')

    def __repr__(self):
        # result = 'State {} (value {}):\n'.format(self.name, self.value)
        # side = ''
        # for state, trans_value in self.__transitions.items():
        #     side += 'on {} -> {}\n'.format(state, trans_value)
        # side = side[:-1]
        # return result + self.__wrap(side)
        return self.name

    @staticmethod
    def __wrap(state_string):
        return ('{\n' + state_string).replace('\n', '\n\t') + '\n}'

    def forward(self, value):

        res = self.__transitions.get(value, -1)

        return None if res == -1 else res



