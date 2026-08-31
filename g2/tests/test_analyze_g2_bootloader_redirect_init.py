#!/usr/bin/env python3
"""Tests for the G2 bootloader redirect-init source closure."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/analyze_g2_bootloader_redirect_init.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_bootloader_redirect_init", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class BootloaderRedirectInitAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.audit()

    def test_software_closure_is_reproducible(self) -> None:
        self.assertEqual(self.report["software_gap_count"], 0)
        self.assertEqual(self.report["stock"]["size"], 88)
        self.assertEqual(self.report["source"]["text_bytes"], 132)
        self.assertEqual(self.report["source"]["closure_bytes"], 275)
        self.assertEqual(
            self.report["provider"]["source_owned_bytes"]
            + self.report["provider"]["retained_official_bytes"],
            147_350,
        )
        self.assertGreater(self.report["deployment"]["apple_package"]["size"], 0)
        self.assertGreater(self.report["deployment"]["linux_package"]["size"], 0)
        self.assertEqual(self.report["deployment"]["unresolved_flash_regions"], 0)

    def test_hardware_validation_remains_explicitly_blocked(self) -> None:
        self.assertEqual(self.report["status"], "implemented-in-source / hardware-validation-blocked-by-unavailable-physical-evidence")
        self.assertFalse(self.report["hardware_block"]["physical_evidence_available"])
        self.assertTrue(self.report["hardware_block"]["stock_bootloader_retained_for_hardware"])
        self.assertEqual(
            self.report["hardware_block"]["required_evidence"],
            "authorized G2 hardware with boot UART and debugger visibility "
            "validating both mutex allocations, IAR stream serialization, "
            "failure logging, and boot continuation",
        )
        self.assertEqual(self.report["safety"]["hardware_operations"], [])

    def test_source_pin_mutation_is_rejected(self) -> None:
        original = MODULE.PINS[MODULE.SOURCE]
        try:
            MODULE.PINS[MODULE.SOURCE] = (original[0], "0" * 64)
            with self.assertRaises(MODULE.AuditError):
                MODULE.audit()
        finally:
            MODULE.PINS[MODULE.SOURCE] = original


if __name__ == "__main__":
    unittest.main()
