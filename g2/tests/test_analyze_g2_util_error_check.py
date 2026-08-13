#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_util_error_check.py"


class UtilErrorCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_util_error_check", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_physical_object_is_closed(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 1)
        self.assertEqual(surface["path_anchored_functions"], 1)
        self.assertEqual(surface["body_bytes"], 178)
        self.assertEqual(surface["literal_pool_bytes"], 34)
        self.assertEqual(surface["physical_bytes"], 212)
        self.assertEqual(surface["external_direct_bl_entry_sites"], 103)
        self.assertEqual(surface["direct_body_calls"], 8)
        self.assertEqual(surface["stored_entry_pointers"], 0)
        self.assertEqual(surface["strict_interior_raw_bl_decodes"], 0)
        self.assertEqual(surface["unrecovered_direct_object_targets"], 0)

    def test_goodix_source_version_is_exactly_discriminated(self) -> None:
        lineage = self.report["goodix_source_lineage"]
        self.assertEqual(lineage["exact_source_snapshot_version"], "1.7.0")
        self.assertEqual(lineage["source_table_rows"], 43)
        self.assertEqual(lineage["stock_table_rows"], 43)
        self.assertEqual(lineage["stock_table_bytes"], 344)
        self.assertEqual(lineage["first_located_incompatible_version"], "2.0.1")
        self.assertTrue(lineage["official_2_0_2_confirms_incompatible_blob"])

    def test_commit_claim_is_qualified(self) -> None:
        lineage = self.report["goodix_source_lineage"]
        self.assertEqual(
            lineage["selected_public_carrier_commit"],
            "854c43e0b96a24051ffce4c06ff629255aa56c59",
        )
        self.assertEqual(
            lineage["selected_git_blob"],
            "d5027735dd01b0948a7315d9c595356fcb91f59b",
        )
        self.assertIsNone(lineage["exact_generating_commit"])
        self.assertFalse(lineage["public_carrier_is_official_goodix_release_commit"])

    def test_local_delta_and_provider_boundary(self) -> None:
        delta = self.report["local_delta"]
        self.assertIn("APP_errorFaultHandler", delta["handler_name"])
        self.assertIn("fallback", delta["removed_behavior"])
        providers = self.report["provider_boundary"]
        self.assertEqual(providers["provider_rows"], 3)
        self.assertEqual(providers["direct_external_targets"], 5)
        self.assertEqual(providers["direct_external_calls"], 8)

    def test_hidden_copied_dependency_is_not_a_linked_goodix_stack(self) -> None:
        identity = self.report["identity"]
        self.assertEqual(identity["source_derived_third_party_functions"], ["APP_errorFaultHandler"])
        self.assertEqual(
            identity["source_derived_third_party_data_regions"],
            ["[0x006C8E60,0x006C8FB8)"],
        )
        self.assertFalse(identity["goodix_ble_stack_linkage_proven"])
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
