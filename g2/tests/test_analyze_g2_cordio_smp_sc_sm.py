#!/usr/bin/env python3
"""Guard the bounded G2 Cordio SMP Secure Connections state machines."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_smp_sc_sm.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_cordio_smp_sc_sm", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SmpScStateMachineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_complete_pair(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["translation_units"], 2)
        self.assertEqual(module["linked_function_count"], 4)
        self.assertEqual(module["linked_function_bytes"], 598)
        self.assertEqual(module["physical_object_bytes"], 936)
        self.assertEqual(module["dispatch_data_bytes"], 1495)
        self.assertEqual(module["total_identified_owned_bytes"], 2431)
        self.assertEqual(module["direct_bl_ingress_sites"], 4)
        self.assertEqual(module["stored_function_pointers"], 0)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(report["roles"]["initiator"]["action_count"], 51)
        self.assertEqual(report["roles"]["initiator"]["state_count"], 38)
        self.assertEqual(report["roles"]["responder"]["action_count"], 55)
        self.assertEqual(report["roles"]["responder"]["state_count"], 40)
        self.assertTrue(report["lineage"]["independent_release_discriminator"])
        production = report["production"]
        self.assertEqual(production["function_count"], 4)
        self.assertEqual(production["compiled_closure_bytes"], 1696)
        self.assertEqual(production["alignment_bytes"], 6)
        self.assertEqual(production["dispatch_data_bytes"], 1495)
        self.assertEqual(production["dispatch_placement_count"], 86)
        self.assertEqual(production["stock_bytes_replaced"], 2093)
        self.assertEqual(production["source_owned_bytes_added"], 3197)
        self.assertTrue(production["all_function_entries_routed"])
        self.assertTrue(production["all_dispatch_data_installed"])
        self.assertEqual(production["hardware_validation"]["status"], "deferred by project direction")


if __name__ == "__main__":
    unittest.main()
