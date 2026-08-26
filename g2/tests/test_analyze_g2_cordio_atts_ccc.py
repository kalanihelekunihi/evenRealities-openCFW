#!/usr/bin/env python3
"""Guard the complete G2 Cordio ATT CCC evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_atts_ccc.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_atts_ccc", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttsCccAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_complete_tu_callers_callbacks_and_configuration_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 14)
        self.assertEqual(module["linked_function_bytes"], 2770)
        self.assertEqual(module["translation_unit_bytes"], 2908)
        self.assertEqual(module["inline_and_trailing_data_bytes"], 138)
        self.assertEqual(module["source_only_dead_stripped"], [])
        self.assertEqual(module["direct_bl_ingress_sites"], 23)
        self.assertEqual(len(module["registered_indirect_consumer_sites"]), 8)
        self.assertEqual(report["abi"]["control_block"], 0x20073B00)
        self.assertEqual(report["abi"]["control_block_size"], 24)
        self.assertEqual(report["abi"]["connection_count"], 3)
        self.assertEqual(report["abi"]["set_length"], 6)
        self.assertEqual(report["abi"]["registered_main_callback"], 0x52C0AD)
        self.assertEqual(report["abi"]["ccc_state_event"], 0x14)
        self.assertEqual(report["readiness"]["linked_unresolved_symbols"], 0)
        self.assertEqual(report["production"]["status"], "routed")
        self.assertEqual(report["production"]["source_owned_bytes_added"], 784)
        self.assertEqual(report["production"]["alignment_bytes"], 8)
        self.assertEqual(report["production"]["strict_relocations"], 14)
        self.assertEqual(report["production"]["guarded_redirects"], 14)


if __name__ == "__main__":
    unittest.main()
