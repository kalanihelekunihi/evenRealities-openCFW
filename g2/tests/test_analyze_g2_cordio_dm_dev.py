#!/usr/bin/env python3
"""Guard the complete G2 Cordio local-device evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_dm_dev.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_dm_dev", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioDmDevAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_complete_module_dispatch_abi_and_lineage_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        dispatch = report["dispatch"]
        self.assertEqual(module["linked_function_count"], 12)
        self.assertEqual(module["linked_function_bytes"], 626)
        self.assertEqual(module["physical_bytes"], 672)
        self.assertEqual(module["literal_pool_bytes"], 44)
        self.assertEqual(module["trailing_pad_bytes"], 2)
        self.assertEqual(module["direct_bl_ingress_sites"], 29)
        self.assertEqual(module["registered_function_pointers"], 3)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(module["source_inventory_functions"], 18)
        self.assertEqual(len(module["source_only_functions"]), 6)
        self.assertEqual(dispatch["dm_num_ids"], 21)
        self.assertEqual(dispatch["dm_message_mask"], 7)
        self.assertEqual(dispatch["dm_dev_reset_event"], 0x38)
        self.assertEqual(dispatch["dm_conn_cte_state_event"], 0x6F)
        self.assertEqual(dispatch["hci_inputs"], [0, 18, 19, 20])
        self.assertEqual(dispatch["dm_callback_outputs"], [0x20, 0x7B, 0x7A, 0x79])
        self.assertEqual(report["abi"]["device_privacy_component_id"], 1)
        self.assertEqual(report["abi"]["connection_cte_component_id"], 13)
        readiness = report["readiness"]
        self.assertEqual(readiness["provider_seams"], 14)
        self.assertEqual(readiness["valid_non_vacuous_closure_profiles"], 2)
        self.assertEqual(readiness["linked_unresolved_symbols"], 0)
        production = report["production"]
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(production["redirected_stock_functions"], 12)
        self.assertEqual(production["redirected_stock_bytes"], 626)
        self.assertEqual(production["source_owned_bytes_added"], 448)
        self.assertEqual(production["alignment_bytes_added"], 18)
        self.assertEqual(production["strict_relocations"], 9)
        self.assertEqual(len(production["source_only_target_compiled"]), 6)
        self.assertEqual(production["manifest_regions"], 33)
        self.assertEqual(production["flash_plan_counts"], (7006, 0, 6, 6))


if __name__ == "__main__":
    unittest.main()
