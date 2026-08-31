#!/usr/bin/env python3
"""Guard the clean-room Ambiq Cordio HCI-command closure."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_hci_cmd.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_hci_cmd", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioHciCommandAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_complete_source_inventory_is_classified(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["source_inventory_functions"], 72)
        self.assertEqual(module["linked_function_count"], 50)
        self.assertEqual(len(module["source_only_functions"]), 22)
        self.assertEqual(module["linked_function_bytes"], 2_654)
        self.assertEqual(module["physical_bytes"], 2_668)

    def test_command_queue_abi_is_exact(self) -> None:
        abi = self.report["abi"]
        self.assertEqual(abi["hci_cmd_cb"], 0x20073A90)
        self.assertEqual(abi["queue_offset"], 0x10)
        self.assertEqual(abi["opcode_offset"], 0x18)
        self.assertEqual(abi["command_credit_offset"], 0x1A)
        self.assertEqual(abi["command_timeout_seconds"], 10)

    def test_ingress_and_callee_closure_are_fail_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["direct_bl_ingress_sites"], 156)
        self.assertEqual(module["direct_body_call_sites"], 127)
        self.assertEqual(module["stored_entry_pointers"], 0)
        self.assertEqual(module["accepted_strict_interior_pointers"], 0)
        self.assertEqual(
            module["excluded_data_words_resembling_interior_pointers"],
            [(0x006317C0, 0x0052B5EF)],
        )

    def test_proprietary_boundary_is_preserved(self) -> None:
        self.assertEqual(self.report["lineage"]["license"], "Arm Cordio proprietary SLA")
        self.assertFalse(self.report["lineage"]["historical_generating_commit_resolved"])
        production = self.report["production"]
        self.assertFalse(production["proprietary_source_copied"])
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(production["redirected_stock_functions"], 50)
        self.assertEqual(production["redirected_stock_bytes"], 2_654)
        self.assertEqual(production["source_owned_bytes_added"], 4_052)
        self.assertEqual(production["alignment_bytes_added"], 68)
        self.assertEqual(production["strict_relocations"], 106)
        self.assertEqual(production["source_only_functions_compiled"], 22)
        self.assertEqual(production["manifest_regions"], 91)
        self.assertEqual(production["flash_plan_counts"], (6_586, 0, 6, 6))
        self.assertEqual(production["remaining_unrouted_linked_functions"], 0)
        self.assertEqual(production["remaining_source_only_functions"], 0)
        self.assertTrue(production["full_command_layer_complete"])


if __name__ == "__main__":
    unittest.main()
