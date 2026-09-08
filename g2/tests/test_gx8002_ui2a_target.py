# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compare_gx8002_ui2a import execute


class IntegerTargetTests(unittest.TestCase):
    def test_word_pointer_and_postincrement_byte_writes(self):
        code = {0: ('ld.w', 'r2, (r1, 0xc)', 2), 2: ('movi', 'r3, 321', 2),
                4: ('stbi.b', 'r3, (r2)', 4), 8: ('movi', 'r3, 0', 2),
                10: ('st.b', 'r3, (r2, 0x0)', 2), 12: ('rts', '', 2)}
        output, writes = execute(code, 0, 0, 10, 0)
        self.assertEqual(output, b'A\0' + b'\xa5'*38)
        self.assertEqual(writes, [(0x2000, 65), (0x2001, 0)])

    def test_unsigned_division_and_signed_compare(self):
        code = {0: ('movi', 'r3, 2', 2), 2: ('divu', 'r2, r0, r3', 4),
                6: ('cmplti', 'r0, 0', 4), 10: ('bt', '0x10', 2),
                12: ('unknown', '', 4), 16: ('rts', '', 2)}
        execute(code, 0, 0xffffffff, 10, 0)
        code[0] = ('movi', 'r3, 0', 2)
        with self.assertRaisesRegex(ValueError, 'division by zero'):
            execute(code, 0, 0xffffffff, 10, 0)

    def test_unknown_instruction_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsupported instruction'):
            execute({0: ('unknown', '', 2)}, 0, 0, 10, 0)


if __name__ == '__main__': unittest.main()
