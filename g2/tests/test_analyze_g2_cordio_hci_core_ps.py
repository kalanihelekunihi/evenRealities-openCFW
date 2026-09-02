#!/usr/bin/env python3
"""Guard the clean-room closure of Ambiq Cordio's HCI platform shim."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_hci_core_ps.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_hci_core_ps", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioHciCorePlatformAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_function_inventory_is_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["source_inventory_functions"], 20)
        self.assertEqual(module["linked_function_count"], 9)
        self.assertEqual(module["linked_function_bytes"], 360)
        self.assertEqual(module["physical_bytes"], 372)
        self.assertEqual(len(module["source_only_functions"]), 11)

    def test_iso_and_feature_abi_select_the_later_family(self) -> None:
        self.assertEqual(self.report["abi"]["le_feature_bits"], 64)
        self.assertEqual(self.report["abi"]["iso_callback_offset_in_hci_cb"], 0x18)
        self.assertEqual(self.report["abi"]["bd_addr"], 0x200714E0)
        self.assertTrue(self.report["behavior"]["iso_receive_dispatch"])
        self.assertEqual(self.report["lineage"]["r25_source_functions"], 18)
        self.assertEqual(self.report["lineage"]["r44_source_functions"], 20)

    def test_ingress_is_fail_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["direct_bl_ingress_sites"], 21)
        self.assertEqual(module["stored_entry_pointers"], 0)
        self.assertEqual(module["strict_interior_pointers"], 0)

    def test_proprietary_boundary_is_metadata_only(self) -> None:
        self.assertFalse(self.report["lineage"]["historical_generating_commit_resolved"])
        self.assertEqual(self.report["lineage"]["license"], "Arm Cordio proprietary SLA")
        production = self.report["production"]
        self.assertFalse(production["proprietary_source_copied"])
        self.assertEqual(production["public_behavior_license"], "Apache-2.0")
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(production["stock_bytes_replaced"], 360)
        self.assertEqual(production["source_owned_bytes_added"], 514)
        self.assertEqual(production["alignment_bytes_added"], 6)
        self.assertEqual(production["strict_relocations"], 13)
        self.assertEqual(production["source_only_functions_compiled"], 11)
        self.assertEqual(production["manifest_regions"], 21)
        self.assertEqual(production["flash_plan_counts"], (7006, 0, 6, 6))
        self.assertTrue(production["completed_count_underflow_hardened"])
        self.assertTrue(production["unknown_receive_type_hardened"])


if __name__ == "__main__":
    unittest.main()
