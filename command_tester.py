import argparse
from misc.command_testers import CommandTester

# LOG_FILENAME = 'log{}.log'.format(datetime.datetime.date(datetime.datetime.utcnow()))

# logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

DESTINATION = '.'
INPUT_FORMAT = '.a'
TEST_FORMAT = '.b'
ERROR_FORCE = False

# known_tests = {'DFA', 'NFA', 'E_NFA', 'DFA_MIN', 'DPDA'}

test_type = 'E_NFA'

parser = argparse.ArgumentParser()
parser.add_argument("--type", help="Test types: DFA, NFA, E_NFA, DFA_MIN. The default is {} run. Not case sensitive.".format(test_type))
parser.add_argument("--dest", help="Relative destination to the current destination.")
parser.add_argument("--inp", help="Name of of input data format. (Example: test.a => --inp a)")
parser.add_argument("--out", help="Name of input data format. (Example: test.b => --out b)")
parser.add_argument("-v", help="Verbose output. Prints out both output and expected results for all tests.", action='store_true')
parser.add_argument("-vf", help="Verbose failed output. Prints out both output and expected results for failed tests.", action='store_true')
parser.add_argument("-fe", help="Force an error when test has failed.", action='store_true')

args = parser.parse_args()

if args.type:
    test_type = args.type.upper()

if args.dest:
    DESTINATION = args.dest

if args.inp:
    INPUT_FORMAT = '.' + args.inp

if args.out:
    TEST_FORMAT = '.' + args.out

if args.fe:
    ERROR_FORCE = True

#0 for no verbosity, 1 for failed, 2 for all
if args.v:
    verbose_lvl = 2
else:
    verbose_lvl = 1 if args.vf else 0

if __name__ == '__main__':
    executor = CommandTester(INPUT_FORMAT, TEST_FORMAT, DESTINATION, verbose_lvl)
    executor.execute_test(test_type, ERROR_FORCE)