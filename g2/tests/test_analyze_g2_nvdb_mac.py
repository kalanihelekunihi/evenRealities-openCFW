#!/usr/bin/env python3
"""Guard the bounded first-party NVDB MAC audit."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_nvdb_mac.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_nvdb_mac", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class NvdbMacAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_surface_and_ingress_are_closed(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 3)
        self.assertEqual(surface["body_bytes"], 280)
        self.assertEqual(surface["physical_bytes"], 312)
        self.assertEqual(surface["literal_bytes"], 32)
        self.assertEqual(surface["direct_bl_ingress_sites"], 2)
        self.assertEqual(surface["direct_provider_calls"], 18)
        self.assertEqual(
            surface["stored_entry_pointers"],
            [(0x006D1E8C, 0x005D9F49), (0x0078F51C, 0x005D9FC3)],
        )
        self.assertEqual(surface["stored_strict_interior_pointers"], 0)
        self.assertEqual(surface["direct_strict_interior_branches"], 0)

    def test_record_and_address_derivation_are_pinned(self) -> None:
        record = self.report["record"]
        self.assertEqual(record["address"], 0x200038E4)
        self.assertEqual(record["boot_hex"], "01000000000000000000")
        self.assertEqual(record["version"], 1)
        self.assertEqual(record["key"], "nvMAC")
        self.assertEqual(record["example_initialized_hex"], "0147e23b4411c800ef1d")
        derivation = self.report["derivation"]
        self.assertEqual(
            derivation["serial_order"],
            "CHIPID1 little-endian, then CHIPID0 little-endian",
        )
        self.assertEqual(derivation["last_octet_mask"], "(value & 0xFC) | 0xC0")
        self.assertEqual(derivation["record_crc_coverage_bytes"], 8)

    def test_migration_lineage_and_production_claims_are_conservative(self) -> None:
        behavior = self.report["behavior"]
        self.assertTrue(behavior["missing_record_rewrites_current_address"])
        self.assertTrue(behavior["v0_crc_mismatch_rewrites_current_address"])
        self.assertFalse(behavior["v1_crc_mismatch_rewrites_current_address"])
        self.assertFalse(behavior["read_payload_copied_into_current_record"])
        self.assertEqual(self.report["lineage"]["retained_exact_symbol"], "_nvdbUpdataMac")
        self.assertFalse(self.report["lineage"]["whole_file_source_exact"])
        self.assertFalse(self.report["lineage"]["historical_generating_commit_resolved"])
        self.assertFalse(self.report["production"]["production_routed"])
        self.assertEqual(self.report["production"]["ownership_bytes"], 0)

    def test_mutated_image_is_rejected(self) -> None:
        data = bytearray(self.analyzer.IMAGE.read_bytes())
        data[0x005D9FA4 - self.analyzer.BASE] ^= 1
        with tempfile.NamedTemporaryFile() as handle:
            handle.write(data)
            handle.flush()
            with self.assertRaises(self.analyzer.AuditError):
                self.analyzer.analyze(Path(handle.name))


if __name__ == "__main__":
    unittest.main()
