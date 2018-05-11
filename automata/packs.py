import copy

class RecordPack:

    def __init__(self, current, accepted):

        self.current = current
        self.accepted = copy.deepcopy(accepted)

    @property
    def unpack(self):
        return self.current, self.accepted

    def __repr__(self):
        return 'pack:[{}, {}]'.format(self.current, self.accepted)

class PushRecordPack(RecordPack):

    def __init__(self, current, accepted, stack):

        super().__init__(current, accepted)
        self.stack = copy.deepcopy(stack)

    @property
    def unpack(self):
        return self.current, self.accepted, self.stack

    def __repr__(self):
        return 'pushpack:[{}, {}, {}]'.format(self.current, self.accepted, self.stack)

class Records:

    def __init__(self, *records):

        self.records = []

        self.add_records(*records)

    def __repr__(self):
        return 'records:' + repr(self.records)

    @property
    def size(self):
        return len(self.records)

    def add_record(self, record):

        self.records.append(record)

    def add_records(self, *records):

        for record in records:
            self.add_record(record)

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= self.size:
            raise StopIteration
        res = self.records[self._index]
        self._index += 1
        return res

    def __getitem__(self, item):
        return self.records[item]

class InputPack:
    """
    Contains State as a 'key', stack symbol as a 'value'
    """
    def __init__(self, key, value):

        self.key = key
        self.value = value

    @property
    def unpack(self):
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

    def reverse(self):
        self._container.reverse()
        return self

    def exclude(self, symbol):

        temp = self.__class__()
        for i in self:
            if i != symbol: temp.push(i)

        return temp.reverse()

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
        tmp2 = copy.deepcopy(other)
        tmp2._container.reverse()
        tmp._container += tmp2.container

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