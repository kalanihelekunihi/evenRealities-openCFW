#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_logger_setting.py"


class LoggerSettingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_logger_setting", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_recursive_object_closure(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 8)
        self.assertEqual(surface["ghidra_discovered_functions"], 3)
        self.assertEqual(surface["additional_recovered_functions"], 5)
        self.assertEqual(surface["path_anchored_functions"], 2)
        self.assertEqual(surface["baseline_ghidra_path_anchors"], 1)
        self.assertEqual(surface["body_bytes"], 5_574)
        self.assertEqual(surface["reachable_instruction_bytes"], 5_466)
        self.assertEqual(surface["embedded_data_regions"], 8)
        self.assertEqual(surface["embedded_data_bytes"], 108)
        self.assertEqual(surface["outer_pool_regions"], 4)
        self.assertEqual(surface["outer_pool_bytes"], 418)
        self.assertEqual(surface["physical_bytes"], 5_992)
        self.assertEqual(surface["direct_bl_entry_sites"], 9)
        self.assertEqual(surface["external_direct_bl_entry_sites"], 1)
        self.assertEqual(surface["direct_body_calls"], 346)
        self.assertEqual(surface["internal_direct_body_calls"], 8)
        self.assertEqual(surface["external_direct_body_calls"], 338)
        self.assertEqual(surface["stored_entry_pointers"], 1)
        self.assertEqual(surface["strict_interior_raw_bl_decodes"], 0)
        self.assertEqual(surface["unrecovered_direct_object_targets"], 0)

    def test_logger_protocol_behavior(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["directory"], "/log")
        self.assertEqual(behavior["maximum_file_entries"], 20)
        self.assertEqual(behavior["file_record_bytes"], 40)
        self.assertEqual(behavior["excluded_file"], "compress_manager.bin")
        self.assertEqual(set(behavior["phone_command_ids"]), {"0", "1", "2", "4", "5", "6"})
        self.assertEqual(set(behavior["peer_event_ids"]), {"0x0B", "0x0C"})
        self.assertEqual(behavior["accepted_delete_prefixes"], ["L:/log/", "R:/log/"])
        self.assertTrue(behavior["role_and_phone_forwarding"])

    def test_existing_third_party_seams_only(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["provider_rows"], 8)
        self.assertEqual(boundary["direct_external_targets"], 32)
        self.assertEqual(boundary["direct_external_calls"], 338)
        self.assertEqual(boundary["easylogger"]["diagnostic_calls"], 250)
        self.assertEqual(boundary["easylogger"]["control_calls"], 4)
        self.assertEqual(boundary["nanopb"]["selected_version"], "0.4.9")
        self.assertEqual(boundary["nanopb"]["calls"], 16)
        self.assertIsNone(boundary["nanopb"]["exact_g2_point_release"])
        self.assertEqual(boundary["littlefs"]["wrapper_calls"], 12)
        self.assertEqual(boundary["freertos_kernel"]["version"], "V10.5.1")
        self.assertEqual(
            boundary["freertos_kernel"]["selected_commit"],
            "def7d2df2b0506d3d249334974f51e427c17a41c",
        )
        self.assertEqual(boundary["iar_dlib"]["calls"], 39)
        self.assertFalse(boundary["iar_dlib"]["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertEqual(
            self.report["identity"]["ownership"],
            "g2_local_logger_file_protocol_and_routing_policy",
        )
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
