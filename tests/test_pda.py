import unittest
from misc.command_testers import CommandTester

class TestDeterministicPDA(unittest.TestCase):

    def setUp(self):
        self.executor = CommandTester('.in', '.out', '..\\lab3_primjeri')

    def test_all(self):

        self.executor.execute_test('dpda', True)
