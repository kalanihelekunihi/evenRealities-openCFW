#!/usr/bin/env python3
"""Guard the stock Cordio ATT core and its default EATT routing."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_att_main.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_att_main", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttMainAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_complete_core_object_is_closed(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["classification"], "linked_att_core_with_eatt_defaults")
        self.assertEqual(module["physical_bytes"], 1104)
        self.assertEqual(module["linked_function_count"], 21)
        self.assertEqual(module["linked_function_bytes"], 1030)
        self.assertEqual(module["owned_noncode_bytes"], 74)
        self.assertEqual(module["source_inventory_functions"], 23)
        self.assertEqual(module["source_only_functions"], ["attCcbByHandle", "AttMsgAlloc"])
        self.assertEqual(module["direct_bl_ingress_sites"], 65)
        self.assertEqual(module["registered_function_pointers"], 14)
        self.assertEqual(module["direct_callee_sites"], 32)
        self.assertEqual(module["strict_interior_pointers"], 0)

    def test_default_legacy_and_eatt_routing_is_pinned(self) -> None:
        dispatch = self.report["dispatch"]
        architecture = self.report["architecture"]
        self.assertEqual(dispatch["att_control_block"], 0x200610AC)
        self.assertEqual(dispatch["legacy_default_interface"], 0x007851E0)
        self.assertEqual(dispatch["eatt_default_interface"], 0x007851F0)
        self.assertEqual(dispatch["handler_pointer_cell"], 0x004B8788)
        self.assertEqual(architecture["connection_count"], 3)
        self.assertEqual(architecture["bearers_per_connection"], 3)
        self.assertEqual(architecture["handler_message_thresholds"], [0x20, 0x40, 0x60, 0x80])
        self.assertTrue(architecture["eatt_defaults_installed_by_att_handler_init"])
        self.assertFalse(architecture["enhanced_att_runtime_override_seen_in_this_tu"])

    def test_lineage_and_production_boundary_are_explicit(self) -> None:
        lineage = self.report["lineage"]
        self.assertTrue(lineage["r20_eatt_architecture_proven"])
        self.assertEqual(lineage["selected_blob"], "decbdafce60ebc2fe2b9e986ffd97207fceebcb2")
        self.assertFalse(lineage["historical_generating_commit_resolved"])
        self.assertEqual(self.report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
