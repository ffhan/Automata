import unittest
from misc.command_testers import CommandTester

class TestEpsilonNFA(unittest.TestCase):

    def setUp(self):

        self.executor = CommandTester('.a', '.b', '..')

    def test_all(self):
        self.executor.execute_test('e_nfa', True)