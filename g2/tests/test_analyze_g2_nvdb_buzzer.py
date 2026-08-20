#!/usr/bin/env python3
"""Guard the bounded first-party NVDB buzzer audit."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_nvdb_buzzer.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_nvdb_buzzer", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class NvdbBuzzerAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_surface_and_ingress_are_closed(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 5)
        self.assertEqual(surface["body_bytes"], 188)
        self.assertEqual(surface["physical_bytes"], 216)
        self.assertEqual(surface["literal_bytes"], 28)
        self.assertEqual(surface["direct_bl_ingress_sites"], 5)
        self.assertEqual(surface["direct_provider_calls"], 11)
        self.assertEqual(
            surface["stored_entry_pointers"],
            [(0x006D1E84, 0x0058F9D5), (0x0078F518, 0x0058F9E9)],
        )
        self.assertEqual(surface["stored_strict_interior_pointers"], 0)
        self.assertEqual(surface["direct_strict_interior_branches"], 0)

    def test_record_and_migration_policy_are_pinned(self) -> None:
        record = self.report["record"]
        self.assertEqual(record["address"], 0x200038D8)
        self.assertEqual(record["boot_hex"], "02000000a00f00001e000000")
        self.assertEqual(record["version"], 2)
        self.assertEqual(record["frequency_hz"], 4000)
        self.assertEqual(record["duty_percent"], 30)
        self.assertEqual(record["boot_crc16"], 0)
        self.assertEqual(record["initialized_crc16"], 0x9B1E)
        self.assertEqual(record["key"], "nvBuzzer")
        self.assertTrue(self.report["behavior"]["pre_v2_crc_mismatch_rewrites_defaults"])
        self.assertFalse(self.report["behavior"]["v2_crc_mismatch_rewrites_defaults"])
        self.assertFalse(self.report["behavior"]["read_payload_copied_into_current_record"])

    def test_lineage_claims_are_conservative(self) -> None:
        self.assertEqual(self.report["lineage"]["retained_exact_symbol"], "_nvdbUpdataBuzzer")
        self.assertFalse(self.report["lineage"]["whole_file_source_exact"])
        self.assertFalse(self.report["lineage"]["historical_generating_commit_resolved"])

    def test_production_routed(self) -> None:
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 188)
        self.assertEqual(production["retained_stock_noncode_bytes"], 28)
        self.assertEqual(production["toolchain_profiles"], ["apple-clang"])
        self.assertEqual(production["relocated_leaves"], [
            "open_cfw_nvdb_buzzer_default_crc_initialize",
            "open_cfw_nvdb_buzzer_duty_get",
            "open_cfw_nvdb_buzzer_frequency_get",
            "open_cfw_nvdb_buzzer_load_and_migrate",
            "open_cfw_nvdb_buzzer_update",
        ])
        self.assertEqual(production["patch_sites"], [
            "replace_nvdb_buzzer_default_crc_initialize",
            "replace_nvdb_buzzer_duty_get",
            "replace_nvdb_buzzer_frequency_get",
            "replace_nvdb_buzzer_load_and_migrate",
            "replace_nvdb_buzzer_update",
        ])

    def test_mutated_image_is_rejected(self) -> None:
        data = bytearray(self.analyzer.IMAGE.read_bytes())
        data[0x0058FA76 - self.analyzer.BASE] ^= 1
        with tempfile.NamedTemporaryFile() as handle:
            handle.write(data)
            handle.flush()
            with self.assertRaises(self.analyzer.AuditError):
                self.analyzer.analyze(Path(handle.name))


if __name__ == "__main__":
    unittest.main()
