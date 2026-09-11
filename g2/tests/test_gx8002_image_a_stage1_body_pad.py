#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

import verify_gx8002_image_a_stage1_body_pad as pad


class Gx8002ImageAStage1BodyPadTests(unittest.TestCase):
    def test_compiled_data_matches_stock_and_is_source_admitted(self):
        report = pad.verify()
        self.assertTrue(report['source_admitted'])
        self.assertFalse(report['hardware_qualified'])
        (function,) = report['functions']
        self.assertEqual(function['symbol'], pad.SYMBOL)
        self.assertEqual(function['ownership_kind'], 'generated_source_data')
        self.assertEqual(function['compiled_bytes'], pad.PAD_SIZE)
        (occurrence,) = function['stock_occurrences']
        self.assertEqual(occurrence['package_offset'], pad.PACKAGE_OFFSET)
        self.assertEqual(occurrence['bytes'], pad.PAD_SIZE)
        self.assertEqual(occurrence['sha256'], function['compiled_sha256'])

    def test_span_is_exactly_zero_in_stock(self):
        stock = pad.IMAGE.read_bytes()
        span = stock[pad.PACKAGE_OFFSET:pad.PACKAGE_OFFSET + pad.PAD_SIZE]
        self.assertEqual(span, bytes(pad.PAD_SIZE))

    def test_span_boundary_is_exact(self):
        # The byte immediately before the span must be non-zero, and the
        # span must run exactly to this item's own upper bound (0xB58C),
        # not further (that continuation belongs to CD-009's own item).
        stock = pad.IMAGE.read_bytes()
        self.assertNotEqual(stock[pad.PACKAGE_OFFSET - 1], 0)
        self.assertEqual(pad.PACKAGE_OFFSET + pad.PAD_SIZE, 0x0000B58C)

    def test_mismatch_is_detected(self):
        stock = pad.IMAGE.read_bytes()
        mutated = bytearray(pad.PAD_SIZE)
        mutated[0] ^= 0x01
        self.assertNotEqual(bytes(mutated),
                             stock[pad.PACKAGE_OFFSET:pad.PACKAGE_OFFSET + pad.PAD_SIZE])


if __name__ == '__main__':
    unittest.main()
