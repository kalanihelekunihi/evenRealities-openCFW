#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_terminal_core.py"


class TerminalCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_terminal_core", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_recursive_object_closure(self) -> None:
        surface = self.report["surface"]
        expected = {
            "linked_functions": 9,
            "ghidra_discovered_functions": 1,
            "additional_recovered_functions": 8,
            "path_anchored_functions": 1,
            "body_bytes": 1_144,
            "reachable_instruction_bytes": 1_144,
            "outer_pool_regions": 1,
            "outer_pool_bytes": 104,
            "physical_bytes": 1_248,
            "direct_bl_entry_sites": 68,
            "external_direct_bl_entry_sites": 60,
            "direct_body_calls": 73,
            "internal_direct_body_calls": 8,
            "external_direct_body_calls": 65,
            "indirect_body_calls": 0,
            "stored_entry_pointers": 3,
            "strict_interior_raw_bl_decodes": 0,
            "unrecovered_direct_object_targets": 0,
        }
        for key, value in expected.items():
            self.assertEqual(surface[key], value, key)

    def test_terminal_policy(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["terminal_display_request_message_id"], 0x30)
        self.assertEqual(behavior["terminal_display_request_bytes"], 8)
        self.assertEqual(behavior["swapped_input_event_pair"], [0x44, 0x45])
        self.assertEqual(len(behavior["terminal_command_ids"]), 13)
        self.assertEqual(behavior["terminal_command_dispatch_provider_calls"], 12)
        self.assertEqual(len(behavior["stored_callbacks"]), 3)

    def test_provider_closure(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["direct_external_calls"], 65)
        self.assertEqual(boundary["easylogger"]["calls"], 30)
        self.assertEqual(boundary["cmsis_freertos"]["calls"], 3)
        self.assertEqual(boundary["cmsis_freertos"]["version"], "v10.5.1")
        self.assertEqual(boundary["iar_dlib_calls"], 3)
        self.assertEqual(boundary["g2_first_party_calls"], 29)
        self.assertEqual(boundary["nanopb_direct_calls"], 0)
        self.assertFalse(boundary["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self) -> None:
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
