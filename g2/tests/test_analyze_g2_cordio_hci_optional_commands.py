#!/usr/bin/env python3
"""Guard the optional Ambiq Cordio HCI-command exclusions."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_hci_optional_commands.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_hci_optional_commands", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioOptionalHciCommandAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_six_optional_translation_units_are_excluded(self) -> None:
        exclusion = self.report["exclusion"]
        self.assertEqual(len(exclusion["translation_units"]), 6)
        self.assertEqual(exclusion["source_inventory_functions"], 57)
        self.assertEqual(exclusion["stock_linked_functions"], 0)
        self.assertEqual(exclusion["stock_owned_bytes"], 0)

    def test_mandatory_allocator_closure_has_no_unexplained_caller(self) -> None:
        exclusion = self.report["exclusion"]
        self.assertEqual(exclusion["mandatory_alloc_calls_in_sources"], 57)
        self.assertEqual(exclusion["stock_alloc_callers"], 45)
        self.assertEqual(exclusion["unexplained_stock_alloc_callers"], 0)
        self.assertEqual(exclusion["retained_source_markers"], 0)

    def test_proprietary_boundary_is_preserved(self) -> None:
        self.assertEqual(self.report["lineage"]["license"], "Arm Cordio proprietary SLA")
        self.assertFalse(self.report["production"]["proprietary_source_copied"])
        self.assertEqual(self.report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
