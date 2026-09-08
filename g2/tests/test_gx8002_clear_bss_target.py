# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_clear_bss import execute, START, END


class ClearBSSTargetTests(unittest.TestCase):
    def test_end_excluded(self):
        with self.assertRaisesRegex(ValueError, 'write outside BSS'):
            execute({0: ('lrw', f'r3, {END}', 2),
                     2: ('stbi.w', 'r1, (r3)', 4)}, 0, 0)

    def test_unaligned_write(self):
        with self.assertRaisesRegex(ValueError, 'write outside BSS'):
            execute({0: ('lrw', f'r3, {START+1}', 2),
                     2: ('st.w', 'r1, (r3, 0x0)', 4)}, 0, 0)

    def test_corrupt_preserved_register(self):
        with self.assertRaisesRegex(ValueError, 'preserved register mismatch'):
            execute({0: ('movi', 'r4, 0', 2), 2: ('rts', '', 2)}, 0, 0)

    def test_store_postincrement(self):
        code = {0: ('lrw', f'r3, {START}', 2), 2: ('movi', 'r1, 0', 2),
                4: ('stbi.w', 'r1, (r3)', 4), 8: ('stbi.w', 'r1, (r3)', 4),
                12: ('rts', '', 2)}
        self.assertEqual(execute(code, 0, 1), [[START, 0], [START+4, 0]])


if __name__ == '__main__':
    unittest.main()
