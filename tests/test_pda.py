import unittest
from automata.pda import Stack

class TestStack(unittest.TestCase):

    def setUp(self):

        self.s1 = Stack(1,2,3,4)
        self.s2 = Stack(5,6)

    def test_addition(self):

        size1 = self.s1.size
        size2 = self.s2.size
        self.assertEqual(self.s1 + self.s2, Stack(1,2,3,4,6,5))

        self.assertTrue(self.s1.size == size1)
        self.assertTrue(self.s2.size == size2)

    def test_push(self):

        self.s1.push(5,6)
        self.assertEqual(self.s1, Stack(1,2,3,4,5,6))

    def test_equality(self):

        self.assertTrue(self.s1 == self.s1)
        self.assertFalse(self.s1 == self.s2)
        self.assertFalse(self.s1 == 2)

    def test_iadd(self):

        self.s1 += self.s2
        size1 = self.s1.size
        size2 = self.s2.size
        self.assertEqual(self.s1, Stack(1,2,3,4,6,5))


    def test_pop(self):

        val1 = self.s1.pop()
        val2 = self.s1.pop()

        self.assertEqual(val1, 4)
        self.assertEqual(val2, 3)