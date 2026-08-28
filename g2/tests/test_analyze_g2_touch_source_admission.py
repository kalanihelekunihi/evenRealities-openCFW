# SPDX-License-Identifier: MIT
"""Tests for isolated touch runtime/CAT2 source admission."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_source_admission.py"
S = importlib.util.spec_from_file_location("g2_touch_source_admission", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchSourceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_exact_admission_count_and_reduced_gap(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["admitted_functions"], 13)
        self.assertEqual(metrics["admission_counts"],
                         {"cat2_apache": 9, "runtime_mit": 4})
        self.assertEqual(metrics["semantic_gap_before"], 223)
        self.assertEqual(metrics["semantic_gap_after"], 210)

    def test_cat2_admissions_are_exact_bounded_symbols(self):
        self.assertEqual(set(M.CAT2_ADMISSIONS),
                         {0x7024, 0x7144, 0x7228, 0x728C, 0x72F4,
                          0x7320, 0x7338, 0x7350, 0x73A8})
        self.assertEqual(self.rows[0x7024]["stock_candidate"],
                         "Cy_SysLib_DelayUs")
        self.assertEqual(self.rows[0x7350]["stock_candidate"],
                         "Cy_SysTick_Init")
        self.assertTrue(all(self.rows[entry]["license"] == "Apache-2.0"
                            for entry in M.CAT2_ADMISSIONS))
        self.assertTrue(all(self.rows[entry]["provider_commit"] == M.CAT2_COMMIT
                            for entry in M.CAT2_ADMISSIONS))

    def test_runtime_admissions_are_mit_clean_room(self):
        self.assertEqual(set(M.RUNTIME_ADMISSIONS),
                         {0x76AC, 0x76E4, 0x7740, 0x7744})
        self.assertTrue(all(self.rows[entry]["license"] == "MIT"
                            for entry in M.RUNTIME_ADMISSIONS))
        self.assertEqual(self.rows[0x76E4]["admitted_symbol"],
                         "open_cfw_touch_runtime_init_arrays")

    def test_unsafe_batches_are_not_admitted(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["mixed_eula_application_admitted"], 0)
        self.assertEqual(metrics["cat2_candidates_before"], 54)
        self.assertEqual(metrics["cat2_candidates_admitted"], 9)
        self.assertEqual(metrics["cat2_candidates_remaining"], 45)
        self.assertEqual(self.result["remaining"]["total"], 210)

    def test_licenses_and_target_compile_are_pinned(self):
        self.assertIn("MIT clean-room", self.result["license_policy"])
        self.assertIn("Apache-2.0", self.result["license_policy"])
        self.assertEqual(self.result["target"], "ARM Cortex-M0+ freestanding Thumb")
        self.assertTrue(all(size > 0 for size in self.result["target_objects"].values()))
        self.assertEqual(self.result["integration"],
                         "isolated adapters; not production-routed")

    def test_digest_and_software_only_mode(self):
        self.assertEqual(
            self.result["metrics"]["admission_digest"],
            "2e9179bdae38cb2d825c46f048fb7a03b992b64d010d178f9a91518d69d71218",
        )
        self.assertIn("no hardware", self.result["analysis_mode"])

    def test_manifests_are_deterministic(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                first = M.write_manifests(self.result)
                first_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in first}
                second = M.write_manifests(M.analyze())
                second_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in second}
                self.assertEqual(first_hashes, second_hashes)
                self.assertEqual(set(first_hashes), {
                    "g2-touch-source-admission.tsv",
                    "g2-touch-source-admission-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
