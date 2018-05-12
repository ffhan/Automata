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

def get_e_nfa(string):
    parser = format.parsers.StandardFormatWithInputParser()
    e_nfa = automata.nfa.EpsilonNFA(string, parser)

    for entries in parser.entries:
        e_nfa.enter(*entries)
        e_nfa.reset()
    return e_nfa

def get_pda(string):
    parser = format.parsers.PushDownFormatWithInputParser()
    pda = automata.pda.DeterministicPDA(string, parser)

    for entries in parser.entries:
        pda.enter(*entries)
        pda.reset()
    # print(pda.records)
    return pda

def print_verbose(result, test_output, level):
    def printer(res, out):
        print(res)
        print(out.strip())
    if level == 1 and result != test_output.strip():
        printer(result, test_output)
    elif level == 2:
        printer(result, test_output)

def test_factory(getter_func, compositor, compositor_method):

    def wrapper(string, test_output, verbose):
        fa = getter_func(string)
        result = compositor_method(compositor(fa))

        print_verbose(result, test_output, verbose)

        return result == test_output.strip()

    return wrapper

test_pda = test_factory(get_pda, format.compositors.StandardPushDownCompositor, format.compositors.StandardPushDownCompositor.composite_output)
test_e_nfa = test_factory(get_e_nfa, format.compositors.StandardCompositor, format.compositors.StandardCompositor.composite_output)
test_dfa_min = test_factory(get_dfa_min, format.compositors.StandardCompositor, format.compositors.StandardCompositor.composite_automaton)