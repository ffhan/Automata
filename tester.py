import os
import argparse
from format import preformat
import logging
import datetime

LOG_FILENAME = 'log{}.log'.format(datetime.datetime.date(datetime.datetime.utcnow()))

logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

DESTINATION = '.'
INPUT_FORMAT = '.a'
TEST_FORMAT = '.b'

known_tests = {'DFA', 'NFA', 'E_NFA', 'DFA_MIN'}

test_type = 'DFA'

parser = argparse.ArgumentParser()
parser.add_argument("--type", help="Test types: DFA, NFA, E_NFA, DFA_MIN. The default is {} run. Not case sensitive.".format(test_type))
parser.add_argument("--dest", help="Relative destination to the current destination.")
parser.add_argument("--inp", help="Name of of input data format. (Example: test.a => --inp a)")
parser.add_argument("--out", help="Name of input data format. (Example: test.b => --out b)")

args = parser.parse_args()

if args.type and args.type.upper() in known_tests:
    test_type = args.type.upper()

if args.dest:
    DESTINATION = args.dest

if args.inp:
    INPUT_FORMAT = '.' + args.inp

if args.out:
    TEST_FORMAT = '.' + args.out

'''
RUN FROM DIRECTORY IN WHICH TESTS ARE CARRIED OUT

example:
    python tester --type e_nfa 
'''

def tester(func, comparator = preformat.compare_output):

    def wrapper(in_file, out_file):
        def file_to_string(file):
            text = ''

            with open(file, 'r') as inp:
                for s in inp.readlines():
                    text += s
            return text

        in_text = ''
        out_text = ''

        in_text = file_to_string(in_file)

        out_text = file_to_string(out_file)

        return comparator(func(in_text), out_text)

    return wrapper

test_e_nfa = tester(preformat.parse_e_nfa) #define E_NFA tester function
test_dfa_min = tester(preformat.parse_dfa, preformat.compare_encoding)

exec_function = test_e_nfa

if test_type == 'DFA_MIN':
    exec_function = test_dfa_min
print(INPUT_FORMAT, TEST_FORMAT, DESTINATION, test_type)
for root, dirs, files in os.walk(DESTINATION):
    path = root.split(os.sep)
    inp, outp = False, False

    folder = os.path.basename(root)

    # print((len(path) - 1) * '---', os.path.basename(root))
    for file in files:
        if file.endswith(INPUT_FORMAT):
            in_file = file
            inp = True
        elif file.endswith(TEST_FORMAT):
            test_file = file
            outp = True

        if inp and outp:
            break
    if inp and outp:
        try:
            result = exec_function(root + '\\' + in_file, root + '\\' + test_file)

            message = 'Test {}: {}'.format(folder, ' PASSED ' if result else '!FAILED!')

            print(message)

            if not result:
                logging.warning(message)
            else:
                logging.info(message)
        except Exception as e:
            print('Test {}: !FAILED!'.format(folder))
            logging.error(' [{}] {} - {}'.format(datetime.datetime.utcnow().time(), folder, e))
            raise e