# SPDX-License-Identifier: MIT
"""Tests for exhaustive CAPSENSE provider-boundary resolution."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_capsense_provider_boundary.py"
S = importlib.util.spec_from_file_location("g2_touch_capsense_boundary", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchCapsenseBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_all_mixed_rows_are_provider_typed(self):
        metrics = self.result["metrics"]
        self.assertEqual(len(self.rows), 55)
        self.assertEqual(metrics["provider_family_resolved"], 55)
        self.assertEqual(metrics["typed_external_functions"], 55)
        self.assertEqual(metrics["concrete_source_functions"], 0)
        self.assertTrue(all(row["status"] ==
                            "typed_external_eula_provider_boundary"
                            for row in self.rows.values()))
        self.assertTrue(all(not row["concrete_source"]
                            for row in self.rows.values()))

    def test_provider_pin_is_comparison_not_historical_claim(self):
        provider = self.result["provider"]
        self.assertEqual(provider["commit"], M.PROVIDER_COMMIT)
        self.assertEqual(provider["license_sha256"], M.LICENSE_SHA256)
        self.assertEqual(provider["c_source_count"], 15)
        self.assertIn("comparison/provider API pin only",
                      provider["version_claim"])
        self.assertTrue(all(row["provider_version_claim"] ==
                            "comparison-only-not-historical-build"
                            for row in self.rows.values()))

    def test_topology_and_actionable_gap(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["component_sizes"], [50, 2, 1, 1, 1])
        self.assertEqual(metrics["external_dependency_entries"], 23)
        self.assertEqual((metrics["mixed_provider_gap_before"],
                          metrics["mixed_provider_gap_after"]), (55, 0))
        self.assertEqual((metrics["semantic_source_gap_before"],
                          metrics["semantic_source_gap_after_external_typing"]),
                         (166, 111))
        self.assertEqual(metrics["row_digest"],
                         "eb837e2abd0e62d4628a22476d4db2588ba92dbca2bd27f8ecac3996733a65b4")

    def test_clean_room_boundary_is_not_production_source(self):
        self.assertEqual(self.result["adapter"]["license"], "MIT")
        self.assertGreater(self.result["adapter"]["target_object_bytes"], 0)
        self.assertIn("not production-routed", self.result["integration"])
        self.assertIn("no vendor body copied", self.result["analysis_mode"])
        self.assertIn("not concrete OpenCFW source", self.result["remaining"]["note"])

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
                    "g2-touch-capsense-provider-boundary.tsv",
                    "g2-touch-capsense-provider-topology.tsv",
                    "g2-touch-capsense-provider-boundary-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
