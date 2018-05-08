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

class InputPack:
    def __init__(self, inp, symbol):
        self.input = inp
        self.symbol = symbol
    def __repr__(self):
        return '(' + repr(self.input) + ',' + repr(self.symbol) + ')'
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.input == other.input and self.symbol == other.symbol
    def __hash__(self):
        return hash(self.input) + hash(self.symbol)

class PushDownAutomaton(NFA):

    def __init__(self, text, parser, empty_symbol = '$'):

        self.empty_symbol = empty_symbol
        super().__init__(text, parser)

        self.inputs.add(self.empty_symbol)

        self.stack_alphabet = parser.stack_alphabet
        self.stack_alphabet.add(self.empty_symbol)

        self.stack_start = parser.start_stack
        self.stack = Stack(self.stack_start)

        assert self.stack_start in self.stack_alphabet

    def reset(self):
        super().reset()
        self.stack.clear()
        self.stack.push(self.stack_start)