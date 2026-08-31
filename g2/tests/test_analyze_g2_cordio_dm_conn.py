#!/usr/bin/env python3
"""Guard the complete G2 Cordio DM connection-manager evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_dm_conn.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_dm_conn", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioDmConnAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_functions_tables_abi_lineage_and_readiness_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 57)
        self.assertEqual(module["linked_public_source_functions"], 56)
        self.assertEqual(module["linked_vendor_helpers"], 1)
        self.assertEqual(module["linked_function_bytes"], 6216)
        self.assertEqual(module["physical_bytes"], 6484)
        self.assertEqual(module["interstitial_bytes"], 186)
        self.assertEqual(module["trailing_pool_bytes"], 82)
        self.assertEqual(module["direct_bl_ingress_sites"], 209)
        self.assertEqual(module["stored_entry_pointers"], 13)
        self.assertEqual(module["rejected_unaligned_nonpointer_sequences"], 1)
        self.assertEqual(module["unexpected_entry_or_interior_pointers"], 0)
        self.assertEqual(len(module["source_only_dead_stripped"]), 5)
        self.assertEqual(report["abi"]["dm_conn_max"], 3)
        self.assertEqual(report["abi"]["dm_num_phys"], 2)
        self.assertEqual(report["abi"]["ccb_size"], 0x30)
        self.assertEqual(report["abi"]["control_block_size"], 0xC4)
        self.assertEqual(report["readiness"]["provider_seams"], 30)
        self.assertEqual(
            report["readiness"]["linked_unresolved_symbols"], 0
        )
        production = report["production"]
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(
            (
                production["production_owned_stock_functions"],
                production["guarded_redirects"],
                production["exact_in_place_copies"],
                production["production_owned_stock_bytes"],
            ),
            (57, 55, 2, 6216),
        )
        self.assertEqual(
            (
                production["source_owned_bytes_added"],
                production["alignment_bytes_added"],
                production["strict_relocations"],
                production["manifest_regions"],
            ),
            (4540, 54, 92, 141),
        )
        self.assertEqual(production["source_only_functions_compiled"], 5)
        self.assertEqual(production["flash_plan_counts"], (6588, 0, 6, 6))


if __name__ == "__main__":
    unittest.main()
