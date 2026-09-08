# SPDX-License-Identifier: MIT
"""Fail-closed checks for restricted target instruction comparison."""
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
from verify_gx8002_analog_source import execute


class TargetTraceTests(unittest.TestCase):
    def test_unknown_instruction_does_not_silently_pass(self):
        with self.assertRaisesRegex(ValueError, 'unsupported executable instruction'):
            execute([('jsr', 'r3'), ('rts', '')], 0, 0)

    def test_unknown_mmio_address_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'out-of-scope register address'):
            execute([('lrw', 'r2, 0xa0000000'), ('ld.w', 'r3, (r2, 0x8)')], 0, 0)

    def test_masking_variants_agree_only_after_byte_narrowing(self):
        prefix = [('lrw', 'r2, 0xa0005080'), ('ld.w', 'r3, (r2, 0x8)')]
        suffix = [('zextb', 'r3, r3'), ('st.w', 'r3, (r2, 0x8)'), ('movi', 'r0, 0'), ('rts', '')]
        old = prefix + [('andi', 'r3, r3, 191')]
        new = prefix + [('andni', 'r3, r3, 64')]
        self.assertEqual(execute(old + suffix, 0, 0xdeadbeef), execute(new + suffix, 0, 0xdeadbeef))
        self.assertNotEqual(execute(old + suffix[1:], 0, 0xdeadbeef), execute(new + suffix[1:], 0, 0xdeadbeef))

    def test_missing_return_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'did not return'):
            execute([('movi', 'r0, 0')], 1, 2)


if __name__ == '__main__':
    unittest.main()
