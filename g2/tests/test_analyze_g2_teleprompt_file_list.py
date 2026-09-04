#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_teleprompt_file_list.py"


class TelepromptFileListClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_teleprompt_file_list", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_complete_object_closure(self) -> None:
        expected = {
            "linked_functions": 3,
            "ghidra_discovered_functions": 1,
            "additional_recovered_functions": 2,
            "path_anchored_functions": 1,
            "body_bytes": 166,
            "reachable_instruction_bytes": 166,
            "outer_pool_regions": 1,
            "outer_pool_bytes": 34,
            "physical_bytes": 200,
            "direct_bl_entry_sites": 6,
            "external_direct_bl_entry_sites": 6,
            "direct_body_calls": 12,
            "internal_direct_body_calls": 0,
            "external_direct_body_calls": 12,
            "indirect_body_calls": 0,
            "stored_entry_pointers": 0,
            "strict_interior_raw_bl_decodes": 0,
            "unrecovered_direct_object_targets": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.report["surface"][key], value, key)

    def test_record_contract(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["global_record_address"], 0x201093D4)
        self.assertEqual(behavior["record_bytes"], 0xF52)
        self.assertEqual(behavior["file_count_bytes"], 2)
        self.assertEqual(behavior["payload_bytes_after_count"], 0xF50)
        self.assertTrue(behavior["update_null_is_ignored"])
        self.assertTrue(behavior["get_returns_live_global"])
        self.assertTrue(behavior["reset_zeroes_complete_record"])

    def test_provider_closure(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["direct_external_calls"], 12)
        self.assertEqual(boundary["easylogger_calls"], 10)
        self.assertEqual(boundary["iar_dlib_calls"], 2)
        self.assertEqual(boundary["nanopb_direct_calls"], 0)
        self.assertFalse(boundary["new_version_discriminator"])
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_production_routed_from_compilable_c(self) -> None:
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertFalse(production["software_gap"])
        self.assertEqual(production["source_routed_functions"], 3)
        self.assertEqual(production["source_compiled_bytes"], {
            "apple-clang": 52,
            "linux-clang": 52,
        })
        self.assertEqual(production["strict_relocations"], 2)
        self.assertEqual(production["stock_body_bytes_displaced"], 166)
        self.assertEqual(production["retained_diagnostic_pool_bytes"], 34)
        self.assertEqual(
            production["hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(production["hardware_operations"], [])


if __name__ == "__main__":
    unittest.main()
