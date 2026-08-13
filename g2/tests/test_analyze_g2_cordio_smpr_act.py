#!/usr/bin/env python3
"""Guard the bounded G2 Cordio SMP responder-action evidence."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_smpr_act.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_smpr_act", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SmprActTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_closure(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 10)
        self.assertEqual(module["source_inventory_functions"], 10)
        self.assertEqual(module["linked_function_bytes"], 1160)
        self.assertEqual(module["owned_noncode_bytes"], 44)
        self.assertEqual(module["physical_bytes"], 1204)
        self.assertEqual(module["source_only_functions"], [])
        self.assertEqual(module["direct_bl_ingress_sites"], 2)
        self.assertEqual(module["external_direct_bl_ingress_sites"], 0)
        self.assertEqual(module["registered_function_pointers"], 20)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(report["architecture"]["ccb_key_ready_offset"], 0x44)
        self.assertTrue(report["lineage"]["independent_release_discriminator"])


if __name__ == "__main__":
    unittest.main()
