# SPDX-License-Identifier: MIT
"""Aggregate link/package gate for the source-built Touch image."""

from __future__ import annotations

import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "components/touch/source_image/build_image.py"
SPEC = importlib.util.spec_from_file_location("touch_source_image", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TouchSourceImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="g2-touch-image-test-")
        cls.output = Path(cls.temp.name)
        cls.report = MODULE.build(cls.output)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_every_touch_unit_links_without_undefined_symbols(self) -> None:
        expected = (len(list(MODULE.SHARED.glob("*.c"))) +
                    len(list(MODULE.SHARED.glob("*.S"))) +
                    len(list(MODULE.COMPONENT.glob("*.c"))))
        self.assertEqual(self.report["source_translation_units"], expected)
        self.assertEqual(self.report["undefined_symbols"], 0)
        self.assertTrue(self.report["software_link_complete"])
        self.assertTrue((self.output / "touch-source.elf").is_file())

    def test_raw_image_has_valid_vectors_and_trailing_crc(self) -> None:
        raw = (self.output / "touch-source.bin").read_bytes()
        stack, reset = struct.unpack_from("<II", raw)
        self.assertEqual(stack, 0x20002000)
        self.assertEqual(reset & 1, 1)
        self.assertLess(reset & ~1, len(raw))
        self.assertLessEqual(len(raw), 65536)
        self.assertEqual(struct.unpack_from("<I", raw, len(raw) - 4)[0],
                         MODULE.crc32c(raw[:-4]))

    def test_fwpk_is_self_consistent(self) -> None:
        package = (self.output / "firmware_touch.bin").read_bytes()
        self.assertEqual(package[:4], b"FWPK")
        self.assertEqual(package[4:8], bytes.fromhex("01000202"))
        record_type, size, offset, checksum = struct.unpack_from(
            "<IIII", package, 16)
        self.assertEqual((record_type, offset), (3, 0x20))
        self.assertEqual(offset + size, len(package))
        self.assertEqual(MODULE.crc32c(package[offset:]), checksum)

    def test_hardware_lock_is_fail_closed_and_explicit(self) -> None:
        summary = json.loads((self.output /
            "touch-source-image-summary.json").read_text())
        self.assertFalse(summary["production_routed"])
        self.assertEqual(summary["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(summary["hardware_blocker"],
                         "blocked by unavailable physical evidence")


if __name__ == "__main__":
    unittest.main()
