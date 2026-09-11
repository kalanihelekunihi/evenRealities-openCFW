# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_analog_config_update_enable as v


class AnalogConfigUpdateEnableTests(unittest.TestCase):
    def test_qualifies_exact_byte_match_against_stock_envelope(self):
        report = v.verify()
        row = report['functions'][0]
        self.assertEqual(row['symbol'], v.SYMBOL)
        self.assertEqual(row['ownership_kind'], 'compiled_c')
        self.assertEqual(row['compiled_bytes'], v.ENVELOPE_BYTES)
        occurrence = row['stock_occurrences'][0]
        self.assertEqual(occurrence['package_offset'], v.PACKAGE_OFFSET)
        self.assertEqual(occurrence['bytes'], v.ENVELOPE_BYTES)
        self.assertEqual(occurrence['region'], 'boot_stage2')
        # The candidate is proven byte-identical, not merely equivalent.
        self.assertEqual(row['compiled_sha256'], occurrence['sha256'])
        self.assertTrue(report['source_admitted'])
        self.assertFalse(report['hardware_qualified'])


if __name__ == '__main__':
    unittest.main()
