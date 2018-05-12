import unittest
import command_tester as cmd

class TestEpsilonNFA(unittest.TestCase):

    def setUp(self):

        self.exec_function = cmd.test_e_nfa
        self.ERROR_FORCE = True
        cmd.test_type = 'E_NFA'
        self.INPUT_FORMAT = '.a'
        self.TEST_FORMAT = '.b'
        self.DESTINATION = '..'

    def test_all(self):
        cmd.execute_test(self.DESTINATION, self.INPUT_FORMAT,
                         self.TEST_FORMAT, self.exec_function)