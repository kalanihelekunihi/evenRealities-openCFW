# SPDX-License-Identifier: MIT
"""Authenticate the reviewed gx_dcache_disable assembly against pinned stock."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from analyze_gx8002_upstream_objects import IMAGE
import verify_gx8002_dcache_disable as v


class DcacheDisableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        prefix = ROOT / 'build/csky-macos/install/bin'
        sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
        if not (prefix / 'csky-unknown-elf-gcc').exists() or not sdk.exists():
            raise unittest.SkipTest('C-SKY toolchain or pinned SDK checkout unavailable')
        cls.report = v.verify(prefix, sdk, ROOT / 'build/gx8002-dcache-disable-source')

    def test_exact_stock_equivalence(self):
        self.assertEqual(self.report['symbol'], 'gx_dcache_disable')
        self.assertEqual(self.report['ownership_kind'], 'compiled_assembly')
        self.assertEqual(self.report['compiled_bytes'], 36)

    def test_covers_all_three_stock_occurrences(self):
        occurrences = self.report['stock_occurrences']
        self.assertEqual(len(occurrences), 3)
        regions = {row['region'] for row in occurrences}
        self.assertEqual(regions, {'boot_stage2', 'image_a_sram_text', 'image_b_sram_text'})
        self.assertTrue(any(row['package_offset'] == 12804 for row in occurrences))

    def test_no_relocations_or_undefined_symbols(self):
        # verify() already raises if this is violated; re-running should stay stable.
        second = v.verify(ROOT / 'build/csky-macos/install/bin',
                           ROOT / 'build/upstream-nationalchip-lvp-kws',
                           ROOT / 'build/gx8002-dcache-disable-source')
        self.assertEqual(second, self.report)


if __name__ == '__main__':
    unittest.main()
