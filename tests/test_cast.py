"""
Defines cast API tests.
"""
import unittest
from random import randint
import automata.nfa as nfa
import form.generators
import automata.cast_api as api
import grammar.operators as op
import misc.helper as hel
import grammar.regular_expressions as rgx

def casting_tester(original, cast, test_func, output_results = False):
    """
    Tests if original FA contains the same language as the casted object.
    Exits with code 1 if it fails and prints where it failed.

    :param FA original: original FA
    :param FA cast: cast FA
    :param test_func: unit test method to _assemble
    :param bool output_results: defines if tester prints out all results
    :return:
    """
    def custom_print(*args):
        """
        Prints based on outside parameters.

        :param args: items to print
        :return:
        """
        if output_results:
            print(*args)
    states = list(cast.states.values())
    for index, state in enumerate(list(original.states.values())):
        original.rename_state(state.name, str(index))
    for index, state in enumerate(states):
        cast.rename_state(state.name, str(index))
    custom_print(original)
    custom_print(cast)
    for i in range(600):
        inp = ''
        for j in range(10 * (i // 100 + 1)):
            single_input = str(randint(0,1))
            inp += single_input
            original.enter(single_input)
            cast.enter(single_input)
            test_func(cast.accepted, original.accepted)
            # try:
            #     assert cast.accepted == original.accepted
            # except AssertionError:
            #     custom_print(inp, original.current, cast.current)
            #     exit(1)
        # assert original.accepted == cast.accepted
        test_func(original.accepted, cast.accepted)
        custom_print("PASSED", inp, original.accepted, cast.accepted)
        original.reset()
        cast.reset()

class TestCastAPI(unittest.TestCase):
    """
    Tests all cast API functions with renaming included.
    This guarantees that there are no loose references.
    """
    def setUp(self):
        self.E_NFA = nfa.EpsilonNFA.factory(
            """s0,s1
0,1
s1
s0
s0,0->s1""", form.generators.StandardFormatGenerator()
        )
        self.E_NFA2 = nfa.EpsilonNFA.factory(
            """s2,s3
0,1
s3
s2
s2,1->s3
s3,0->s3
s3,1->s3""", form.generators.StandardFormatGenerator()
        )

        self.NFA3 = nfa.NFA.factory(
            """q0,q1
0,1
q1
q0
q0,0->q0,q1
q0,1->q1
q1,1->q0,q1""", form.generators.StandardFormatGenerator()
        )
        self.original = self.E_NFA + self.E_NFA2 * api.nfa_to_epsilon_nfa(self.NFA3)
        self.cast = api.epsilon_nfa_to_dfa(self.original)
    def test_fa_casts(self):
        casting_tester(self.original, self.cast, self.assertEqual)
    def test_regexes(self):
        for regex in rgx.REGEXES.values():
            if regex.name == 'VARIABLE':
                self.assertFalse(regex.check(''))
                self.assertFalse(regex.check('12'))
                self.assertFalse(regex.check('12fgt'))
                self.assertTrue(regex.check('_12'))
                self.assertTrue(regex.check('_12fht'))
                self.assertTrue(regex.check('hnefns_'))
                self.assertTrue(regex.check('_hnefns_'))
                self.assertTrue(regex.check('_hne_fns_'))
                self.assertTrue(regex.check('_hn34ef55ns_'))
                self.assertFalse(regex.check('_hn34ef 55ns_'))
            elif regex.name == 'INTEGER':
                self.assertFalse(regex.check(''))
                self.assertFalse(regex.check('.12'))
                self.assertFalse(regex.check('95.12'))
                self.assertFalse(regex.check('95 .12'))
                self.assertFalse(regex.check('95 12'))
                self.assertTrue(regex.check('9512'))
                self.assertTrue(regex.check('1'))
            elif regex.name == 'FLOAT':
                self.assertFalse(regex.check(''))
                self.assertFalse(regex.check('.'))
                self.assertFalse(regex.check('12'))
                self.assertFalse(regex.check('12454 .'))
                self.assertFalse(regex.check('. 12454'))
                self.assertTrue(regex.check('.12454'))
                self.assertTrue(regex.check('12454.'))
                self.assertTrue(regex.check('98.765'))
                self.assertFalse(regex.check('98.765.456'))
                self.assertFalse(regex.check('98.765.'))
                self.assertFalse(regex.check('.98.765'))
            elif regex.name == 'NUMBER':
                self.assertFalse(regex.check(''))
                self.assertFalse(regex.check('.'))
                self.assertTrue(regex.check('123'))
                self.assertTrue(regex.check('123.456'))
                self.assertTrue(regex.check('123.'))
                self.assertTrue(regex.check('.456'))
            else:
                self.assertFalse(regex.check(''))
                self.assertTrue(regex.check(*hel.de_escape_string(regex._text.lower())))
                self.assertFalse(regex.check(*hel.de_escape_string(regex._text.lower() * 2)))
