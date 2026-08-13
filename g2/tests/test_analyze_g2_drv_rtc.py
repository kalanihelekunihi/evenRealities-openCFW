#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_drv_rtc.py"


class DrvRtcClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_drv_rtc", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_complete_object_closure(self) -> None:
        expected = {
            "linked_functions": 1,
            "ghidra_discovered_functions": 1,
            "additional_recovered_functions": 0,
            "path_anchored_functions": 1,
            "body_bytes": 130,
            "reachable_instruction_bytes": 130,
            "outer_pool_regions": 1,
            "outer_pool_bytes": 22,
            "physical_bytes": 152,
            "direct_bl_entry_sites": 1,
            "external_direct_bl_entry_sites": 1,
            "direct_body_calls": 7,
            "internal_direct_body_calls": 0,
            "external_direct_body_calls": 7,
            "indirect_body_calls": 0,
            "stored_entry_pointers": 0,
            "strict_interior_raw_bl_decodes": 0,
            "unrecovered_direct_object_targets": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.report["surface"][key], value, key)

    def test_ambiq_utility_and_hal_sources_are_identified(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["ambiq_calendar_utility_calls"], 1)
        self.assertEqual(boundary["ambiq_rtc_hal_calls"], 1)
        self.assertEqual(boundary["easylogger_calls"], 5)
        self.assertEqual(boundary["selected_sdk_revision"], "release_sdk5p1p0-366b80e084")
        self.assertEqual(boundary["selected_public_commit"], "5efc0228528a8adce5eae0d226fac85d2551eb3b")
        self.assertTrue(boundary["executable_logic_compatible_with_5_0_0"])
        self.assertFalse(boundary["new_version_discriminator"])

    def test_compatibility_behavior_is_explicit(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["calendar_helper"], "am_util_time_computeDayofWeek")
        self.assertEqual(behavior["rtc_setter"], "am_hal_rtc_time_set")
        self.assertEqual(behavior["input_year_base"], 2000)
        self.assertEqual(behavior["success_return"], 0)
        self.assertEqual(behavior["failure_return"], 1)
        self.assertIn("year % 400 != 0", behavior["leap_predicate"])

    def test_existing_source_replacement_is_production_routed(self) -> None:
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["patch_name"], "replace_rtc_time_set")
        self.assertEqual(production["target_function"], "open_cfw_rtc_time_set")


if __name__ == "__main__":
    unittest.main()
