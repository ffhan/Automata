"""
Defines miscellaneous tests.
"""
import unittest
import os
import misc.helper as helper
import automata.nfa as nfa
import form.generators as generator

class TestHelper(unittest.TestCase):

    def setUp(self):
        self.test = nfa.EpsilonNFA.factory("""s0,s1
0,1
s1
s0
s0,0->s1
s1,1->s0""", generator.StandardFormatGenerator())

    def test_flatten(self):
        self.assertEqual(helper.flatten_automaton_to_table(self.test).strip(), """ state name   0     1     $     accepted  
------------------------------------------
     s0      [s1]   -     -        0      
     s1       -    [s0]   -        1      """.strip())

    def test_escaping(self):
        self.assertEqual(helper.escape_string('test'), ['\\t\\e\\s\\t'])
        self.assertEqual(helper.de_escape_string('\\t\\e\\st'), ['test'])

    def test_save_load(self):
        original = [1,2,3,4,['test', 'another']]
        helper.save_object(original, 'tester', 'test')
        test = helper.load_object('.\\tester.test')
        os.remove('.\\tester.test')
        self.assertEqual(test, original)
