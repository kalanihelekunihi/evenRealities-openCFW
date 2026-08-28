# SPDX-License-Identifier: MIT
"""Tests for the exact SCB-common CAT2 source-admission batch."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_cat2_source_admission3.py"
S = importlib.util.spec_from_file_location("g2_touch_cat2_admission3", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchCat2Admission3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_scb_common_batch(self):
        self.assertEqual(set(self.rows), {
            0x5F18, 0x5F50, 0x5F6E, 0x5FA6, 0x5FD6, 0x5FE6, 0x6016,
        })
        self.assertEqual(self.rows[0x5F18]["symbol"], "Cy_SCB_ReadArrayNoCheck")
        self.assertEqual(self.rows[0x5FE6]["symbol"], "Cy_SCB_WriteDefaultArray")
        self.assertEqual(self.rows[0x6016]["symbol"], "Cy_SCB_SetRxFifoLevel")
        self.assertEqual(self.result["metrics"]["scb_source_functions"], 6)
        self.assertEqual(self.result["metrics"]["scb_inline_functions"], 1)

    def test_pinned_public_provider_identity(self):
        self.assertEqual(self.result["provider_sources"], {
            "commit": M.CAT2_COMMIT,
            "cy_scb_common.c_sha256": M.SCB_SOURCE_SHA256,
            "cy_scb_common.h_sha256": M.SCB_HEADER_SHA256,
        })
        self.assertTrue(all(row["provider_commit"] == M.CAT2_COMMIT
                            for row in self.rows.values()))
        self.assertTrue(all(row["license"] == "Apache-2.0"
                            for row in self.rows.values()))
        self.assertTrue(all(len(row["target_signature_sha256"]) == 64
                            for row in self.rows.values()))

    def test_exact_residual_and_exclusions(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["cat2_gap_before"], metrics["cat2_gap_after"]),
                         (36, 29))
        self.assertEqual((metrics["semantic_gap_before"],
                          metrics["semantic_gap_after"]), (201, 194))
        self.assertEqual(metrics["unsafe_batch_admissions"], 0)
        self.assertIn("larger SCB I2C bodies", self.result["exclusions"])
        self.assertIn("Em_EEPROM EULA", self.result["exclusions"])

    def test_adapter_is_target_buildable_and_host_mmio_free(self):
        self.assertGreater(self.result["adapter"]["target_object_bytes"], 0)
        self.assertIn("fail-closed on host", self.result["integration"])
        self.assertIn("no hardware", self.result["analysis_mode"])
        self.assertEqual(self.result["metrics"]["row_digest"],
                         "06c631b19f2ed0f3c0fe4781a7eed1fb5b5672eace69f9eedb5fb8512c4735f2")

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
                    "g2-touch-cat2-source-admission3.tsv",
                    "g2-touch-cat2-source-admission3-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
