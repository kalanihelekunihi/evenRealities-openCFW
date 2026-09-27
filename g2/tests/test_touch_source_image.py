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
        self.assertEqual(stack, MODULE.board_config_u32("OPEN_CFW_TOUCH_STACK_TOP"))
        self.assertEqual(reset & 1, 1)
        flash_base = MODULE.board_config_u32("OPEN_CFW_TOUCH_FLASH_BASE")
        self.assertGreaterEqual(reset & ~1, flash_base)
        self.assertLess(reset & ~1, flash_base + len(raw))
        self.assertLessEqual(
            len(raw), MODULE.board_config_u32("OPEN_CFW_TOUCH_FLASH_BYTES"))
        self.assertEqual(struct.unpack_from("<I", raw, len(raw) - 4)[0],
                         MODULE.crc32c(raw[:-4]))

    def test_fwpk_is_self_consistent(self) -> None:
        package = (self.output / "firmware_touch.bin").read_bytes()
        self.assertEqual(struct.unpack_from("<I", package)[0],
                         MODULE.board_config_u32("OPEN_CFW_TOUCH_FWPK_MAGIC"))
        self.assertEqual(struct.unpack_from("<I", package, 4)[0],
                         MODULE.board_config_u32("OPEN_CFW_TOUCH_FWPK_VERSION"))
        record_type, size, offset, checksum = struct.unpack_from(
            "<IIII", package, 16)
        self.assertEqual(
            (record_type, offset),
            (MODULE.board_config_u32("OPEN_CFW_TOUCH_FWPK_RECORD_TYPE"),
             MODULE.board_config_u32("OPEN_CFW_TOUCH_FWPK_PAYLOAD_OFFSET")))
        self.assertEqual(offset + size, len(package))
        self.assertEqual(MODULE.crc32c(package[offset:]), checksum)

    def test_board_contract_is_named_and_inventoried(self) -> None:
        summary = json.loads((self.output /
            "touch-source-image-summary.json").read_text())
        self.assertIn("components/touch/source_image/board_config.h", {
            row["path"] for row in summary["source_inventory"]})
        self.assertEqual(
            summary["board_contract"]["blocked_contracts"],
            [
                "SCB1_I2C_SHIFT_REGISTER_SERVICE",
                "MSCLP_CAPSENSE_SCAN_RESULT_DRAIN",
                "SPCIF_FLASH_SROM_ROW_PROGRAMMING",
                "GPIO_PIN_AND_ATTENTION_LINE_ROUTING",
                "RESIDENT_DFU_MAILBOX_RESET_HANDOFF",
            ])

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
