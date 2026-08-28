#!/usr/bin/env python3
"""Tests for the touch sensing source closure."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/analyze_g2_touch_sensing_source.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_touch_sensing_source", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TouchSensingSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.audit()

    def test_source_surface_and_msc_contract(self) -> None:
        self.assertEqual(self.report["software_gap_count"], 0)
        self.assertEqual(len(self.report["exports"]), 6)
        self.assertEqual(self.report["msc_contract"]["selector"], "0x06D9")
        self.assertEqual(self.report["msc_contract"]["failure_status"], 4)

    def test_all_observed_transition_labels_have_policy(self) -> None:
        self.assertEqual(self.report["implemented_policy"][:4],
                         ["ACT->ALR", "ALR->WOT", "WOT->ACT", "WOT->ALR"])
        self.assertEqual(len(self.report["implemented_policy"]), 8)

    def test_physical_validation_is_deferred(self) -> None:
        self.assertFalse(self.report["hardware_block"]["physical_evidence_available"])
        self.assertTrue(self.report["hardware_block"]["shipped_touch_application_retained"])


if __name__ == "__main__":
    unittest.main()
