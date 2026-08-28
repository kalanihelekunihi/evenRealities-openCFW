#!/usr/bin/env python3
"""Guard the bounded G2 Cordio SMP-main evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_smp_main.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_smp_main", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioSmpMainAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_stock_spans_abi_vendor_patch_and_readiness_result_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 20)
        self.assertEqual(module["linked_function_bytes"], 3076)
        self.assertEqual(module["literal_or_data_gap_bytes"], 112)
        self.assertEqual(module["source_only_dead_stripped"], ["SmpDmGetLtk"])
        self.assertEqual(module["direct_bl_callers"], 58)
        self.assertEqual(len(module["intentional_function_pointers"]), 4)
        self.assertEqual(report["abi"]["control_block"], 0x20070AEC)
        self.assertEqual(report["abi"]["control_block_size"], 0xFC)
        self.assertEqual(report["abi"]["connection_count"], 3)
        self.assertEqual(report["abi"]["ccb_size"], 0x4C)
        self.assertEqual(report["abi"]["ccb_offsets"]["key_ready"], 0x44)
        self.assertEqual(report["abi"]["security_control_block"], 0x20072CD8)
        self.assertEqual(report["abi"]["database_service_event"], 0x20)
        self.assertEqual(report["readiness"]["external_provider_seams"], 32)
        self.assertEqual(report["readiness"]["linked_unresolved_symbols"], 0)
        production = report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["live_functions"], 21)
        self.assertEqual(production["compiled_leaf_bytes"], 2146)
        self.assertEqual(production["source_owned_bytes_added"], 2170)
        self.assertEqual(production["stock_bytes_replaced"], 3076)
        self.assertIn("deferred by project direction", production["hardware_validation"])


if __name__ == "__main__":
    unittest.main()
