import unittest
from index import Index

class TestIndex(unittest.TestCase):
    def setUp(self):
        self.index = Index()

    def test_set_and_get(self):
        self.index.set("fruit", "apple")

        record = self.index.search("fruit")

        self.assertIsNotNone(record)
        self.assertEqual(record.value, "apple")

    def test_delete(self):
        self.index.set("fruit", "apple")
        result = self.index.delete("fruit")
        self.assertTrue(result)

        record = self.index.search("fruit")
        self.assertIsNone(record)

    def test_update_existing_key(self):
        self.index.set("fruit", "apple")
        self.index.set("fruit", "banana")

        record = self.index.search("fruit")

        self.assertEqual(record.value, "banana")
        self.assertEqual(len(self.index.records), 1)

    def test_delete_nonexistent_key(self):
        result = self.index.delete("missing_key")

        self.assertFalse(result)