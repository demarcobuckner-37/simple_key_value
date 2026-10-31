import time
import unittest

from index import Index


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.index = Index()

    def test_set_and_get(self):
        self.index.set('fruit', 'apple')
        record = self.index.search('fruit')
        self.assertIsNotNone(record)
        self.assertEqual(record.value, 'apple')

    def test_delete(self):
        self.index.set('fruit', 'apple')
        self.assertTrue(self.index.delete('fruit'))
        self.assertIsNone(self.index.search('fruit'))

    def test_update_existing_key(self):
        self.index.set('fruit', 'apple')
        self.index.set('fruit', 'banana')
        self.assertEqual(self.index.search('fruit').value, 'banana')
        self.assertEqual(len(self.index.records), 1)

    def test_delete_nonexistent_key(self):
        self.assertFalse(self.index.delete('missing_key'))

    def test_expired_key_is_not_found(self):
        self.index.set('old', 'value')
        self.index.search('old').expires_at = time.time() - 1
        self.assertIsNone(self.index.search('old'))

    def test_delete_expired_key(self):
        self.index.set('old', 'value')
        self.index.search('old').expires_at = time.time() - 1
        self.assertFalse(self.index.delete('old'))

    def test_set_clears_expiration(self):
        self.index.set('key', 'old')
        self.index.search('key').expires_at = time.time() + 100
        self.index.set('key', 'new')
        self.assertEqual(self.index.search('key').value, 'new')
        self.assertIsNone(self.index.search('key').expires_at)

    def test_reuse_expired_key(self):
        self.index.set('key', 'old')
        self.index.search('key').expires_at = time.time() - 1
        self.index.set('key', 'new')
        self.assertEqual(self.index.search('key').value, 'new')

    def test_range_sorted_and_inclusive(self):
        for key in ('c', 'a', 'b'):
            self.index.set(key, key.upper())
        self.assertEqual([r.key for r in self.index.range_query('a', 'c')], ['a', 'b', 'c'])

    def test_range_excludes_expired(self):
        self.index.set('a', 'one')
        self.index.set('b', 'two')
        self.index.search('b').expires_at = time.time() - 1
        self.assertEqual([r.key for r in self.index.range_query('a', 'z')], ['a'])

    def test_range_no_matches(self):
        self.assertEqual(self.index.range_query('x', 'z'), [])

    def test_hash_create_update_and_read(self):
        self.index.hset('profile', 'name', 'Ada')
        self.index.hset('profile', 'name', 'Grace')
        self.index.hset('profile', 'city', 'Dallas')
        self.assertEqual(self.index.hget('profile', 'name'), 'Grace')
        self.assertEqual([(f.field, f.value) for f in self.index.hgetall('profile')],
                         [('name', 'Grace'), ('city', 'Dallas')])

    def test_hash_missing(self):
        self.assertIsNone(self.index.hget('missing', 'field'))
        self.assertEqual(self.index.hgetall('missing'), [])

    def test_list_pushes(self):
        self.index.rpush('fruits', 'apple')
        self.index.rpush('fruits', 'banana')
        self.index.lpush('fruits', 'orange')
        self.assertEqual(self.index.lrange('fruits', 0, -1),
                         ['orange', 'apple', 'banana'])

    def test_list_partial_and_out_of_bounds(self):
        for item in ('a', 'b', 'c'):
            self.index.rpush('list', item)
        self.assertEqual(self.index.lrange('list', 1, 2), ['b', 'c'])
        self.assertEqual(self.index.lrange('list', 0, 100), ['a', 'b', 'c'])
        self.assertEqual(self.index.lrange('list', 0, -10), [])
        self.assertEqual(self.index.lrange('list', -2, -1), ['b', 'c'])

    def test_missing_list(self):
        self.assertEqual(self.index.lrange('missing', 0, -1), [])

    def test_flushdb(self):
        self.index.set('one', '1')
        self.index.hset('two', 'field', 'value')
        self.index.rpush('three', 'item')
        self.index.flushdb()
        self.assertEqual(len(self.index.records), 0)
        self.assertIsNone(self.index.search('one'))

    def test_negative_start_beyond_list_is_empty(self):
        # Redis-style LRANGE: a start far before the list is clamped to zero.
        self.index.rpush('list', 'a')
        self.index.rpush('list', 'b')
        self.assertEqual(self.index.lrange('list', -10, -1), ['a', 'b'])


if __name__ == '__main__':
    unittest.main()