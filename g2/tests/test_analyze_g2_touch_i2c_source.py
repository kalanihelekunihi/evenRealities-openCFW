#!/usr/bin/env python3
"""Tests for the G2 touch I2C source closure."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/analyze_g2_touch_i2c_source.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_touch_i2c_source", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TouchI2cSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.audit()

    def test_software_surface_target_compiles(self) -> None:
        self.assertEqual(self.report["software_gap_count"], 0)
        self.assertEqual(len(self.report["exports"]), 8)
        self.assertEqual(len(self.report["implemented_contracts"]), 7)
        self.assertIn("Cortex-M0+", self.report["target"])

    def test_physical_and_resident_blocks_are_separate(self) -> None:
        self.assertFalse(self.report["hardware_block"]["physical_evidence_available"])
        self.assertTrue(self.report["hardware_block"]["shipped_prefix_retained"])
        self.assertEqual(self.report["proprietary_block"]["resident_region"], "flash >=0x8680")
        self.assertEqual(len(self.report["proprietary_block"]["unavailable_inputs"]), 3)

    def test_source_pin_mutation_is_rejected(self) -> None:
        original = MODULE.PINS[MODULE.HEADER]
        try:
            MODULE.PINS[MODULE.HEADER] = (original[0], "0" * 64)
            with self.assertRaises(MODULE.AuditError):
                MODULE.audit()
        finally:
            MODULE.PINS[MODULE.HEADER] = original


if __name__ == "__main__":
    unittest.main()
