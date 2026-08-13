#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_dashboard_watchface_manager.py"


class DashboardWatchfaceManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_dashboard_watchface_manager", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_recursive_object_closure(self) -> None:
        surface = self.report["surface"]
        expected = {
            "linked_functions": 17,
            "ghidra_discovered_functions": 9,
            "additional_recovered_functions": 8,
            "path_anchored_functions": 3,
            "body_bytes": 956,
            "reachable_instruction_bytes": 956,
            "outer_pool_regions": 1,
            "outer_pool_bytes": 88,
            "physical_bytes": 1_044,
            "direct_bl_entry_sites": 24,
            "external_direct_bl_entry_sites": 21,
            "direct_body_calls": 34,
            "internal_direct_body_calls": 3,
            "external_direct_body_calls": 31,
            "indirect_body_calls": 15,
            "stored_entry_pointers": 1,
            "strict_interior_raw_bl_decodes": 0,
            "unrecovered_direct_object_targets": 0,
        }
        for key, value in expected.items():
            self.assertEqual(surface[key], value, key)

    def test_watchface_operation_tables(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["watchface_kinds"], [1, 2, 3, 4])
        self.assertEqual(behavior["operation_table_words"], 15)
        self.assertEqual(behavior["operation_table_non_null_slots"], {1: 15, 2: 15, 3: 11, 4: 9})
        self.assertEqual(behavior["battery_slot_offset"], 0x18)
        self.assertEqual(len(behavior["forwarded_slot_offsets"]), 13)

    def test_provider_closure(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["direct_external_calls"], 31)
        self.assertEqual(boundary["easylogger"]["calls"], 30)
        self.assertEqual(boundary["g2_dashboard_state_getter_calls"], 1)
        self.assertEqual(boundary["first_party_vtable_calls"], 15)
        self.assertEqual(boundary["cmsis_freertos_calls"], 0)
        self.assertFalse(boundary["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
