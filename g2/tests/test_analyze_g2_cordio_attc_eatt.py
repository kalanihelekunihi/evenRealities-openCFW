#!/usr/bin/env python3
"""Guard the fail-closed exclusion of the optional Cordio EATT client."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_attc_eatt.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_attc_eatt", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttcEattAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_all_eatt_client_definitions_are_absent(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["classification"], "not_linked_or_dead_stripped")
        self.assertEqual(module["linked_function_count"], 0)
        self.assertEqual(module["source_inventory_functions"], 20)
        self.assertEqual(len(module["source_only_functions"]), 20)

    def test_default_interface_and_provider_closures_are_exact(self) -> None:
        exclusion = self.report["exclusion"]
        self.assertEqual(exclusion["eatt_client_interface_offset"], 0x48)
        self.assertEqual(exclusion["default_eatt_client_interface"], 0x007851F0)
        self.assertEqual(exclusion["eatt_client_initializers"], 0)
        self.assertEqual(exclusion["eatt_core_linked_functions"], 0)
        self.assertEqual(len(exclusion["att_msg_alloc_callers"]), 26)
        self.assertEqual(exclusion["attc_ccb_by_conn_id_callers"], [0x004B5656, 0x0053133A, 0x00531712])

    def test_source_family_and_production_boundary_are_explicit(self) -> None:
        self.assertEqual(self.report["lineage"]["selected_optional_blob"], "45305ddb59ed34713f02f9a2783b62eca25cfc04")
        self.assertFalse(self.report["lineage"]["stock_body_version_discriminated"])
        self.assertEqual(self.report["production"]["stock_bytes_replaced"], 0)


if __name__ == "__main__":
    unittest.main()
