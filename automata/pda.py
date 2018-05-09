import automata
import format
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

    def peek(self):
        return self._container[-1]

    def clear(self):
        self._container.clear()

    @property
    def container(self):
        return copy.deepcopy(self._container)

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
    """
    Contains State as a 'key', stack symbol as a 'value'
    """
    def __init__(self, key, value):

        self.key = key
        self.value = value

    @property
    def pack(self):
        return self.key, self.value

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.key == other.key and self.value == other.value

    def __hash__(self):
        return hash(self.key) + hash(self.value)

    def __repr__(self):

        return '(' + repr(self.key) + ',' + repr(self.value) + ')'

    def __lt__(self, other):
        if self.key == other.key:
            return self.value < other.value
        return self.key < other.key

class DeterministicPA(automata.dfa.DFA): #todo: correct implementation would be to inherit from abstract PA.

    def __init__(self, text, parser, empty_symbol = '$'):

        super().__init__(text, parser)

        self.start_symbol = parser.start_stack
        self.stack = Stack(self.start_symbol)

        self.stack_alphabet = parser.stack_alphabet

        self.inputs.add(empty_symbol)
        self.empty_symbol = empty_symbol

        self.failed_symbol = automata.state.PushState('fail', 0)

    def _check_structure(self):
        pass #not checking anything. todo: check parser results.

    def reset(self):
        super().reset()
        # self.current = self.start_state
        self.stack.clear()
        self.stack.push(self.start_symbol)

    def _access(self, value):
        if self.stack.size > 0:
            symbol = self.stack.pop()
        else:
            self.current = self.failed_symbol
            return

        if self.current == self.failed_symbol:
            return

        current = self.current.clean_forward(InputPack(value, symbol))

        #todo: check izlaz.txt for a detailed overview.

        self.current = current
        if not isinstance(current, automata.state.PushState):
            self.current = self.failed_symbol


        self.stack += self.current.stack

    def _process(self, *entry):
        self.records.append([])
        self.records[-1].append(InputPack(self.current, self.stack.container))
        for inp in entry:
            self._access(inp)
            self.records[-1].append(InputPack(self.current, self.stack.container))

