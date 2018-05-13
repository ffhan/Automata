"""
Defines Push down automata (currently only Deterministic version).
"""
import automata.dfa as dfa
import automata.state as st
import automata.packs as pk

class DeterministicPDA(dfa.DFA): # the correct implementation would be to inherit from abstract PA.

    """
    Deterministic push down automaton implementation.
    """

    def __init__(self, text, lexer, empty_symbol='$'):

        super().__init__(text, lexer)

        self.start_symbol = lexer.start_stack
        self.stack = pk.Stack(self.start_symbol)

        self.stack_alphabet = lexer.stack_alphabet

        self.inputs.add(empty_symbol)
        self.empty_symbol = empty_symbol

        self.failed_state = st.State('fail', 0, epsilon=empty_symbol)
        self.processed_all = True

    def _check_structure(self):
        # not checking anything. should be checking if every symbol,
        # input and state is registered within pda.
        pass

    @property
    def accepted(self):
        if self.processed_all:
            return self.current in self.accepted_states
        return False

    def reset(self):
        super().reset()
        # self.current = self.start_state
        self.processed_all = True
        self.stack.clear()
        self.stack.push(self.start_symbol)

    def _access(self, value):
        go_on = True
        if self.stack.size == 0:
            self.current = self.failed_state
            # error_print('Stack size 0')
            return True

        symbol = self.stack.pop()

        current = self.current.clean_forward(pk.InputPack(self.empty_symbol, symbol))
        # print(self.current, self.empty_symbol, symbol, current, self.stack)

        if current == set():
            current = self.current.clean_forward(pk.InputPack(value, symbol))
            # print(self.current, value, symbol, current, self.stack)
            if current == set():
                self.current = self.failed_state
                # error_print('Both failed')
                return True
        else:
            go_on = False
        current, stack = current.unpack

        self.stack += stack.exclude(self.empty_symbol)

        self.current = current
        # print('Go on: {}'.form(go_on), self.stack, self.current)
        return go_on

    def _access_epsilon(self):

        """
        Goes through all possible epsilon transitions if
        the stack is not empty and DPDA is still not accepted.

        :return:
        """

        if self.stack.size == 0:
            return False
        symbol = self.stack.pop()

        current = self.current.clean_forward(pk.InputPack(self.empty_symbol, symbol))
        # print(self.current, self.empty_symbol, symbol, current, self.stack)

        if current == set():
            return False

        current, stack = current.unpack

        self.stack += stack.exclude(self.empty_symbol)
        self.current = current
        return True

    def _process(self, *entry):
        record = pk.Records()
        entry = list(entry)

        while entry: # same as len(entry) > 0
            # go through epsilon transitions until the stack is depleted
            # or there aren't any possible moves left.
            record.add_record(pk.PushRecordPack(self.current, self.accepted, self.stack))
            # print(entry)
            if self.current == self.failed_state:
                self.processed_all = False
                break
            value = entry.pop(0)

            if not self._access(value):
                entry.insert(0, value)
        # self.processed_all = True
        if self.processed_all:
            record.add_record(pk.PushRecordPack(self.current, self.accepted, self.stack))

            while (not self.accepted) and self._access_epsilon():
                record.add_record(pk.PushRecordPack(self.current, self.accepted, self.stack))

        self.records.add_record(record)

        # print(self.records)
