# SPDX-License-Identifier: MIT
"""Tests for exact GPIO-inline and SysClk CAT2 source admission."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_cat2_source_admission4.py"
S = importlib.util.spec_from_file_location("g2_touch_cat2_admission4", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchCat2Admission4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_gpio_and_sysclk_batch(self):
        metrics = self.result["metrics"]
        self.assertEqual(len(self.rows), 19)
        self.assertEqual(metrics["gpio_inline_functions"], 4)
        self.assertEqual(metrics["sysclk_functions"], 15)
        self.assertEqual(self.rows[0x5B28]["symbol"], "Cy_GPIO_SetHSIOM")
        self.assertEqual(self.rows[0x6A90]["symbol"], "Cy_SysClk_IloStartMeasurement")
        self.assertEqual(self.rows[0x6B18]["symbol"], "Cy_SysClk_IloCompensate")
        self.assertEqual(self.rows[0x6E88]["symbol"], "Cy_SysClk_ClkHfSetSource")

    def test_pinned_apache_provider_and_target_signatures(self):
        self.assertEqual(self.result["provider_sources"]["commit"], M.CAT2_COMMIT)
        self.assertTrue(all(row["license"] == "Apache-2.0"
                            for row in self.rows.values()))
        self.assertTrue(all(row["provider_commit"] == M.CAT2_COMMIT
                            for row in self.rows.values()))
        self.assertTrue(all(len(row["instruction_sha256"]) == 64 and
                            len(row["target_signature_sha256"]) == 64
                            for row in self.rows.values()))
        self.assertEqual(self.result["metrics"]["row_digest"],
                         "8367deeecf6856157a281c1bf14e8ec646bf9d35e3b609aad1867e8b299a8b8c")

    def test_residual_is_exact_and_unsafe_batches_are_excluded(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["cat2_gap_before"], metrics["cat2_gap_after"]),
                         (29, 10))
        self.assertEqual((metrics["semantic_gap_before"],
                          metrics["semantic_gap_after"]), (194, 175))
        self.assertEqual(metrics["unsafe_batch_admissions"], 0)
        self.assertEqual(len(self.result["remaining_entries"]), 10)
        self.assertIn("0x7038", self.result["remaining_entries"])
        self.assertIn("Em_EEPROM EULA", self.result["exclusions"])

    def test_adapter_target_build_and_fail_closed_contract(self):
        self.assertGreater(self.result["adapter"]["target_object_bytes"], 0)
        self.assertIn("fail-closed on host", self.result["integration"])
        self.assertIn("no hardware", self.result["analysis_mode"])

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
                    "g2-touch-cat2-source-admission4.tsv",
                    "g2-touch-cat2-source-admission4-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
