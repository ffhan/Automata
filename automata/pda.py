from automata.nfa import NFA
import copy

class Stack:
    def __init__(self, *items):
        self._container = list()
        for item in items:
            self.push(item)
    def push(self, *item):
        for it in item:
            self._container.append(it)

    def pop(self):
        return self._container.pop()

    def clear(self):
        self._container.clear()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self._container == other._container

    def __hash__(self):
        res = 0
        counter = 1
        for item in self._container:
            res += counter * hash(item)
            counter += 1
        return res


    @property
    def size(self):
        return len(self._container)

    def __repr__(self):
        def wrap(text):
            return '[' + text + ']'

        result = ''
        for item in self._container:
            result += repr(item) + ','
        result = result[:-1]
        return wrap(result)

    def __add__(self, other):
        assert isinstance(other, self.__class__)
        tmp = copy.deepcopy(self) # DO NOT REMOVE OR CHANGE.
        for val in other:
            tmp.push(val)

        return tmp

    def __iadd__(self, other):
        return self.__add__(other)

    def _reset_index(self):
        self._index = 1

    def __iter__(self):
        self._reset_index()
        return self

    def __next__(self):
        if self._index <= self.size:
            res = self._container[self.size - self._index]
            self._index += 1
            return res
        self._reset_index()
        raise StopIteration

class InputPack: #todo: seems more like a hack than a solution.
    def __init__(self, inp, symbol):
        """
        Initializes an InputPack.
        It has interface that mathes both StateName (partly) and State.

        :param inp: input
        :param symbol: input symbol
        """
        self.name = inp
        self.value = symbol
    def __repr__(self):
        return '(' + repr(self.name) + ',' + repr(self.value) + ')'
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name and self.value == other.value
    def __hash__(self):
        return hash(self.name) + hash(self.value)

class PushDownAutomaton(NFA):

    def __init__(self, text, parser, empty_symbol = '$', fail_symbol = '\b'):

        self.empty_symbol = empty_symbol
        super().__init__(text, parser)

        self.inputs.add(self.empty_symbol)

        self.stack_alphabet = parser.stack_alphabet
        self.stack_alphabet.add(self.empty_symbol)

        self.fail_symbol = fail_symbol

        self.stack_start = parser.start_stack
        self.stack = Stack(self.stack_start)

        assert self.stack_start in self.stack_alphabet

    def reset(self):
        super().reset()
        self.stack.clear()
        self.stack.push(self.stack_start)

    def _access(self, value):

        if self.current == self.fail_symbol:
            return
        if value not in self.inputs:
            raise ValueError(self._input_error(value))

        old_currents = set()
        try:
            symbol = self.stack.pop()
        except Exception:
            self.current = self.fail_symbol
            return

        for state in sorted(list(self.current)):

            res = state.forward(InputPack(value, symbol))

            for res in sorted(list(res)):
                st = res.name
                sym = res.value
                self.stack.push(sym)
                old_currents.add(st) #todo: fix pushdown automata. Records don't work, stack isn't correct, structure seems incorrect.

        self.current = old_currents

    def __repr__(self):
        def wrap_in_braces(string, last_brace_newline=False):
            return '{' + string + ('\n}' if last_brace_newline else '}')

        def tab(string):
            return '\t' + string.replace('\n', '\n\t')

        def space(*strings):
            result = ''
            for s in strings:
                result += s + ' '
            return result[:-1]

        def newline(*lines):
            """
            Returns concatenated string composed of all line arguments with newline added between them.

            :param str lines: lines of text that need to be newlined.
            :return: full string composed of individual lines concatenated with newline in-between
            """
            res = '\n'
            for line in lines:
                res += line + '\n'
            return res[:-1]
        states = ''
        final = ''

        for state, state_object in self.states.items():
            states += state + ','
            if state_object.value:
                # print(final, state)
                final += state.name

        final = 'F=' + wrap_in_braces(final)

        states = 'Q=' + wrap_in_braces(states[:-1])

        stack_alphabet = ''
        for sym in self.stack_alphabet:
            stack_alphabet += sym

        stack_alphabet = u'\u0394=' + wrap_in_braces(stack_alphabet[:-1])

        inputs = ''

        for inp in self.inputs:
            inputs += str(inp) + ','

        inputs = u'\u03A3=' + wrap_in_braces(inputs[:-1])

        start_stack = u'\u0393=' + self.stack_start

        funcs = u'\u03B4=' + wrap_in_braces(self.functions)

        start = 'q0=' + self.start_state.name

        return '{} '.format(self.__class__.__name__) + wrap_in_braces(tab(
            newline(states, inputs, stack_alphabet, funcs, start, start_stack, final)
        ), True)
