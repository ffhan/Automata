import unittest
from automata.state import *

class TestStateName(unittest.TestCase):

    def setUp(self):

        self.test = StateName('testing')

    def test_add(self):

        self.assertEqual(self.test + self.test, 'testingtesting')

        self.assertEqual(self.test + 'second', 'testingsecond')

        self.test += 'third'
        self.assertEqual(self.test.name, 'testingthird')

        self.test += self.test
        self.assertEqual(self.test.name, 'testingthirdtestingthird')

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

class TestState(unittest.TestCase):

    def setUp(self):

        self.s1 = State('state1', 0)
        self.s2 = State('state2', 0)
        self.s3 = State('state3', 1)

        self.s1.add_function(self.s2, 1)
        self.s1.add_function(self.s1, 0)

        self.s2.add_function(self.s3, 1)
        self.s2.add_function(self.s2, 0)

        self.s3.add_function(self.s1, 1)
        self.s3.add_function(self.s3, 0)

    def test_reach(self):

        self.assertEqual(self.s1.reach, {self.s1, self.s2})
        self.assertEqual(self.s2.reach, {self.s2, self.s3})
        self.assertEqual(self.s3.reach, {self.s1, self.s3})

    def test_lt(self):

        self.assertTrue(self.s1 < self.s2)
        self.assertTrue(self.s2 < self.s3)
        self.assertTrue(self.s1 < 1)

    def test_eq(self):

        self.assertFalse(self.s1 == self.s2)
        self.assertFalse(self.s2 == self.s3)

        self.assertFalse(self.s1 == 1)
        self.assertTrue(self.s1 == self.s1)

        s2 = self.s1
        self.assertTrue(self.s1 == s2)

    def test_forward(self):

        self.assertEqual(self.s1.clean_forward(0), self.s1)
        self.assertEqual(self.s1.clean_forward(1), self.s2)

        self.s1.add_function(self.s3, 0)

        self.assertEqual(self.s1.forward(0), {self.s1, self.s3})