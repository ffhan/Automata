"""
Defines Non-deterministic finite automata, including epsilon non deterministic finite automata.
"""
import copy
import automata.fa as fa
import automata.state as st
import misc.helper as helper

class NFA(fa.FiniteAutomaton):
    '''
    Non-deterministic finite automata.
    '''

    def distinguish(self):
        raise NotImplementedError

    def minimize(self):
        raise NotImplementedError

    def _check_structure(self):
        #does nothing.
        pass

    @property
    def accepted(self):
        for state in self.current:
            if state in self.accepted_states:
                return True
        return False

    def _access(self, value):

        if value not in self.inputs:
            raise ValueError(self._input_error(value))

        old_currents = set()

        for state in sorted(list(self.current)):
            res = state.forward(value)

            for end in res:
                old_currents.add(self.states[self._get_alias(end.name)])

        self.current = old_currents

    @staticmethod
    def factory(input_text, lexer):
        lexer.scan(input_text)
        return __class__(lexer.states, lexer.inputs, lexer.start_state)

class EpsilonNFA(NFA):
    """
    Epsilon non-deterministic finite automata.
    """

    def minimize(self):
        raise NotImplementedError

    def distinguish(self):
        raise NotImplementedError

    def __init__(self, states, inputs, start_state, epsilon='$'):

        self._epsilon = epsilon

        super().__init__(states, inputs, start_state)

        self.inputs.add(epsilon)

    @property
    def epsilon(self):
        return self._epsilon

    @property
    def accepted(self):
        for state in self._all_closures():
            if state in self.accepted_states:
                return True
        return False

    def _e_closure(self, state, closure):
        """
        Returns an epsilon closure of a state.

        :param State state: state
        :param set closure: closure set
        :return set: epsilon closure of a state
        """

        if state not in self:
            raise ValueError(self._input_error(state))

        if isinstance(state, str):
            closure -= {state}
            state = self.states[state]
        closure |= {state}

        for eps in state.forward(self._epsilon):
            if eps not in closure:
                self._e_closure(eps, closure)

        return closure

    def e_closures(self, *states):
        """
        Returns epsilon closure for all specified states.

        :param states: specified states
        :return set: epsilon closure for specified states
        """
        currents = set(states) if not isinstance(states, set) else states

        for i in states:
            currents |= self._e_closure(i, currents)

        return currents

    def _all_closures(self):

        """
        Returns epsilon closure of all current states.

        :return set: epsilon closure
        """

        return self.e_closures(*self.current)

    def _access(self, value):

        super()._access(value)

        self.current = self._all_closures()

    def _process(self, *entry):

        self.current = self._all_closures()

        return super()._process(*entry)

    def __add__(self, other):
        """
        Allows for epsilon NFA addition.

        :param EpsilonNFA other: other epsilon NFA
        :return EpsilonNFA: resulting NFA
        """
        import form.generators as lex

        #ensuring state names are not identical when doing multiple additions.
        ending = 'end_'
        for state in self.accepted_states:
            ending += str(state.name)
        for state in other.accepted_states:
            ending += str(state.name)

        # ensuring state names are not identical when doing multiple additions.
        starting = 'start_' + str(self.start_state.name) + str(other.start_state.name)

        #we need a clean epsilon NFA instance. See NFA union.
        new_e_nfa = self.factory(
            """{0},{1}

{1}
{0}
""".format(starting, ending), lex.StandardFormatGenerator())

        starting = new_e_nfa.start_state
        ending = list(new_e_nfa.accepted_states)[0]

        copied_self = self.deepcopy()
        copied_other = other.deepcopy()
        states = dict()

        for name in list(copied_self.states):
            new_name = 'a_0' + name.name
            state = copied_self.states[name]
            state.name = st.StateName(new_name)
            states[state.name] = state
        for name in list(copied_other.states):
            new_name = 'a_1' + name.name
            state = copied_other.states[name]
            state.name = st.StateName(new_name)
            states[state.name] = state

        # new_e_nfa.states.update(copied_self.states)
        # new_e_nfa.states.update(copied_other.states)
        new_e_nfa.states.update(states)
        new_e_nfa.inputs |= copied_self.inputs | copied_other.inputs

        starting.add_function(new_e_nfa.states[copied_self.start_state.name], self._epsilon)
        starting.add_function(new_e_nfa.states[copied_other.start_state.name], self._epsilon)

        for state in new_e_nfa.accepted_states:
            if state != ending:
                state.add_function(ending, self._epsilon)

        for state in new_e_nfa.accepted_states:
            if state != ending:
                state.value = 0

        return new_e_nfa

    def __mul__(self, other):
        """
        Allows for multiplying epsilon NFA-s.

        :param EpsilonNFA other: other EpsilonNFA
        :return EpsilonNFA: multiplied NFA-s
        """

        first = self.deepcopy()
        size1 = len(first.states)
        other = other.deepcopy()
        size2 = len(other.states)

        states = dict()

        for name in list(first.states):
            new_name = 'm_0' + name.name
            state = first.states[name]
            state.name = st.StateName(new_name)
            states[state.name] = state

        for name in list(other.states):
            new_name = 'm_1' + name.name
            state = other.states[name]
            state.name = st.StateName(new_name)
            states[state.name] = state

        for state in list(first.accepted_states):
            state.add_function(other.start_state, first.epsilon)

        # first.states.update(other.states)
        first.states = states

        try:
            assert len(first.states) == size1 + size2
        except AssertionError as err:
            raise err
        first.inputs |= other.inputs

        for state in first.accepted_states:
            if state not in other.accepted_states:
                state.value = 0

        return first

    def kleene_operator(self):

        import form.generators as lex

        # ensuring state names are not identical when doing multiple additions.
        ending = 'end_'
        for state in self.accepted_states:
            ending += str(state.name)

        # ensuring state names are not identical when doing multiple additions.
        starting = 'start_' + str(self.start_state.name)

        # we need a clean epsilon NFA instance. See NFA union.
        new_e_nfa = self.factory(
            """{0},{1}

{1}
{0}
""".format(starting, ending), lex.StandardFormatGenerator()) # starting and ending might need escaping

        starting = new_e_nfa.start_state
        ending = list(new_e_nfa.accepted_states)[0]
        starting.add_function(ending, self._epsilon)

        copied_self = self.deepcopy()

        new_e_nfa.states.update(copied_self.states)
        new_e_nfa.inputs |= copied_self.inputs

        starting.add_function(new_e_nfa.states[self.start_state.name], self._epsilon)
        ending.add_function(new_e_nfa.states[self.start_state.name], self._epsilon)

        for state in new_e_nfa.accepted_states:
            if state != ending:
                state.add_function(ending, self._epsilon)

        for state in new_e_nfa.accepted_states:
            if state != ending:
                state.value = 0

        return new_e_nfa

    @staticmethod
    def factory(input_text, lexer):
        lexer.scan(input_text)
        return __class__(lexer.states, lexer.inputs, lexer.start_state)

    def _create_copy(self, *args):
        return self.__class__(*args, epsilon=copy.deepcopy(self._epsilon))

    def _create_state(self, *args):
        return st.State(*args, epsilon=self._epsilon)
