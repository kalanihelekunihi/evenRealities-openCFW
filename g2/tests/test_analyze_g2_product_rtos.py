#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_product_rtos.py"


class ProductRtosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_product_rtos", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_closed_object(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 13)
        self.assertEqual(surface["path_anchored_functions"], 1)
        self.assertEqual(surface["additional_recovered_functions"], 12)
        self.assertEqual(surface["body_bytes"], 512)
        self.assertEqual(surface["literal_pool_bytes"], 36)
        self.assertEqual(surface["physical_bytes"], 548)
        self.assertEqual(surface["external_direct_bl_entry_sites"], 13)
        self.assertEqual(surface["stored_entry_pointers"], 0)
        self.assertEqual(surface["strict_interior_raw_bl_decodes"], 0)
        self.assertEqual(surface["unrecovered_direct_object_targets"], 0)

    def test_task_vote_and_hook_behavior(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["vote_slots"], 32)
        self.assertEqual(behavior["vote_state_bytes"], 0x108)
        self.assertTrue(behavior["deep_sleep_requires_zero_active_votes"])
        self.assertEqual(
            behavior["watchdog_feed_hooks"],
            ["pre-sleep", "post-sleep", "idle"],
        )
        self.assertEqual(behavior["freertos_config"]["configUSE_IDLE_HOOK"], 1)
        self.assertEqual(behavior["freertos_config"]["configUSE_TICK_HOOK"], 0)

    def test_provider_provenance_and_ambiq_discriminator(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["provider_rows"], 6)
        self.assertEqual(boundary["direct_external_targets"], 9)
        self.assertEqual(boundary["direct_external_calls"], 18)
        self.assertEqual(boundary["cmsis_freertos"]["version"], "v10.5.1")
        self.assertTrue(boundary["cmsis_freertos"]["production_source_owned"])
        ambiq = boundary["ambiq_hal"]
        self.assertEqual(ambiq["selected_source_equivalent_version"], "5.1.0")
        self.assertEqual(ambiq["stock_sleep_wfi_count"], 2)
        self.assertEqual(ambiq["sdk_5_0_sleep_wfi_count"], 1)
        self.assertEqual(ambiq["sdk_5_1_sleep_wfi_count"], 2)
        self.assertTrue(ambiq["build_predates_public_import"])
        self.assertIsNone(ambiq["exact_private_pre_release_commit"])
        self.assertFalse(boundary["iar_dlib"]["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
