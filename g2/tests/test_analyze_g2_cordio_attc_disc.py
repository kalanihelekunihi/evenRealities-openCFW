#!/usr/bin/env python3
"""Guard the complete G2 Cordio ATT client-discovery evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_attc_disc.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_attc_disc", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttcDiscAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_complete_tu_callers_abi_lineage_and_readiness_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 15)
        self.assertEqual(module["linked_function_bytes"], 2908)
        self.assertEqual(module["translation_unit_bytes"], 3012)
        self.assertEqual(module["literal_and_alignment_bytes"], 104)
        self.assertEqual(module["direct_bl_ingress_sites"], 20)
        self.assertEqual(module["indirect_ingress_sites"], 0)
        self.assertEqual(module["stored_entry_or_interior_pointers"], 0)
        self.assertEqual(len(module["source_only_dead_stripped"]), 3)
        self.assertEqual(report["abi"]["attcDiscCb_size"], 20)
        self.assertEqual(report["abi"]["owned_mutable_globals"], 0)
        self.assertEqual(report["lineage"]["r20_only_included_service_functions"], "dead-stripped")
        self.assertEqual(report["readiness"]["source_inventory_functions"], 18)
        self.assertEqual(report["readiness"]["linked_unresolved_symbols"], 0)
        self.assertEqual(report["production"]["status"], "routed")
        self.assertEqual(report["production"]["source_owned_bytes_added"], 1610)
        self.assertEqual(report["production"]["stock_bytes_replaced"], 2908)
        self.assertTrue(report["production"]["response_shape_bounds_hardened"])


if __name__ == "__main__":
    unittest.main()
