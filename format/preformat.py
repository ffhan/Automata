from automata.nfa import EPSILON_NFA
from automata.dfa import DFA
from format.parsers import StandardFormatWithInputParser, StandardFormatParser

'''
Preformatting scripts, an endpoint between FA system and outer format connections. 
'''

def parse_e_nfa(string):
    parser = StandardFormatWithInputParser()
    nfa = EPSILON_NFA(string, parser)

    records = []

    for entry in parser.entries:
        records.append(nfa.record(*entry).copy())
        nfa.reset()
    # print(entries)
    # print(len(functions.replace(';', ';\n')))
    return records

def parse_dfa(string):
    # waste, states, inputs, final, start, functions= general_parse('\n' + string)
    # print(waste, states, inputs, final, start, functions)
    # print(states,inputs,final,start,functions,waste)

    parser = StandardFormatParser()

    dfa = DFA(string, parser)

    dfa.minimize()

    return dfa

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
    final = list(sorted(automat.accepted_states))
    start_state = automat.start_state
    functions = automat.functions
    # print(states,inputs,final,start_state,functions)

    result = ''

    result += coma_it(states)
    result += coma_it(inputs)
    result += coma_it(final)
    result += str(start_state)
    result += '\n' + functions

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