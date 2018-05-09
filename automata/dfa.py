import automata.fa as fa

class DFA(fa.FiniteAutomaton):
    '''
    Deterministic finite automata.
    '''

    def __init__(self, text, parser):

        super().__init__(text, parser)

        self.current = list(self.current)[0]

    def _check_structure(self):

        function_num = 0

        error_msg = 'Incorrect {} structure.'.format(self.__class__.__name__)

        for state in self.states.values():
            if len(state.transitions) != len(self.inputs):
                raise ValueError(error_msg)
            for end in state.transitions.values():
                if len(end) != 1:
                    raise ValueError(error_msg)

    def reset(self):

        super().reset()
        self.current = self.start_state

    def _access(self, value):

        self.current = self.states[self._get_alias(self.current.clean_forward(value).name)]

    def distinguish(self):

        def is_in(v1, v2, tab):
            return (v1,v2) in tab or (v2,v1) in tab


        states = list(self.states.values())

        table = set()

        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                if states[i].value == states[j].value:
                    table.add((states[i], states[j]))

        added = 1

        while added != 0:
            added = 0
            temp = table.copy()
            for inp in self.inputs:

                for s1, s2 in temp:

                    r1, r2 = s1.clean_forward(inp), s2.clean_forward(inp)
                    if r1 != r2 and not is_in(r1, r2, table):
                        table -= {(s1,s2)} | {(s2, s1)}
                        added += 1

        for s1, s2 in table:
            if s1.name > s2.name:
                c = s1
                s1 = s2
                s2 = c
            self._set_alias(s1.name, s2.name)

        for old_state, new_state in self._alias.items():
            self.states.pop(old_state)

        return table

    def minimize(self):

        self.reachable()
        # print(self)
        self.distinguish()
        # print(self)
        self.start_state = self.states[self._get_alias(self.start_state.name)]