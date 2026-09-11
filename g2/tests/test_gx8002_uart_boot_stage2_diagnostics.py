# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_boot_stage2_diagnostics import verify, ROWS


class UartBootStage2DiagnosticsTest(unittest.TestCase):
    def test_strings_match_stock_and_pinned_upstream(self):
        result = verify()
        self.assertTrue(result['source_admitted'])
        self.assertFalse(result['hardware_qualified'])
        self.assertEqual(len(result['functions']), len(ROWS))
        total = 0
        for row, (suffix, offset, _, _) in zip(result['functions'], ROWS):
            self.assertEqual(row['ownership_kind'], 'generated_source_data')
            self.assertEqual(row['symbol'], 'open_cfw_gx8002_uart_boot_stage2_str_' + suffix)
            occurrence = row['stock_occurrences'][0]
            self.assertEqual(occurrence['package_offset'], offset)
            self.assertEqual(occurrence['sha256'], row['compiled_sha256'])
            total += occurrence['bytes']
        self.assertEqual(total, 83)

    def test_occurrences_are_disjoint_and_within_the_target_span(self):
        result = verify()
        spans = sorted((o['package_offset'], o['package_offset'] + o['bytes'])
                        for f in result['functions'] for o in f['stock_occurrences'])
        for (start, end) in spans:
            self.assertGreaterEqual(start, 0x7204)
            self.assertLessEqual(end, 0x9204)
        for (_, end), (next_start, _) in zip(spans, spans[1:]):
            self.assertLessEqual(end, next_start)


if __name__ == '__main__':
    unittest.main()
