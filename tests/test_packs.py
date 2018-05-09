from automata.packs import Records
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

    def test_getitem(self):

        self.assertEqual(self.r[1], 2)
        self.assertEqual(self.r[0:3], [1,2,3])
        self.assertEqual(self.r[1:4:2], [2,4])