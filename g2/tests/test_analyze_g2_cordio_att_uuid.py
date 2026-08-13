#!/usr/bin/env python3
"""Guard the linker-retained Cordio ATT UUID object census."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_att_uuid.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_att_uuid", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttUuidAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_complete_constant_inventory_is_accounted(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["classification"], "partially_linked_constant_object")
        self.assertEqual(module["source_inventory_objects"], 152)
        self.assertEqual(module["linked_object_count"], 11)
        self.assertEqual(module["source_only_object_count"], 141)
        self.assertEqual(len(module["source_only_objects"]), 141)
        self.assertIn("attGapSvcUuid", module["source_only_objects"])
        self.assertIn("attSsfChUuid", module["source_only_objects"])

    def test_retained_block_and_reference_topology_are_exact(self) -> None:
        module = self.report["module"]
        objects = self.report["objects"]
        self.assertEqual(module["start"], 0x0078F53A)
        self.assertEqual(module["end_exclusive"], 0x0078F550)
        self.assertEqual(module["linked_data_bytes"], 22)
        self.assertEqual(module["stored_reference_cells"], 54)
        self.assertEqual(module["unaligned_reference_windows"], 0)
        self.assertEqual(objects["attGattSvcUuid"], {"address": 0x0078F53A, "uuid16": 0x1801, "reference_cells": 1})
        self.assertEqual(objects["attChUuid"]["reference_cells"], 23)
        self.assertEqual(objects["attGattDbhChUuid"]["address"], 0x0078F54E)
        self.assertEqual(self.report["boundaries"]["following_att_uuid_owner"], "atts_read.c")

    def test_exact_source_lineage_and_production_boundary_are_explicit(self) -> None:
        lineage = self.report["lineage"]
        self.assertEqual(lineage["selected_blob"], "52cda51039c7665b66711cb45093395b0d55da34")
        self.assertTrue(lineage["r4_byte_identical"])
        self.assertTrue(lineage["legacy_family_also_contains_all_linked_objects"])
        self.assertFalse(lineage["independently_release_discriminating"])
        self.assertFalse(lineage["historical_generating_commit_resolved"])
        self.assertEqual(self.report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
