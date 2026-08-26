#!/usr/bin/env python3
"""Guard the bounded G2 Cordio ATT client PDU-processing evidence."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_attc_proc.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_attc_proc", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AttcProcTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_closure(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 15)
        self.assertEqual(module["source_inventory_functions"], 16)
        self.assertEqual(module["linked_function_bytes"], 1884)
        self.assertEqual(module["physical_bytes"], 1936)
        self.assertEqual(module["source_only_functions"], ["AttcCancelReq"])
        self.assertEqual(module["direct_bl_ingress_sites"], 20)
        self.assertEqual(module["registered_function_pointers"], 10)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(module["unaligned_false_pointer_windows"], 5)
        self.assertEqual(module["aligned_ascii_pointer_collisions"], 1)
        architecture = report["architecture"]
        self.assertEqual(architecture["response_table_entries"], 17)
        self.assertEqual(architecture["minimum_pdu_table_entries"], 13)
        self.assertTrue(architecture["r4_event_and_length_guards"])
        self.assertTrue(architecture["inherited_method_16_17_bounds_defect"])
        self.assertTrue(report["lineage"]["independent_release_discriminator"])
        self.assertEqual(report["production"]["status"], "routed")
        self.assertEqual(report["production"]["stock_bytes_replaced"], 1884)
        self.assertEqual(report["production"]["source_owned_bytes_added"], 1694)
        self.assertEqual(report["production"]["guarded_redirects"], 13)
        self.assertEqual(report["production"]["exact_in_place_copies"], 2)
        self.assertTrue(report["production"]["method_table_bounds_defect_remediated"])


if __name__ == "__main__":
    unittest.main()
