import automata.dfa as dfa
import automata.state as st
import automata.packs as pk
import copy

class DeterministicPA(dfa.DFA): #todo: correct implementation would be to inherit from abstract PA.

    def __init__(self, text, parser, empty_symbol = '$'):

        super().__init__(text, parser)

        self.start_symbol = parser.start_stack
        self.stack = pk.Stack(self.start_symbol)

        self.stack_alphabet = parser.stack_alphabet

        self.inputs.add(empty_symbol)
        self.empty_symbol = empty_symbol

        self.failed_symbol = st.PushState('fail', 0)

    def _check_structure(self):
        pass #not checking anything. todo: check parser results.

    def reset(self):
        super().reset()
        # self.current = self.start_state
        self.stack.clear()
        self.stack.push(self.start_symbol)

    def _access(self, value):
        if self.stack.size > 0:
            symbol = self.stack.pop()
        else:
            self.current = self.failed_symbol
            return

        if self.current == self.failed_symbol:
            return

        current = self.current.clean_forward(pk.InputPack(value, symbol))

        #todo: check izlaz.txt for a detailed overview.

        self.current = current
        if not isinstance(current, st.PushState):
            self.current = self.failed_symbol


        self.stack += self.current.stack

    def _process(self, *entry):
        self.records.append([])
        self.records[-1].append(pk.InputPack(self.current, self.stack.container))
        for inp in entry:
            self._access(inp)
            self.records[-1].append(pk.InputPack(self.current, self.stack.container))

