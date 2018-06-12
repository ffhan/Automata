"""
Defines a Turing machine implementation.
"""
import automata.dfa as dfa
import automata.packs as pk
import automata.state as st

class TuringMachine(dfa.DFA):
    """
    A Turing machine implementation.
    It is inherited from DFA because it shares the same interface
    but adds directly on it. DPDA is not suitable for inheritance
    here because we don't need a stack here.
    Could've maybe produced Tape inherited from a Stack?

    This is not a standard Turing machine because it also
    allows for explicitly rejected states (the machine is halted
    if it encounters an accepted or rejected state.
    All other states are inconclusive and do not stop the machine.

    The machine also stops if there are no other possible transitions.
    """
    def __init__(self, states, inputs, alphabet, start_state, empty_cell_symbol, head_index = 0):
        # don't move this after super().__init__ because it's used in structure check
        self.alphabet = alphabet
        self.empty_cell_symbol = empty_cell_symbol
        super().__init__(states, inputs, start_state)

        self._head_index = head_index
        self.tape = pk.Tape()
        self.tape._index = head_index

    def __repr__(self):
        def wrap_in_braces(string, last_brace_newline=False):
            """
            Wraps up a string in {}.

            :param str string: string to be wrapped
            :param bool last_brace_newline: defines if newline will be put after braces
            :return str: wrapped string
            """
            return '{' + string + ('\n}' if last_brace_newline else '}')

        def tab(string):
            """
            Puts tabs in front of all lines in a string.

            Example:
            -------------
            For example,
            this becomes:
            -------------
                For example,
                this becomes:
            -------------

            :param str string: input string
            :return str: tabbed strings
            """
            return '\t' + string.replace('\n', '\n\t')

        def newline(*lines):
            """
            Returns string composed of all line arguments with newline added between them.

            :param str lines: lines of text that need to be newlined.
            :return: full string composed of individual lines concatenated with newline in-between
            """
            res = '\n'
            for line in lines:
                res += line + '\n'
            return res[:-1]

        states = ''
        final = ''

        for state, state_object in sorted(self.states.items(), key=lambda t: t[0]):
            states += str(state) + ','
            if state_object.value:
                # print(final, state)
                final += str(state.name) + ','

        final = 'F=' + wrap_in_braces(final[:-1])

        states = 'Q=' + wrap_in_braces(states[:-1])

        inputs = ''

        for inp in sorted(self.inputs):
            inputs += str(inp) + ','

        alphabet = ''

        for sym in sorted(self.alphabet):
            alphabet += str(sym) + ','

        inputs = u'\u03A3=' + wrap_in_braces(inputs[:-1])
        alphabet = u'\u03B3=' + wrap_in_braces(alphabet[:-1])

        funcs = u'\u03B4=' + wrap_in_braces(self.functions)

        try:
            assert isinstance(self.start_state, st.State)
        except AssertionError as error:
            print("Start state is not a state, it's {}".format(type(self.start_state)), error)
            raise error
        start = 'q0=' + str(self.start_state.name)
        try:
            assert isinstance(self.start_state, st.State)
        except AssertionError as error:
            print("Start state is not a state, it's {}".format(type(self.start_state)), error)
            raise error
        return '{} '.format(type(self).__name__) + wrap_in_braces(tab(
            newline(states, inputs, alphabet, funcs, start, final)
        ), True)

    def _check_structure(self):
        err = ValueError('Set of all inputs should be a proper subset of an alphabet')
        err2 = ValueError('Empty cell symbol should NOT be in inputs')
        for item in self.inputs:
            if item not in self.alphabet:
                raise ValueError('Item {} is not in alphabet {} and it should be.'.format(
                    item, self.alphabet
                ))
        if len(self.inputs) >= len(self.alphabet):
            raise err
        if self.empty_cell_symbol not in self.alphabet:
            raise err2
        return True

    @property
    def functions(self) -> str:
        """
        Returns functions for repr() function.

        :return str: string representation of transition functions
        """

        result = ''

        for state in sorted(self.states.values()):
            for event, pack in state.transitions.items():
                # extremely bad code, but it's a part of an interface
                result += '{},{}->'.format(self._get_alias(state.name), event)
                end, symbol, movement = list(pack)[0].unpack
                movement = 'L' if pk.TuringOutputPack.LEFT else 'R'
                result += '{},{},{}'.format(self._get_alias(end.name), symbol, movement)
                result = result + '\n'
        return result.strip()

    def reset(self):
        super().reset()
        self.tape.clear()
        self._head_index = self._head_index

    @property
    def rejected_states(self):
        """
        Returns all rejected states.
        A state is explicitly rejected (in this context)
        if it contains value -1.

        A state that is not accepted is NOT explicitly
        rejected.

        :return set: a set of all rejected states.
        """

        final = set()

        for state in self.states.values():

            if state.value == -1:
                final.add(state)

        return final

    @property
    def accepted(self):
        return self.current.value > 0

    def enter(self, *entry):
        self.tape.add(*entry)
        return super().enter(*entry)

    def _access(self, value):
        raise NotImplementedError('Access method is not needed in a Turing machine.')

    def _process(self, *entry):
        """
        Processes the entry arguments.

        :param entry: entries that have to be handled.
        :return:
        """
        records = pk.Records()
        records.add_record(pk.RecordPack(self.current, bool(self.accepted)))

        while True:
            read = self.tape.read
            print('-'*35)
            if not read:
                read = self.empty_cell_symbol
            output = self.current.clean_forward(read)
            print(self.current, read, output)
            if output == set():
                break
            new_state, symbol, movement = output.unpack
            _ = self.tape.consume
            print(self.current, read, output, symbol, self.tape._index)
            # if new_state in self.accepted_states | self.rejected_states:
            #     break
            if movement == pk.TuringOutputPack.LEFT:
                movement = self.tape.move_left
            elif movement == pk.TuringOutputPack.RIGHT:
                movement = self.tape.move_right
            else:
                raise ValueError('Invalid movement value!')
            movement(symbol)
            self.current = self.states[self._get_alias(new_state.name)]

            if self.current in self.accepted_states | self.rejected_states:
                break
            records.add_record(pk.RecordPack(self.current, bool(self.accepted)))
        self.records.add_record(records)

    @staticmethod
    def factory(input_text, lexer):
        lexer.scan(input_text)
        return __class__(lexer.states, lexer.inputs, lexer.alphabet, lexer.start_state, lexer.empty_cell_symbol, lexer.head_index)
