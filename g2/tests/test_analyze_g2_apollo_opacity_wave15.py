# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave15.py"
DOC = G2 / "docs/research/g2-apollo-opacity-wave15-round-cap-mve-closure.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave15", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().run_audit()

    def test_selected_delta_and_residual(self) -> None:
        self.assertEqual(self.report["before"], {"functions": 1292, "bytes": 134476})
        self.assertEqual(self.report["selected_root_range"], {"start": "0x0051B8F0", "end_exclusive": "0x0051BF74"})
        self.assertEqual(self.report["typed_unavailable"], {"functions": 1, "bytes": 1668})
        self.assertEqual(self.report["after"], {"functions": 1291, "bytes": 132808})
        self.assertEqual(self.report["largest_remaining"], {"entry": "0x0051BF7C", "envelope_bytes": 1640})

    def test_machine_call_closure_is_exact(self) -> None:
        self.assertEqual(self.report["actionable_graph"], {"positive_functions": 1, "positive_bytes": 1668, "terminal_functions": 9, "static_callsites": 20})
        self.assertEqual(self.report["machine_branch_closure"], {"direct_bl_sites": 20, "wide_nonlink_sites": 0, "register_blx_sites": 0, "targets": 9})
        self.assertEqual(len(self.report["frontier_records"]), 9)

    def test_callother_and_data_are_nonopaque(self) -> None:
        self.assertEqual(self.report["callother_reconciliation"], {"artifacts": 8, "occurrences": 8, "machine_branch_sites": 0, "additional_function_bytes": 0})
        self.assertEqual(self.report["range_partition"], {"functions": 1, "interior_islands": 1, "interior_physical_bytes": 4, "additional_function_bytes": 0})
        self.assertEqual(self.report["shared_data"], {"islands": 2, "physical_bytes": 8, "prior_reconciled_bytes": 4, "direct_dat_cells": 3, "additional_function_bytes": 0})

    def test_provider_and_production_fail_closed(self) -> None:
        self.assertIsNone(self.report["provider"]["authenticated_function_identity"])
        self.assertIsNone(self.report["provider"]["authenticated_license"])
        self.assertFalse(self.report["production_routed"])
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertIn("maintained implementation source", self.report["production_blocker"])

    def test_mapping_and_documentation(self) -> None:
        self.assertEqual(self.report["mapping_sha256"], "5890e09b018d76583d985ff78c5e5a36c259d33072d035f192c78d80fc19b7d5")
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("1,291 functions / 132,808 bytes", text)
        self.assertIn("typed-external-provider-unavailable", text)


if __name__ == "__main__":
    unittest.main()
