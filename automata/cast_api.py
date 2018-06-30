"""
API used to cast various automata to other types.
"""
import copy
import automata.nfa, automata.dfa
import automata.state as st
import pprint

def epsilon_nfa_to_nfa(e_nfa: automata.nfa.EpsilonNFA)->automata.nfa.NFA: # todo: add tests
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
                # forward = state_of_closure.forward(single_input)
                # new_forward = set()
                # for one_state in forward:
                #     new_forward.add(work.states[one_state.name])
                caught_states |= state_of_closure.forward(single_input)

            state.transitions[single_input] = work.e_closures(*caught_states)
        if state.epsilon in state.transitions:
            state.transitions.pop(state.epsilon)

        for event in work.inputs:
            if not state.transitions.get(event, True):
                state.transitions.pop(event)

    work.inputs.remove(work.epsilon)

    for state in work.states:
        for event, end_states in work.states[state].transitions.items():
            transitions = set()
            for end_state in end_states:
                transitions.add(work.states[end_state.name])
            work.states[state].transitions[event] = transitions

    # print(work.states)
    print("done to nfa")
    return automata.nfa.NFA(work.states, work.inputs, work.start_state)

def nfa_to_dfa(nfa: automata.nfa.NFA)->automata.dfa.DFA:
    """
        Casts non-deterministic finite automata to deterministic finite automata.

        :param automata.nfa.NFA nfa: NFA to be cast
        :return autmoata.dfa.DFA: cast object
    """

    def concatenate(*args):
        """
        Returns concatenated State names and values

        :param args: States
        :return: new_name, new_value
        """
        name = ''
        acc = 0
        for single_state in sorted(args, key=lambda t : t.name):
            name += repr(single_state) + '_'
            if single_state.value:
                acc = 1
        return name[:-1], acc

    assert type(nfa) is automata.nfa.NFA
    work = nfa.deepcopy() #created so that I don't have to copy existing States manually.

    created_states = dict()

    epsilon = work.start_state.epsilon
    empty_state = st.State('empty', 0, epsilon)

    created_states[work.start_state.name] = work.start_state
    associations = dict() #holds references for new states to old states
    for alias in nfa.states.values():
        state = work.states[alias.name] #this neat trick allows me to change work nfa on the fly
        for single_input in nfa.inputs:
            empty_state.transitions[single_input] = {empty_state}

            throughput = state.forward(single_input)
            if not throughput:
                new_state = empty_state
            elif len(throughput) > 1:
                new_state_name, accepted = concatenate(*throughput)
                new_state = st.State(new_state_name, accepted, epsilon)
            else:
                new_state, = throughput
            if not new_state in associations and len(throughput) > 1:
                associations[new_state] = set(throughput)
            if new_state.name not in created_states:
                created_states[new_state.name] = new_state
            state.transitions[single_input] = {created_states[new_state.name]}
    done_assoc = dict()
    while associations:
        print(associations)
        state = list(associations.keys())[0]
        for single_input in sorted(work.inputs):
            transition = set()
            for _ in sorted(associations[state]):
                link = nfa.states[_.name]
                output = link.forward(single_input)
                transition |= output
            if not transition:
                transition = {empty_state}
                state.transitions[single_input] = transition
                continue
            if transition in associations.values():
                for key, value in sorted(associations.items()):
                    if transition == value:
                        # print('matched {} with hash {} on input {} for state {} with hash {}..'.format(
                        #     key, hash(key), single_input, state, hash(state)))
                        state.transitions[single_input] = {created_states[key.name]}
                        break
            else:
                name, accept = concatenate(*transition)
                new_state = st.State(name, accept, epsilon)
                if new_state in done_assoc:
                    new_state = done_assoc[new_state]
                # print('creating {} with hash {}..'.format(name, hash(new_state)))
                created_states[new_state.name] = new_state
                associations[new_state] = transition
                state.transitions[single_input] = {created_states[new_state.name]}
        if len(state.transitions) == len(work.inputs):
            done_assoc[state] = state
            del(associations[state])
    # for state in created_states.values():
    #     print(state, state.transitions, state.value)
    print("done to dfa")
    return automata.dfa.DFA(created_states, work.inputs, work.start_state)

def epsilon_nfa_to_dfa(automaton: automata.nfa.EpsilonNFA)->automata.dfa.DFA:
    """
    Casts an epsilon NFA to DFA.

    :param EpsilonNFA automaton: automaton to be cast
    :return DFA: cast object
    """

    return nfa_to_dfa(epsilon_nfa_to_nfa(automaton))

def nfa_to_epsilon_nfa(automaton: automata.nfa.NFA)->automata.nfa.EpsilonNFA:
    """
    Casts an NFA to epsilon NFA.

    :param NFA automaton: automaton to be cast
    :return EpsikonNFA: cast object
    """
    work = automaton.deepcopy()
    return automata.nfa.EpsilonNFA(work.states, work.inputs, work.start_state)
