import unittest
from misc.command_testers import CommandTester
from automata.nfa import EpsilonNFA
from form.generators import StandardFormatGenerator
from automata.cast_api import epsilon_nfa_to_nfa

class TestEpsilonNFA(unittest.TestCase):

    def setUp(self):
        self.executor = CommandTester('.a', '.b', '..')
        self.test = EpsilonNFA.factory("""s0,s1,s2
0,1
s1,s2
s0
s0,0->s1
s1,1->s2
s2,0->s1""", StandardFormatGenerator())
        self.test2 = EpsilonNFA.factory("""s0,s1
1
s1
s0
s0,1->s1
s1,1->s1""", StandardFormatGenerator())

    def test_all(self):
        self.executor.execute_test('e_nfa', True)

    def test_add(self):
        added = self.test + self.test2
        self.assertEqual(added.inputs, {'0', '1', '$'})
        self.assertFalse(added.accepted)
        self.assertTrue(added.output('1'))
        self.assertTrue(added.output('1'))
        self.assertTrue(added.output('1'))
        self.assertTrue(added.output('1'))
        added.reset()
        self.assertTrue(added.output('0'))
        self.assertTrue(added.output('1'))
        self.assertTrue(added.output('0'))
        self.assertTrue(added.output('1'))
        self.assertFalse(added.output('1'))
        self.assertFalse(added.output('1'))
        added.reset()
        self.assertTrue(added.output('0'))
        self.assertFalse(added.output('0'))

    def test_mul(self):
        added = self.test * self.test2
        self.assertEqual(added.inputs, {'0', '1', '$'})
        self.assertFalse(added.accepted)
        self.assertFalse(added.output('0'))
        self.assertTrue(added.output('1'))
        self.assertFalse(added.output('0'))
        self.assertTrue(added.output('1'))
        self.assertTrue(added.output('1'))
        self.assertTrue(added.output('1'))
        self.assertTrue(added.output('1'))
        self.assertTrue(added.output('1'))
        added.reset()
        self.assertFalse(added.output('1'))
        self.assertFalse(added.output('1'))

    def test_kleene(self):
        kleene = EpsilonNFA.factory("""s0,s1
0
s1
s0
s0,0->s1""", StandardFormatGenerator()).kleene_operator()
        self.assertTrue(kleene.accepted)
        self.assertTrue(kleene.enter('0'))
        self.assertTrue(kleene.enter('0'))
        self.assertTrue(kleene.enter('0'))

    def test_cast_to_nfa(self):
        cast = epsilon_nfa_to_nfa(self.test)
        self.assertEqual(cast.accepted, self.test.accepted)
        self.assertEqual(cast.enter('0'), self.test.enter('0'))
        self.assertEqual(cast.enter('1'), self.test.enter('1'))
        self.assertEqual(cast.enter('0'), self.test.enter('0'))
        self.assertEqual(cast.enter('0'), self.test.enter('0'))
