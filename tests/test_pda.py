import unittest
import command_tester as cmd

class TestDeterministicPDA(unittest.TestCase):

    def setUp(self):
        cmd.ERROR_FORCE = True
        self.exec_function = cmd.test_dpda
        self.INPUT_FORMAT = '.in'
        self.TEST_FORMAT = '.out'
        self.DESTINATION = '..'
        cmd.test_type = 'DPDA'

    def test_all(self):

        cmd.execute_test(self.DESTINATION, self.INPUT_FORMAT, self.TEST_FORMAT, self.exec_function)
