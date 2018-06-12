"""
Defines all types that contain complex data.
It allows separation of concern and managing complex behaviour.

Packs are used to transport complex data through the system.
"""
import copy

class RecordPack:

    """
    Packs a current state of an automaton.
    """

    def __init__(self, current, accepted):

        """
        Initializes a RecordPack.

        :param current: current state(s)
        :param bool accepted: automaton acceptance for the current automaton state
        """

        self.current = current
        self.accepted = copy.deepcopy(accepted)

    @property
    def unpack(self):
        """
        Unpacks inner values.

        :return: unpacked values
        """
        return self.current, self.accepted

    def __repr__(self):
        return 'pack:[{}, {}]'.format(self.current, self.accepted)

class PushRecordPack(RecordPack):
    """
    Record pack that also contains a stack. Used primarily in Push down automata.
    """

    def __init__(self, current, accepted, stack):

        """
        Initializes a PushRecordPack.

        :param current: current state(s)
        :param accepted: automaton acceptance
        :param stack: automaton stack
        """

        super().__init__(current, accepted)
        self.stack = copy.deepcopy(stack)

    @property
    def unpack(self):
        return self.current, self.accepted, self.stack

    def __repr__(self):
        return 'pushpack:[{}, {}, {}]'.format(self.current, self.accepted, self.stack)

