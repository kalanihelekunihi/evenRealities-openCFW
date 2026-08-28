# SPDX-License-Identifier: MIT
"""Tests for isolated touch application-policy source closure."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_policy_helpers_source.py"
S = importlib.util.spec_from_file_location("g2_touch_policy_helpers_source", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchPolicyHelperSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["stock_entry"]: row for row in cls.result["boundaries"]}

    def test_complete_eight_boundary_closure(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["stock_boundaries"], 8)
        self.assertEqual(metrics["source_exports"], 8)
        self.assertEqual(metrics["implemented_boundaries"], 4)
        self.assertEqual(metrics["fail_closed_provider_boundaries"], 4)
        self.assertEqual(set(self.rows),
                         {0x0268, 0x071C, 0x0738, 0x07FC,
                          0x0BE8, 0x0BFC, 0x0D70, 0x111C})

    def test_executable_boundaries(self):
        for entry in (0x0268, 0x071C, 0x0738, 0x0BE8):
            self.assertEqual(self.rows[entry]["closure"], "implemented")

    def test_uncertain_boundaries_are_provider_required(self):
        for entry in (0x07FC, 0x0BFC, 0x0D70, 0x111C):
            row = self.rows[entry]
            self.assertEqual(row["closure"], "provider_contract_fail_closed")
            self.assertNotEqual(row["provider_contract"], "none")
        self.assertIn("no fallback semantics invented",
                      self.rows[0x0BFC]["evidence_limit"])

    def test_mit_and_eula_separation(self):
        self.assertEqual(self.result["license"], "MIT")
        self.assertEqual(self.result["metrics"]["direct_mmio_dependencies"], 0)
        self.assertEqual(self.result["metrics"]["infineon_eula_source_dependencies"], 0)
        self.assertIn("no EULA source copied",
                      self.result["provider_policy"]["infineon_capsense_and_emeeprom"])

    def test_target_exports(self):
        self.assertEqual(set(self.result["exports"]), M.EXPORTS)
        self.assertGreater(self.result["target_object_bytes"], 0)
        self.assertIn("Cortex-M0+", self.result["target"])

    def test_isolated_and_software_only(self):
        self.assertEqual(self.result["integration"],
                         "isolated candidate; not production-routed by this tranche")
        self.assertIn("no hardware", self.result["analysis_mode"])

    def test_manifests_write(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                paths = M.write_manifests(self.result)
                self.assertEqual({path.name for path in paths}, {
                    "g2-touch-policy-helper-source-closure.tsv",
                    "g2-touch-policy-helper-source-summary.json",
                })
                for path in paths:
                    self.assertTrue(path.read_text())
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
