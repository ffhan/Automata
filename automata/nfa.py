"""
Defines Non-deterministic finite automata, including epsilon non deterministic finite automata.
"""
import automata.fa as fa

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

class EpsilonNFA(NFA):
    """
    Epsilon non-deterministic finite automata.
    """

    def minimize(self):
        raise NotImplementedError

    def distinguish(self):
        raise NotImplementedError

    def __init__(self, text, lexer, epsilon='$'):

        self._epsilon = epsilon

        super().__init__(text, lexer)

        self.inputs.add(epsilon)

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

    def _e_closures(self, *states):
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

        return self._e_closures(*self.current)

    def _access(self, value):

        super()._access(value)

        self.current = self._all_closures()

    def _process(self, *entry):

        self.current = self._all_closures()

        return super()._process(*entry)
