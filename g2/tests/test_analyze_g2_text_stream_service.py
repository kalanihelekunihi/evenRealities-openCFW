#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_text_stream_service.py"


class TextStreamServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_text_stream_service", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_recursive_object_closure(self) -> None:
        surface = self.report["surface"]
        expected = {
            "linked_functions": 26,
            "ghidra_discovered_functions": 8,
            "additional_recovered_functions": 18,
            "path_anchored_functions": 1,
            "body_bytes": 3_188,
            "reachable_instruction_bytes": 3_188,
            "outer_pool_regions": 3,
            "outer_pool_bytes": 40,
            "physical_bytes": 3_228,
            "direct_bl_entry_sites": 65,
            "external_direct_bl_entry_sites": 34,
            "direct_body_calls": 144,
            "internal_direct_body_calls": 31,
            "external_direct_body_calls": 113,
            "indirect_body_calls": 7,
            "pc_relative_callback_constructions": 1,
            "stored_entry_pointers": 0,
            "strict_interior_raw_bl_decodes": 0,
            "unrecovered_direct_object_targets": 0,
        }
        for key, value in expected.items():
            self.assertEqual(surface[key], value, key)

    def test_utf8_animation_contract(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["service_struct_bytes"], 0x30)
        self.assertEqual(behavior["initial_text_capacity_bytes"], 0x200)
        self.assertEqual(behavior["default_animation_period_ticks"], 100)
        self.assertEqual(behavior["utf8_code_point_widths"], [1, 2, 3, 4])
        self.assertEqual(behavior["callback_field_offset"], 0x18)
        self.assertEqual(behavior["callback_dispatch_sites"], 7)
        self.assertEqual(behavior["animation_presets"], 4)

    def test_provider_closure(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["direct_external_calls"], 113)
        self.assertEqual(boundary["easylogger_calls"], 10)
        self.assertEqual(boundary["cmsis_freertos"]["calls"], 39)
        self.assertEqual(boundary["cmsis_freertos"]["version"], "v10.5.1")
        self.assertEqual(boundary["lvgl"]["calls"], 17)
        self.assertEqual(boundary["nanopb"]["calls"], 5)
        self.assertEqual(boundary["tlsf_allocator_wrappers"]["calls"], 9)
        self.assertEqual(boundary["iar_dlib_calls"], 22)
        self.assertFalse(boundary["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
