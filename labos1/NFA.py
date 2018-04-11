from labos1.FA import FA

class NFA(FA):
    '''
    Non-deterministic finite automata.
    '''

    def __init__(self, states, inputs, functions, start_state, final_states, in_type=int):
        super().__init__(states,inputs,functions,start_state,final_states,in_type)

        self.current = {self.current} #NFA holds current states in a set

    def check_fis_output(self, funcs_added):
        #does nothing for NFA.
        pass

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
                raise ValueError(self.__state_error(clean_state, '(ending)'))
            states.append(clean_state)
        return states

    def enter(self, *entry):
        raise NotImplementedError