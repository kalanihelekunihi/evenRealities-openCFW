#!/usr/bin/env python3
"""Guard the fail-closed exclusion of the optional Cordio EATT server."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_atts_eatt.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_atts_eatt", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttsEattAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_all_optional_server_definitions_are_absent(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["classification"], "not_linked_or_dead_stripped")
        self.assertEqual(module["linked_function_count"], 0)
        self.assertEqual(module["source_inventory_functions"], 12)
        self.assertEqual(len(module["source_only_functions"]), 12)
        self.assertEqual(module["retained_path_anchors"], 0)

    def test_default_interface_and_provider_closures_exclude_overrides(self) -> None:
        exclusion = self.report["exclusion"]
        self.assertEqual(exclusion["att_control_block"], 0x200610AC)
        self.assertEqual(exclusion["eatt_server_interface_offset"], 0x44)
        self.assertEqual(exclusion["default_eatt_server_interface"], 0x007851F0)
        self.assertEqual(exclusion["eatt_server_initializers"], 0)
        self.assertEqual(exclusion["att_ccb_by_conn_id_callers"], [0x004B4E10, 0x004B4E58, 0x004B5208])
        self.assertEqual(exclusion["handle_value_worker_callers"], [0x00533ED2, 0x00533EEE])
        self.assertEqual(exclusion["l2cap_coc_linked_functions"], 0)

    def test_optional_source_and_production_boundary_are_explicit(self) -> None:
        self.assertEqual(self.report["lineage"]["selected_optional_blob"], "f1ca4879c8c32ef42127971399592329ca084680")
        self.assertFalse(self.report["lineage"]["stock_body_version_discriminated"])
        self.assertEqual(self.report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
