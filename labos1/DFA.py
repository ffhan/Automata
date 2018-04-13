from labos1 import collections
from labos1.FA import FA

class DFA(FA): #todo: see if you can utilize class inheritance so that NFA doesn't have to be rewritten.
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

    def enter(self, *entry): #I hate this function. Redo it.

        def access(value):
            self.current = self.states[list(self.current.forward(self.type(value)))[0]]

        for inp in entry:
            if isinstance(inp, collections.Iterable):
                for i in inp:
                    access(i)
            else:
                access(inp)
        return self.current