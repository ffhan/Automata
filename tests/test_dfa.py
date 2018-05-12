import unittest
import command_tester

class TestDeterministicFA(unittest.TestCase):

    def setUp(self):
        command_tester.ERROR_FORCE = True
        self.exec_function = command_tester.test_dfa_min
        self.INPUT_FORMAT = '.ul'
        self.TEST_FORMAT = '.iz'
        self.DESTINATION = '..'
        command_tester.test_type = 'DFA_MIN'

    def test_all(self):

        command_tester.execute_test(self.DESTINATION, self.INPUT_FORMAT,
                                    self.TEST_FORMAT, self.exec_function)