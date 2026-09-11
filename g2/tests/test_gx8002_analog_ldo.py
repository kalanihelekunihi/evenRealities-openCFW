# SPDX-License-Identifier: MIT
"""Authenticate the reviewed gx_analog_set_ldo_ana_voltage assembly against pinned stock."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from analyze_gx8002_upstream_objects import IMAGE
import verify_gx8002_analog_ldo as v


class AnalogLdoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        prefix = ROOT / 'build/csky-macos/install/bin'
        sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
        if not (prefix / 'csky-unknown-elf-gcc').exists() or not sdk.exists():
            raise unittest.SkipTest('C-SKY toolchain or pinned SDK checkout unavailable')
        cls.report = v.verify(prefix, sdk, ROOT / 'build/gx8002-analog-ldo-source')

    def test_exact_stock_equivalence(self):
        self.assertEqual(self.report['symbol'], 'gx_analog_set_ldo_ana_voltage')
        self.assertEqual(self.report['ownership_kind'], 'compiled_assembly')
        self.assertEqual(self.report['compiled_bytes'], 32)
        self.assertEqual(self.report['differential_cases'], 144)

    def test_covers_both_stock_occurrences(self):
        occurrences = self.report['stock_occurrences']
        self.assertEqual(len(occurrences), 2)
        regions = {row['region'] for row in occurrences}
        self.assertEqual(regions, {'boot_stage2', 'image_a_sram_text'})
        self.assertTrue(any(row['package_offset'] == 17496 for row in occurrences))

    def test_sentinel_leaves_register_untouched(self):
        code = [('movi', 'r3, 0'), ('subi', 'r3, 1'), ('cmpne', 'r0, r3'), ('bf', '0x99')]
        result, trace = v.execute(code, 0xffffffff, 0x5a)
        self.assertEqual(result, 0xffffffff)
        self.assertEqual(trace, [])


class AnalogLdoFailClosedTests(unittest.TestCase):
    def test_unknown_instruction_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsupported LDO instruction'):
            v.execute([('jsr', 'r3'), ('rts', '')], 0, 0)

    def test_unexpected_address_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unexpected LDO read address'):
            v.execute([('lrw', 'r2, 0xa0000000'), ('ld.w', 'r3, (r2, 0x54)')], 0, 0)

    def test_missing_return_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'did not return'):
            v.execute([('movi', 'r0, 0')], 1, 2)


if __name__ == '__main__':
    unittest.main()
