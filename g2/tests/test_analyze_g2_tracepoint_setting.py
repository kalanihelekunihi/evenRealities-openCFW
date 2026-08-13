#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_tracepoint_setting.py"


class TracepointSettingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_tracepoint_setting", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_closed_object(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 21)
        self.assertEqual(surface["path_anchored_functions"], 9)
        self.assertEqual(surface["additional_recovered_functions"], 12)
        self.assertEqual(surface["recursive_decode_recoveries"], 4)
        self.assertEqual(surface["body_bytes"], 5_100)
        self.assertEqual(surface["literal_pool_bytes"], 488)
        self.assertEqual(surface["physical_bytes"], 5_588)
        self.assertEqual(surface["external_direct_bl_entry_sites"], 0)
        self.assertEqual(surface["stored_entry_pointers"], 1)
        self.assertEqual(surface["strict_interior_raw_bl_decodes"], 0)
        self.assertEqual(surface["unrecovered_direct_object_targets"], 0)

    def test_protocol_behavior(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["directory"], "/log/tp")
        self.assertEqual(behavior["filename_pattern"], "tp_%u.bin")
        self.assertEqual(behavior["display_name_pattern"], "%c:%c%u")
        self.assertEqual(behavior["roles"], ["L", "R"])
        self.assertEqual(
            behavior["commands"],
            ["heartbeat", "file-list", "delete-file", "delete-all"],
        )

    def test_provider_provenance(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["provider_rows"], 5)
        self.assertEqual(boundary["direct_external_targets"], 29)
        self.assertEqual(boundary["direct_external_calls"], 252)
        self.assertEqual(boundary["easylogger"]["calls"], 205)
        self.assertEqual(boundary["nanopb"]["selected_version"], "0.4.9")
        self.assertIsNone(boundary["nanopb"]["exact_g2_point_release"])
        self.assertEqual(boundary["littlefs"]["wrapper_calls"], 14)
        self.assertEqual(boundary["littlefs"]["direct_calls"], 0)
        self.assertEqual(boundary["iar_dlib"]["calls"], 19)
        self.assertFalse(boundary["iar_dlib"]["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
