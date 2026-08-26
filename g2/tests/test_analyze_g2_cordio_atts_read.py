#!/usr/bin/env python3
"""Guard the optional Cordio ATT server read processors and live roots."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_atts_read.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_atts_read", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttsReadAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_complete_read_object_is_closed(self) -> None:
        module = self.analyzer.analyze()["module"]
        self.assertEqual(module["classification"], "linked_optional_server_read_processors")
        self.assertEqual(module["physical_bytes"], 3004)
        self.assertEqual(module["linked_function_count"], 7)
        self.assertEqual(module["linked_function_bytes"], 2984)
        self.assertEqual(module["owned_noncode_bytes"], 20)
        self.assertEqual(module["source_inventory_functions"], 7)
        self.assertEqual(module["source_only_functions"], [])
        self.assertEqual(module["direct_bl_ingress_sites"], 9)
        self.assertEqual(module["direct_callee_sites"], 50)
        self.assertEqual(module["raw_bl_like_wide_instruction_overlaps"], 3)
        self.assertEqual(module["strict_interior_pointers"], 0)

    def test_live_read_method_roots_are_exact(self) -> None:
        dispatch = self.analyzer.analyze()["dispatch"]
        self.assertEqual(dispatch["processor_table_live_sram"], 0x2000045C)
        self.assertEqual(dispatch["methods"]["3"]["entry"], 0x0056DC05)
        self.assertEqual(dispatch["methods"]["4"]["entry"], 0x0056DD9D)
        self.assertEqual(dispatch["methods"]["6"]["entry"], 0x0056DA9F)
        self.assertEqual(dispatch["methods"]["7"]["entry"], 0x0056E0DF)
        self.assertEqual(dispatch["methods"]["8"]["entry"], 0x0056E26D)
        self.assertTrue(dispatch["initializer_stream_is_not_runtime_table"])

    def test_r4_fit_checks_and_lineage_are_pinned(self) -> None:
        report = self.analyzer.analyze()
        self.assertTrue(report["architecture"]["csf_database_hash_deferral"])
        self.assertTrue(report["architecture"]["iar_subtraction_safe_fit_checks"])
        self.assertEqual(report["architecture"]["fit_check_windows"], 3)
        self.assertEqual(report["lineage"]["selected_blob"], "52a7f290710c12ecba0850175c9bc1fe21f8e0aa")
        self.assertFalse(report["lineage"]["historical_generating_commit_resolved"])
        production = report["production"]
        self.assertEqual(production["status"], "routed")
        self.assertEqual(production["source_owned_bytes_added"], 2786)
        self.assertEqual(production["stock_bytes_replaced"], 2984)
        self.assertEqual(production["alignment_bytes"], 8)
        self.assertEqual(production["strict_relocations"], 44)
        self.assertEqual(production["guarded_redirects"], 7)


if __name__ == "__main__":
    unittest.main()
