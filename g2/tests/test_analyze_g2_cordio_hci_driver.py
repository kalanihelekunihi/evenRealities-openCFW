#!/usr/bin/env python3
"""Guard the clean-room Apollo3 Cordio HCI-driver closure."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_hci_driver.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_hci_driver", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioHciDriverAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_complete_driver_inventory_is_classified(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["source_inventory_functions"], 16)
        self.assertEqual(module["linked_function_count"], 12)
        self.assertEqual(module["linked_function_bytes"], 1_188)
        self.assertEqual(module["main_interval_bytes"], 1_158)
        self.assertEqual(len(module["source_only_functions"]), 4)

    def test_blocking_transport_abi_is_exact(self) -> None:
        abi = self.report["abi"]
        self.assertFalse(abi["nonblocking_hci"])
        self.assertTrue(abi["heartbeat_enabled"])
        self.assertEqual(abi["write_buffer_count"], 8)
        self.assertEqual(abi["write_record_bytes"], 260)
        self.assertEqual(abi["read_buffer_bytes"], 256)
        self.assertEqual(abi["max_transactions_per_handler"], 1000)
        self.assertEqual(abi["max_consecutive_reads"], 4)

    def test_ingress_and_interior_classification_are_fail_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["direct_bl_ingress_sites"], 30)
        self.assertEqual(module["direct_provider_calls"], 66)
        self.assertEqual(module["stored_entry_pointers"], [(0x004B8798, 0x004B4AB3)])
        self.assertEqual(module["accepted_strict_interior_pointers"], 0)
        self.assertEqual(module["excluded_aligned_interior_lookalikes"], 30)

    def test_mixed_lineage_and_vendor_commands_are_explicit(self) -> None:
        behavior = self.report["behavior"]
        lineage = self.report["lineage"]
        self.assertTrue(behavior["handler_null_message_guard"])
        self.assertEqual(behavior["rf_power_opcode"], 0xFCC4)
        self.assertEqual(behavior["bd_address_opcode"], 0xFC43)
        self.assertEqual(behavior["nvds_update_opcode"], 0xFFF2)
        self.assertEqual(lineage["classification"], "mixed-version Ambiq driver")
        self.assertFalse(lineage["whole_file_source_exact"])
        self.assertFalse(lineage["historical_generating_commit_resolved"])
        production = self.report["production"]
        self.assertEqual(
            production["status"], "software-complete-hardware-validation-blocked-by-unavailable-physical-evidence"
        )
        self.assertEqual(production["source_inventory_compiled"], 16)
        self.assertEqual(production["redirected_stock_functions"], 9)
        self.assertEqual(production["redirected_stock_bytes"], 368)
        self.assertEqual(production["remaining_unimplemented_software_functions"], 0)
        self.assertEqual(len(production["hardware_evidence_blocked_functions"]), 6)
        self.assertFalse(production["production_hardware_substitution_validated"])
        self.assertFalse(production["vendor_source_copied"])


if __name__ == "__main__":
    unittest.main()
