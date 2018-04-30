from NFA import E_NFA, NFA

def create_function_string(newline = False, **rules):
    '''
    Creates function string from parameters. This enables the programmer to use both string-type functional input or direct programming.

    Example:
        create_function_string(q0={0:'q0', 1:'q1'}, q1={0:'q0', 1:'q1'})
    :param bool newline: defines if FIS is going to have each function defined in its' own row
    :param dict rules: dictionary with keys (str) being inputs and values (str) being state names
    :return: Function instruction string
    '''
    result = ''

    for start, value_and_end in rules.items():
        for value, end in value_and_end.items():
            result += start + ',' + str(value) + '->' + end + ';' + ('\n' if newline else '')
    return result

def sets(func):
    def wrapper(*args):
        return set(func(*args))
    return wrapper


def splitter(string, char):
    return string.split(char)

@sets
def set_splitter(string,char):
    return splitter(string, char)

def comma(*args):
    result = ''
    for arg in args:
        if arg != '':
            result += arg + ';'
    return result[:-1]

def printer(*args):
    for arg in args:
        print(arg)

def parse(string):
    lines = splitter(string, '\n')

    entries = splitter(lines[0], '|')
    states = set_splitter(lines[1], ',')
    inputs = set_splitter(lines[2], ',')
    final = set_splitter(lines[3], ',')
    start = lines[4]
    functions = comma(*lines[5:])

    #printer(entries, states, inputs, final, start, functions)

    nfa = E_NFA(states, inputs, functions, start, final)

    records = []

    for entry in entries:
        records.append(nfa.record(*entry.split(',')).copy())
        nfa.reset()
    # print(entries)
    # print(len(functions.replace(';', ';\n')))
    return records

def output(records):
    result = ''

    for record in records:
        r = list(record)
        for s in r:
            states = sorted(list(s))
            if len(states) == 0:
                result += '#' + '|'
                continue
            for state in states:
                result += state.name + ','
            result = result[:-1]
            result += '|'
        result = result[:-1]
        result += '\n'

    return result

def print_out(records):

    print(output(records))

def compare(records, test_output):

    return output(records) == test_output