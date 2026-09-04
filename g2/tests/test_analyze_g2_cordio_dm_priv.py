#!/usr/bin/env python3
"""Guard the complete G2 Cordio privacy-manager evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_dm_priv.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_dm_priv", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioDmPrivAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_split_privacy_architecture_and_linkage_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        architecture = report["architecture"]
        self.assertEqual(module["linked_function_count"], 21)
        self.assertEqual(module["linked_function_bytes"], 980)
        self.assertEqual(module["physical_bytes"], 1008)
        self.assertEqual(module["source_inventory_functions"], 25)
        self.assertEqual(len(module["source_only_functions"]), 4)
        self.assertEqual(module["direct_bl_ingress_sites"], 19)
        self.assertEqual(module["registered_function_pointers"], 13)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(architecture["privacy_component_id"], 6)
        self.assertEqual(architecture["privacy_aes_component_id"], 15)
        self.assertEqual(architecture["main_action_count"], 7)
        self.assertEqual(architecture["aes_action_count"], 2)
        self.assertTrue(architecture["task_locked_dual_interface_install"])
        self.assertEqual(report["abi"]["dm_priv_cb_bytes"], 0x1A)
        self.assertFalse(report["lineage"]["historical_generating_commit_resolved"])
        readiness = report["readiness"]
        self.assertEqual(readiness["provider_seams"], 24)
        self.assertEqual(readiness["valid_non_vacuous_closure_profiles"], 2)
        self.assertEqual(readiness["linked_unresolved_symbols"], 0)
        production = report["production"]
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(
            (production["redirected_stock_functions"], production["redirected_stock_bytes"]),
            (21, 980),
        )
        self.assertEqual(
            (production["source_owned_bytes_added"], production["alignment_bytes_added"],
             production["strict_relocations"]),
            (1_688, 20, 25),
        )
        self.assertEqual(production["source_only_functions_compiled"], 4)
        self.assertEqual(production["manifest_regions"], 51)
        self.assertEqual(production["flash_plan_counts"], (7_822, 0, 8, 6))


if __name__ == "__main__":
    unittest.main()
