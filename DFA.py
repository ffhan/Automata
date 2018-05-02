import FA
import copy

class DFA(FA.FA):
    '''
    Deterministic finite automata.
    '''

    def _check_fis_output(self, funcs_added):
        function_check = funcs_added - len(self.states) * len(self.inputs)
        if function_check < 0:
            raise AttributeError('Some transition functions were undefined! Check your function instruction string!')
        elif function_check > 0:
            raise AttributeError(
                'You have defined too many transition functions! DFA has to have a function mapped from each state through each input!')

    def _end_state_parser(self, end_state_string):
        if end_state_string not in self:
            raise ValueError(self._state_error(end_state_string, '(ending)'))
        return end_state_string

    def _access(self, value):

        self.current = self.states[list(self.current.forward(self.type(value)))[0]]

    def _reachable(self, state, visited = set()): #todo: migrate to FA.
        visited |= {state}
        for i in self.states[state]._transitions.values():
            for j in i:
                if not j in visited:
                    self._reachable(j, visited)

    def reachable(self):

        visited = set()

        self._reachable(self.start_state, visited)

        states = dict()

        start = set(self.states.copy().values())
        for state_name in visited:

            states[state_name] = self.states[state_name]

        # print(visited, states)
        # print(start - set(states.values()), states)
        self.states = states
        self._update_functions()

    def distinguish(self):

        def is_in(v1, v2, tab):
            v1 = self.states[v1]
            v2 = self.states[v2]
            return (v1,v2) in tab or (v2,v1) in tab


        states = list(self.states.values())

        table = set()

        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                if states[i].value == states[j].value:
                    table |= {(states[i], states[j])}

        added = 1

        aliases = dict()

        while added != 0:
            added = 0
            temp = copy.deepcopy(table)
            for inp in self.inputs:

                for s1, s2 in temp:
                    # if not in_table(s1, s2, 'fake'):
                    #     continue
                    r1, r2 = s1.clean_forward(inp), s2.clean_forward(inp)

                    # print('step {}:'.format(step), s1, s2, inp, r1, r2)
                    if r1 != r2 and not is_in(r1, r2, table):
                        # print(s1, s2, inp, r1, r2, added)
                        table -= {(s1,s2)} | {(s2, s1)}
                        added += 1
                    # elif r1 != r2:
                    #     if r1 > r2: # make sure there's only one possible key tuple
                    #         c = r1
                    #         r1 = r2
                    #         r2 = c
                    #     if not aliases.get((r1,r2), False):
                    #         aliases[(r1,r2)] = {s1,s2}
                    #     else:
                    #         aliases[(r1,r2)] |= {s1,s2}
        # table |= {(self.states['p1'], self.states['p2'])}
        for s1, s2 in table:
            if s1.name > s2.name:
                c = s1
                s1 = s2
                s2 = c
            self._set_alias(s1.name, s2.name)
            if not aliases.get(s1, False):
                aliases[s1] = {s2}
            else:
                aliases[s1] |= {s2}

        # print(aliases, self.alias)

        # new_states = self.states.copy()

        for old_state, new_state in self.alias.items():
            self.states.pop(old_state)
            old_state = new_state

        # print(self.alias)
        #
        # for state, alias in aliases.items():
        #     for key, my_state in self.states.items():
        #         for al in alias:
        #             if my_state == al:
        #                 # print(al)
        #                 # print("deleted {} that is aliased with {}".format(key, self.get_alias(key)))
        #                 if new_states.get(key, False):
        #                     new_states.pop(key)
        #             else:
        #                 my_alias = self._get_alias(key)
        #                 # print(new_states, self.alias, self.states, my_alias, type(my_alias), key, type(key), al, type(al), state, type(state))
        #                 try:
        #                     if new_states.get(my_alias, False):
        #                         new_states[my_alias].alias(al.name, state.name)
        #                 except Exception as e:
        #                     raise e
        #
        #             # print(state,al,key,my_state,new_states)
        # self.states = new_states.copy()
        # print(self.alias)
        self._update_functions()
        return table

    def minimize(self):

        self.reachable()
        # print(self)
        self.distinguish()
        # print(self)