from NFA import E_NFA, NFA
from DFA import DFA

'''
Preformatting scripts, an endpoint between FA system and outer format connections. 
'''

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

def parse_e_nfa(string):

    entries, states, inputs, final, start, functions = general_parse(string)
    #printer(entries, states, inputs, final, start, functions)

    nfa = E_NFA(states, inputs, functions, start, final)

    records = []

    for entry in entries:
        records.append(nfa.record(*entry.split(',')).copy())
        nfa.reset()
    # print(entries)
    # print(len(functions.replace(';', ';\n')))
    return records

def parse_dfa(string):
    waste, states, inputs, final, start, functions= general_parse('\n' + string)
    # print(waste, states, inputs, final, start, functions)
    # print(states,inputs,final,start,functions,waste)
    dfa = DFA(states,inputs,functions,start,final)

    dfa.minimize()

    return dfa

def general_parse(string):
    lines = splitter(string, '\n')

    entries = splitter(lines[0], '|')
    states = set_splitter(lines[1], ',')
    inputs = set_splitter(lines[2], ',')
    final = set_splitter(lines[3], ',')
    start = lines[4]
    functions = comma(*lines[5:])

    return entries, states, inputs, final, start, functions

def encode(automat):
    def general_it(iterable, symbol = ','):
        res = ''
        for iter in iterable:
            res += '{}{}'.format(iter, symbol)
        return res[:-1] + '\n'
    def coma_it(iterable):
        return general_it(iterable)

    '''
    Format za zapis definicije ulaznog i izlaznog automata jest sljedeći:
    1. redak: Skup stanja odvojenih zarezom, leksikografski poredana.
    2. redak: Skup simbola abecede odvojenih zarezom, leksikografski poredana.
    3. redak: Skup prihvatljivih stanja odvojenih zarezom, leksikografski poredana.
    4. redak: Početno stanje.
    5. redak i svi ostali retci: Funkcija prijelaza u formatu
    :param FA automatum: FA that has to be encoded
    :return str: String output
    '''

    states = list(sorted(automat.states.values()))
    inputs = list(sorted(automat.inputs))
    final = []
    for state in states:
        if state.value:
            final.append(state)
    start_state = automat.start_state
    functions = automat.functions

    result = ''

    result += coma_it(states)
    result += coma_it(inputs)
    result += coma_it(final)
    result += str(start_state)
    result += general_it(sorted(functions.split(';')), '\n')[:-1]

    return result.strip().strip('\n').strip()

def encode_minimized_dfa(text):

    return encode(parse_dfa(text))

def fa_output(records):
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

def print_output(records):

    print(fa_output(records))

def compare_output(records, test_output):

    return fa_output(records) == test_output

def compare_encoding(fa, test_output):
    # print(encode(fa))
    return encode(fa).strip() == test_output.strip().strip('\n').strip()

def print_encoding(fa):
    print(encode(fa))



# USE TO CHECK MINIMIZATION TABLE
# def print_minimize_table(start_index, end_index, table):
#
#     def tuple_equal(v1, v2):
#         v1 = 'p' + str(v1)
#         v2 = 'p' + str(v2)
#
#         for t1, t2 in table:
#             if (v1 == t1.name and v2 == t2.name) or (v1 == t2.name and v2 == t1.name):
#                 return False
#         return True
#
#     lines = ['p{}'.format(index + 1) + ' |' + ' . |' * index for index in range(start_index, end_index)]
#
#     lines = ''
#
#     for index in range(start_index + 1, end_index + 1):
#         line = ' |'
#         for i in range(0, index - 1):
#             line += ' {} |'.format(' ' if not tuple_equal(index, i + 1) else 'x')
#         lines+= 'p{}'.format(index) + line + '\n'
#     lines += '   '
#     for i in range(start_index, end_index):
#         lines += '  p{}'.format(i)
#
#     return lines

# print(print_minimize_table(1, 8, df.distinguish()))