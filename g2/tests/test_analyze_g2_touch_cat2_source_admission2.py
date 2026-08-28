# SPDX-License-Identifier: MIT
"""Tests for the second exact CAT2 touch source-admission batch."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_cat2_source_admission2.py"
S = importlib.util.spec_from_file_location("g2_touch_cat2_admission2", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchCat2Admission2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_subsystem_batch(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["admitted_functions"], 9)
        self.assertEqual(metrics["flash_functions"], 7)
        self.assertEqual(metrics["gpio_functions"], 1)
        self.assertEqual(metrics["scb_i2c_functions"], 1)
        self.assertEqual(set(self.rows),
                         {0x58F4, 0x5974, 0x59A8, 0x59C4, 0x5A00,
                          0x5A20, 0x5A50, 0x5BE4, 0x680C})

    def test_symbols_and_upstream_license(self):
        self.assertEqual(self.rows[0x58F4]["symbol"], "ProcessStatusCode")
        self.assertEqual(self.rows[0x5A50]["symbol"], "Cy_Flash_WriteRow")
        self.assertEqual(self.rows[0x5BE4]["symbol"], "Cy_GPIO_Pin_Init")
        self.assertEqual(self.rows[0x680C]["symbol"],
                         "Cy_SCB_I2C_SlaveInterrupt")
        self.assertTrue(all(row["license"] == "Apache-2.0"
                            for row in self.rows.values()))
        self.assertTrue(all(row["provider_commit"] == M.CAT2_COMMIT
                            for row in self.rows.values()))

    def test_gap_reduction_and_exclusions(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["cat2_gap_before"], metrics["cat2_gap_after"]),
                         (45, 36))
        self.assertEqual((metrics["semantic_gap_before"],
                          metrics["semantic_gap_after"]), (210, 201))
        self.assertEqual(metrics["unsafe_batch_admissions"], 0)
        self.assertIn("Em_EEPROM EULA", self.result["exclusions"])

    def test_adapter_target_and_digest(self):
        self.assertGreater(self.result["adapter"]["target_object_bytes"], 0)
        self.assertEqual(self.result["integration"],
                         "isolated Apache provider routes; not production-routed")
        self.assertEqual(self.result["metrics"]["row_digest"],
                         "fb1160f25a1f4a0fa843147aa879f8e8038756dc64742b8cf007940c087eacb9")
        self.assertIn("no hardware", self.result["analysis_mode"])

    def test_manifest_determinism(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                first = M.write_manifests(self.result)
                h1 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in first}
                second = M.write_manifests(M.analyze())
                h2 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in second}
                self.assertEqual(h1, h2)
                self.assertEqual(set(h1), {
                    "g2-touch-cat2-source-admission2.tsv",
                    "g2-touch-cat2-source-admission2-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
