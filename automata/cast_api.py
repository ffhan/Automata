import copy
import automata.nfa

def epsilon_nfa_to_nfa(e_nfa: automata.nfa.EpsilonNFA):
    """
    Casts epsilon NFA to NFA.

    :param EpsilonNFA e_nfa: original epsilon NFA
    :return NFA: cast NFA that takes the same languages.
    """

    def item_copy(item):
        """
        Deep copies an item.

        :param item: item to be copied
        :return: deep copied item
        """
        return copy.deepcopy(item)

    work = item_copy(e_nfa)
    closure = set()
    work._e_closure(work.start_state, closure)
    for state in closure:
        if state.value:
            work.start_state.value = 1
            break

    for state in work.states.values():
        for single_input in work.inputs - {work._epsilon}:
            closure = set()
            work._e_closure(state, closure)
            caught_states = set()
            for state_of_closure in closure:
                caught_states |= state_of_closure.forward(single_input)
            state.transitions[single_input] = work.e_closures(*caught_states)
        if work._epsilon in state.transitions:
            state.transitions.pop(work._epsilon)
        transit = item_copy(state.transitions)
        for event, transitions in state.transitions.items():
            if not transitions:
                transit.pop(event)
        state.transitions = transit

    work.inputs.remove(work._epsilon)

    return work # todo: cast this to NFA, it's still in E_NFA. Enable initialization with states, inputs etc. This might be tough.


