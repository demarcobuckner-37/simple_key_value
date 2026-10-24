class Record:
    def __init__(self, key, value):
        self.key = key
        self.value = value

class Index:
    def __init__(self):
        self.records = []

    def search(self, key):
        for record in self.records:
            if record.key == key:
                return record
        return None

    def set(self, key, value):
        record = self.search(key)

        if record is not None:
            record.value = value
        else:
            self.records.append(Record(key, value))

    
    def delete(self, key):
        for i, record in enumerate(self.records):
            if record.key == key:
                self.records.pop(i)
                return True
        return False