class Records:

    """
    Collection of RecordPacks.
    """

    def __init__(self, *records):

        """
        Initializes a Records object.

        :param records: (Push)RecordPacks
        """

        self.records = []
        self._index = 0

        self.add_records(*records)

    def __repr__(self):
        return 'records:' + repr(self.records)

    @property
    def size(self):
        """
        :return int: count of records held internally
        """
        return len(self.records)

    def add_record(self, record):
        """
        Adds a RecordPack.

        :param RecordPack record: a record
        :return:
        """

        self.records.append(record)

    def add_records(self, *records):
        """
        Adds multiple records.

        :param records: records
        :return:
        """

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
    Differs from RecordPack in usage and internal mechanisms.
    InputPack is designed so that it can be reinitialized and
    reproduced and be identical to objects created on a different reference.
    """
    def __init__(self, key, value):

        self.key = key
        self.value = value

    @property
    def unpack(self):
        """
        Unpacks internal values

        :return: internal values in a tuple
        """
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
        if not isinstance(other, self.__class__):
            return False
        if self.key == other.key:
            return self.value < other.value
        return self.key < other.key

class TuringOutputPack:
    """
    Classic Turing machine transition output.
    Key is the new state, value is a symbol that is going to be written to the tape
    and side indicates where the tape is going to move.

    TuringOutputPack.LEFT indicates leftwards move, RIGHT rightwards.
    LEFT is defined by integer -1, RIGHT by integer 1

    It's really important to distinct between head movement and tape movement.
    In current context we are talking about HEAD movement.
    Tape movement to the left is opposite of the head movement (to the right).
    """
    LEFT = -1
    RIGHT = 1
    def __init__(self, key, value, side):
        """
        Initialises a TuringOutputPack.
        The class itself does not inherit InputPack by purpose.
        Most of the code has to be rewritten and they do not share
        the same interface.

        :param key: new state
        :param value: symbol that is going to be written to the tape
        :param side: tape movement side
        """
        self.key = key
        self.value = value
        self._side = 0
        self.side = side
        assert self._side in (self.LEFT, self.RIGHT)

    @property
    def side(self):
        """
        Returns a side property.

        :return int: side movement
        """
        return self._side
    @side.setter
    def side(self, value):
        """
        Defines a side movement, checks if it's valid.

        :param value: LEFT or RIGHT movement.
        :return:
        """
        if value in (self.LEFT, self.RIGHT):
            self._side = value
        else:
            raise ValueError('Side value must be LEFT (-1) or RIGHT (1)')
    @property
    def unpack(self):
        """
        Unpacks all values out of this pack.

        :return:
        """
        return self.key, self.value, self.side

class Stack:
    """
    A classic Stack implementation.
    """
    def __init__(self, *items):
        """
        Initializes a Stack.

        :param items: items to be added to a stack
        """
        self._container = list()
        for item in items:
            self.push(item)

        self._index = 1
    def push(self, *item):
        """
        Push items to the stack.

        :param item: items to be added
        :return:
        """
        for single_item in item:
            self._container.append(single_item)

    def pop(self):
        """
        Pop the last item of a stack.

        :return: last item of a stack
        """
        return self._container.pop()

    def peek(self):
        """
        Return the last item of a stack but don't remove it.

        :return: last item of a stack
        """
        return self._container[-1]

    def clear(self):
        """
        Clears the stack.

        :return:
        """
        self._container.clear()

    @property
    def container(self):
        """
        Returns the internal stack container.
        It returns a deep copy so it's not bound by reference to the original object.
        Changing the returned container doesn't change Stack container.

        :return list: deep copy of an internal container
        """
        return copy.deepcopy(self._container)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self._container == other.container

    def __hash__(self):
        res = 0
        counter = 1
        for item in self._container:
            res += counter * hash(item)
            counter += 1
        return res

    def reverse(self):
        """
        Reverses a Stack.
        Doesn't copy the stack so the returned reference is exactly the same as this object.
        Changing returned object also changes this object.

        :return Stack: reversed stack
        """
        self._container.reverse()
        return self

    def exclude(self, symbol):
        """
        Excludes all occurrences of a specified item (symbol) from a stack.
        Returns a Stack that is not bound by reference to this object.
        Changing the returned Stack does not change this stack.

        :param symbol: an item to be excluded from a stack.
        :return Stack: new Stack with all elements without a specified symbol.
        """

        temp = self.__class__()
        for i in self:
            if i != symbol:
                temp.push(i)

        return temp.reverse()

    @property
    def size(self):
        """
        Returns the size of the container

        :return: size
        """
        return len(self._container)

    def __repr__(self):
        def wrap(text):
            """
            Wraps a text in []

            :param str text: text to be wrapped
            :return str: wrapped text
            """
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
        tmp2.reverse()
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

class Tape:
    """
    Defines a Turing machine tape.
    """
    def __init__(self, *initial_items):
        self._container = list(initial_items)
        self._index = 0

    # @property
    # def index(self)->int:
    #     """
    #     Defines an index property
    #
    #     :return int: index value
    #     """
    #     return self._index
    #
    # @index.setter
    # def index(self, value):
    #     """
    #     Sets an index to a new value.
    #
    #     :param value: new index value
    #     :return:
    #     """
    #     if 0 <= value < len(self._container):
    #         self._index = value
    #     else:
    #         raise ValueError('New index value {} is outside of the acceptable range {}-{}'.format(
    #             value, 0, len(self._container)))
    def __repr__(self):
        result = 'Tape: ['
        for i, item in enumerate(self._container):
            fix = ''
            if i == self._index:
                fix = '_'
            result += fix + (item if isinstance(item, str) else repr(item)) + fix + ', '
        result = result[:-2] + ']'
        return result

    @property
    def read(self):
        """
        Reads an item that the tape head currently points to.

        :return:
        """
        if 0 <= self._index < len(self._container):
            return self._container[self._index]
        return None
    @property
    def consume(self):
        """
        Reads an item and removes it from the tape at the
        current position of the head.

        :return: item from the tape
        """
        if 0 <= self._index < len(self._container):
            result = self._container.pop(self._index)
        else:
            result = None
        return result

    def add(self, *items):
        """
        Adds specified items to the tape.

        :param items: items to be added
        :return:
        """
        if 0 <= self._index < len(self._container):
            index = self._index
        elif self._index < 0:
            index = 0
        else:
            index = len(self._container) - 1
        # self._index += len(items) + 1 if items else 0
        self._container = self._container[:index] + list(items) + self._container[index:]

    def _internal_move(self, movement: int, *items):
        """
        Adds all specified items to the tape and moves the head index.

        :param items: items to be added to a tape
        :param int movement: movement side. It's possible to use
        TuringOutputPack LEFT and RIGHT as movement side.
        :return: item that the head currently points at
        """
        self.add(*items)
        self._index += movement
        read = self.read
        # if self._index < 0:
        #     self._index = -1
        # elif self._index > len(self._container):
        #     self._index = len(self._container)
        return read
    def move_left(self, *items):
        """
        Adds all specified items to the tape and move the tape to the left.

        :param items:
        :return: item that the head currently points at
        """
        # it might be a really bad idea to produce such a tight coupling
        # between movement here and movement in TuringOutputPack
        # the reason why i'm currently okay with that is because it
        # ensures a uniform behaviour.
        return self._internal_move(TuringOutputPack.LEFT, *items)
    def move_right(self, *items):
        """
        Adds all specified items to the tape and move the tape to the right.

        :param items:
        :return: item that the head currently points at
        """
        return self._internal_move(TuringOutputPack.RIGHT, *items)
