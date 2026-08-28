# SPDX-License-Identifier: MIT
"""Tests for touch configuration/start source admission batch 14."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = (Path(__file__).resolve().parents[1] / "tools" /
     "analyze_g2_touch_configuration_start_pipeline_admission.py")
S = importlib.util.spec_from_file_location("g2_touch_configuration_start_admission", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchConfigurationStartAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_typed_provider_family(self):
        self.assertEqual(set(self.rows), {0x1944, 0x1972, 0x197C})
        self.assertTrue(all(row["status"] ==
                            "clean_room_configuration_source_with_typed_providers"
                            for row in self.rows.values()))
        self.assertEqual(self.rows[0x1944]["typed_providers"], [0x37C0, 0x5CA0])
        self.assertEqual(self.rows[0x197C]["typed_providers"], [0x37C0])
        self.assertEqual(self.rows[0x1972]["typed_providers"], [])

    def test_function_and_byte_gap_reduction(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (63, 60))
        self.assertEqual(metrics["admitted_instruction_bytes"], 354)
        self.assertEqual(metrics["input_gap_instruction_bytes"] -
                         metrics["residual_gap_instruction_bytes"], 354)

    def test_provider_and_external_boundaries_remain_conservative(self):
        self.assertIn("MIT OR GPL-3.0-only wrapper",
                      self.rows[0x1944]["provider_licenses"])
        self.assertIn("Apache-2.0", self.rows[0x1944]["provider_licenses"])
        self.assertTrue(all(not row["resident_table_dependency"] and
                            not row["product_semantics_asserted"]
                            for row in self.rows.values()))
        self.assertEqual(self.result["metrics"]["resident_table_admissions"], 0)
        self.assertEqual(self.result["metrics"]["typed_external_or_unavailable_functions"], 12)
        self.assertIn("0xB41C/0xB4C4", self.result["remaining"]["note"])

    def test_source_is_isolated_mit_and_target_builds(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertIn("not production-routed", self.result["integration"])

    def test_manifest_determinism(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                first = M.write_manifests(self.result)
                h1 = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in first}
                second = M.write_manifests(self.result)
                h2 = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in second}
                self.assertEqual(h1, h2)
                self.assertEqual(set(h1), {
                    "g2-touch-configuration-start-pipeline-admission.tsv",
                    "g2-touch-configuration-start-pipeline-residual.tsv",
                    "g2-touch-configuration-start-pipeline-admission-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
