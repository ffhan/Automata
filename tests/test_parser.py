import unittest
import format.parsers as ps
import format.readers as rs

class TestParser(unittest.TestCase):

    def test_abstraction(self):

        with self.assertRaises(TypeError):
            test = ps.Parser()

class TestStandardFormatParser(unittest.TestCase):

    def setUp(self):
        self.test = ps.StandardFormatParser()

    def test_file_parsing(self):

        try:
            text = rs.Reader.read_file('.\\file_test.a')
            self.test.parse(text)
        except FileNotFoundError:
            self.fail('File not found. Check if file_test_w_input.a exists in format/tests')

        self._output_testing()

    def _output_testing(self):

        # It's enough to test only keys because they are directly pulled from the value.
        self.assertEqual(list(self.test.states.keys()),
                         ['s1', 's10', 's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19', 's2', 's20',
                          's21', 's22', 's23', 's24', 's25', 's26', 's27', 's28', 's29', 's3', 's30', 's31', 's32',
                          's33', 's34', 's35', 's36', 's37', 's38', 's39', 's4', 's40', 's41', 's42', 's43', 's44',
                          's45', 's46', 's47', 's48', 's49', 's5', 's50', 's6', 's7', 's8', 's9'])

        self.assertEqual(self.test.inputs, {'b', 'd', 'a', 'c'})

        # self.assertEqual(set(self.test.final_states.keys()), {'s46'})

        self.assertEqual(str(self.test.start_state), 's1')

class TestStandardFormatWithInputParser(TestStandardFormatParser):

    def setUp(self):
        self.test = ps.StandardFormatWithInputParser()

    def test_file_parsing(self):

        try:
            text = rs.Reader.read_file('.\\file_test_w_input.a')
            self.test.parse(text)
        except FileNotFoundError:
            self.fail('File not found. Check if file_test_w_input.a exists in format/tests')

        self._output_testing()

    def _output_testing(self):
        super()._output_testing()
        self.assertEqual(self.test.entries,
                         [['a', 'b', 'a', 'd'], ['a', 'a', 'b', 'b', 'a'], ['a', 'b', 'c', 'b', 'a', 'a'],
                          ['a', 'b', 'c', 'b', 'a', 'a', 'a', 'b'],
                          ['d', 'b', 'c', 'b', 'a', 'a', 'a', 'b', 'c', 'b', 'c', 'b', 'a', 'a', 'a', 'b', 'c', 'b',
                           'c', 'b', 'a', 'a', 'a', 'b', 'c', 'd', 'a', 'b', 'b', 'a', 'c', 'a', 'b', 'd', 'b', 'a',
                           'a', 'b', 'c', 'b', 'a', 'd', 'a', 'd', 'a', 'a', 'a', 'b', 'c', 'b', 'a', 'a'],
                          ['a', 'b', 'c', 'b', 'c', 'b', 'c', 'b', 'b', 'c', 'b', 'a', 'd', 'a', 'd', 'a', 'a', 'a',
                           'a', 'b', 'c', 'd', 'a', 'b']])