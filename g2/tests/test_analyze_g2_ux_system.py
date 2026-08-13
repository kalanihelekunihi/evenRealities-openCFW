#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_ux_system.py"


class UxSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_ux_system", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_recursive_object_closure(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 11)
        self.assertEqual(surface["ghidra_discovered_functions"], 10)
        self.assertEqual(surface["additional_recovered_functions"], 1)
        self.assertEqual(surface["path_anchored_functions"], 2)
        self.assertEqual(surface["baseline_ghidra_path_anchors"], 1)
        self.assertEqual(surface["body_bytes"], 2_668)
        self.assertEqual(surface["reachable_instruction_bytes"], 2_668)
        self.assertEqual(surface["embedded_data_regions"], 0)
        self.assertEqual(surface["outer_pool_regions"], 1)
        self.assertEqual(surface["outer_pool_bytes"], 200)
        self.assertEqual(surface["physical_bytes"], 2_868)
        self.assertEqual(surface["direct_bl_entry_sites"], 51)
        self.assertEqual(surface["external_direct_bl_entry_sites"], 35)
        self.assertEqual(surface["direct_body_calls"], 163)
        self.assertEqual(surface["internal_direct_body_calls"], 16)
        self.assertEqual(surface["external_direct_body_calls"], 147)
        self.assertEqual(surface["stored_entry_pointers"], 1)
        self.assertEqual(surface["strict_interior_raw_bl_decodes"], 0)
        self.assertEqual(surface["unrecovered_direct_object_targets"], 0)

    def test_system_status_protocol(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(set(behavior["status_ids"]), {"1", "2", "3", "4", "5", "6"})
        self.assertEqual(set(behavior["packed_status_bits"]), {"0", "1", "2", "3", "4", "5", "6"})
        self.assertEqual(behavior["peer_service_id"], "0x0103")
        self.assertTrue(behavior["ring_mac_guarded_sync"])
        self.assertIn("bits 2 and 3", behavior["system_ble_status"])

    def test_existing_third_party_seam_only(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["provider_rows"], 4)
        self.assertEqual(boundary["direct_external_targets"], 17)
        self.assertEqual(boundary["direct_external_calls"], 147)
        self.assertEqual(boundary["easylogger"]["diagnostic_calls"], 95)
        self.assertEqual(boundary["easylogger"]["version"], "2.2.99 source-equivalent core")
        self.assertEqual(
            boundary["easylogger"]["selected_commit"],
            "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
        )
        self.assertEqual(boundary["g2_first_party_calls"], 52)
        self.assertFalse(boundary["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertEqual(
            self.report["identity"]["ownership"],
            "g2_local_system_status_and_ring_sync_policy",
        )
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
