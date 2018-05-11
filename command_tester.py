import os
import argparse
from format import preformat
import logging
import datetime
from format.readers import Reader
from misc.errors import CommandTestError

LOG_FILENAME = 'log{}.log'.format(datetime.datetime.date(datetime.datetime.utcnow()))

logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

DESTINATION = '.'
INPUT_FORMAT = '.a'
TEST_FORMAT = '.b'
ERROR_FORCE = False

known_tests = {'DFA', 'NFA', 'E_NFA', 'DFA_MIN', 'PDA'}

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
    verbose_level = 2
else:
    verbose_level = 1 if args.vf else 0
'''
RUN FROM DIRECTORY IN WHICH TESTS ARE CARRIED OUT

example:
    python tester --type e_nfa 
'''

def tester(func, verbose = 0):

    def wrapper(in_file, out_file):
        def file_to_string(file):

            return Reader.read_file(file)

        in_text = ''
        out_text = ''

        in_text = file_to_string(in_file)

        out_text = file_to_string(out_file)

        return func(in_text, out_text, verbose)

    return wrapper

test_e_nfa = tester(preformat.test_e_nfa, verbose_level) #define E_NFA tester function
test_dfa_min = tester(preformat.test_dfa_min, verbose_level)
test_dpa = tester(preformat.test_pda, verbose_level)

exec_function = test_e_nfa

if not test_type in known_tests:
    raise TypeError("Test {} doesn't exist".format(test_type))

if test_type == 'DFA_MIN':
    exec_function = test_dfa_min
elif test_type == 'PDA':
    exec_function = test_dpa
elif test_type == 'E_NFA':
    exec_function = test_e_nfa
else:
    raise NotImplementedError("Test {} has not yet been implemented.".format(test_type))

def execute_test(destination, input_format, test_format, test_function):
    for root, dirs, files in os.walk(destination):
        path = root.split(os.sep)
        inp, outp = False, False

        folder = os.path.basename(root)

        # print((len(path) - 1) * '---', os.path.basename(root))
        for file in files:
            if file.endswith(input_format):
                in_file = file
                inp = True
            elif file.endswith(test_format):
                test_file = file
                outp = True

            if inp and outp:
                break
        if inp and outp:
            try:
                result = test_function(root + '\\' + in_file, root + '\\' + test_file)

                message = 'Test {}: {}'.format(folder, ' PASSED ' if result else '!FAILED!')
                print(message)

                if not result:
                    logging.warning(message)
                else:
                    logging.info(message)

                if ERROR_FORCE and not result:
                    raise CommandTestError('Forced a test stop.')
            except Exception as e:
                print('Test {}: !FAILED!'.format(folder))
                logging.error(' [{}] {} - {}'.format(datetime.datetime.utcnow().time(), folder, e))
                raise e

if __name__ == '__main__':
    print(INPUT_FORMAT, TEST_FORMAT, DESTINATION, test_type)
    execute_test(DESTINATION, INPUT_FORMAT, TEST_FORMAT, exec_function)