"""
Defines all parser tests.
"""
import unittest
from Parser_implementation import parser
import command_tester

class TestParser(unittest.TestCase):

    def setUp(self):
        self.tester = command_tester.CommandTester('.in', '.out', '..\\lab4_primjeri')

    def test_parser(self):
        self.tester.execute_test('parser', True)