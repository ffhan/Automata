class SingleRecord:

    def __init__(self, current, accepted):

        self.current = current
        self.accepted = accepted

    @property
    def pack(self):
        return self.current, self.accepted

class SinglePushRecord(SingleRecord):

    def __init__(self, current, accepted, stack):

        super().__init__(current, accepted)
        self.stack = stack

    @property
    def pack(self):
        return super().pack, self.stack

class Records:

    def __init__(self, records):

        self.records = []

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