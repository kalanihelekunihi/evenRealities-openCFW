#!/usr/bin/env python3
"""Guard the clean-room closure of Ambiq Cordio's HCI transport."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_hci_tr.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_hci_tr", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioHciTransportAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_function_inventory_is_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["source_inventory_functions"], 4)
        self.assertEqual(module["linked_function_count"], 3)
        self.assertEqual(module["linked_function_bytes"], 524)
        self.assertEqual(module["physical_bytes"], 552)
        self.assertEqual(module["source_only_functions"], ["hciTrReceivingPacket"])

    def test_send_ownership_selects_the_later_family(self) -> None:
        behavior = self.report["behavior"]
        self.assertTrue(behavior["acl_send_returns_length_or_zero"])
        self.assertTrue(behavior["command_send_returns_success"])
        self.assertTrue(behavior["transport_does_not_complete_tx_buffers"])
        self.assertEqual(
            self.report["lineage"]["r44_send_ownership"],
            "caller completes/frees after return status",
        )

    def test_receive_state_and_ingress_are_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["direct_bl_ingress_sites"], 4)
        self.assertEqual(module["direct_provider_calls"], 6)
        self.assertEqual(module["stored_entry_pointers"], 0)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(self.report["abi"]["receiving_packet"], 0x20074FCD)
        self.assertTrue(self.report["behavior"]["invalid_packet_type_is_discarded"])

    def test_proprietary_boundary_is_metadata_only(self) -> None:
        self.assertFalse(self.report["lineage"]["historical_generating_commit_resolved"])
        self.assertEqual(self.report["lineage"]["license"], "Arm Cordio proprietary SLA")
        self.assertFalse(self.report["production"]["proprietary_source_copied"])
        production = self.report["production"]
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(production["stock_bytes_replaced"], 524)
        self.assertEqual(production["source_owned_bytes_added"], 454)
        self.assertEqual(production["strict_relocations"], 6)
        self.assertEqual(production["source_only_functions_compiled"], 1)
        self.assertEqual(production["manifest_regions"], 6)
        self.assertEqual(production["flash_plan_counts"], (5863, 2, 5, 6))
        self.assertTrue(production["failure_state_reset_hardened"])


if __name__ == "__main__":
    unittest.main()
