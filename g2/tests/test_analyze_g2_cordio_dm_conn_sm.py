#!/usr/bin/env python3
"""Guard the complete G2 Cordio connection state-machine evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_dm_conn_sm.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_dm_conn_sm", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioDmConnSmAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_function_table_action_sets_and_lineage_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        state = report["state_machine"]
        self.assertEqual(module["linked_function_count"], 1)
        self.assertEqual(module["linked_function_bytes"], 1_598)
        self.assertEqual(module["physical_bytes"], 1_656)
        self.assertEqual(module["literal_pool_bytes"], 58)
        self.assertEqual(module["direct_bl_ingress_sites"], 2)
        self.assertEqual(module["direct_logger_relocations"], 90)
        self.assertEqual(module["stored_function_pointers"], 0)
        self.assertEqual((state["states"], state["events"]), (5, 8))
        self.assertEqual(state["event_mask"], 7)
        self.assertEqual(state["ccb_state_offset"], 0x15)
        self.assertEqual(state["message_event_offset"], 2)
        self.assertEqual(state["action_set_count"], 3)
        self.assertEqual(state["action_set_global"], 0x20073FE4)
        self.assertEqual(len(state["action_tables"]), 3)
        readiness = report["readiness"]
        self.assertEqual(readiness["provider_seams"], 2)
        self.assertEqual(readiness["valid_non_vacuous_closure_profiles"], 2)
        self.assertEqual(readiness["linked_unresolved_symbols"], 0)
        production = report["production"]
        self.assertEqual(production["status"], "production-routed")
        self.assertEqual(production["redirected_stock_functions"], 1)
        self.assertEqual(production["redirected_stock_bytes"], 1_598)
        self.assertEqual(production["source_owned_bytes_added"], 120)
        self.assertEqual(production["alignment_bytes_added"], 0)
        self.assertEqual(production["strict_relocations"], 2)
        self.assertEqual(production["retained_state_table_bytes"], 80)
        self.assertEqual(production["retained_literal_pool_bytes"], 58)
        self.assertEqual(production["manifest_regions"], 2)
        self.assertEqual(production["flash_plan_counts"], (5863, 2, 5, 6))


if __name__ == "__main__":
    unittest.main()
