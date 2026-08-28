# SPDX-License-Identifier: MIT
"""Tests for touch application-state source admission batch 11."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = (Path(__file__).resolve().parents[1] / "tools" /
     "analyze_g2_touch_application_state_pipeline_admission.py")
S = importlib.util.spec_from_file_location("g2_touch_application_state_admission", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchApplicationStateAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_internal_family(self):
        self.assertEqual(set(self.rows), set(M.ADMISSIONS))
        self.assertEqual(len(self.rows), 11)
        self.assertTrue(all(row["status"] ==
                            "clean_room_argument_relative_application_state_source"
                            for row in self.rows.values()))
        self.assertTrue(all(not row["resident_table_dependency"] and
                            not row["product_semantics_asserted"]
                            for row in self.rows.values()))

    def test_function_and_byte_gap_reduction(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (79, 68))
        self.assertEqual(metrics["admitted_instruction_bytes"], 952)
        self.assertEqual(metrics["input_gap_instruction_bytes"] -
                         metrics["residual_gap_instruction_bytes"], 952)

    def test_literal_and_external_boundaries_remain_conservative(self):
        self.assertEqual(self.rows[0x1EBC]["shipped_immediate_literal"],
                         "0x1FB8=0x0FFF0000")
        self.assertEqual(self.result["metrics"]["resident_table_admissions"], 0)
        self.assertEqual(self.result["metrics"]["mmio_admissions"], 0)
        self.assertEqual(self.result["metrics"]["typed_external_or_unavailable_functions"], 12)
        self.assertEqual(self.result["metrics"]["unimplemented_application_contracts_after"], 56)
        self.assertIn("0xB41C table loader", self.result["remaining"]["note"])
        self.assertIn("0x1B6C/0x1C54/0x2638", self.result["exclusions"])

    def test_source_is_isolated_mit_and_target_closure_builds(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertIn("not production-routed", self.result["integration"])
        self.assertIn("bounded MIT loops", self.result["source"]["dependencies"][1])

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
                    "g2-touch-application-state-pipeline-admission.tsv",
                    "g2-touch-application-state-pipeline-residual.tsv",
                    "g2-touch-application-state-pipeline-admission-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
