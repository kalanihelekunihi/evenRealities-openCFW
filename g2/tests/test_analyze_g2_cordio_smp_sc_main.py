#!/usr/bin/env python3
"""Guard the bounded G2 Cordio SMP Secure Connections main evidence."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_smp_sc_main.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_cordio_smp_sc_main", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SmpScMainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_closure(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 18)
        self.assertEqual(module["linked_function_bytes"], 2626)
        self.assertEqual(module["physical_bytes"], 2820)
        self.assertEqual(
            module["source_only_functions"],
            [
                "SmpScFree",
                "smpGetPeerPublicKey",
                "smpSetPeerPublicKey",
                "SmpScSetOobCfg",
            ],
        )
        self.assertEqual(module["direct_bl_ingress_sites"], 111)
        self.assertEqual(module["registered_function_pointers"], 0)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertTrue(report["lineage"]["independent_release_discriminator"])
        self.assertEqual(report["architecture"]["cleanup_event"], 0x1F)
        production = report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["live_functions"], 18)
        self.assertEqual(production["compiled_leaf_bytes"], 2278)
        self.assertEqual(production["source_owned_bytes_added"], 2730)
        self.assertEqual(production["stock_bytes_replaced"], 2626)
        self.assertIn("blocked by unavailable physical evidence", production["hardware_validation"])


if __name__ == "__main__":
    unittest.main()
