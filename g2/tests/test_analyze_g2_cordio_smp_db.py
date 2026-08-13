#!/usr/bin/env python3
"""Guard the bounded G2 Cordio SMP pairing-database evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_smp_db.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_smp_db", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioSmpDbAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_stock_spans_callers_abi_and_readiness_result_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["linked_function_count"], 11)
        self.assertEqual(module["linked_function_bytes"], 2952)
        self.assertEqual(module["literal_or_data_gap_bytes"], 54)
        self.assertEqual(
            module["source_only_dead_stripped"],
            ["SmpDbRemoveAllDevices", "SmpDbRemoveDevice"],
        )
        self.assertEqual(
            sum(len(item["direct_bl_callers"]) for item in module["functions"]),
            24,
        )
        self.assertEqual(report["abi"]["control_block"], 0x200708EC)
        self.assertEqual(report["abi"]["control_block_size"], 0x100)
        self.assertEqual(report["abi"]["record_count"], 10)
        self.assertEqual(report["abi"]["record_size"], 24)
        self.assertEqual(report["abi"]["service_timer_offset"], 0xF0)
        self.assertEqual(report["abi"]["service_event"], 0x20)
        self.assertEqual(
            report["configuration"]["boot_data_initializer"]["attempt_timeout_ms"],
            500,
        )
        self.assertEqual(
            report["configuration"]["normal_product_runtime_override"]
            ["attempt_timeout_ms"],
            3000,
        )
        self.assertEqual(report["readiness"]["linked_unresolved_symbols"], 0)
        self.assertEqual(report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
