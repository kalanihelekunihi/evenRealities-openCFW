# SPDX-License-Identifier: MIT
"""Tests for instruction-exact clean-room touch leaf admission."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_leaf_primitives_admission.py"
S = importlib.util.spec_from_file_location("g2_touch_leaf_admission", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchLeafAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_complete_safe_leaf_family_is_admitted(self):
        metrics = self.result["metrics"]
        self.assertEqual(len(self.rows), 16)
        self.assertEqual(metrics["register_passthrough_functions"], 6)
        self.assertEqual(metrics["constant_return_functions"], 6)
        self.assertEqual(metrics["pure_arithmetic_functions"], 4)
        self.assertEqual(metrics["pointer_or_mmio_admissions"], 0)
        self.assertTrue(all(row["status"] ==
                            "clean_room_instruction_exact_source"
                            for row in self.rows.values()))
        self.assertTrue(all(row["raw_aapcs_register_behavior_complete"]
                            and not row["product_semantics_asserted"]
                            for row in self.rows.values()))

    def test_residual_census_is_exhaustive_and_non_source(self):
        metrics = self.result["metrics"]
        self.assertEqual(len(self.result["residual_rows"]), 93)
        self.assertEqual(metrics["unimplemented_application_contracts_after"], 81)
        self.assertEqual(metrics["typed_external_eula_functions"], 10)
        self.assertEqual(metrics["typed_system_handoff_functions"], 1)
        self.assertEqual(metrics["typed_unavailable_halt_functions"], 1)
        self.assertTrue(all(not row["concrete_source"] and not row["implemented"]
                            for row in self.result["residual_rows"]))

    def test_gap_reduction_is_only_concrete_admissions(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (109, 93))
        self.assertEqual(metrics["clean_room_instruction_exact_sources"], 16)
        self.assertEqual(metrics["upstream_body_admissions"], 0)
        self.assertIn("not production-routed", self.result["integration"])
        self.assertIn("remain non-source", self.result["remaining"]["note"])

    def test_source_is_mit_and_target_builds(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_object_bytes"], 0)
        self.assertIn("no product semantic names", self.result["exclusions"])

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
                    "g2-touch-leaf-primitives-admission.tsv",
                    "g2-touch-leaf-primitives-residual.tsv",
                    "g2-touch-leaf-primitives-admission-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
