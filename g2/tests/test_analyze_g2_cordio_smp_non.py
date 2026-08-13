#!/usr/bin/env python3
"""Guard the fail-closed exclusion of Cordio's non-SMP alternative."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_smp_non.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_smp_non", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioSmpNonAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_all_non_smp_definitions_are_configuration_excluded(self) -> None:
        module = self.report["module"]
        self.assertEqual(module["classification"], "configuration_excluded_not_linked")
        self.assertEqual(module["linked_function_count"], 0)
        self.assertEqual(module["source_inventory_functions"], 3)
        self.assertEqual(
            module["source_only_functions"],
            ["smpNonL2cCtrlCback", "smpNonL2cDataCback", "SmpNonInit"],
        )

    def test_full_smp_exclusively_owns_the_smp_fixed_channel(self) -> None:
        exclusion = self.report["exclusion"]
        self.assertEqual(exclusion["l2c_register_call_count"], 2)
        self.assertEqual(exclusion["registered_fixed_channels"], [4, 6])
        self.assertEqual(exclusion["smp_registration_call"], 0x00537CEA)
        self.assertEqual(exclusion["smp_data_callback"], 0x00537279)
        self.assertEqual(exclusion["smp_control_callback"], 0x00537445)
        self.assertEqual(exclusion["alternate_smp_registration_calls"], 0)
        self.assertEqual(exclusion["alternate_smp_callback_pointers"], 0)
        self.assertEqual(exclusion["smp_msg_alloc_calls_reviewed"], 13)
        self.assertEqual(exclusion["l2c_data_req_calls_reviewed"], 8)

    def test_optional_source_identity_and_ownership_are_explicit(self) -> None:
        lineage = self.report["lineage"]
        self.assertEqual(lineage["selected_blob"], "b024dc746c712284f2cb0b54669358b3f3cbd0fd")
        self.assertTrue(lineage["later_r4_exact"])
        self.assertFalse(lineage["stock_body_version_discriminated"])
        self.assertEqual(self.report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
