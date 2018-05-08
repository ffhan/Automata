from automata.nfa import EPSILON_NFA

class PushDownAutomaton(EPSILON_NFA):

    def __init__(self, text, parser):

        super().__init__(text, parser)

        raise NotImplementedError