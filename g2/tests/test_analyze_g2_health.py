#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_health.py"


class HealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_health", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_recursive_object_closure(self) -> None:
        surface = self.report["surface"]
        expected = {
            "linked_functions": 4, "ghidra_discovered_functions": 2,
            "additional_recovered_functions": 2, "path_anchored_functions": 3,
            "baseline_ghidra_path_anchors": 1, "body_bytes": 504,
            "reachable_instruction_bytes": 504, "embedded_data_regions": 0,
            "outer_pool_regions": 1, "outer_pool_bytes": 68, "physical_bytes": 572,
            "direct_bl_entry_sites": 58, "external_direct_bl_entry_sites": 57,
            "direct_body_calls": 34, "internal_direct_body_calls": 1,
            "external_direct_body_calls": 33, "stored_entry_pointers": 1,
            "strict_interior_raw_bl_decodes": 0, "unrecovered_direct_object_targets": 0,
        }
        for key, value in expected.items():
            self.assertEqual(surface[key], value, key)

    def test_mutex_and_event_policy(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["mutex_create"], "lazy osMutexNew")
        self.assertEqual(behavior["mutex_acquire_timeout"], "osWaitForever")
        self.assertEqual(behavior["handled_common_events"], [0, 5])
        self.assertIn("six-byte service-one", behavior["event_zero"])

    def test_admitted_third_party_seams(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["direct_external_calls"], 33)
        self.assertEqual(boundary["easylogger"]["diagnostic_calls"], 25)
        self.assertEqual(boundary["cmsis_freertos"]["calls"], 3)
        self.assertEqual(boundary["cmsis_freertos"]["version"], "v10.5.1")
        self.assertTrue(boundary["cmsis_freertos"]["production_source_owned"])
        self.assertEqual(boundary["nanopb"]["direct_calls"], 0)
        self.assertTrue(boundary["nanopb"]["through_first_party_health_provider"])
        self.assertFalse(boundary["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_production_routed(self) -> None:
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["candidate"], "components/apollo_main/core_overlay/health.c")
        self.assertEqual(production["ownership_bytes"], 504)
        self.assertEqual(production["compiled_leaf_bytes"], 198)
        self.assertEqual(len(production["functions"]), 4)


if __name__ == "__main__":
    unittest.main()
