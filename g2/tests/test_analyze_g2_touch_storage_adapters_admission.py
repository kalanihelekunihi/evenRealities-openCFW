# SPDX-License-Identifier: MIT
"""Tests for touch storage adapter source admission batch 15."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = (Path(__file__).resolve().parents[1] / "tools" /
     "analyze_g2_touch_storage_adapters_admission.py")
S = importlib.util.spec_from_file_location("g2_touch_storage_admission", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchStorageAdapterAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_storage_adapter_family(self):
        self.assertEqual(set(self.rows), {0x01D8, 0x0220, 0x02B0, 0x02E4})
        self.assertTrue(all(row["status"] ==
                            "clean_room_storage_adapter_with_typed_eula_provider"
                            for row in self.rows.values()))
        self.assertEqual(self.rows[0x02E4]["typed_providers"], [])

    def test_gap_reduction_and_eula_boundary(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (60, 56))
        self.assertEqual(metrics["admitted_instruction_bytes"], 158)
        self.assertEqual(metrics["residual_gap_instruction_bytes"], 5120)
        self.assertEqual(metrics["typed_eula_provider_admissions"], 3)
        self.assertEqual(metrics["typed_external_or_unavailable_functions"], 12)

    def test_source_is_mit_target_closed_and_not_production_routed(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertIn("not production-routed", self.result["integration"])
        self.assertTrue(all(not row["resident_table_dependency"]
                            for row in self.rows.values()))

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
                    "g2-touch-storage-adapters-admission.tsv",
                    "g2-touch-storage-adapters-residual.tsv",
                    "g2-touch-storage-adapters-admission-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
