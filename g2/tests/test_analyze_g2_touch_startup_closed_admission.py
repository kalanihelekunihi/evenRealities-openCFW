# SPDX-License-Identifier: MIT
"""Tests for Touch evidence-closed startup admission batch 18."""

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

P = (Path(__file__).resolve().parents[1] / "tools" /
     "analyze_g2_touch_startup_closed_admission.py")
S = importlib.util.spec_from_file_location("g2_touch_startup_closed", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchStartupClosedAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_entries_and_call_closure(self):
        self.assertEqual(set(self.rows), {0x0D4C, 0x11B4, 0x11D0, 0x1228})
        self.assertEqual(self.rows[0x11D0]["direct_callees"],
                         [0x6CD4, 0x6D1C, 0x6E04, 0x6E48])
        self.assertEqual(self.rows[0x1228]["direct_callees"], [0x6DBC])
        self.assertTrue(all(not row["resident_table_dependency"]
                            and not row["mmio_execution"]
                            for row in self.rows.values()))

    def test_gap_reduction_and_external_count(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (54, 50))
        self.assertEqual(metrics["admitted_instruction_bytes"], 150)
        self.assertEqual(metrics["residual_gap_instruction_bytes"], 4722)
        self.assertEqual(metrics["typed_external_or_unavailable_functions"], 12)

    def test_mit_source_is_target_closed_and_isolated(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertIn("not production-routed", self.result["integration"])

    def test_manifest_determinism_and_current_readiness(self):
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
                current = json.loads(next(
                    path for path in first if path.name ==
                    "g2-touch-current-source-readiness-summary.json").read_text())
                self.assertEqual(current["authoritative_batch"], 18)
                self.assertEqual(current["hardware_validation"],
                                 "deferred by project direction")
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
