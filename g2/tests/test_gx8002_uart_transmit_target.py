# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compare_gx8002_uart_transmit import execute


class UartTransmitTargetTests(unittest.TestCase):
    def setUp(self):
        self.code = {0: ('ld.w', 'r2, (r0, 0x4)', 2),
                     2: ('ld.w', 'r3, (r2, 0x14)', 2),
                     4: ('andi', 'r3, r3, 32', 4),
                     8: ('bez', 'r3, 0x2', 4),
                     12: ('st.w', 'r1, (r2, 0x0)', 2),
                     14: ('rts', '', 2)}

    def test_wait_and_full_word_write(self):
        state, trace = execute(self.code, 0, 0x1000, 0xa0000000, 0xffffffff, [31, 32])
        self.assertEqual(state, 'returned')
        self.assertEqual(trace, [('read', 0x1004, 4, 0xa0000000),
                                 ('read', 0xa0000014, 4, 31),
                                 ('read', 0xa0000014, 4, 32),
                                 ('write', 0xa0000000, 4, 0xffffffff)])

    def test_finite_never_ready_prefix_has_no_write(self):
        state, trace = execute(self.code, 0, 0x1000, 0xa0000000, 10, [0, 31])
        self.assertEqual(state, 'waiting')
        self.assertEqual(len(trace), 3)
        self.assertTrue(all(row[0] == 'read' for row in trace))

    def test_reject_unknown_instruction_and_wrong_mmio(self):
        with self.assertRaisesRegex(ValueError, 'unsupported instruction'):
            execute({0: ('ld.b', 'r0, (r0, 0x4)', 2)}, 0, 0x1000, 0xa0000000, 0, [32])
        self.code[12] = ('st.w', 'r1, (r2, 0x4)', 2)
        with self.assertRaisesRegex(ValueError, 'unexpected write address'):
            execute(self.code, 0, 0x1000, 0xa0000000, 0, [32])


if __name__ == '__main__':
    unittest.main()
