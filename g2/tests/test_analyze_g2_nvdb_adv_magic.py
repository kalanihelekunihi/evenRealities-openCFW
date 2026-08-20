#!/usr/bin/env python3
"""Guard the bounded first-party NVDB advertising-magic audit."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_nvdb_adv_magic.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_nvdb_adv_magic", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class NvdbAdvMagicAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_surface_and_ingress_are_closed(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 3)
        self.assertEqual(surface["body_bytes"], 110)
        self.assertEqual(surface["physical_bytes"], 120)
        self.assertEqual(surface["literal_bytes"], 10)
        self.assertEqual(surface["direct_bl_ingress_sites"], 2)
        self.assertEqual(surface["direct_provider_calls"], 6)
        self.assertEqual(
            surface["stored_entry_pointers"],
            [(0x006D1E7C, 0x005D9ED1), (0x0078F514, 0x005D9EE5)],
        )
        self.assertEqual(surface["stored_strict_interior_pointers"], 0)
        self.assertEqual(surface["direct_strict_interior_branches"], 0)

    def test_record_and_migration_policy_are_pinned(self) -> None:
        record = self.report["record"]
        self.assertEqual(record["address"], 0x200038D4)
        self.assertEqual(record["boot_hex"], "01200000")
        self.assertEqual(record["version"], 1)
        self.assertEqual(record["magic"], 0x20)
        self.assertEqual(record["boot_crc16"], 0)
        self.assertEqual(record["initialized_crc16"], 0x0A5C)
        self.assertEqual(record["key"], "nvAdvMagic")
        behavior = self.report["behavior"]
        self.assertTrue(behavior["v0_crc_mismatch_rewrites_current_magic"])
        self.assertFalse(behavior["v1_crc_mismatch_rewrites_current_magic"])
        self.assertFalse(behavior["read_payload_copied_into_current_record"])

    def test_lineage_and_production_claims_are_conservative(self) -> None:
        self.assertIsNone(self.report["lineage"]["retained_path"])
        self.assertIsNone(self.report["lineage"]["retained_exact_symbol"])
        self.assertFalse(self.report["lineage"]["whole_file_source_exact"])
        self.assertFalse(self.report["lineage"]["historical_generating_commit_resolved"])

    def test_production_routed(self) -> None:
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 110)
        self.assertEqual(production["retained_stock_noncode_bytes"], 10)
        self.assertEqual(production["toolchain_profiles"], ["apple-clang"])
        self.assertEqual(
            production["relocated_leaves"],
            [
                "open_cfw_nvdb_adv_magic_default_crc_initialize",
                "open_cfw_nvdb_adv_magic_load_and_migrate",
                "open_cfw_nvdb_adv_magic_update",
            ],
        )
        self.assertEqual(
            production["patch_sites"],
            [
                "replace_nvdb_adv_magic_default_crc_initialize",
                "replace_nvdb_adv_magic_load_and_migrate",
                "replace_nvdb_adv_magic_update",
            ],
        )

    def test_mutated_image_is_rejected(self) -> None:
        data = bytearray(self.analyzer.IMAGE.read_bytes())
        data[0x005D9F2A - self.analyzer.BASE] ^= 1
        with tempfile.NamedTemporaryFile() as handle:
            handle.write(data)
            handle.flush()
            with self.assertRaises(self.analyzer.AuditError):
                self.analyzer.analyze(Path(handle.name))


if __name__ == "__main__":
    unittest.main()
