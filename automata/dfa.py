"""
Defines Deterministic finite automata.
"""
import automata.fa as fa

class DFA(fa.FiniteAutomaton):
    '''
    Deterministic finite automata.
    '''

    def __init__(self, text, lexer):

        super().__init__(text, lexer)

        self.current = list(self.current)[0]

    @property
    def accepted(self) -> bool:
        """
        Defines if current automaton state is defined

        :return bool: True if accepted, False if not
        """
        return self.current in self.accepted_states

    def _check_structure(self):

        error_msg = 'Incorrect {} structure.'.format(self.__class__.__name__)

        for state in self.states.values():
            if len(state.transitions) != len(self.inputs):
                raise ValueError(error_msg)
            for end in state.transitions.values():
                if len(end) != 1:
                    raise ValueError(error_msg)

    def reset(self):

        """
        Resets the current state.
        Doesn't delete the records.

        :return:
        """

        super().reset()
        self.current = self.start_state

    def _access(self, value):

        self.current = self.states[self._get_alias(self.current.clean_forward(value).name)]

    def distinguish(self):

        def is_in(value_1, value_2, tab):
            """
            Determines if tuple of values is in a collection.

            :param value_1: any value
            :param value_2: any value
            :param tab: any collection
            :return bool: does (value_1, value_2) or (value_2, value_1) exist in tab?
            """
            return (value_1, value_2) in tab or (value_2, value_1) in tab


        states = list(self.states.values())

        table = set()

        for i in enumerate(states):
            i = i[0]
            for j in range(i + 1, len(states)):
                if states[i].value == states[j].value:
                    table.add((states[i], states[j]))

        added = 1

        while added != 0:
            added = 0
            temp = table.copy()
            for inp in self.inputs:

                for state_1, state_2 in temp:

                    result_1, result_2 = state_1.clean_forward(inp), state_2.clean_forward(inp)
                    if result_1 != result_2 and not is_in(result_1, result_2, table):
                        table -= {(state_1, state_2)} | {(state_2, state_1)}
                        added += 1

        for state_1, state_2 in table:
            if state_1.name > state_2.name:
                temporary = state_1
                state_1 = state_2
                state_2 = temporary
            self._set_alias(state_1.name, state_2.name)

        for old_state in self._alias:
            self.states.pop(old_state)

        return table

    def minimize(self):

        self.reachable()
        # print(self)
        self.distinguish()
        # print(self)
        self.start_state = self.states[self._get_alias(self.start_state.name)]
