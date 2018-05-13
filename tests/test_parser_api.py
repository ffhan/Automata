import unittest
from form.lexer_api import split_factory

class TestSplitting(unittest.TestCase):

    def test_split_factory(self):

        comma_list = split_factory(',')
        self.assertEqual(comma_list('test1, test2,  test3, '), ['test1','test2','test3'])

        comma_set = split_factory(',', set)
        self.assertEqual(comma_set('test1, test2,  test3, '), {'test1', 'test2', 'test3'})

        banana = split_factory('an', set)
        self.assertEqual(banana('banana'), {'b','a'})

        with self.assertRaises(RuntimeError):
            error_test = split_factory('test', set())
