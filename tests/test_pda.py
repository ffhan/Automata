import unittest
from automata.pda import Stack, InputPack

class TestStack(unittest.TestCase):

    def setUp(self):

        self.s1 = Stack(1,2,3,4)
        self.s2 = Stack(5,6)

    def test_addition(self):

        size1 = self.s1.size
        size2 = self.s2.size
        self.assertEqual(self.s1 + self.s2, Stack(1,2,3,4,6,5))

        self.s1.pop()
        self.s2.pop()
        self.s2.pop()

        self.assertTrue(self.s1.size == size1 - 1)
        self.assertTrue(self.s2.size == size2 - 2)

    def test_push(self):

        self.s1.push(5,6)
        self.assertEqual(self.s1, Stack(1,2,3,4,5,6))

    def test_equality(self):

        self.assertTrue(self.s1 == self.s1)
        self.assertFalse(self.s1 == self.s2)
        self.assertFalse(self.s1 == 2)

    def test_iadd(self):
        size0 = self.s1.size
        self.s1 += self.s2
        size1 = self.s1.size
        size2 = self.s2.size
        self.assertEqual(self.s1, Stack(1,2,3,4,6,5))

        self.s2.pop()

        self.assertEqual(self.s1.size, size1)
        self.assertEqual(self.s1.size, size0 + size2)
        self.assertEqual(self.s2.size, size2 - 1)

    def test_peek(self):
        size1 = self.s1.size
        p = self.s1.peek()
        s = self.s1.peek()
        self.assertEqual(p, 4)
        self.assertEqual(s, p)
        self.assertTrue(size1 == self.s1.size)

    def test_pop(self):

        val1 = self.s1.pop()
        val2 = self.s1.pop()

        self.assertEqual(val1, 4)
        self.assertEqual(val2, 3)

class TestInputPack(unittest.TestCase):

    def setUp(self):

        self.s1 = InputPack(1, 'a')
        self.s2 = InputPack(2, 'b')

    def test_equality(self):

        self.assertEqual(self.s1, InputPack(1, 'a'))
        self.assertTrue(self.s1 == self.s1)
        self.assertFalse(self.s1 == self.s2)

    def test_pack(self):

        self.assertEqual(self.s1.pack, (1, 'a'))