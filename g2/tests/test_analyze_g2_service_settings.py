#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_service_settings.py"


class ServiceSettingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_service_settings", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_closed_object_and_recursive_recovery(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 31)
        self.assertEqual(surface["path_anchored_functions"], 13)
        self.assertEqual(surface["additional_recovered_functions"], 18)
        self.assertEqual(surface["recursive_decode_recoveries"], 11)
        self.assertEqual(surface["body_bytes"], 5_146)
        self.assertEqual(surface["literal_pool_regions"], 19)
        self.assertEqual(surface["literal_pool_bytes"], 566)
        self.assertEqual(surface["physical_bytes"], 5_712)
        self.assertEqual(surface["stored_entry_pointers"], 1)
        self.assertEqual(surface["strict_interior_raw_bl_decodes"], 0)
        self.assertEqual(surface["unrecovered_direct_object_targets"], 0)
        self.assertEqual(surface["out_of_image_false_positive_decodes"], 2)

    def test_settings_behavior(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["version"], "2.2.6.10")
        self.assertEqual(behavior["settings_record_bytes"], 28)
        self.assertEqual(behavior["settings_crc_covered_bytes"], 24)
        self.assertEqual(behavior["version_request_throttle_ticks"], 500)
        self.assertEqual(behavior["brightness_range"], [2, 100])
        self.assertEqual(behavior["head_up_angle_range_degrees"], [-90, 90])
        self.assertEqual(behavior["peer_service_id"], 9)

    def test_third_party_provider_boundary(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["provider_rows"], 8)
        self.assertEqual(boundary["direct_external_targets"], 36)
        self.assertEqual(boundary["direct_external_calls"], 317)
        self.assertEqual(boundary["cmsis_freertos"]["version"], "v10.5.1")
        self.assertEqual(
            boundary["cmsis_freertos"]["commit"],
            "d213f261b5be6bb29a7cce8b84071706b72f4d53",
        )
        self.assertEqual(boundary["easylogger"]["calls"], 250)
        self.assertEqual(boundary["iar_dlib"]["calls"], 13)
        self.assertIsNone(boundary["iar_dlib"]["exact_release"])
        self.assertFalse(boundary["iar_dlib"]["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertEqual(self.report["identity"]["ownership"], "g2_local_settings_policy")
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
