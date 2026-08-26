#!/usr/bin/env python3
"""Guard the clean-room closure of Ambiq Cordio's stock HCI core port."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_hci_core.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_hci_core", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioHciCoreAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_complete_function_inventory_is_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["source_inventory_functions"], 24)
        self.assertEqual(module["linked_function_count"], 22)
        self.assertEqual(module["linked_function_bytes"], 1_964)
        self.assertEqual(module["physical_bytes"], 1_980)
        self.assertEqual(module["source_only_functions"], [
            "hciCoreTxAclDataFragmented", "HciSetAclQueueWatermarks",
        ])

    def test_r44_era_abi_is_exact(self) -> None:
        abi = self.report["abi"]
        self.assertEqual(abi["hci_core_cb"], 0x20071478)
        self.assertEqual(abi["hci_cb"], 0x20073870)
        self.assertEqual(abi["hci_le_sup_feat_cfg"], 0x20000028)
        self.assertEqual(abi["hci_core_cis"], 0x200714CC)
        self.assertEqual(abi["connection_records"], 3)
        self.assertEqual(abi["cis_records"], 6)
        self.assertEqual(abi["le_feature_bits"], 64)

    def test_ingress_is_fail_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["direct_bl_ingress_sites"], 32)
        self.assertEqual(module["stored_entry_pointers"], 0)
        self.assertEqual(module["strict_interior_pointers"], 0)

    def test_proprietary_source_family_is_not_overclaimed(self) -> None:
        lineage = self.report["lineage"]
        self.assertFalse(lineage["historical_generating_commit_resolved"])
        self.assertFalse(lineage["whole_file_source_exact"])
        self.assertTrue(lineage["stock_excludes_r44_neuralspot_delay"])
        self.assertTrue(lineage["stock_excludes_nsx_priority_trace_path"])
        self.assertEqual(lineage["license"], "Arm Cordio proprietary SLA")
        self.assertEqual(lineage["public_behavior_license"], "Apache-2.0")
        production = self.report["production"]
        self.assertFalse(production["proprietary_source_copied"])
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(production["stock_bytes_replaced"], 1_964)
        self.assertEqual(production["source_owned_bytes_added"], 3_690)
        self.assertEqual(production["alignment_bytes_added"], 26)
        self.assertEqual(production["strict_relocations"], 50)
        self.assertEqual(production["source_only_functions_compiled"], 2)
        self.assertEqual(production["manifest_regions"], 57)
        self.assertEqual(production["flash_plan_counts"], (5_864, 2, 5, 6))
        self.assertTrue(production["transport_rejection_preserves_fragment"])
        self.assertTrue(production["partial_l2cap_header_hardened"])
        self.assertTrue(production["overlong_continuation_hardened"])
        self.assertTrue(production["watermark_validation_hardened"])


if __name__ == "__main__":
    unittest.main()
