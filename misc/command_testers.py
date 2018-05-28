"""
Defines a CommandTester type which allows easy testing.
"""
import datetime
import logging
import os
from misc.errors import CommandTestError
from form import readers, preformat

class CommandTester:

    """
    Command tester implementation.
    """

    def __init__(self, input_format, test_format, destination='.', verbose_level=0):
        """
        Initializes a CommandTester object.

        Verbose level:
            0: doesn't print program output and expected output
            1: prints program output and expected output when a test fails
            2: always prints program output and expected output when a test fails

        :param str input_format: input file form (for example '.in')
        :param str test_format: test file form (for example '.test')
        :param str destination: test files destination
        :param int verbose_level: verbose level
        """

        self.destination = destination
        self.input_format = input_format
        self.test_format = test_format

        self.log_filename = 'log{}.log'.format(datetime.datetime.date(datetime.datetime.utcnow()))
        logging.basicConfig(filename=self.log_filename, level=logging.DEBUG)

        self.verbose_level = verbose_level

        self._tests = dict()

        self.listeners = list()

    def register_listener(self, listener_function):
        """
        Registers a listener function that is executed when the test report is done.

        :param function listener_function: listener function
        :return:
        """
        self.listeners.append(listener_function)

    def _known_tests(self):
        """
        Internal return of known _all_tests.
        Implemented separately because of known

        :return dict: all known _all_tests
        """
        self._tests.clear()
        # define E_NFA tester function
        self._tests['E_NFA'] = self._test_factory(preformat.TEST_E_NFA)
        self._tests['DFA_MIN'] = self._test_factory(preformat.TEST_DFA_MIN)
        self._tests['DPDA'] = self._test_factory(preformat.TEST_PDA)
        self._tests['PARSER'] = self._test_factory(preformat.TEST_PARSER)
        return self._tests

    @property
    def known_tests(self):
        """
        Names of all known tests.

        :return list: names of all known tests
        """
        return list(self._known_tests().keys())

    @property
    def _all_tests(self):
        """
        Defines all known _all_tests with a correct configuration.

        :return dict: all known _all_tests
        """
        return self._known_tests()

    def execute_test(self, test_type, error_force=False):
        """
        Executes a specific test.

        :param str test_type: test type
        :param error_force:
        :return:
        """
        test_type = test_type.upper()
        tests = self._all_tests

        if test_type not in tests:
            raise NotImplementedError("Test {} has not yet been implemented.".format(test_type))

        test_function = tests.get(test_type)

        print(self.input_format, self.test_format, self.destination, test_type)
        counter = 0
        success_counter = 0
        for root in os.walk(self.destination):
            # path = root.split(os.sep)
            root, files = root[0], root[2]
            input_bool, output_bool = False, False

            folder = os.path.basename(root)

            # print((len(path) - 1) * '---', os.path.basename(root))
            for file in files:
                if file.endswith(self.input_format):
                    in_file = file
                    input_bool = True
                elif file.endswith(self.test_format):
                    test_file = file
                    output_bool = True

                if input_bool and output_bool:
                    break
            if input_bool and output_bool:
                try:
                    result = test_function(root + '\\' + in_file, root + '\\' + test_file)
                    counter += 1

                    message = 'Test {}: {}'.format(folder, ' PASSED ' if result else '!FAILED!')
                    if result:
                        success_counter += 1
                    print(message)

                    for listener_function in self.listeners:
                        listener_function(result)

                    if not result:
                        logging.warning(message)
                    else:
                        logging.info(message)

                    if error_force and not result:
                        raise CommandTestError('Forced a test stop.')
                except CommandTestError:
                    print('------------------------------------------')
                    print('Force stopped execution (-fe flag present)')
                    exit(1)
                except Exception as exception_error:
                    print('Test %s: !FAILED!' %folder)
                    logging.error(' [%s] %s - %s' %(
                        datetime.datetime.utcnow().time(),
                        folder, exception_error), exception_error)
                    raise exception_error
        if counter == 0:
            print('NO TESTS FOUND')
        else:
            print("-" * 60)
            print("{:30s}{:^20s}".format("Successful tests: " + str(success_counter) + '/' + str(counter),
                                          "Rate of success: " + "{:.2f}%".format(success_counter * 100 / counter)))

    def _test_factory(self, func):
        """
        Internal test factory. Used to create tests easily.

        :param function func: preformat test function
        :return function: testing function wrapper that imports input and test files
        """
        def wrapper(in_file, out_file):
            """
            Test function wrapper.
            Reads files and delegates testing to an external testing function.

            :param str in_file: input file destination
            :param str out_file: test file destination
            :return bool: testing result
            """

            in_text = readers.Reader.read_file(in_file)

            out_text = readers.Reader.read_file(out_file)

            return func(in_text, out_text, self.verbose_level)

        return wrapper
