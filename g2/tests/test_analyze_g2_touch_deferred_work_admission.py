# SPDX-License-Identifier: MIT
"""Tests for touch deferred-work admission batch 17."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = (Path(__file__).resolve().parents[1] / "tools" /
     "analyze_g2_touch_deferred_work_admission.py")
S = importlib.util.spec_from_file_location("g2_touch_deferred_work_admission", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchDeferredWorkAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.row = cls.result["rows"][0]

    def test_exact_entry_and_call_closure(self):
        self.assertEqual(self.row["entry"], 0x0780)
        self.assertEqual(self.row["direct_callees"],
                         [0x0738, 0x0BE0, 0x0D4C, 0x1192, 0x119A])
        self.assertFalse(self.row["eula_provider_body_admitted"])
        self.assertFalse(self.row["resident_table_dependency"])

    def test_gap_reduction(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (55, 54))
        self.assertEqual(metrics["admitted_instruction_bytes"], 92)
        self.assertEqual(metrics["residual_gap_instruction_bytes"], 4872)
        self.assertEqual(metrics["typed_external_or_unavailable_functions"], 12)

    def test_source_is_mit_target_closed_and_isolated(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertIn("not production-routed", self.result["integration"])

    def test_manifest_determinism_and_current_summary(self):
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
                current = next(path for path in first if path.name ==
                               "g2-touch-current-source-readiness-summary.json")
                self.assertIn('"authoritative_batch": 17', current.read_text())
                self.assertIn('"hardware_validation": "deferred by project direction"',
                              current.read_text())
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
