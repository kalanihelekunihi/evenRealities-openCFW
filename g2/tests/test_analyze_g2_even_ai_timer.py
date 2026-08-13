#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_even_ai_timer.py"


class EvenAiTimerClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_even_ai_timer", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_complete_object_closure(self) -> None:
        expected = {
            "linked_functions": 13,
            "ghidra_discovered_functions": 3,
            "additional_recovered_functions": 10,
            "path_anchored_functions": 2,
            "body_bytes": 856,
            "reachable_instruction_bytes": 856,
            "outer_pool_regions": 1,
            "outer_pool_bytes": 100,
            "physical_bytes": 956,
            "direct_bl_entry_sites": 28,
            "external_direct_bl_entry_sites": 16,
            "direct_body_calls": 57,
            "internal_direct_body_calls": 12,
            "external_direct_body_calls": 45,
            "indirect_body_calls": 0,
            "stored_entry_pointers": 0,
            "strict_interior_raw_bl_decodes": 0,
            "unrecovered_direct_object_targets": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.report["surface"][key], value, key)

    def test_private_tick_timer_contract(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["common_timer_record"], 0x20074008)
        self.assertEqual(behavior["heartbeat_timer_record"], 0x20074014)
        self.assertEqual(behavior["timer_record_bytes"], 12)
        self.assertEqual(
            behavior["record_fields"],
            {"start_tick": 0, "duration_ticks": 4, "state": 8, "armed": 9},
        )
        self.assertEqual(behavior["heartbeat_default_ticks"], 10_000)
        self.assertEqual(behavior["common_restart_ticks"], 3_000)
        self.assertFalse(behavior["uses_cmsis_software_timers"])

    def test_provider_closure(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["direct_external_calls"], 45)
        self.assertEqual(boundary["easylogger_calls"], 30)
        self.assertEqual(boundary["cmsis_freertos_tick_calls"], 4)
        self.assertEqual(boundary["iar_dlib_calls"], 1)
        self.assertEqual(boundary["first_party_calls"], 10)
        self.assertEqual(
            boundary["cmsis_freertos_commit"],
            "d213f261b5be6bb29a7cce8b84071706b72f4d53",
        )
        self.assertFalse(boundary["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
