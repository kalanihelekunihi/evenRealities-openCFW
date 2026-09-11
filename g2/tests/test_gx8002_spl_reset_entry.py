#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import verify_gx8002_spl_reset_entry as spl
from verify_gx8002_memcpy_source import decode


class Gx8002SplResetEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = spl.verify()
        cls.code = decode(Path(spl.build()['disassembly_path']).read_text())

    def test_report_admits_two_functions_byte_exact_against_stock(self):
        self.assertTrue(self.report['source_admitted'])
        self.assertFalse(self.report['hardware_qualified'])
        header, entry = self.report['functions']
        self.assertEqual(header['symbol'], spl.HEADER_SYMBOL)
        self.assertEqual(header['ownership_kind'], 'generated_source_data')
        self.assertEqual(header['compiled_bytes'], spl.HEADER_SIZE)
        self.assertEqual(entry['symbol'], spl.ENTRY_SYMBOL)
        self.assertEqual(entry['ownership_kind'], 'compiled_assembly')
        self.assertEqual(entry['compiled_bytes'], spl.ENTRY_SIZE)
        for function in self.report['functions']:
            (occurrence,) = function['stock_occurrences']
            self.assertEqual(occurrence['sha256'], function['compiled_sha256'])

    def test_header_package_offset_immediately_precedes_entry(self):
        header, entry = self.report['functions']
        (header_occ,) = header['stock_occurrences']
        (entry_occ,) = entry['stock_occurrences']
        self.assertEqual(header_occ['package_offset'] + header_occ['bytes'],
                          entry_occ['package_offset'])

    def test_vector_table_targets_this_build_own_functions(self):
        stock = spl.IMAGE.read_bytes()
        header = stock[spl.HEADER_PACKAGE_OFFSET:spl.HEADER_PACKAGE_OFFSET + spl.HEADER_SIZE]
        vectors = header[24:]
        reset_vector = int.from_bytes(vectors[0:4], 'little')
        trap_vectors = {int.from_bytes(vectors[i:i + 4], 'little') for i in range(4, 256, 4)}
        self.assertEqual(reset_vector, spl.ENTRY_ADDRESS)
        self.assertEqual(trap_vectors, {spl.DEFAULT_HANDLER_ADDRESS})

    def test_wrong_control_source_rejected(self):
        code = self.code.copy()
        code[0x10000106] = ('mfcr', 'r1, cr<30, 0>', 4)
        with self.assertRaisesRegex(ValueError, 'unexpected control source'):
            spl.execute(code, 0, 0)

    def test_unknown_call_target_rejected(self):
        code = self.code.copy()
        code[0x1000011a] = ('bsr', '0x10020000', 4)
        with self.assertRaisesRegex(ValueError, 'unexpected call target'):
            spl.execute(code, 0, 0)

    def test_control_bit_clear_effect_is_checked(self):
        code = self.code.copy()
        code[0x1000010a] = ('nop16', '', 2)
        with self.assertRaisesRegex(ValueError, 'unexpected instruction'):
            spl.execute(code, 0, 0)

    def test_mutated_header_is_detected(self):
        stock = spl.IMAGE.read_bytes()
        expected = spl.expected_header_and_vectors(stock)
        mutated = bytearray(expected)
        mutated[0] ^= 0x01
        self.assertNotEqual(bytes(mutated),
                             stock[spl.HEADER_PACKAGE_OFFSET:spl.HEADER_PACKAGE_OFFSET + spl.HEADER_SIZE])


if __name__ == '__main__':
    unittest.main()
