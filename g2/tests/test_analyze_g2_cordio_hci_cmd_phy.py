#!/usr/bin/env python3
"""Guard the clean-room Cordio HCI PHY-command closure."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_hci_cmd_phy.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_hci_cmd_phy", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CordioHciPhyCommandAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_inventory_is_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["source_inventory_functions"], 3)
        self.assertEqual(module["linked_function_count"], 1)
        self.assertEqual(module["linked_function_bytes"], 74)
        self.assertEqual(module["physical_bytes"], 76)
        self.assertEqual(
            module["source_only_functions"],
            ["HciLeReadPhyCmd", "HciLeSetDefaultPhyCmd"],
        )

    def test_stock_command_encoding_is_exact(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["opcode"], 0x2032)
        self.assertEqual(behavior["parameter_bytes"], 7)
        self.assertTrue(behavior["null_safe_allocation"])
        self.assertTrue(behavior["command_sent_through_hci_cmd_queue"])

    def test_ingress_is_fail_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["direct_bl_ingress_sites"], 1)
        self.assertEqual(module["direct_provider_calls"], 2)
        self.assertEqual(module["stored_entry_pointers"], 0)
        self.assertEqual(module["strict_interior_pointers"], 0)

    def test_public_source_boundary(self) -> None:
        self.assertEqual(self.report["lineage"]["license"], "Apache-2.0")
        self.assertTrue(self.report["lineage"]["definition_bodies_match_ambiq_r25"])
        production = self.report["production"]
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(production["stock_bytes_replaced"], 74)
        self.assertEqual(production["source_owned_bytes_added"], 60)
        self.assertEqual(production["strict_relocations"], 2)
        self.assertEqual(production["source_only_functions_compiled"], 2)
        self.assertEqual(production["manifest_regions"], 2)
        self.assertEqual(production["flash_plan_counts"], (6588, 0, 6, 6))


if __name__ == "__main__":
    unittest.main()
