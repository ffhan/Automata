import datetime, logging, os
from format import preformat
from misc.errors import CommandTestError
from format.readers import Reader

class CommandTester:

    def __init__(self, input_format, test_format, destination = '.', verbose_level = 0):

        self.DESTINATION = destination
        self.INPUT_FORMAT = input_format
        self.TEST_FORMAT = test_format

        self.LOG_FILENAME = 'log{}.log'.format(datetime.datetime.date(datetime.datetime.utcnow()))
        logging.basicConfig(filename = self.LOG_FILENAME, level = logging.DEBUG)

        self.verbose_level = verbose_level

        self._tests = dict()

        self.listeners = list()

    def register_listener(self, listener_function):
        self.listeners.append(listener_function)

    @property
    def tests(self):
        self._tests.clear()
        self._tests['E_NFA'] = self._test_factory(preformat.test_e_nfa) #define E_NFA tester function
        self._tests['DFA_MIN'] = self._test_factory(preformat.test_dfa_min)
        self._tests['DPDA'] = self._test_factory(preformat.test_pda)
        return self._tests

    def execute_test(self, test_type, error_force = False):
        test_type = test_type.upper()
        tests = self.tests

        if test_type not in tests:
            raise NotImplementedError("Test {} has not yet been implemented.".format(test_type))

        test_function = tests.get(test_type)

        print(self.INPUT_FORMAT, self.TEST_FORMAT, self.DESTINATION, test_type)
        counter = 0
        for root, dirs, files in os.walk(self.DESTINATION):
            path = root.split(os.sep)
            inp, outp = False, False

            folder = os.path.basename(root)

            # print((len(path) - 1) * '---', os.path.basename(root))
            for file in files:
                if file.endswith(self.INPUT_FORMAT):
                    in_file = file
                    inp = True
                elif file.endswith(self.TEST_FORMAT):
                    test_file = file
                    outp = True

                if inp and outp:
                    break
            if inp and outp:
                try:
                    result = test_function(root + '\\' + in_file, root + '\\' + test_file)
                    counter += 1

                    message = 'Test {}: {}'.format(folder, ' PASSED ' if result else '!FAILED!')
                    print(message)

                    for listener_function in self.listeners:
                        listener_function(result)

                    if not result:
                        logging.warning(message)
                    else:
                        logging.info(message)

                    if error_force and not result:
                        raise CommandTestError('Forced a test stop.')
                except Exception as e:
                    print('Test {}: !FAILED!'.format(folder))
                    logging.error(' [{}] {} - {}'.format(datetime.datetime.utcnow().time(), folder, e))
                    raise e
        if counter == 0:
            print('NO TESTS FOUND')

    def _test_factory(self, func):
        def wrapper(in_file, out_file):
            def file_to_string(file):
                return Reader.read_file(file)

            in_text = ''
            out_text = ''

            in_text = file_to_string(in_file)

            out_text = file_to_string(out_file)

            return func(in_text, out_text, self.verbose_level)

        return wrapper