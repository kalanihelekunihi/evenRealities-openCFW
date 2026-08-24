#!/usr/bin/env python3
"""Guard the bounded G2 Cordio legacy SMP state-machine evidence."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SmpLegacyStateMachineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = ROOT / "tools/analyze_g2_cordio_smp_legacy_sm.py"
        spec = importlib.util.spec_from_file_location("analyze_g2_cordio_smp_legacy_sm", path)
        assert spec is not None and spec.loader is not None
        cls.analyzer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.analyzer
        spec.loader.exec_module(cls.analyzer)

    def test_complete_pair(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["translation_units"], 2)
        self.assertEqual(module["linked_function_count"], 2)
        self.assertEqual(module["linked_function_bytes"], 44)
        self.assertEqual(module["dispatch_data_bytes"], 705)
        self.assertEqual(module["total_identified_owned_bytes"], 785)
        self.assertEqual(module["source_only_functions"], [])
        self.assertEqual(module["direct_bl_ingress_sites"], 2)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(report["roles"]["initiator"]["action_count"], 25)
        self.assertEqual(report["roles"]["responder"]["action_count"], 27)
        self.assertTrue(report["lineage"]["independent_release_discriminator"])
        production = report["production"]
        self.assertEqual(production["function_count"], 2)
        self.assertEqual(production["compiled_closure_bytes"], 88)
        self.assertEqual(production["dispatch_data_bytes"], 705)
        self.assertEqual(production["dispatch_placement_count"], 37)
        self.assertEqual(production["stock_bytes_replaced"], 749)
        self.assertEqual(production["source_owned_bytes_added"], 793)
        self.assertTrue(production["all_function_entries_routed"])
        self.assertTrue(production["all_dispatch_data_installed"])
        self.assertEqual(production["hardware_validation"]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
