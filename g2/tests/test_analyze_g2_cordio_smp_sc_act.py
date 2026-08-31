#!/usr/bin/env python3
"""Guard the bounded G2 Cordio shared SMP Secure Connections evidence."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SmpScActTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = ROOT / "tools/analyze_g2_cordio_smp_sc_act.py"
        spec = importlib.util.spec_from_file_location("analyze_g2_cordio_smp_sc_act", path)
        assert spec is not None and spec.loader is not None
        cls.analyzer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.analyzer
        spec.loader.exec_module(cls.analyzer)

    def test_closure(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 20)
        self.assertEqual(module["linked_function_bytes"], 2662)
        self.assertEqual(module["owned_noncode_bytes"], 54)
        self.assertEqual(module["physical_bytes"], 2716)
        self.assertEqual(module["source_inventory_functions"], 21)
        self.assertEqual(module["configuration_excluded_functions"], ["SmpScEnableZeroDhKey"])
        self.assertEqual(module["direct_bl_ingress_sites"], 19)
        self.assertEqual(module["external_direct_bl_ingress_sites"], 9)
        self.assertEqual(module["registered_function_pointer_cells"], 26)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertTrue(report["lineage"]["independent_release_discriminator"])
        self.assertTrue(report["lineage"]["r20_message_and_table_abi"])
        production = report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["live_functions"], 20)
        self.assertEqual(production["relocated_functions"], 20)
        self.assertEqual(production["compiled_leaf_bytes"], 2258)
        self.assertEqual(production["source_owned_bytes_added"], 2276)
        self.assertEqual(production["stock_bytes_replaced"], 2662)
        self.assertIn("blocked by unavailable physical evidence", production["hardware_validation"])


if __name__ == "__main__":
    unittest.main()
