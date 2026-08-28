# SPDX-License-Identifier: MIT
"""Tests for touch configuration bootstrap admission batch 16."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = (Path(__file__).resolve().parents[1] / "tools" /
     "analyze_g2_touch_configuration_bootstrap_admission.py")
S = importlib.util.spec_from_file_location("g2_touch_bootstrap_admission", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchConfigurationBootstrapAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.row = cls.result["rows"][0]

    def test_exact_bootstrap_and_call_closure(self):
        self.assertEqual(self.row["entry"], 0x065C)
        self.assertEqual(self.row["direct_callees"],
                         [0x01D8, 0x0220, 0x0268, 0x02B0, 0x0BE0, 0x6FF0])
        self.assertFalse(self.row["eula_provider_body_admitted"])
        self.assertFalse(self.row["resident_table_dependency"])

    def test_gap_reduction(self):
        metrics = self.result["metrics"]
        self.assertEqual((metrics["input_concrete_gap"],
                          metrics["concrete_source_or_implementation_gap_after"]),
                         (56, 55))
        self.assertEqual(metrics["admitted_instruction_bytes"], 156)
        self.assertEqual(metrics["residual_gap_instruction_bytes"], 4964)
        self.assertEqual(metrics["typed_external_or_unavailable_functions"], 12)

    def test_source_is_mit_target_closed_and_isolated(self):
        self.assertEqual(self.result["source"]["license"], "MIT")
        self.assertGreater(self.result["source"]["target_closure_object_bytes"], 0)
        self.assertIn("not production-routed", self.result["integration"])

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
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
