# SPDX-License-Identifier: MIT
"""Tests for Touch flash-row admission batch 19."""

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_flash_row_admission.py"
S = importlib.util.spec_from_file_location("g2_touch_flash_row", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchFlashRowAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_family_and_provider_closure(self):
        self.assertEqual(set(self.rows), {0x14B0, 0x1510, 0x1560})
        self.assertEqual(self.rows[0x14B0]["direct_callees"],
                         [0x1488, 0x5A50, 0x74CC, 0x76D4])
        self.assertTrue(all(not row["resident_table_dependency"]
                            and not row["mmio_execution"]
                            for row in self.rows.values()))

    def test_gap_reduction(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (50, 47))
        self.assertEqual(metrics["admitted_instruction_bytes"], 172)
        self.assertEqual(metrics["residual_gap_instruction_bytes"], 4550)
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
                h1 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in first}
                second = M.write_manifests(self.result)
                h2 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in second}
                self.assertEqual(h1, h2)
                current = json.loads(next(p for p in first if p.name ==
                    "g2-touch-current-source-readiness-summary.json").read_text())
                self.assertEqual(current["authoritative_batch"], 19)
                self.assertEqual(current["hardware_validation"],
                                 "deferred by project direction")
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
