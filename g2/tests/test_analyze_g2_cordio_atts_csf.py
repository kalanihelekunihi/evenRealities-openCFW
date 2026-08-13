#!/usr/bin/env python3
"""Guard the bounded G2 Cordio ATT client-features evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_atts_csf.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_atts_csf", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttsCsfAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_stock_spans_callers_abi_and_readiness_result_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 10)
        self.assertEqual(module["linked_function_bytes"], 4814)
        self.assertEqual(module["literal_or_data_gap_bytes"], 126)
        self.assertEqual(module["source_only_dead_stripped"], ["AttsCsfInit"])
        self.assertEqual(
            sum(len(item["direct_bl_callers"]) for item in module["functions"]),
            20,
        )
        self.assertEqual(report["abi"]["control_block"], 0x20073E04)
        self.assertEqual(report["abi"]["record_count"], 3)
        self.assertEqual(report["abi"]["write_callback_offset"], 8)
        self.assertEqual(report["abi"]["hash_update_offset"], 12)
        self.assertEqual(report["readiness"]["linked_unresolved_symbols"], 0)
        self.assertEqual(report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
