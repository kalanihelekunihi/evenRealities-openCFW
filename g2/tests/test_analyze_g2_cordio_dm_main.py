#!/usr/bin/env python3
"""Guard the complete G2 Cordio DM-router evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_dm_main.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_dm_main", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioDmMainAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_complete_router_tables_abi_and_lineage_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        routing = report["routing"]
        self.assertEqual(module["linked_function_count"], 16)
        self.assertEqual(module["linked_function_bytes"], 484)
        self.assertEqual(module["physical_bytes"], 508)
        self.assertEqual(module["source_only_functions"], [])
        self.assertEqual(module["direct_bl_ingress_sites"], 29)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertEqual(routing["hci_route_entries"], 90)
        self.assertEqual(routing["event_length_entries"], 92)
        self.assertEqual(routing["component_interface_slots"], 21)
        self.assertEqual(routing["message_component_shift"], 3)
        self.assertEqual(routing["message_ordinal_mask"], 7)
        self.assertEqual(routing["request_peer_sca_route_value"], 22)
        self.assertEqual(report["abi"]["dm_num_adv_sets"], 2)
        self.assertEqual(report["abi"]["dm_num_phys"], 2)
        self.assertFalse(report["lineage"]["historical_generating_commit_resolved"])
        readiness = report["readiness"]
        self.assertEqual(readiness["provider_seams"], 4)
        self.assertEqual(readiness["valid_non_vacuous_closure_profiles"], 4)
        self.assertEqual(readiness["linked_unresolved_symbols"], 0)
        self.assertTrue(readiness["r441_build_is_hybrid"])
        self.assertEqual(report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
