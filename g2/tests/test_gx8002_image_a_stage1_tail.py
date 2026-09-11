#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from analyze_g2_codec_fwpk_segments import crc32_mpeg2
import verify_gx8002_image_a_stage1_tail as tail


class Gx8002ImageAStage1TailTests(unittest.TestCase):
    def test_compiled_data_matches_stock_and_is_source_admitted(self):
        report = tail.verify()
        self.assertTrue(report["source_admitted"])
        self.assertFalse(report["hardware_qualified"])
        (function,) = report["functions"]
        self.assertEqual(function["symbol"], "open_cfw_gx8002_image_a_stage1_tail")
        self.assertEqual(function["ownership_kind"], "generated_source_data")
        self.assertEqual(function["compiled_bytes"], tail.TAIL_SIZE)
        (occurrence,) = function["stock_occurrences"]
        self.assertEqual(occurrence["package_offset"], tail.PACKAGE_OFFSET)
        self.assertEqual(occurrence["bytes"], tail.TAIL_SIZE)
        self.assertEqual(occurrence["sha256"], function["compiled_sha256"])

    def test_zero_fill_span_is_exactly_zero_in_stock(self):
        stock = tail.IMAGE.read_bytes()
        span = stock[tail.PACKAGE_OFFSET:tail.PACKAGE_OFFSET + tail.ZERO_SIZE]
        self.assertEqual(span, bytes(tail.ZERO_SIZE))

    def test_trailer_is_independently_reproducible_via_public_crc(self):
        # Recompute the CRC-32/MPEG-2 trailer a second, independent way: run
        # the same algorithm directly over the raw stage-1 block bytes
        # (header + code + this file's own zero-fill), rather than trusting
        # analyze_g2_codec_fwpk_segments.parse_main_image's cached result.
        stock = tail.IMAGE.read_bytes()
        block = stock[0x0000958C:0x0000C58C]
        stored = int.from_bytes(block[-4:], "little")
        recomputed = crc32_mpeg2(block[24:len(block) - 4])
        self.assertEqual(recomputed, stored)
        expected, _ = tail._expected_bytes(stock)
        self.assertEqual(int.from_bytes(expected[tail.ZERO_SIZE:tail.ZERO_SIZE + 4], "little"), stored)

    def test_mismatch_is_detected(self):
        stock = tail.IMAGE.read_bytes()
        expected, _ = tail._expected_bytes(stock)
        mutated = bytearray(expected)
        mutated[0] ^= 0x01
        self.assertNotEqual(bytes(mutated),
                             stock[tail.PACKAGE_OFFSET:tail.PACKAGE_OFFSET + tail.TAIL_SIZE])


if __name__ == "__main__":
    unittest.main()
