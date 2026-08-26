#!/usr/bin/env python3
"""Guard the Cordio ATT server write processors and live roots."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_atts_write.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_atts_write", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttsWriteAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_complete_write_object_is_closed(self) -> None:
        module = self.analyzer.analyze()["module"]
        self.assertEqual(module["classification"], "linked_eatt_server_write_processors")
        self.assertEqual(module["physical_bytes"], 1228)
        self.assertEqual(module["linked_function_count"], 4)
        self.assertEqual(module["linked_function_bytes"], 1220)
        self.assertEqual(module["owned_noncode_bytes"], 8)
        self.assertEqual(module["source_inventory_functions"], 5)
        self.assertEqual(module["source_only_functions"], ["AttsContinueWriteReq"])
        self.assertEqual(module["direct_callee_sites"], 28)
        self.assertEqual(module["raw_bl_like_wide_instruction_overlaps"], 1)
        self.assertEqual(module["strict_interior_pointers"], 0)

    def test_live_write_method_roots_are_exact(self) -> None:
        dispatch = self.analyzer.analyze()["dispatch"]
        self.assertEqual(dispatch["processor_table_live_sram"], 0x2000045C)
        self.assertEqual(dispatch["methods"]["9"]["entry"], 0x005A5E3B)
        self.assertEqual(dispatch["methods"]["10"]["entry"], 0x005A5E3B)
        self.assertEqual(dispatch["methods"]["11"]["entry"], 0x005A5FC3)
        self.assertEqual(dispatch["methods"]["12"]["entry"], 0x005A6171)
        self.assertTrue(dispatch["initializer_stream_is_not_runtime_table"])

    def test_eatt_prepare_queue_and_lineage_are_pinned(self) -> None:
        report = self.analyzer.analyze()
        self.assertTrue(report["architecture"]["per_connection_prepare_write_queues"])
        self.assertTrue(report["architecture"]["response_pending_state_supported"])
        self.assertFalse(report["architecture"]["continue_pending_response_api_linked"])
        self.assertEqual(report["abi"]["prep_write_queues_offset"], 0x238)
        self.assertEqual(report["lineage"]["selected_blob"], "1b41582c58124a49014317b987f304dd216ce100")
        self.assertEqual(report["production"]["status"], "routed")
        self.assertEqual(report["production"]["source_owned_bytes_added"], 1644)
        self.assertEqual(report["production"]["alignment_bytes"], 12)
        self.assertEqual(report["production"]["strict_relocations"], 25)
        self.assertEqual(report["production"]["guarded_redirects"], 4)


if __name__ == "__main__":
    unittest.main()
