# SPDX-License-Identifier: MIT
"""Tests for argument-relative touch record primitive admission."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_record_primitives_admission.py"
S = importlib.util.spec_from_file_location("g2_touch_record_admission", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchRecordAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_complete_argument_relative_family(self):
        self.assertEqual(set(self.rows), set(M.ADMISSIONS))
        self.assertEqual(len(self.rows), 7)
        self.assertTrue(all(row["status"] ==
                            "clean_room_argument_relative_record_source"
                            for row in self.rows.values()))
        self.assertTrue(all(row["argument_relative_memory_only"]
                            and not row["product_semantics_asserted"]
                            for row in self.rows.values()))

    def test_function_and_byte_gap_reduction(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (93, 86))
        self.assertEqual(metrics["admitted_instruction_bytes"], 200)
        self.assertEqual(metrics["input_gap_instruction_bytes"] -
                         metrics["residual_gap_instruction_bytes"], 200)

    def test_residual_providers_stay_external(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["unimplemented_application_contracts_after"], 74)
        self.assertEqual(metrics["typed_external_or_unavailable_functions"], 12)
        self.assertTrue(all(not row["concrete_source"] and not row["implemented"]
                            for row in self.result["residual_rows"]))
        self.assertIn("residual providers/contracts remain non-source",
                      self.result["remaining"]["note"])

    def test_source_is_isolated_mit_and_target_builds(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_object_bytes"], 0)
        self.assertIn("not production-routed", self.result["integration"])
        self.assertIn("nested pointer graphs", self.result["exclusions"])

    def test_manifest_determinism(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                first = M.write_manifests(self.result)
                h1 = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in first}
                second = M.write_manifests(M.analyze())
                h2 = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in second}
                self.assertEqual(h1, h2)
                self.assertEqual(set(h1), {
                    "g2-touch-record-primitives-admission.tsv",
                    "g2-touch-record-primitives-residual.tsv",
                    "g2-touch-record-primitives-admission-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
