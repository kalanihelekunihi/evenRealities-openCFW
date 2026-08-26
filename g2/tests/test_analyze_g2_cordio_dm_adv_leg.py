#!/usr/bin/env python3
"""Guard the complete G2 Cordio legacy advertising evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_dm_adv_leg.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_dm_adv_leg", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioDmAdvLegAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_functions_tables_abi_lineage_and_readiness_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 17)
        self.assertEqual(module["linked_function_bytes"], 4396)
        self.assertEqual(module["code_interval_bytes"], 4558)
        self.assertEqual(module["inline_literal_and_alignment_bytes"], 162)
        self.assertEqual(module["trailing_literal_pool_bytes"], 100)
        self.assertEqual(module["direct_bl_ingress_sites"], 6)
        self.assertEqual(module["registered_function_entries"], 11)
        self.assertEqual(module["unexpected_aligned_entry_or_interior_pointers"], 0)
        self.assertEqual(len(module["source_only_dead_stripped"]), 1)
        self.assertEqual(report["abi"]["dm_num_adv_sets"], 2)
        self.assertEqual(report["abi"]["message_data_payload_offset"], 8)
        self.assertEqual(report["readiness"]["source_inventory_functions"], 18)
        self.assertEqual(report["readiness"]["linked_unresolved_symbols"], 0)
        production = report["production"]
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(production["redirected_stock_functions"], 17)
        self.assertEqual(production["redirected_stock_bytes"], 4396)
        self.assertEqual(production["source_owned_bytes_added"], 948)
        self.assertEqual(production["alignment_bytes_added"], 26)
        self.assertEqual(production["strict_relocations"], 32)
        self.assertEqual(production["manifest_regions"], 47)
        self.assertEqual(production["flash_plan_counts"], (5863, 2, 5, 6))
        self.assertEqual(production["source_only_target_compiled"], ["DmAdvModeLeg"])


if __name__ == "__main__":
    unittest.main()
