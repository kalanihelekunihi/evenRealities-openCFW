# SPDX-License-Identifier: MIT
"""Fail-closed tests for final Touch function and physical-byte typing."""

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_touch_final_frontier.py"
S = importlib.util.spec_from_file_location("g2_touch_final_frontier", P)
M = importlib.util.module_from_spec(S); sys.modules[S.name] = M; S.loader.exec_module(M)


class TouchFinalFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()

    def test_exact_frontier_is_exhaustively_typed(self):
        metrics = self.result["metrics"]
        self.assertTrue(self.result["classification_complete"])
        self.assertEqual((metrics["frontier_functions"],
                          metrics["frontier_instruction_row_bytes"]),
                         (0, 0))
        self.assertEqual(metrics["typed_external_or_unsupported_functions"], 0)
        self.assertTrue(self.result["software_function_frontier_complete"])
        self.assertEqual(metrics["unclassified_functions"], 0)
        self.assertTrue(all(row["missing_fact_or_reason"]
                            for row in self.result["function_rows"]))

    def test_physical_buckets_are_disjoint_pinned_and_conservative(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["whole_blob_bucket_bytes"], {
            "generated_transport_fill": 512,
            "project_source_candidate": 14510,
            "typed_external_or_unsupported": 19442,
            "still_unclassified": 0,
        })
        self.assertEqual(sum(metrics["whole_blob_bucket_bytes"].values()), 34464)
        self.assertEqual(len(self.result["physical_rows"]), 3)
        self.assertEqual(len({row["address_set_sha256"]
                              for row in self.result["physical_rows"]}), 3)
        self.assertEqual(len({row["content_sha256"]
                              for row in self.result["physical_rows"]}), 3)
        self.assertTrue(self.result["physical_derivation"]
                        ["instruction_rows_are_not_summed_for_physical_buckets"])

    def test_current_and_final_summaries_are_identical_at_boundary(self):
        current = json.loads((M.MANIFEST_DIR /
            "g2-touch-current-source-readiness-summary.json").read_text())
        final = json.loads((M.MANIFEST_DIR /
            "g2-touch-final-classification-summary.json").read_text())
        self.assertEqual(current["whole_blob_bucket_bytes"],
                         final["metrics"]["whole_blob_bucket_bytes"])
        self.assertEqual(current["physical_bucket_digest"],
                         final["metrics"]["physical_bucket_digest"])
        self.assertTrue(current["classification_complete"])
        self.assertEqual(current["authoritative_batch"], 26)

    def test_only_final_classifier_writes_current_summary(self):
        for analyzer in M.TOOLS.glob("analyze_g2_touch_*admission*.py"):
            self.assertNotIn(
                "current.write_text",
                analyzer.read_text(encoding="utf-8"),
                analyzer.name,
            )

    def test_policy_is_software_only_and_not_production_routed(self):
        self.assertEqual(self.result["hardware_validation"],
                         "deferred by project direction")
        self.assertEqual(self.result["hardware_blocker"],
                         "deferred by project direction")
        self.assertFalse(self.result["production_routed"])
        self.assertNotIn("hardware_operations", self.result)

    def test_authenticated_blob_mutation_is_rejected(self):
        original = Path.read_bytes

        def changed(path):
            data = original(path)
            if path.name == "firmware_touch.bin":
                mutated = bytearray(data); mutated[0x100] ^= 1
                return bytes(mutated)
            return data

        with mock.patch.object(Path, "read_bytes", changed):
            with self.assertRaises((M.AuditError, RuntimeError, SystemExit)):
                M.analyze()


if __name__ == "__main__":
    unittest.main()
