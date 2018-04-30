import FA
import copy

class DFA(FA.FA): #todo: see if you can utilize class inheritance so that NFA doesn't have to be rewritten.
    '''
    Deterministic finite automata.
    '''

    def check_fis_output(self, funcs_added):
        function_check = funcs_added - len(self.states) * len(self.inputs)
        if function_check < 0:
            raise AttributeError('Some transition functions were undefined! Check your function instruction string!')
        elif function_check > 0:
            raise AttributeError(
                'You have defined too many transition functions! DFA has to have a function mapped from each state through each input!')

    def end_state_parser(self, end_state_string):
        if end_state_string not in self:
            raise ValueError(self._state_error(end_state_string, '(ending)'))
        return end_state_string

    def _access(self, value):

        self.current = self.states[list(self.current.forward(self.type(value)))[0]]

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
            if not aliases.get(s1, False):
                aliases[s1] = {s2}
            else:
                aliases[s1] |= {s2}

        print(aliases)

        new_states = self.states.copy()

        for state, alias in aliases.items():
            for key, my_state in self.states.items():
                for al in alias:
                    if my_state == al:
                        # print(al)
                        new_states.pop(key)
                        self.set_alias(state, key)
                    else:
                        new_states[self.get_alias(key).name].alias(al, state)  # todo: neka mijenja sve tranzicije koje spominju alias sa stateom i neka na kraju izbrise state i regenerira functions

                    # print(state,al,key,my_state,new_states)
        self.states = new_states.copy()
        print(self.alias)
        return table