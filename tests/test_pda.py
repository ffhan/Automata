import unittest
import command_tester as cmd

class TestDeterministicPDA(unittest.TestCase):

    def setUp(self):
        self.executor = cmd.CommandTester('.in', '.out', '..')

    def test_all(self):

        self.executor.execute_test('dpda', True)
