import collections

class StateName:
    '''
    Wrapper for the State name, enables direct object renaming.
    Inherits string class, allowing us to treat it as a string.
    '''

    def __init__(self, name):
        #super().__init__()
        self._name = ''
        self.name = name
		
    def __add__(self, other):
        """
        Concatenates a string or other State name.

        :param other: State name (StateName or string)
        :return str: Concatenated name
        """
        if isinstance(other, str):
            return self.name + other
        return self.__add__(other.name)

    def __iadd__(self, other):

        self.name = self.__add__(other)
        return self

    def __lt__(self, other):
        if isinstance(other, str):
            return self.name < other
        return self.name < other.name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, other):
        if isinstance(other, str):
            self._name = other
        else:
            raise TypeError('State name has to be a string.')


    def __eq__(self, other):

        if isinstance(other, str):
            return other == self.name

        if not isinstance(other, self.__class__):
            return False

        if other.name == self.name:
            return True

    def __hash__(self):

        return hash(self.name)

    def __repr__(self):

        return self.name

class State:
    def __init__(self, name, value, epsilon = '$'):
        '''
        Initialises an automata state.

        :param name: name of the state
        :param value: value the state holds (can be used externally to define if a state is accepted or not)
        :param parent: parent automata (any class derived from FA)
        :param rules: transition functions
        '''

        self.name = StateName(name)
        self.value = value

        self._transitions = dict()

        self.epsilon = epsilon

    @property
    def accepted(self):
        """
        Returns if a State is accepted.

        :return: True if accepted, False if not.
        """
        return bool(self.value)

    @property
    def reach(self):

        return list(self._transitions.values())

    @property
    def transitions(self):

        return list(self._transitions.items())

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
                if self._transitions.get(ev, -1) == -1:
                    self._transitions[ev] = {state}
                else:
                    self._transitions[ev] |= {state}

    def __repr__(self):
        # result = 'State {} (value {}):\n'.format(self.name, self.value)
        # side = ''
        # for state, trans_value in self.__transitions.items():
        #     side += 'on {} -> {}\n'.format(state, trans_value)
        # side = side[:-1]
        # return result + self.__wrap(side)
        return str(self.name)

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

        if other.name == self.name and other.value == self.value and other._transitions == self._transitions:
            return True
        return False

    def __hash__(self):
        result = '{}{}'.format(self.name.name, self.value)
        side = ''
        for state, trans_value in self._transitions.items():
            side += '{}{}\n'.format(state, trans_value)
        side = result + side[:-1]

        return hash(self.name) + hash(self.value) + hash(side) + hash(len(self._transitions))

    def forward(self, value):

        '''
        Pass a value through the automatum and return the end state.

        :param value: input
        :return set: End State(s)
        '''

        return self._transitions.get(value, set()) # | self._transitions.get(self.epsilon, set())

    def clean_forward(self, value):
        '''
        Return a single value instead of a set if set length is 1.

        :param value: input
        :return: End State(s)
        '''

        res = self.forward(value)

        if len(res) == 1:
            return list(res)[0]
        return res