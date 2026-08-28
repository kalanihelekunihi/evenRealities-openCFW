# SPDX-License-Identifier: MIT
"""Tests for touch selection/update source admission batch 13."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = (Path(__file__).resolve().parents[1] / "tools" /
     "analyze_g2_touch_selection_update_pipeline_admission.py")
S = importlib.util.spec_from_file_location("g2_touch_selection_update_admission", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchSelectionUpdateAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_closed_family(self):
        self.assertEqual(set(self.rows), {0x15CC, 0x2794, 0x28A2})
        self.assertTrue(all(row["status"] ==
                            "clean_room_argument_relative_selection_update_source"
                            for row in self.rows.values()))
        self.assertTrue(all(row["call_closure"] ==
                            "same_batch_or_previously_admitted_mit_or_exact_runtime_behavior"
                            for row in self.rows.values()))

    def test_function_and_byte_gap_reduction(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (66, 63))
        self.assertEqual(metrics["admitted_instruction_bytes"], 558)
        self.assertEqual(metrics["input_gap_instruction_bytes"] -
                         metrics["residual_gap_instruction_bytes"], 558)

    def test_literal_and_external_boundaries_remain_conservative(self):
        self.assertEqual(self.rows[0x15CC]["shipped_immediate_literal"],
                         "0x16D0=0x0000FFFF")
        self.assertTrue(all(not row["resident_table_dependency"] and
                            not row["product_semantics_asserted"]
                            for row in self.rows.values()))
        self.assertEqual(self.result["metrics"]["resident_table_admissions"], 0)
        self.assertEqual(self.result["metrics"]["typed_external_or_unavailable_functions"], 12)
        self.assertEqual(self.result["metrics"]["unimplemented_application_contracts_after"], 51)
        self.assertIn("0xB41C loader", self.result["remaining"]["note"])

    def test_source_is_isolated_mit_and_target_closure_builds(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertEqual(len(self.result["source"]["dependencies"]), 2)
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
                    "g2-touch-selection-update-pipeline-admission.tsv",
                    "g2-touch-selection-update-pipeline-residual.tsv",
                    "g2-touch-selection-update-pipeline-admission-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
