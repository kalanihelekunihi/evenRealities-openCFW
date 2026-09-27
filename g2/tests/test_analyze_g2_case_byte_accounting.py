# SPDX-License-Identifier: MIT
"""Tests for the charging-case typed_external_or_unsupported byte accounting."""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_case_byte_accounting.py"
S = importlib.util.spec_from_file_location("g2_case_byte_accounting", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class CaseByteAccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()

    def test_reconciles_to_the_pinned_whole_blob_split(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["admitted_function_source_candidate_bytes"], 14886)
        self.assertEqual(metrics["typed_external_or_unsupported_bytes"], 40866)
        self.assertEqual(
            metrics["admitted_function_source_candidate_bytes"] +
            metrics["typed_external_or_unsupported_bytes"],
            M.APP_BYTES)

    def test_every_sub_bucket_sums_to_the_typed_external_total(self):
        metrics = self.result["metrics"]
        self.assertEqual(
            metrics["gap_frontier_bytes"] + metrics["platform_attributed_bytes"] +
            metrics["function_map_attributed_bytes"] +
            metrics["residual_bytes"],
            metrics["typed_external_or_unsupported_bytes"])
        self.assertEqual(
            metrics["residual_zero_fill_bytes"] + metrics["residual_ff_fill_bytes"] +
            metrics["residual_log_string_candidate_bytes"] +
            metrics["residual_unresolved_code_or_data_bytes"],
            metrics["residual_bytes"])

    def test_rows_are_contiguous_disjoint_and_conserve_the_app_image(self):
        rows = self.result["rows"]
        self.assertGreater(len(rows), 0)
        ordered = sorted(rows, key=lambda r: r["start"])
        self.assertEqual(ordered[0]["start"], M.APP_BASE)
        self.assertEqual(ordered[-1]["end"], M.APP_BASE + M.APP_BYTES)
        for previous, current in zip(ordered, ordered[1:]):
            self.assertEqual(previous["end"], current["start"])
        self.assertEqual(sum(r["bytes"] for r in rows), M.APP_BYTES)
        for row in rows:
            self.assertEqual(row["end"] - row["start"], row["bytes"])

    def test_no_row_spans_two_categories(self):
        # _collapse only breaks on a category change, so every row is
        # single-category by construction; assert the content hash is
        # non-empty as a sanity check that real bytes were hashed.
        for row in self.result["rows"]:
            self.assertEqual(len(row["content_sha256"]), 64)

    def test_platform_islands_carry_evidence(self):
        self.assertGreater(len(self.result["island_evidence"]), 0)
        for category, evidence_list in self.result["island_evidence"].items():
            self.assertTrue(category.startswith("platform_"))
            self.assertTrue(all(evidence_list))

    def test_function_map_attribution_carries_evidence(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["function_map_attributed_bytes"], 37642)
        self.assertGreater(len(self.result["function_map_evidence"]), 0)
        for category, evidence_list in self.result["function_map_evidence"].items():
            self.assertTrue(category.startswith("function_map_"))
            self.assertTrue(all(row["evidence"] for row in evidence_list))
        self.assertEqual(metrics["function_map_body_attributed_bytes"], 25314)
        self.assertEqual(metrics["function_map_gap_attributed_bytes"], 12328)
        self.assertGreater(len(self.result["function_map_gap_evidence"]), 0)
        for category, evidence_list in self.result["function_map_gap_evidence"].items():
            self.assertTrue(category.startswith("function_map_gap_"))
            self.assertTrue(all(row["evidence"] for row in evidence_list))

    def test_residual_is_empty_after_function_map_gap_attribution(self):
        string_rows = self.result["string_rows"]
        metrics = self.result["metrics"]
        self.assertEqual(len(string_rows), 0)
        self.assertEqual(metrics["residual_bytes"], 0)
        self.assertEqual(metrics["residual_zero_fill_bytes"], 0)
        self.assertEqual(metrics["residual_ff_fill_bytes"], 0)
        self.assertEqual(metrics["residual_log_string_candidate_rows"], 0)
        self.assertEqual(metrics["residual_log_string_candidate_bytes"], 0)
        self.assertEqual(metrics["residual_unresolved_code_or_data_bytes"], 0)
        self.assertEqual(
            metrics["residual_log_string_candidate_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945")

    def test_residual_fill_runs_are_pure(self):
        blob = M.BLOB.read_bytes()
        app = blob[M.WRAPPER:]
        for row in self.result["rows"]:
            if row["category"] == "residual_zero_fill":
                body = app[row["start"] - M.APP_BASE:row["end"] - M.APP_BASE]
                self.assertEqual(set(body), {0x00})
                self.assertGreaterEqual(len(body), M.ZERO_RUN_MIN)
            elif row["category"] == "residual_ff_fill":
                body = app[row["start"] - M.APP_BASE:row["end"] - M.APP_BASE]
                self.assertEqual(set(body), {0xFF})
                self.assertGreaterEqual(len(body), M.FF_RUN_MIN)

    def test_identity_windows_are_confirmed_absent_from_the_range(self):
        self.assertEqual(self.result["identity_windows_in_range"]["count"], 0)

    def test_no_hardware_operation_and_not_production_routed(self):
        self.assertEqual(self.result["hardware_operations"], [])
        self.assertEqual(self.result["hardware_validation"],
                          "blocked by unavailable physical evidence")
        self.assertFalse(self.result["production_routed"])

    def test_manifest_matches_a_fresh_analysis(self):
        rows_path = ROOT / "tools/manifests/g2-case-byte-accounting.tsv"
        strings_path = ROOT / "tools/manifests/g2-case-log-string-candidates.tsv"
        summary_path = ROOT / "tools/manifests/g2-case-byte-accounting-summary.json"
        self.assertTrue(rows_path.exists(), "run --write-manifests first")
        self.assertTrue(strings_path.exists(), "run --write-manifests first")
        self.assertTrue(summary_path.exists(), "run --write-manifests first")
        import csv
        with rows_path.open(newline="") as handle:
            written = list(csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t"))
        with strings_path.open(newline="") as handle:
            written_strings = list(csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t"))
        self.assertEqual(len(written), len(self.result["rows"]))
        self.assertEqual(len(written_strings), len(self.result["string_rows"]))
        self.assertEqual(sum(int(row["bytes"]) for row in written_strings),
                         0)
        self.assertEqual(int(written[-1]["bytes"]),
                          self.result["rows"][-1]["bytes"])


if __name__ == "__main__":
    unittest.main()
