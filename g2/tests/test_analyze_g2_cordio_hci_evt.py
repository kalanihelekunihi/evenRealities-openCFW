#!/usr/bin/env python3
"""Guard the clean-room closure of Ambiq Cordio's stock HCI event port."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_hci_evt.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_hci_evt", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioHciEventAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_complete_function_inventory_is_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["source_inventory_functions"], 80)
        self.assertEqual(module["linked_function_count"], 79)
        self.assertEqual(module["linked_function_bytes"], 6_718)
        self.assertEqual(module["physical_bytes"], 6_816)
        self.assertEqual(module["source_only_functions"], ["hciEvtGetStats"])

    def test_parser_and_callback_length_tables_match_r44(self) -> None:
        tables = self.report["tables"]
        self.assertEqual(tables["parse_entries"], 85)
        self.assertEqual(tables["parse_nonnull_entries"], 74)
        self.assertEqual(tables["callback_length_entries"], 85)
        self.assertEqual(self.report["module"]["unique_registered_parsers"], 69)
        self.assertEqual(self.report["lineage"]["r25_parse_entries"], 67)

    def test_ingress_and_global_ownership_are_fail_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["direct_bl_ingress_sites"], 10)
        self.assertEqual(module["registered_parser_pointer_cells"], 74)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(self.report["abi"]["hci_cb"], 0x20073870)
        self.assertEqual(self.report["abi"]["hci_evt_stats"], 0x20073BC0)
        self.assertEqual(self.report["abi"]["hci_evt_stats_references"], 1)

    def test_proprietary_oracle_is_metadata_only(self) -> None:
        lineage = self.report["lineage"]
        self.assertEqual(lineage["stock_parse_entries"], 85)
        self.assertFalse(lineage["historical_generating_commit_resolved"])
        self.assertEqual(lineage["license"], "Arm Cordio proprietary SLA")
        production = self.report["production"]
        self.assertFalse(production["proprietary_source_copied"])
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(production["redirected_stock_functions"], 79)
        self.assertEqual(production["redirected_stock_bytes"], 6_718)
        self.assertEqual(production["source_owned_bytes_added"], 23_590)
        self.assertEqual(production["alignment_bytes_added"], 30)
        self.assertEqual(production["strict_relocations"], 52)
        self.assertEqual(production["source_only_functions_compiled"], 1)
        self.assertEqual(production["manifest_regions"], 161)
        self.assertEqual(production["flash_plan_counts"], (7_006, 0, 6, 6))
        self.assertEqual(production["remaining_unrouted_linked_functions"], 0)
        self.assertEqual(production["remaining_source_only_functions"], 0)
        self.assertTrue(production["full_event_layer_complete"])


if __name__ == "__main__":
    unittest.main()
