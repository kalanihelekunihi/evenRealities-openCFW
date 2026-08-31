#!/usr/bin/env python3
"""Guard the bounded G2 Cordio SMP initiator-action evidence."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SmpiActTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = ROOT / "tools/analyze_g2_cordio_smpi_act.py"
        spec = importlib.util.spec_from_file_location("analyze_g2_cordio_smpi_act", path)
        assert spec is not None and spec.loader is not None
        cls.analyzer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.analyzer
        spec.loader.exec_module(cls.analyzer)

    def test_closure(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 10)
        self.assertEqual(module["linked_function_bytes"], 852)
        self.assertEqual(module["owned_noncode_bytes"], 8)
        self.assertEqual(module["physical_bytes"], 860)
        self.assertEqual(module["source_only_functions"], [])
        self.assertEqual(module["direct_bl_ingress_sites"], 0)
        self.assertEqual(module["raw_false_bl_candidates"], 1)
        self.assertEqual(module["registered_function_pointers"], 20)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(report["architecture"]["ccb_key_ready_offset"], 0x44)
        self.assertTrue(report["lineage"]["independent_release_discriminator"])
        production = report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["live_functions"], 10)
        self.assertEqual(production["compiled_leaf_bytes"], 820)
        self.assertEqual(production["source_owned_bytes_added"], 830)
        self.assertEqual(production["stock_bytes_replaced"], 852)
        self.assertIn("blocked by unavailable physical evidence", production["hardware_validation"])


if __name__ == "__main__":
    unittest.main()
