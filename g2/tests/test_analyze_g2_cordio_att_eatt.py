#!/usr/bin/env python3
"""Guard the fail-closed exclusion of the optional Cordio EATT core."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_att_eatt.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_att_eatt", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttEattAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_all_eatt_core_definitions_are_absent(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["classification"], "not_linked_or_dead_stripped")
        self.assertEqual(module["linked_function_count"], 0)
        self.assertEqual(module["source_inventory_functions"], 26)
        self.assertEqual(len(module["source_only_functions"]), 26)

    def test_initializer_and_coc_closure_are_positive(self) -> None:
        exclusion = self.report["exclusion"]
        self.assertEqual(exclusion["att_control_block"], 0x200610AC)
        self.assertEqual(exclusion["eatt_handler_offset"], 0x4C)
        self.assertEqual(exclusion["eatt_dm_callback_offset"], 0x50)
        self.assertEqual(exclusion["eatt_l2c_data_req_offset"], 0x54)
        self.assertEqual(exclusion["eatt_core_initializers"], 0)
        self.assertEqual(exclusion["l2cap_coc_linked_functions"], 0)
        self.assertEqual(exclusion["public_tree_consumers_outside_translation_unit"], 0)

    def test_source_family_and_production_boundary_are_explicit(self) -> None:
        self.assertEqual(self.report["lineage"]["selected_optional_blob"], "330d9efe93ef9c994dc996b54efcd3c3d6a2b135")
        self.assertFalse(self.report["lineage"]["stock_body_version_discriminated"])
        self.assertEqual(self.report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
