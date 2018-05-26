"""
Defines all helper functions that don't have a specific package.
"""
import copy

def get_all_subsets(items: set)->list:
    """
    Returns all possible subsets (including an empty subset).

    :param set items: set of all items
    :return set: set of all possible subsets
    """

    def recurse(current_set: set, leftovers: list):
        """
        fills result with all subsets for a given set and all items not yet passed.

        :param set current_set: set of items
        :param list leftovers: all elements not yet included
        :return:
        """
        print(current_set, leftovers)
        result.append(list(current_set))
        while leftovers:
            current = current_set.copy()
            current.add(leftovers.pop(0))
            recurse(current, leftovers.copy())

    work = list(items) # eases iterating through items uniformly.
    result = list() # add all subsets in this set

    recurse(set(), work)

    return sorted(result, key = lambda t : len(t))

def flatten_automaton_to_table(automaton)->str:
    """
    Returns a string that contains a table describing an automaton.

    :param FA automaton: automaton that has to be described
    :return str: table representation
    """

    name_length = 12
    input_length = 2

    for state in automaton.states:
        input_length += len(repr(state))
        if len(repr(state)) > name_length:
            name_length = len(repr(state))
    # quick, naive width settings. I could do this really accurately in two passes
    # but I don't really care.

    accepted_length = 12

    epsilon_included = False
    epsilon = list(automaton.states.values())[0].epsilon
    if epsilon in automaton.inputs:
        epsilon_included = True
    inputs = sorted(automaton.inputs - {epsilon})
    if epsilon_included:
        inputs.append(epsilon)

    result = ''
    result += '{:^{length}s}'.format('state name', length=name_length)
    for j, single_input in enumerate(inputs):
        result += '{:^{length}s}'.format(single_input, length=input_length)
    result += '{:^{length}s}'.format('accepted', length=accepted_length)
    result += '\n'
    result += '-' * (name_length + input_length * len(inputs) + accepted_length) + '\n'
    for i, name in enumerate(sorted(automaton.states)):

        result += '{:^{length}s}'.format(repr(name), length=name_length)
        for j, single_input in enumerate(inputs):
            output = sorted(automaton.states[name].forward(single_input))
            if not output:
                output = '-'
            result += '{:^{length}s}'.format(str(output), length=input_length)

        result += '{:^{length}d}'.format(automaton.states[name].value, length=accepted_length)
        result += '\n'

    return result
