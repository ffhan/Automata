"""
Pre-formatting scripts, an endpoint between FA system and outer form connections.
"""
import form.generators
import automata

def get_dfa_min(string):
    """
    Gets a minimized DFA from an input text.

    :param str string: input text
    :return: minimized DFA
    """
    # waste, states, inputs, final, start, functions= general_parse('\n' + string)
    # print(waste, states, inputs, final, start, functions)
    # print(states,inputs,final,start,functions,waste)

    parser = form.generators.StandardFormatGenerator()

    dfa = automata.dfa.DFA.factory(string, parser)

    dfa.minimize()

    return dfa

def get_e_nfa(string):
    """
    Gets an epsilon NFA.

    :param str string: input text
    :return: epsilon NFA
    """
    parser = form.generators.StandardFormatWithInputGenerator()
    e_nfa = automata.nfa.EpsilonNFA.factory(string, parser)

    for entries in parser.entries:
        e_nfa.enter(*entries)
        e_nfa.reset()
    return e_nfa

def get_dpda(string):
    """
    Gets a deterministic PDA.

    :param str string: input text
    :return: deterministic push down automaton
    """
    parser = form.generators.PushDownFormatWithInputGenerator()
    pda = automata.pda.DeterministicPDA.factory(string, parser)

    for entries in parser.entries:
        pda.enter(*entries)
        pda.reset()
    # print(pda.records)
    return pda

def print_verbose(result, test_output, level):
    """
    Controls printing according to verbose level

    Verbose level:
        0: doesn't print anything
        1: prints result and test_output when test has failed
        2: always prints result and test_outputs

    :param str result: output from a program
    :param str test_output: expected output
    :param int level: verbose level
    :return:
    """
    def printer(res, out):
        """
        Prints out program result and expected output

        :param str res: program result
        :param str out: expected result
        :return:
        """
        print(res)
        print(out.strip())
    if level == 1 and result != test_output.strip():
        printer(result, test_output)
    elif level == 2:
        printer(result, test_output)

def test_factory(getter_func, lexer, lexer_method):
    """
    Allows easy test creation.

    :param function getter_func: automaton getter function
    :param Generator lexer: defines which concrete Generator implementation to use
    :param function lexer_method: defines which Generator method to execute
    :return function: test function
    """

    def wrapper(string, test_output, verbose):
        """
        Actual test function to be created.

        :param str string: input
        :param str test_output: expected output
        :param int verbose: verbose level (see print_verbose)
        :return bool: test result
        """
        finite_automaton = getter_func(string)
        result = lexer_method(lexer(finite_automaton))

        print_verbose(result, test_output, verbose)

        return result == test_output.strip()

    return wrapper

def TEST_PARSER(string, test_output, verbose):

    import Parser_implementation

    result = Parser_implementation.parser(string)
    print_verbose(result, test_output, verbose)

    return result == test_output.strip()

TEST_PDA = test_factory(get_dpda, form.compositors.StandardPushDownCompositor,
                        form.compositors.StandardPushDownCompositor.composite_output)
TEST_E_NFA = test_factory(get_e_nfa, form.compositors.StandardCompositor,
                          form.compositors.StandardCompositor.composite_output)
TEST_DFA_MIN = test_factory(get_dfa_min, form.compositors.StandardCompositor,
                            form.compositors.StandardCompositor.composite_automaton)
