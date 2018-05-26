"""
API used to cast various automata to other types.
"""
import copy
import automata.nfa, automata.dfa
import automata.state as st

def epsilon_nfa_to_nfa(e_nfa: automata.nfa.EpsilonNFA)->automata.nfa.NFA: # todo: fix this cast, add tests
    """
    Casts epsilon NFA to NFA.

    :param EpsilonNFA e_nfa: original epsilon NFA
    :return NFA: cast NFA that takes the same languages.
    """

    assert type(e_nfa) is automata.nfa.EpsilonNFA
    work = e_nfa.deepcopy()
    closure = work.start_state.epsilon_closure # NOT the same as state.indirect_reach

    #setting start state as accepting if its' epsilon closure contains an accepting state
    for state in closure:
        if state.value:
            work.start_state.value = 1
            break

    structure = work.deepcopy()
    #hold a structure, but use references from work.

    for state in work.states.values():
        for single_input in work.inputs - {state.epsilon}:
            closure = structure.states[state.name].epsilon_closure
            caught_states = set()
            for state_of_closure in closure:
                # if state_of_closure != state:
                #     caught_states.add(state_of_closure)
                caught_states |= state_of_closure.forward(single_input)

            state.transitions[single_input] = work.e_closures(*caught_states)
        if state.epsilon in state.transitions:
            state.transitions.pop(state.epsilon)
        transit = copy.copy(state.transitions)
        for event, transitions in state.transitions.items():
            if not transitions:
                transit.pop(event)
        state.transitions = transit

    work.inputs.remove(work.epsilon)

    return automata.nfa.NFA(work.states, work.inputs, work.start_state)

def nfa_to_dfa(nfa: automata.nfa.NFA)->automata.dfa.DFA:
    """
    Casts non-deterministic finite automata to deterministic finite automata.

    :param automata.nfa.NFA nfa: NFA to be cast
    :return autmoata.dfa.DFA: cast object
    """

    print(nfa)

    assert type(nfa) is automata.nfa.NFA
    work = nfa.deepcopy()

    created_states = dict()
    delete_states = set()

    for single_input in work.inputs:
        for start_state in work.states.values():
            accepted = False
            concatenated_states_name = ''
            end_states = sorted(list(start_state.forward(single_input)))

            new = False

            for end_state in end_states:
                if end_state.value:
                    accepted = True
                concatenated_states_name += str(end_state) + '+'
            concatenated_states_name = concatenated_states_name[:-1]

            if len(end_states) > 1:
                new = True
                new_state = st.State(concatenated_states_name, int(accepted), start_state.epsilon)
                delete_states |= set(end_states)

                if not created_states.get(new_state.name, False):
                    created_states[new_state.name] = new_state
                else:
                    new_state = created_states[new_state.name]
            elif len(end_states) == 1:
                new_state = list(end_states)[0]
            elif not end_states:
                new = True
                new_state = st.State('empty', 0, start_state.epsilon)

                if not created_states.get(new_state.name, False):
                    created_states[new_state.name] = new_state
                else:
                    new_state = created_states[new_state.name]

            if new:
                for one_input in work.inputs:
                    new_state.add_function(new_state, one_input)

            start_state.transitions[single_input] = {new_state}

    for state in delete_states:
        del(work.states[state.name])

    for name, state in created_states.items():
        work.states[name] = state
    print(work.states)
    return automata.dfa.DFA(work.states, work.inputs, work.start_state)

def epsilon_nfa_to_dfa(automaton: automata.nfa.EpsilonNFA)->automata.dfa.DFA:
    """
    Casts an epsilon NFA to DFA.

    :param EpsilonNFA automaton: automaton to be cast
    :return DFA: cast object
    """

    return nfa_to_dfa(epsilon_nfa_to_nfa(automaton))

#todo: both casts do not work properly.