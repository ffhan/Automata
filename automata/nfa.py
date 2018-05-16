"""
Defines Non-deterministic finite automata, including epsilon non deterministic finite automata.
"""
import copy
import automata.fa as fa
import automata.state as st

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

    def __add__(self, other): #todo: implement deepcopy of FA.
        def item_copy(item):
            """
            Deepcopies an item.

            :param item: item to copy
            :return: deep copied item
            """
            return copy.deepcopy(item)
        """
        Allows for epsilon NFA addition.

        :param EpsilonNFA other: other epsilon NFA
        :return EpsilonNFA: resulting NFA
        """
        import form.lexers as lex

        #ensuring state names are not identical when doing multiple additions.
        ending = 'end_'
        for state in self.accepted_states:
            ending += str(state.name)

        # ensuring state names are not identical when doing multiple additions.
        starting = 'start_' + str(self.start_state.name)

        #we need a clean epsilon NFA instance. See NFA union.
        new_e_nfa = self.__class__(
            """{0},{1}
            
            {1}
            {0}
            """.format(starting, ending), lex.StandardFormatLexer()
        )

        starting = new_e_nfa.start_state
        ending = list(new_e_nfa.accepted_states)[0]

        for state in self.states.values():
            copied_state = item_copy(state)
            new_e_nfa.states[copied_state.name] = copied_state
        for state in other.states.values():
            copied_state = item_copy(state)
            new_e_nfa.states[copied_state.name] = copied_state

        for start in new_e_nfa.states.values():
            for event, states in start.transitions.items():
                replace_set = set()
                for state in states:
                    replace_set.add(new_e_nfa.states[state.name])
                start.transitions[event] = replace_set

        for single_input in self.inputs:
            new_e_nfa.inputs.add(item_copy(single_input))
        for single_input in other.inputs:
            new_e_nfa.inputs.add(item_copy(single_input))

        starting.add_function(new_e_nfa.states[self.start_state.name], self._epsilon)
        starting.add_function(new_e_nfa.states[other.start_state.name], self._epsilon)

        for state in new_e_nfa.accepted_states:
            if state != ending:
                state.add_function(ending, self._epsilon)
        #
        # for state in other.accepted_states:
        #     state.add_function(ending, self._epsilon)

        new_e_nfa = item_copy(new_e_nfa)

        for state in new_e_nfa.accepted_states:
            if state != ending:
                state.value = 0

        return new_e_nfa

    def __mul__(self, other):
        def item_copy(item):
            """
            Deep copies an item.

            :param item: item to copy
            :return: deep copied item
            """
            return copy.deepcopy(item)
        """
        Allows for multiplying epsilon NFA-s.

        :param EpsilonNFA other: other EpsilonNFA
        :return EpsilonNFA: multiplied NFA-s
        """

        first = item_copy(self)
        for state in other.states.values():
            copied_state = item_copy(state)
            first.states[copied_state.name] = copied_state
        for single_input in other.inputs:
            first.inputs.add(single_input)
        for state in first.accepted_states:
            if state not in other.accepted_states:
                state.value = 0
                state.add_function(item_copy(other.start_state), self._epsilon)

        for start in first.states.values():
            for event, states in start.transitions.items():
                replace_set = set()
                for state in states:
                    replace_set.add(first.states[state.name])
                start.transitions[event] = replace_set

        new_e_nfa = copy.deepcopy(first)

        return new_e_nfa

    def kleene_operator(self):

        def item_copy(item):
            """
            Deep copy an item.

            :param item: item to copy
            :return: deep copied item
            """
            return copy.deepcopy(item)

        import form.lexers as lex

        # ensuring state names are not identical when doing multiple additions.
        ending = 'end_'
        for state in self.accepted_states:
            ending += str(state.name)

        # ensuring state names are not identical when doing multiple additions.
        starting = 'start_' + str(self.start_state.name)

        # we need a clean epsilon NFA instance. See NFA union.
        new_e_nfa = self.__class__(
            """{0},{1}

            {1}
            {0}
            """.format(starting, ending), lex.StandardFormatLexer()
        )

        starting = new_e_nfa.start_state
        ending = list(new_e_nfa.accepted_states)[0]
        starting.add_function(ending, self._epsilon)

        for state in self.states.values():
            copied_state = item_copy(state)
            new_e_nfa.states[copied_state.name] = copied_state

        for start in new_e_nfa.states.values():
            for event, states in start.transitions.items():
                replace_set = set()
                for state in states:
                    replace_set.add(new_e_nfa.states[state.name])
                start.transitions[event] = replace_set

        for single_input in self.inputs:
            new_e_nfa.inputs.add(item_copy(single_input))

        starting.add_function(new_e_nfa.states[self.start_state.name], self._epsilon)
        ending.add_function(new_e_nfa.states[self.start_state.name], self._epsilon)

        for state in new_e_nfa.accepted_states:
            if state != ending:
                state.add_function(ending, self._epsilon)
        #
        # for state in other.accepted_states:
        #     state.add_function(ending, self._epsilon)

        for state in new_e_nfa.accepted_states:
            if state != ending:
                state.value = 0

        return new_e_nfa
