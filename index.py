
import time


class HashField:
    """Stores a field and its value within a hash record."""

    def __init__(self, field, value):
        """Initialize a hash field with its name and value."""
        self.field = field
        self.value = value


class Record:
    """Represents a database record and its associated data."""

    def __init__(self, key, value):
        """Initialize a record and its optional data structures."""
        self.key = key
        self.value = value
        self.expires_at = None
        self.hash_fields = []
        self.list_values = []


class Index:
    """Manages records and supports database operations."""

    def __init__(self):
        """Initialize an empty collection of records."""
        self.records = []

    def search(self, key):
        """Find a record by key, removing it if it has expired."""
        for record in self.records:
            if record.key == key:
                if record.expires_at is not None:
                    if time.time() >= record.expires_at:
                        self.records.remove(record)
                        return None

                return record
        return None

    def set(self, key, value):
        """Create a new record or update an existing record."""
        record = self.search(key)

        if record is not None:
            record.value = value
            record.expires_at = None
        else:
            self.records.append(Record(key, value))

    def delete(self, key):
        """Delete a record by key and return whether it existed."""
        if self.search(key) is None:
            return False

        for i, record in enumerate(self.records):
            if record.key == key:
                self.records.pop(i)
                return True
        return False

    def range_query(self, start, end):
        """Return active records within the key range in sorted order."""
        results = []

        for record in self.records:
            if record.expires_at is not None:
                if time.time() >= record.expires_at:
                    continue

            if start <= record.key <= end:
                results.append(record)

        results.sort(key=lambda record: record.key)
        return results

    def hset(self, key, field, value):
        """Create or update a field within a hash record."""
        record = self.search(key)

        if record is None:
            record = Record(key, None)
            self.records.append(record)

        # Find the hash field or create a new one
        hash_field = None
        for hf in record.hash_fields:
            if hf.field == field:
                hash_field = hf
                break

        if hash_field is None:
            record.hash_fields.append(HashField(field, value))
        else:
            hash_field.value = value

    def hget(self, key, field):
        """Retrieve a field value from a hash record."""
        record = self.search(key)

        if record is None:
            return None

        for hash_field in record.hash_fields:
            if hash_field.field == field:
                return hash_field.value

        return None

    def hgetall(self, key):
        """Return all fields belonging to a hash record."""
        record = self.search(key)

        if record is None:
            return []

        return record.hash_fields

    def lpush(self, key, value):
        """Insert a value at the beginning of a list."""
        record = self.search(key)
        if record is None:
            record = Record(key, None)
            self.records.append(record)

        record.list_values.insert(0, value)

    def rpush(self, key, value):
        """Append a value to the end of a list."""
        record = self.search(key)
        if record is None:
            record = Record(key, None)
            self.records.append(record)

        record.list_values.append(value)

    def lrange(self, key, start, end):
        """Retrieve list values within the specified index range."""
        record = self.search(key)

        if record is None:
            return []

        if end < 0:
            end = len(record.list_values) + end

        return record.list_values[start:end + 1]

    def flushdb(self):
        """Remove all records from the database."""
        self.records.clear()
