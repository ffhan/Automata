import unittest
import command_tester as cmd

class TestEpsilonNFA(unittest.TestCase):

    def setUp(self):

        self.executor = cmd.CommandTester('.a', '.b', '..')

    def test_all(self):
        self.executor.execute_test('e_nfa', True)