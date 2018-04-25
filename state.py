import collections

class State:
    def __init__(self, name, value, epsilon = '$', **rules):
        '''
        Initialises an automata state.

        :param name: name of the state
        :param value: value the state holds (can be used externally to define if a state is accepted or not)
        :param parent: parent automata (any class derived from FA)
        :param rules: transition functions
        '''

        self.name = name
        self.value = value

        self._transitions = dict()

        self.epsilon = epsilon

        if len(rules) > 0:
            self.add_functions(**rules)

    @staticmethod
    def __clean(value):

        if not isinstance(value, collections.Iterable) or isinstance(value, str):
            value = {value}
        return value

    def add_function(self, end_state, event):
        '''
        Adds a single transition function.
        :param State end_state: a single state or a list of states
        :param event: input value that calls this function
        :return:
        '''

        end_state = self.__clean(end_state)
        event = self.__clean(event)

        for state in end_state:
            for ev in event:
                if self._transitions.get(ev, -1) == -1:
                    self._transitions[ev] = {state}
                else:
                    self._transitions[ev] |= {state}


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

    def __lt__(self, other):

        if type(other) is not type(self):
            return 1

        return self.name < other.name

    def __eq__(self, other):
        '''
        Checks if State has the same name.

        :param State other: second State
        :return: True if States have the same name
        '''

        if not isinstance(other, self.__class__):
            return False

        if other.name == self.name:
            return True
        return False

    def __hash__(self):
        result = '{}{}'.format(self.name, self.value)
        side = ''
        for state, trans_value in self._transitions.items():
            side += '{}{}\n'.format(state, trans_value)
        side = result + side[:-1]

        return hash(self.name) + hash(self.value) + hash(side)

    def distinguish(self, other):
        '''
        Returns True if states are distinguishable, False if they are not.

        It's not the same as equality (==).

        :param State other: second State
        :return: distinguishability
        '''

        return NotImplementedError()


    def forward(self, value):

        return self._transitions.get(value, set()) # | self._transitions.get(self.epsilon, set())