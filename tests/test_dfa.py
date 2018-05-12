import unittest
from misc.command_testers import CommandTester

class TestDeterministicFA(unittest.TestCase):

    def setUp(self):
        self.executor = CommandTester('.ul', '.iz', '..')

    def test_all(self):

        self.executor.execute_test('dfa_min', True)