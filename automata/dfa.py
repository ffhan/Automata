from automata import fa
import copy

class Deterministic(fa.FiniteAutomaton):
    '''
    Deterministic finite automata.
    '''

    def __init__(self, states, inputs, functions, start_state, final_states):

        super().__init__(states, inputs, functions, start_state, final_states)

        self.current = list(self.current)[0]

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
        for i in self.states[state.name].reach:
            if not i in visited:
                self._reachable(i, visited)

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

        while added != 0:
            added = 0
            temp = copy.deepcopy(table)
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
            old_state = new_state

        self._update_functions()
        return table

    def minimize(self):

        self.reachable()
        # print(self)
        self.distinguish()
        # print(self)