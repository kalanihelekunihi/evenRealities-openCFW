# SPDX-License-Identifier: MIT
"""Tests for the Touch contributor-owned source license audit."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = (Path(__file__).resolve().parents[1] / "tools" /
     "analyze_g2_touch_project_license_readiness.py")
S = importlib.util.spec_from_file_location("g2_touch_project_license", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchProjectLicenseReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["component"]: row for row in cls.result["rows"]}

    def test_only_contributor_owned_clean_room_pairs_gain_mit_option(self):
        self.assertEqual(set(self.rows), {"i2c", "sensing"})
        self.assertTrue(all(row["license"] == "MIT OR GPL-3.0-only"
                            for row in self.rows.values()))
        self.assertTrue(all(row["gpl_option_preserved"]
                            for row in self.rows.values()))

    def test_no_upstream_or_provider_material_is_relicensed(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["upstream_or_gpl_derived_files_relicensed"], 0)
        self.assertEqual(metrics["provider_license_changes"], 0)
        self.assertTrue(all(not row["upstream_or_gpl_derived_material_relicensed"]
                            and row["provider_licenses_preserved"]
                            for row in self.rows.values()))

    def test_exact_four_file_boundary_is_pinned(self):
        self.assertEqual(self.result["metrics"]["dual_licensed_project_files"], 4)
        for row in self.rows.values():
            self.assertEqual(len(row["files"]), 2)
            self.assertTrue(all(len(item["sha256"]) == 64
                                for item in row["files"]))

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
                    "g2-touch-project-license-readiness.tsv",
                    "g2-touch-project-license-readiness-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
