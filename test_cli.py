"""Black-box tests: run main.py using stdin in an isolated temporary directory."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MAIN = Path(__file__).resolve().parent / 'main.py'


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def run_db(self, *commands):
        result = subprocess.run(
            [sys.executable, str(MAIN)],
            input='\n'.join([*commands, 'EXIT']) + '\n',
            text=True,
            capture_output=True,
            cwd=self.temp.name,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        if lines and lines[0] == 'Simple Key-Value Store':
            lines = lines[1:]
        return lines

    def test_set_get_exists_and_missing(self):
        self.assertEqual(self.run_db('SET fruit apple', 'GET fruit', 'EXISTS fruit',
                                     'GET absent', 'EXISTS absent'),
                         ['Done', 'apple', '1', 'NULL', '0'])

    def test_delete_and_persistence(self):
        self.assertEqual(self.run_db('SET fruit apple', 'DEL fruit', 'EXISTS fruit'),
                         ['Done', '1', '0'])
        self.assertEqual(self.run_db('GET fruit'), ['NULL'])

    def test_set_persistence_and_last_write_wins(self):
        self.run_db('SET fruit apple', 'SET fruit banana')
        self.assertEqual(self.run_db('GET fruit'), ['banana'])

    def test_mset_mget_and_recovery(self):
        self.assertEqual(self.run_db('MSET a apple b banana', 'MGET a b missing'),
                         ['OK', 'apple', 'banana', 'NULL'])
        self.assertEqual(self.run_db('MGET a b'), ['apple', 'banana'])

    def test_counters_and_recovery(self):
        self.assertEqual(self.run_db('SET count 10', 'INCR count', 'DECR count'),
                         ['Done', '11', '10'])
        self.assertEqual(self.run_db('GET count'), ['10'])

    def test_invalid_counter_value(self):
        self.assertEqual(self.run_db('SET count apple', 'INCR count', 'DECR count'),
                         ['Done', 'ERROR', 'ERROR'])

    def test_hash_and_recovery(self):
        self.assertEqual(self.run_db('HSET user name Ada', 'HGET user name',
                                     'HSET user name Grace', 'HGETALL user'),
                         ['OK', 'Ada', 'OK', 'name Grace'])
        self.assertEqual(self.run_db('HGET user name'), ['Grace'])

    def test_list_and_recovery(self):
        self.assertEqual(self.run_db('RPUSH fruits apple', 'LPUSH fruits banana',
                                     'LRANGE fruits 0 -1'),
                         ['OK', 'OK', 'banana', 'apple'])
        self.assertEqual(self.run_db('LRANGE fruits 0 -1'), ['banana', 'apple'])

    def test_invalid_lrange_does_not_crash(self):
        self.assertEqual(self.run_db('LRANGE fruits abc 2', 'LRANGE fruits 0 xyz'),
                         ['ERROR', 'ERROR'])

    def test_expire_and_ttl(self):
        self.assertEqual(self.run_db('SET old apple', 'EXPIRE old -5',
                                     'EXISTS old', 'TTL old'),
                         ['Done', 'OK', '0', '-2'])
        self.assertEqual(self.run_db('GET old'), ['NULL'])

    def test_set_clears_ttl_across_restart(self):
        self.run_db('SET key apple', 'EXPIRE key 300', 'SET key banana')
        self.assertEqual(self.run_db('GET key', 'TTL key'), ['banana', '-1'])

    def test_range_sorted_and_excludes_expired(self):
        self.assertEqual(self.run_db('SET range_c cherry', 'SET range_a apple',
                                     'SET range_b banana', 'EXPIRE range_b -5',
                                     'RANGE range_a range_c'),
                         ['Done', 'Done', 'Done', 'OK', 'range_a apple', 'range_c cherry'])

    def test_abort_discards_changes(self):
        self.assertEqual(self.run_db('SET key original', 'BEGIN',
                                     'SET key changed', 'ABORT', 'GET key'),
                         ['Done', 'OK', 'Done', 'OK', 'original'])
        self.assertEqual(self.run_db('GET key'), ['original'])

    def test_commit_persists_changes(self):
        self.assertEqual(self.run_db('BEGIN', 'SET key committed', 'COMMIT', 'GET key'),
                         ['OK', 'Done', 'OK', 'committed'])
        self.assertEqual(self.run_db('GET key'), ['committed'])

    def test_flushdb_persists(self):
        self.run_db('SET key value', 'FLUSHDB')
        self.assertEqual(self.run_db('EXISTS key'), ['0'])

    def test_flushdb_abort_and_commit(self):
        self.assertEqual(self.run_db('SET key value', 'BEGIN', 'FLUSHDB',
                                     'ABORT', 'EXISTS key'),
                         ['Done', 'OK', 'OK', 'OK', '1'])
        self.assertEqual(self.run_db('BEGIN', 'FLUSHDB', 'COMMIT', 'EXISTS key'),
                         ['OK', 'OK', 'OK', '0'])
        self.assertEqual(self.run_db('EXISTS key'), ['0'])

    def test_missing_data_file_is_created(self):
        self.run_db('EXIT')
        self.assertTrue((Path(self.temp.name) / 'data.db').exists())

    def test_negative_start_beyond_list(self):
        self.assertEqual(self.run_db('RPUSH fruits apple', 'RPUSH fruits banana',
                                     'LRANGE fruits -10 -1'),
                         ['OK', 'OK', 'apple', 'banana'])


if __name__ == '__main__':
    unittest.main()
