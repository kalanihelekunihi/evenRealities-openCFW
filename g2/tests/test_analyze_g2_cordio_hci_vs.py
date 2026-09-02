#!/usr/bin/env python3
"""Guard the clean-room Apollo3 HCI vendor/reset-sequence closure."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_hci_vs.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_hci_vs", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioHciVendorSequenceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_complete_source_inventory_is_classified(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["source_inventory_functions"], 8)
        self.assertEqual(module["linked_function_count"], 4)
        self.assertEqual(module["linked_function_bytes"], 546)
        self.assertEqual(module["physical_bytes"], 584)
        self.assertEqual(len(module["source_only_functions"]), 4)

    def test_reset_vendor_chain_is_exact(self) -> None:
        sequence = self.report["reset_sequence"]
        self.assertTrue(sequence["start_sends_reset"])
        self.assertTrue(sequence["start_updates_bd_address"])
        self.assertTrue(sequence["reset_completion_sends_nvds_update"])
        self.assertTrue(sequence["nvds_completion_sets_rf_power"])
        self.assertTrue(sequence["rf_power_completion_sets_event_mask"])
        self.assertEqual(sequence["nvds_opcode"], 0xFFF2)
        self.assertEqual(sequence["rf_power_opcode"], 0xFCC4)
        self.assertTrue(sequence["four_rand_completions_finish_reset"])

    def test_ingress_and_state_are_fail_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["direct_bl_ingress_sites"], 5)
        self.assertEqual(module["direct_provider_calls"], 25)
        self.assertEqual(module["stored_entry_pointers"], 0)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(self.report["abi"]["feature_width_bits"], 64)
        self.assertEqual(self.report["abi"]["default_tx_power_parameter"], 6)

    def test_hybrid_lineage_is_not_overclaimed(self) -> None:
        lineage = self.report["lineage"]
        self.assertEqual(lineage["classification"], "product hybrid Apollo3/Cooper reset sequence")
        self.assertFalse(lineage["whole_file_source_exact"])
        self.assertFalse(lineage["historical_generating_commit_resolved"])
        production = self.report["production"]
        self.assertFalse(production["vendor_source_copied"])
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(production["stock_bytes_replaced"], 546)
        self.assertEqual(production["source_owned_bytes_added"], 862)
        self.assertEqual(production["alignment_bytes_added"], 6)
        self.assertEqual(production["strict_relocations"], 23)
        self.assertEqual(production["source_only_functions_compiled"], 4)
        self.assertEqual(production["manifest_regions"], 11)
        self.assertEqual(production["flash_plan_counts"], (7_006, 0, 6, 6))
        self.assertTrue(production["null_and_non_command_events_fail_closed"])
        self.assertTrue(production["missing_extension_callback_falls_back"])


if __name__ == "__main__":
    unittest.main()
