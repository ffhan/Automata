"""
Defines a Turing machine implementation.
"""
import automata.pda as pda

class TuringMachine(pda.DeterministicPDA):
    """
    A Turing machine implementation.
    It is inherited from DFA because it shares the same interface
    but adds directly on it. DPDA is not suitable for inheritance
    here because we don't need a stack here.
    Could've maybe produced Tape inherited from a Stack?
    """
    def __init__(self, states, inputs, alphabet, start_state, empty_cell_symbol):
        super().__init__(states, inputs, alphabet, start_state)
