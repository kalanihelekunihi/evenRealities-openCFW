#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cb_ble_status.py"


class CbBleStatusClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_cb_ble_status", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_complete_object_closure(self) -> None:
        expected = {
            "linked_functions": 3,
            "ghidra_discovered_functions": 3,
            "additional_recovered_functions": 0,
            "path_anchored_functions": 2,
            "body_bytes": 168,
            "reachable_instruction_bytes": 168,
            "outer_pool_regions": 1,
            "outer_pool_bytes": 34,
            "physical_bytes": 202,
            "direct_bl_entry_sites": 10,
            "external_direct_bl_entry_sites": 10,
            "direct_body_calls": 13,
            "internal_direct_body_calls": 0,
            "external_direct_body_calls": 13,
            "indirect_body_calls": 0,
            "stored_entry_pointers": 0,
            "strict_interior_raw_bl_decodes": 0,
            "unrecovered_direct_object_targets": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.report["surface"][key], value, key)

    def test_callback_contract(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["callback_list_address"], 0x20073F6C)
        self.assertTrue(behavior["null_registration_rejected"])
        self.assertTrue(behavior["null_unregistration_rejected"])
        self.assertTrue(behavior["notify_uses_in_out_status_word"])

    def test_provider_closure(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["direct_external_calls"], 13)
        self.assertEqual(boundary["easylogger_calls"], 10)
        self.assertEqual(boundary["first_party_callback_manager_calls"], 3)
        self.assertEqual(boundary["cmsis_freertos_calls"], 0)
        self.assertEqual(boundary["cordio_calls"], 0)
        self.assertEqual(boundary["iar_dlib_calls"], 0)
        self.assertFalse(boundary["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
