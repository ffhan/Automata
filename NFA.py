import FA

class NFA(FA.FA):
    '''
    Non-deterministic finite automata.
    '''

    def __init__(self, states, inputs, functions, start_state, final_states, in_type = str):
        super().__init__(states, inputs, functions, start_state, final_states, in_type)

        self.current = {self.current} #NFA holds current states in a set

    def check_fis_output(self, funcs_added):
        #does nothing for NFA.
        pass

    def reset(self):
        super().reset()
        self.current = {self.current}

    def end_state_parser(self, end_state_string):
        '''
        Parses end states.

        :param str end_state_string: String containing state names divided by a comma.
        :return list: list of all end state names
        '''
        states = []
        for state in end_state_string.split(','):
            clean_state = state.strip()
            if clean_state not in self:
                # print(clean_state, self.states)
                raise ValueError(self._state_err or(clean_state, '(ending)'))
            states.append(clean_state)
        return states


    def _access(self, value):

        if value not in self.inputs:
            raise ValueError(self._input_error(value))

        # print(value, self.current)

        old_currents = set()

        # print(value)
        for state in sorted(list(self.current)):
            res = state.forward(self.type(value))

            # print(state, res)

            # print(state, state._transitions)

            for end in res:
                old_currents |= {self.states[end]}
                # print(end, old_currents)
        # print(old_currents)
        # print("-" * 20)
        self.current = old_currents

class E_NFA(NFA):

    def __init__(self, states, inputs, functions, start_state, final_states, epsilon = '$', in_type = str):

        inputs |= {epsilon}
        self._epsilon = epsilon

        super().__init__(states, inputs, functions, start_state, final_states, in_type)

    def e_closure(self, state, closure = set()):
        if state not in self:
            raise ValueError(self._input_error(state))

        if type(state) is str:
            closure -= {state}
            state = self.states[state]
        closure |= {state}

        for eps in state.forward(self._epsilon):
            if self.states[eps] not in closure:
                self.e_closure(self.states[eps], closure)

        return closure

    def e_closures(self, *states):
        currents = set(states) if type(states) is not set else states

        for i in states:
            currents |= self.e_closure(i, currents)

        return currents

    def all_closures(self):

        return self.e_closures(*self.current)

    def _access(self, value):

        super()._access(value)

        self.current = self.all_closures()

    def _process(self, *entry):

        self.current = self.all_closures()

        return super()._process(*entry)


