"""
Tests all Turing machine implementations.
"""
import unittest
import automata.turing as tr
from misc.command_testers import CommandTester

class TestTuringMachine(unittest.TestCase):
    def setUp(self):
        self.executor = CommandTester('.in', '.out', '..\\lab5_primjeri')

    def test_all(self):

        self.executor.execute_test('turing', True)

