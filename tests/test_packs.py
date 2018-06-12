from automata.packs import Records, PushRecordPack, Stack, InputPack, RecordPack, Tape, TuringOutputPack
import unittest

class TestRecords(unittest.TestCase):

    def setUp(self):
        self.r = Records(1,2,3,4,5,6)

    # def test_add(self):
    #     self.r.add_records(7, 8, 9)
    #     self.assertEqual(self.r.records, [i + 1 for i in range(9)])

    def test_iteration(self):

        lst = list()
        for i in self.r:
            lst.append(i)
        self.assertEqual(self.r.records, lst)

    def test_repr(self):
        self.assertEqual(repr(self.r), 'records:{}'.format([1,2,3,4,5,6]))

    def test_getitem(self):

        self.assertEqual(self.r[1], 2)
        self.assertEqual(self.r[0:3], [1,2,3])
        self.assertEqual(self.r[1:4:2], [2,4])

class TestRecordPack(unittest.TestCase):

    def setUp(self):
        self.r = RecordPack(1,2)

    def test_unpack(self):

        self.assertEqual(self.r.unpack, (1,2))

    def test_repr(self):

        self.assertEqual(repr(self.r), 'pack:[{}, {}]'.format(1,2))

class TestPushRecordPack(unittest.TestCase):

    def setUp(self):
        self.r = PushRecordPack(1,2,3)

    def test_unpack(self):
        self.assertEqual(self.r.unpack, (1,2,3))

    def test_repr(self):
        self.assertEqual(repr(self.r), 'pushpack:[{}, {}, {}]'.format(1,2,3))

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

    def test_clear(self):
        self.s1.clear()
        self.assertEqual(self.s1.container, [])

    def test_reverse(self):
        self.s1.reverse()
        self.assertEqual(self.s1.container, [4,3,2,1])

    def test_exclude(self):
        s3 = self.s1.exclude(3)
        self.assertEqual(s3.container, [1,2,4])

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
        self.assertFalse(self.s1 == 1)

    def test_lt(self):

        self.assertTrue(self.s1 < self.s2)
        self.assertFalse(self.s1 < 5)
        s3 = InputPack(1,'c')
        self.assertTrue(self.s1 < s3)

    def test_pack(self):

        self.assertEqual(self.s1.unpack, (1, 'a'))

class TestTape(unittest.TestCase):
    def setUp(self):
        self.test = Tape(1,2,3,4,5)
        self.LEFT = TuringOutputPack.LEFT
        self.RIGHT = TuringOutputPack.RIGHT
    def test_movement(self):
        results = [2,3,4,5,None,None,None,None]
        for i in range(8):
            self.assertEqual(self.test.move_right(),results[i])
        results = [None,None,None,5,4,3,2,1]
        for i in range(8):
            self.assertEqual(self.test.move_left(),results[i])
        results = [2,1,2,1]
        for i in range(4):
            func = self.test.move_right if i % 2 == 0 else self.test.move_left
            self.assertEqual(func(), results[i])
