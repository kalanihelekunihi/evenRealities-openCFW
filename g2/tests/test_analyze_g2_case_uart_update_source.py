#!/usr/bin/env python3
"""Tests for the charging-case UART/update source closure."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/analyze_g2_case_uart_update_source.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_case_uart_update_source", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CaseUartUpdateSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.audit()

    def test_software_surface_is_complete_and_target_compiled(self) -> None:
        self.assertEqual(self.report["software_gap_count"], 0)
        self.assertEqual(len(self.report["exports"]), 8)
        self.assertIn("Cortex-M0+", self.report["target"])
        self.assertEqual(len(self.report["implemented_contracts"]), 7)

    def test_destructive_hardware_tail_is_explicit(self) -> None:
        self.assertEqual(self.report["status"], "implemented-in-source / hardware-validation-blocked")
        self.assertFalse(self.report["hardware_block"]["physical_evidence_available"])
        self.assertTrue(self.report["hardware_block"]["stock_case_payload_retained"])
        self.assertEqual(len(self.report["hardware_block"]["preserved_windows"]), 4)

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
