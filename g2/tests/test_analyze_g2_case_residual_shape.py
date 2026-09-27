# SPDX-License-Identifier: MIT
"""Tests for the charging-case residual code/data shape audit."""

import csv
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_case_residual_shape.py"
S = importlib.util.spec_from_file_location("g2_case_residual_shape", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)

EMPTY_DIGEST = "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"


class CaseResidualShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()

    def test_residual_frontier_is_empty_after_function_map_gap_attribution(self):
        self.assertEqual(self.result["byte_accounting_sha256"],
                         M.EXPECTED_BYTE_ACCOUNTING_DIGEST)
        self.assertEqual(self.result["row_count"], 0)
        self.assertEqual(self.result["total_bytes"], 0)
        self.assertEqual(self.result["class_rows"], {})
        self.assertEqual(self.result["class_bytes"], {})
        self.assertEqual(self.result["rows_digest"], EMPTY_DIGEST)
        self.assertFalse(self.result["source_admission"])
        self.assertFalse(self.result["production_routed"])

    def test_control_flow_queue_is_empty_and_authenticated(self):
        self.assertEqual(self.result["thumb_branch_count"], 0)
        self.assertEqual(self.result["thumb_call_count"], 0)
        self.assertEqual(self.result["thumb_in_app_target_count"], 0)
        self.assertEqual(self.result["thumb_in_app_target_bucket_counts"], {})
        self.assertEqual(self.result["thumb_in_app_target_relation_counts"], {})
        self.assertEqual(self.result["thumb_in_app_targets_digest"], EMPTY_DIGEST)
        self.assertEqual(self.result["thumb_in_app_target_refs_digest"],
                         EMPTY_DIGEST)
        self.assertEqual(self.result["target_rows"], [])

    def test_recovery_manifests_are_empty_and_authenticated(self):
        self.assertEqual(self.result["residual_recovery_target_count"], 0)
        self.assertEqual(self.result["residual_recovery_queue_digest"],
                         EMPTY_DIGEST)
        self.assertEqual(self.result["residual_recovery_row_count"], 0)
        self.assertEqual(self.result["residual_recovery_row_bytes"], 0)
        self.assertEqual(self.result["residual_recovery_class_rows"], {})
        self.assertEqual(self.result["residual_recovery_class_bytes"], {})
        self.assertEqual(self.result["residual_recovery_rows_digest"],
                         EMPTY_DIGEST)
        self.assertEqual(self.result["residual_non_target_row_count"], 0)
        self.assertEqual(self.result["residual_non_target_row_bytes"], 0)
        self.assertEqual(self.result["residual_non_target_class_rows"], {})
        self.assertEqual(self.result["residual_non_target_class_bytes"], {})
        self.assertEqual(self.result["residual_non_target_rows_digest"],
                         EMPTY_DIGEST)
        self.assertEqual(self.result["residual_partition"], {
            "target_bearing_rows": 0,
            "target_bearing_bytes": 0,
            "non_target_rows": 0,
            "non_target_bytes": 0,
            "total_rows": 0,
            "total_bytes": 0,
        })
        self.assertEqual(
            self.result["residual_partition_digest"],
            "8b8a0fb3dfaf65d7b832fa22e87151d7d6dbc06266643848b58dc61cded876df",
        )

    def test_entry_candidate_frontier_is_empty(self):
        self.assertEqual(self.result["residual_entry_candidate_count"], 0)
        self.assertEqual(self.result["residual_entry_candidate_bytes"], 0)
        self.assertEqual(self.result["residual_entry_candidate_class_rows"], {})
        self.assertEqual(self.result["residual_entry_candidate_class_bytes"], {})
        self.assertEqual(self.result["residual_entry_candidates_digest"],
                         EMPTY_DIGEST)
        self.assertEqual(self.result["entry_candidate_rows"], [])

    def test_manifest_matches_fresh_analysis(self):
        paths = [
            ROOT / "tools/manifests/g2-case-residual-shape.tsv",
            ROOT / "tools/manifests/g2-case-residual-control-flow-targets.tsv",
            ROOT / "tools/manifests/g2-case-residual-recovery-queue.tsv",
            ROOT / "tools/manifests/g2-case-residual-recovery-rows.tsv",
            ROOT / "tools/manifests/g2-case-residual-non-target-rows.tsv",
            ROOT / "tools/manifests/g2-case-residual-entry-candidates.tsv",
        ]
        for path in paths:
            self.assertTrue(path.exists(), "run --write-manifests first")
            with path.open(newline="") as handle:
                rows = list(csv.DictReader(
                    (line for line in handle if not line.startswith("#")),
                    delimiter="\t"))
            self.assertEqual(rows, [])
        self.assertTrue(
            (ROOT / "tools/manifests/g2-case-residual-shape-summary.json")
            .exists(),
            "run --write-manifests first",
        )


if __name__ == "__main__":
    unittest.main()
