# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from verify_gx8002_icache_source import execute


class CacheTraceTests(unittest.TestCase):
    def test_unknown_instruction_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsupported instruction'):
            execute({0: (2, 'jsr', 'r0')}, 0, [2])

    def test_polling_is_distinct_from_return(self):
        code = {0: (2, 'movi', 'r1, 176'), 2: (2, 'lsli', 'r1, r1, 24'),
                4: (2, 'ld.w', 'r2, (r1, 0x4)'), 6: (2, 'cmpnei', 'r2, 2'),
                8: (2, 'bt', '0x4'), 10: (2, 'rts', '')}
        self.assertEqual(execute(code, 0, [0, 0])[0], 'polling')
        self.assertEqual(execute(code, 0, [0, 2])[0], 'returned')

    def test_unbounded_branch_is_stopped_by_execution_limit(self):
        code = {0: (2, 'movi', 'r0, 1'), 2: (2, 'cmpnei', 'r0, 0'), 4: (2, 'bt', '0x4')}
        with self.assertRaisesRegex(ValueError, 'execution bound exceeded'):
            execute(code, 0, [2], limit=10)


if __name__ == '__main__':
    unittest.main()
