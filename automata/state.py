"""
Defines State type which is one of the basic building
blocks of the library.

Also includes StateName.
"""
import collections

class StateName:
    '''
    Wrapper for the State name, enables direct object renaming.
    Inherits string class, allowing us to treat it as a string.
    '''

    def __init__(self, name: str):

        try:
            assert isinstance(name, str)
        except:
            raise TypeError('Name "{}" is not a string!'.format(name))
        self._name = ''
        self.name = name

    def __add__(self, other)->str:
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
        """
        Returns state name

        :return str: state name
        """
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
        elif isinstance(other, State):
            return other.name == self
        elif isinstance(other, self.__class__):
            return other.name == self.name
        return False

    def __hash__(self):

        return hash(self.name)

    def __repr__(self):

        return self.name

class State:
    """
    Defines an automaton State.
    Contains State name, the value it holds and all transition functions.
    """
    def __init__(self, name, value, epsilon='$'):
        '''
        Initialises an automata state.

        :param name: name of the state
        :param value: value the state holds
        '''

        self.name = StateName(name)
        self.value = value

        self.transitions = dict()

        self._epsilon = epsilon

    @property
    def epsilon(self):
        return self._epsilon

    @property
    def accepted(self):
        """
        Returns if a State is accepted.

        :return: True if accepted, False if not.
        """
        return self.value == 1

    @property
    def direct_reach(self):

        """
        Returns all directly reachable states.

        :return: all directly reachable states
        """

        reach = set()

        for states in self.transitions.values():
            for state in states:
                reach.add(state)
        return reach

    @staticmethod
    def __clean(value):

        """
        Cleans output of a state forward.

        :param value: forward return value
        :return:
        """

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
            # assert isinstance(state, self.__class__)
            for single_event in event:
                if self.transitions.get(single_event, -1) == -1:
                    self.transitions[single_event] = {state}
                else:
                    self.transitions[single_event].add(state)

    def __repr__(self):
        # result = 'State {} (value {}):\n'.form(self.name, self.value)
        # side = ''
        # for state, trans_value in self.__transitions.items():
        #     side += 'on {} -> {}\n'.form(state, trans_value)
        # side = side[:-1]
        # return result + self.__wrap(side)
        return str(self.name)

    # def __str__(self):
    #
    #     def wrap(text):
    #         return '\t' + text.replace('\n', '\n\t')
    #     result = 'State {} (value {}):\n'.form(self.name, self.value)
    #     side = ''
    #     for state, trans_value in self._transitions.items():
    #         side += 'on {} -> {}\n'.form(state, trans_value)
    #     side = side[:-1]
    #     return result + wrap(side)

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

        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def forward(self, value):
        '''
        Pass a value through the automatum and return the end state.

        :param value: input
        :return set: End State(s)
        '''

        return self.transitions.get(value, set()) # | self._transitions.get(self.epsilon, set())

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

    @property
    def indirect_reach(self):
        """
        Returns an indirect reach.
        Recursively finds all States that can be reached out of this State.

        Differs from direct_reach because it also returns all reachable
        states of directly reachable states.

        Differs from epsilon closure because it returns all states
        directly or indirectly reachable, not just states bound by epsilon transitions.

        :return set: all indirectly reachable states.
        """

        visits = set()
        self._reachable(self, visits)
        return visits

    @property
    def epsilon_closure(self):
        """
        Returns an epsilon closure.

        To see differences between direct reach, indirect reach and epsilon closure
        see indirect_reach method documentation.

        :return set: epsilon closure for the state
        """
        visited = set()
        return self._epsilon_closure(visited)

    def _epsilon_closure(self, visited):
        """
        Internal recursive epsilon closure finder.
        Do not use directly.

        Does NOT return the whole epsilon closure.

        :param set visited: set of currently visited States
        :return set: part of epsilon closure
        """

        visited.add(self)
        for state in self.forward(self.epsilon):
            if not state in visited:
                visited |= state._epsilon_closure(visited)
        return visited

    def _reachable(self, state, visited):
        """
        Returns all indirectly reachable states for a specified state.
        Defined in a separate (internal) method because
        it could be a subject of change in derived classes.

        :param State state: specified State
        :param set visited: set of all currently visited States.
        :return:
        """
        visited |= {state}
        for i in state.direct_reach:
            if not i in visited:
                self._reachable(i, visited)

    def __contains__(self, item):

        return item in self.transitions
