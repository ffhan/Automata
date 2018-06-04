"""
Defines all helper functions that don't have a specific package.
"""
import pickle

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

def escape_string(*items)->list:
    """
    Escapes a string for a generator:
    every character is individually escaped.

    This avoids formatting problems.

    :param items: strings that have to be escaped
    :return list: list of completely escaped strings
    """
    new_items = []
    for item in items:
        new_string = ''
        for char in item:
            new_string += '\\' + char
        new_items.append(new_string)
    # print(new_items)
    return new_items

def de_escape_string(*items)->list:
    """
    Removes escape symbols from strings.

    Be careful to use os.path.dirname(__file__) if you are not sure about relative path.
    For example, running a misc.helper script from tests will mean that regexes are going to
    try to load from tests\\compiled_regexes directory if using .\\compiled_regexes instead of
    C:\\...\\grammar\\compiled_regexes.

    The same goes for saving an object.

    :param items: strings that have to be de-escaped
    :return list: list of unescaped strings
    """
    new_items = []
    for item in items:
        item_list = list(item)
        new_string = ''
        while item_list:
            char = item_list.pop(0)
            if char == '\\':
                new_string += item_list.pop(0)
            else:
                new_string += char
        new_items.append(new_string)
    return new_items

def save_object(obj, file_name: str, file_suffix: str = 'compiled', file_path: str = '.'):
    """
    Pickles an object and dumps it into a binary file.
    This enables that certain objects don't have to be re-initialized.

    Be careful to use os.path.dirname(__file__) if you are not sure about relative path.
    For example, running a misc.helper script from tests will mean that regexes are going to
    try to load from tests\\compiled_regexes directory if using .\\compiled_regexes instead of
    C:\\...\\grammar\\compiled_regexes.

    The same goes for loading an object.

    :param obj: any pickle-able object
    :param str file_name: name of the file
    :param str file_suffix: file format (for example comp in name_of_file.comp)
    :param str file_path: path to the resulting file
    :return:
    """
    if not file_name.endswith('\\'):
        file_path += '\\'
    with open(file_path + file_name + '.' + file_suffix, 'wb') as file:
        pickle.dump(obj, file, -1)

def load_object(file_path: str):
    with open(file_path, 'rb') as file:
        obj = pickle.load(file)
    return obj