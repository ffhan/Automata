import unittest
from automata.state import *

class TestStateName(unittest.TestCase):

    def setUp(self):

        self.test = StateName('testing')

    def test_add(self):

        self.assertEqual(self.test + 'second', 'testingsecond')

        self.test += 'third'
        self.assertEqual(self.test.name, 'testingthird')

    def test_lt(self):

        test2 = StateName('abcd')
        test3 = StateName('xyz')
        self.assertTrue(self.test > test2)
        self.assertTrue(self.test < test3)
        self.assertTrue(self.test < 'xylophone')

    def test_rename(self):

        with self.assertRaises(TypeError):
            self.test.name = StateName('testing')

        self.test.name = 'tester'
        self.assertEqual(self.test.name, 'tester')

    def test_equality(self):

        test = StateName('test')
        test2 = StateName('testing')

        self.assertFalse(self.test == test)
        self.assertTrue(self.test == test2)

        self.assertTrue(self.test == 'testing')
        self.assertFalse(self.test == 'test')

        self.assertFalse(self.test == ['testing'])

    def test_rename_carry(self):
        """
        Testing if renaming one StateName renames all connected references.
        Should ALWAYS be true, but it's a critical behaviour.

        :return:
        """

        change = 'connected'

        test2 = self.test
        test3 = test2

        test2.name = change

        self.assertEqual(self.test.name, change)
        self.assertEqual(test2.name, change)
        self.assertEqual(test3.name, change)