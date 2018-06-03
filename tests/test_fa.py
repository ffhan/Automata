"""
Defines tests for generic finite automata.
"""
import unittest
import automata.fa as fa
import automata.nfa as nfa
import automata.state as state
import form.generators as generator

class TestFA(unittest.TestCase):
    def setUp(self):
        self.st1 = state.State('test0', 0)
        self.st2 = state.State('test1', 1)
        self.st1.add_function(self.st2, '1')
        self.st2.add_function(self.st1, '0')
        self.test = nfa.NFA.factory("""s0,s1,s2
0,1
s1,s2
s0
s0,0->s1
s1,1->s2
s2,0->s1""", generator.StandardFormatGenerator())

    def test_init(self):
        with self.assertRaises(TypeError):
            finite = fa.FiniteAutomaton({self.st1.name:self.st1, self.st2.name:self.st2},
                                        {'0', '1'}, self.st1)
        with self.assertRaises(TypeError):
            finite = fa.FiniteAutomaton({self.st1.name:self.st1, self.st2.name:self.st2},
                                        {'0', '1'}, self.st1)

        with self.assertRaises(TypeError):
            finite = fa.FiniteAutomaton.factory("""s0,s1
0,1
s1
s0
s0,0->s1
s1,1->s1""", generator.StandardFormatGenerator())

        with self.assertRaises(TypeError):
            finite = nfa.EpsilonNFA({0:0,self.st2.name:self.st2}, {0,1}, self.st1)
        with self.assertRaises(AttributeError):
            finite = nfa.EpsilonNFA({self.st1.name:self.st1,self.st2.name:self.st2},
                                    {0,1}, 4)
        with self.assertRaises(TypeError):
            finite = nfa.EpsilonNFA({self.st1:self.st1,self.st2.name:self.st2},
                                    {0,1}, self.st1)
        with self.assertRaises(TypeError):
            finite = nfa.EpsilonNFA({self.st1.name:self.st1.name,self.st2.name:self.st2},
                                    {0,1}, self.st1)

    def test_output(self):
        self.assertTrue(self.test.output('0'))
        self.assertTrue(self.test.output('1'))
        self.assertTrue(self.test.output('0'))
        self.assertTrue(self.test.output('1'))
        self.assertFalse(self.test.output('1'))

    def test_rename(self):
        nf = nfa.EpsilonNFA({self.st1.name:self.st1, self.st2.name:self.st2},
                            {'0', '1'}, self.st1)
        st1rename = state.State('renamed', self.st1.value)
        nf.rename_state(self.st1.name, 'renamed')
        self.assertEqual(nf.states, {state.StateName('renamed'):st1rename, self.st2.name:self.st2})
        self.assertEqual(nf.start_state, st1rename)
        self.assertEqual(list(nf.current)[0], st1rename)
    def test_deepcopy(self):
        test2 = self.test.deepcopy()
        self.assertEqual(test2.states, self.test.states)
        self.assertEqual(test2.inputs, self.test.inputs)
        self.assertEqual(test2.start_state, self.test.start_state)
        self.assertEqual(test2.current, self.test.current)

        #test renaming.
        for name in list(test2.states):
            state = test2.states[name]
            del(test2.states[name])
            state.name.name = 'renamed' + name.name
            test2.states[state.name] = state
        for name, state in test2.states.items():
            self.assertTrue(name.name.startswith('renamed'))
            self.assertTrue(state.name.name.startswith('renamed'))
        self.assertTrue(test2.start_state.name.name.startswith('renamed'))
        self.assertTrue(list(test2.current)[0].name.name.startswith('renamed'))
        for name, state in self.test.states.items():
            self.assertFalse(name.name.startswith('renamed'))
            self.assertFalse(state.name.name.startswith('renamed'))

    def test_repr(self):
        self.assertEqual(repr(self.test), """NFA {	
	Q={s0,s1,s2}
	Σ={0,1}
	δ={s0,0->s1
	s1,1->s2
	s2,0->s1}
	q0=s0
	F={s1,s2}
}""")
    def test_contains(self):
        self.assertTrue(state.StateName('s0') in self.test)
        self.assertTrue(state.State('s0', 0) in self.test)
        self.assertFalse(state.State('st0', 0) in self.test)
        self.assertFalse(4 in self.test)
