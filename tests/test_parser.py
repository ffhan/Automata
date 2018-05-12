import unittest
from format.parsers import Parser, StandardFormatParser, \
    StandardFormatWithInputParser, PushDownFormatWithInputParser
from format.readers import Reader

class TestParser(unittest.TestCase):

    def test_abstraction(self):

        with self.assertRaises(TypeError):
            test = Parser()

class TestStandardFormatParser(unittest.TestCase):

    def setUp(self):
        self.test = StandardFormatParser()

    def test_file_parsing(self):
        with self.assertRaises(FileNotFoundError):
            text = Reader.read_file('.\\file_test.a')
            self.test.parse(text)
            fail_text = Reader.read_file('.\\doesnt.exist')

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
        self.test = StandardFormatWithInputParser()

    def test_file_parsing(self):

        text = Reader.read_file('.\\file_test_w_input.a')
        self.test.parse(text)

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

class TestPushDownFormatWithInputParser(unittest.TestCase):

    def setUp(self):
        self.test = PushDownFormatWithInputParser()

    def test_file_parsing(self):

        text = Reader.read_file('.\\push_file_test.in')
        self.test.parse(text)
        print(self.test.entries)
        print(self.test.states)
        print(self.test.inputs)
        print(self.test.stack_alphabet)
        print(self.test.start_state)
        print(self.test.start_stack)
        for state in self.test.states.values():
            print(state, state.transitions)
        self.assertEqual(self.test.stack_alphabet, {'K', 'X', 'Y'})
        self.assertEqual(self.test.start_stack, 'K')
