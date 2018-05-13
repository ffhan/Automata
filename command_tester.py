"""
Allows testing through command prompt.

For help type python command_tester.py -h
"""

import argparse
from misc.command_testers import CommandTester

# LOG_FILENAME = 'log{}.log'.form(datetime.datetime.date(datetime.datetime.utcnow()))

# logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

DESTINATION = '.'
INPUT_FORMAT = '.a'
TEST_FORMAT = '.b'
ERROR_FORCE = False

# known_tests = {'DFA', 'NFA', 'E_NFA', 'DFA_MIN', 'DPDA'}

TEST_TYPE = 'E_NFA'

PARSER = argparse.ArgumentParser()
PARSER.add_argument("--type", help="Test types: DFA, NFA, E_NFA, DFA_MIN. " +
                    "The default is {} run. Not case sensitive.".format(TEST_TYPE))
PARSER.add_argument("--dest", help="Relative destination to the current destination.")
PARSER.add_argument("--inp", help="Name of of input data form. (Example: test.a => --inp a)")
PARSER.add_argument("--out", help="Name of input data form. (Example: test.b => --out b)")
PARSER.add_argument("-v", help="Verbose output. Prints out both output and expected " +
                    "results for all _all_tests.", action='store_true')
PARSER.add_argument("-vf", help="Verbose failed output. Prints out both output and expected " +
                    "results for failed _all_tests.", action='store_true')
PARSER.add_argument("-fe", help="Force an error when test has failed.", action='store_true')

ARGS = PARSER.parse_args()

if ARGS.type:
    TEST_TYPE = ARGS.type.upper()

if ARGS.dest:
    DESTINATION = ARGS.dest

if ARGS.inp:
    INPUT_FORMAT = '.' + ARGS.inp

if ARGS.out:
    TEST_FORMAT = '.' + ARGS.out

if ARGS.fe:
    ERROR_FORCE = True

#0 for no verbosity, 1 for failed, 2 for all
if ARGS.v:
    VERBOSE_LVL = 2
else:
    VERBOSE_LVL = 1 if ARGS.vf else 0

if __name__ == '__main__':
    EXECUTOR = CommandTester(INPUT_FORMAT, TEST_FORMAT, DESTINATION, VERBOSE_LVL)
    EXECUTOR.execute_test(TEST_TYPE, ERROR_FORCE)
