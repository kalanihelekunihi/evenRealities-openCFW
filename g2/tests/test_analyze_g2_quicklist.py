#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_quicklist.py"


class QuicklistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_quicklist", ANALYZER)
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
            "body_bytes": 310, "reachable_instruction_bytes": 310,
            "outer_pool_regions": 1, "outer_pool_bytes": 50, "physical_bytes": 360,
            "direct_bl_entry_sites": 25, "external_direct_bl_entry_sites": 24,
            "direct_body_calls": 22, "internal_direct_body_calls": 1,
            "external_direct_body_calls": 21, "stored_entry_pointers": 1,
            "strict_interior_raw_bl_decodes": 0, "unrecovered_direct_object_targets": 0,
        }
        for key, value in expected.items(): self.assertEqual(surface[key], value, key)

    def test_policy_and_provider_closure(self) -> None:
        self.assertEqual(self.report["behavior"]["handled_common_events"], [0])
        self.assertEqual(self.report["behavior"]["mutex_acquire_timeout"], "osWaitForever")
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["direct_external_calls"], 21)
        self.assertEqual(boundary["easylogger"]["calls"], 15)
        self.assertEqual(boundary["cmsis_freertos"]["calls"], 3)
        self.assertEqual(boundary["cmsis_freertos"]["version"], "v10.5.1")
        self.assertTrue(boundary["nanopb"]["through_first_party_quicklist_provider"])
        self.assertFalse(boundary["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
