import unittest
import command_tester

class TestDeterministicFA(unittest.TestCase):

    def setUp(self):
        self.executor = command_tester.CommandTester('.ul', '.iz', '..')

    def test_all(self):

        self.executor.execute_test('dfa_min', True)