# SPDX-License-Identifier: MIT
"""Tests for the fully closed touch record-processing admission."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = (Path(__file__).resolve().parents[1] / "tools" /
     "analyze_g2_touch_closed_record_pipeline_admission.py")
S = importlib.util.spec_from_file_location("g2_touch_closed_pipeline_admission", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchClosedPipelineAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_closed_family(self):
        self.assertEqual(set(self.rows), set(M.ADMISSIONS))
        self.assertEqual(len(self.rows), 7)
        self.assertTrue(all(row["status"] ==
                            "clean_room_closed_record_pipeline_source"
                            for row in self.rows.values()))
        self.assertTrue(all(row["call_closure"] ==
                            "same_batch_or_previously_admitted_mit_source"
                            for row in self.rows.values()))
        self.assertTrue(all(not row["product_semantics_asserted"]
                            for row in self.rows.values()))

    def test_function_and_byte_gap_reduction(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (86, 79))
        self.assertEqual(metrics["admitted_instruction_bytes"], 388)
        self.assertEqual(metrics["input_gap_instruction_bytes"] -
                         metrics["residual_gap_instruction_bytes"], 388)

    def test_pointer_graph_and_provider_boundaries_are_explicit(self):
        self.assertEqual({entry for entry, row in self.rows.items()
                          if row["raw_pointer_graph"]},
                         {0x1AC4, 0x1AEC, 0x1B1C})
        metrics = self.result["metrics"]
        self.assertEqual(metrics["unimplemented_application_contracts_after"], 67)
        self.assertEqual(metrics["typed_external_or_unavailable_functions"], 12)
        self.assertIn("Em_EEPROM EULA", self.result["remaining"]["note"])
        self.assertIn("0x1B6C", self.result["exclusions"])

    def test_source_is_isolated_mit_and_target_closure_builds(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertEqual(len(self.result["source"]["dependencies"]), 2)
        self.assertIn("not production-routed", self.result["integration"])
        self.assertEqual(self.result["metrics"]["literal_or_mmio_admissions"], 0)

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
                    "g2-touch-closed-record-pipeline-admission.tsv",
                    "g2-touch-closed-record-pipeline-residual.tsv",
                    "g2-touch-closed-record-pipeline-admission-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
