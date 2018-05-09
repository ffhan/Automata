import format
import automata
from format.readers import Reader

'''
Preformatting scripts, an endpoint between FA system and outer format connections. 
'''

def get_dfa_min(string):
    # waste, states, inputs, final, start, functions= general_parse('\n' + string)
    # print(waste, states, inputs, final, start, functions)
    # print(states,inputs,final,start,functions,waste)

    parser = format.parsers.StandardFormatParser()

    dfa = automata.dfa.DFA(string, parser)

    dfa.minimize()

    return dfa

def test_dfa_min(string, test_output):
    dfa = get_dfa_min(string)
    return format.compositors.StandardCompositor(dfa).composite_automaton() == test_output.strip()

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

    return encode(get_dfa_min(text))

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

def get_e_nfa(string):
    parser = format.parsers.StandardFormatWithInputParser()
    e_nfa = automata.nfa.EpsilonNFA(string, parser)

    for entries in parser.entries:
        e_nfa.enter(*entries)
        e_nfa.reset()
    return e_nfa

def get_pda(string):
    parser = format.parsers.PushDownFormatWithInputParser()
    pda = automata.pda.DeterministicPA(string, parser)

    for entries in parser.entries:
        pda.enter(*entries)
        pda.reset()
    return pda

def test_pda(string, test_output):
    pda = get_pda(string)
    # print(pda)
    # print(pda.records)
    result = format.compositors.StandardPushDownCompositor(pda).composite_output()

    print(result)
    print(test_output.strip())
    return result == test_output.strip()

def test_e_nfa(string, test_output):
    e_nfa = get_e_nfa(string)
    return format.compositors.StandardCompositor(e_nfa).composite_output() == test_output.strip()

