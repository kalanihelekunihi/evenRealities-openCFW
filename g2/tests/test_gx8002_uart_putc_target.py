# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from compare_gx8002_uart_putc import execute, register_list


class UartPutcTargetTests(unittest.TestCase):
    def test_call_clobbers_arguments_but_save_preserves_character(self):
        code = {0: ('push', 'r4, r15', 2), 2: ('mov', 'r4, r1', 2),
                4: ('bsr', '0x100', 4), 8: ('zextb', 'r1, r4', 2),
                10: ('movi', 'r0, 8192', 2), 12: ('bsr', '0x100', 4),
                16: ('pop', 'r4, r15', 2)}
        self.assertEqual(execute(code, 0, 256, 7, 266), [(7, 266), (8192, 10)])

    def test_unbalanced_save_and_wrong_target_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unbalanced save'):
            execute({0: ('push', 'r4, r15', 2), 2: ('pop', 'r5, r15', 2)}, 0, 256, 0, 0)
        with self.assertRaisesRegex(ValueError, 'unexpected transmit target'):
            execute({0: ('bsr', '0x102', 4)}, 0, 256, 0, 0)

    def test_register_range(self):
        self.assertEqual(register_list('r4-r6, r15'), ['r4', 'r5', 'r6', 'r15'])


if __name__ == '__main__':
    unittest.main()
