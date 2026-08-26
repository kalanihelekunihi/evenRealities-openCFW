#!/usr/bin/env python3
"""Guard the common Cordio ATT server processors and live method roots."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_atts_proc.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_atts_proc", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttsProcAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_complete_processor_object_is_closed(self) -> None:
        module = self.analyzer.analyze()["module"]
        self.assertEqual(module["classification"], "linked_eatt_common_server_processors")
        self.assertEqual(module["physical_bytes"], 2160)
        self.assertEqual(module["linked_function_count"], 9)
        self.assertEqual(module["linked_function_bytes"], 2106)
        self.assertEqual(module["owned_noncode_bytes"], 54)
        self.assertEqual(module["source_inventory_functions"], 9)
        self.assertEqual(module["source_only_functions"], [])
        self.assertEqual(module["direct_bl_ingress_sites"], 26)
        self.assertEqual(module["strict_interior_pointers"], 0)

    def test_live_method_roots_are_exact(self) -> None:
        dispatch = self.analyzer.analyze()["dispatch"]
        self.assertEqual(dispatch["processor_table_live_sram"], 0x2000045C)
        self.assertEqual(dispatch["methods"]["1"]["entry"], 0x0056C6FD)
        self.assertEqual(dispatch["methods"]["2"]["entry"], 0x0056C931)
        self.assertEqual(dispatch["methods"]["5"]["entry"], 0x0056CAA9)
        self.assertEqual(dispatch["methods"]["16"]["entry"], 0x0056CBCB)
        self.assertTrue(dispatch["initializer_stream_is_not_runtime_table"])

    def test_r20_eatt_features_and_lineage_are_pinned(self) -> None:
        report = self.analyzer.analyze()
        self.assertTrue(report["architecture"]["eatt_aware"])
        self.assertTrue(report["architecture"]["read_multiple_variable_linked"])
        self.assertTrue(report["architecture"]["mtu_request_rejected_on_eatt_bearer"])
        self.assertEqual(report["lineage"]["selected_blob"], "455950e73bd19d0a6ee02e5bdfcd86149d0cb1cb")
        self.assertEqual(report["production"]["status"], "routed")
        self.assertEqual(report["production"]["source_owned_bytes_added"], 1722)
        self.assertEqual(report["production"]["alignment_bytes"], 10)
        self.assertEqual(report["production"]["strict_relocations"], 28)
        self.assertEqual(report["production"]["guarded_redirects"], 9)


if __name__ == "__main__":
    unittest.main()
