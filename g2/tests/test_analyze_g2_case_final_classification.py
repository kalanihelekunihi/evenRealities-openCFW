# SPDX-License-Identifier: MIT
"""Tests for exhaustive charging-case frontier classification."""

import importlib.util, json, sys, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_case_final_classification.py"
S = importlib.util.spec_from_file_location("g2_case_final", P)
M = importlib.util.module_from_spec(S); sys.modules[S.name] = M; S.loader.exec_module(M)


class CaseFinalClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.result = M.analyze()

    def test_exact_prior_frontier_is_fully_typed(self):
        metrics = self.result["metrics"]
        self.assertTrue(self.result["classification_complete"])
        self.assertEqual((metrics["frontier_function_rows"],
                          metrics["frontier_function_bytes"]), (222, 14886))
        self.assertEqual((metrics["frontier_gap_rows"],
                          metrics["frontier_gap_bytes"]), (229, 2184))
        self.assertEqual(metrics["prior_unresolved_bytes"], 17070)
        self.assertEqual((metrics["unclassified_functions"],
                          metrics["unclassified_bytes"]), (0, 0))
        self.assertTrue(all(r["missing_fact_or_reason"]
                            for r in self.result["function_rows"] +
                            self.result["gap_rows"]))

    def test_physical_buckets_are_disjoint_and_conserve_blob(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["whole_blob_bucket_bytes"], {
            "generated_transport_fill": 32,
            "project_source_candidate": 14886,
            "typed_external_or_unsupported": 40866,
            "still_unclassified": 0,
        })
        self.assertEqual(sum(metrics["whole_blob_bucket_bytes"].values()), 55784)
        self.assertEqual(len(self.result["physical_rows"]), 3)
        self.assertEqual(len({r["address_set_sha256"]
                              for r in self.result["physical_rows"]}), 3)

    def test_source_candidates_are_exactly_the_admitted_leaves(self):
        rows = [r for r in self.result["function_rows"]
                if r["classification"] == "project_source_candidate_not_routed"]
        self.assertEqual((len(rows), sum(r["size"] for r in rows)), (222, 14886))
        self.assertEqual(
            self.result["metrics"]["authenticated_candidate_decompilation_rows"],
            222)
        self.assertEqual(self.result["metrics"]["candidate_source_breakdown"], {
            "g2-case-register-primitives-admission.tsv": {
                "functions": 13, "instruction_bytes": 120},
            "g2-case-register-transforms-admission.tsv": {
                "functions": 5, "instruction_bytes": 96},
            "g2-case-semantic-leaves-admission.tsv": {
                "functions": 189, "instruction_bytes": 14208},
            "g2-case-pure-helpers-admission.tsv": {
                "functions": 7, "instruction_bytes": 248},
            "g2-case-register-policies-admission.tsv": {
                "functions": 8, "instruction_bytes": 214},
        })
        self.assertFalse(self.result["production_routed"])
        self.assertEqual(self.result["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.result["hardware_operations"], [])

    def test_authenticated_blob_mutation_is_rejected(self):
        original = Path.read_bytes
        def changed(path):
            data = original(path)
            if path.name == "firmware_box.bin":
                result = bytearray(data); result[0x100] ^= 1; return bytes(result)
            return data
        with mock.patch.object(Path, "read_bytes", changed):
            with self.assertRaises(M.AuditError): M.analyze()

    def _assert_summary_mutation_rejected(self, mutate):
        original = Path.read_text

        def changed(path, *args, **kwargs):
            data = original(path, *args, **kwargs)
            if path == M.FUNCTION_SUMMARY:
                summary = json.loads(data)
                mutate(summary)
                return json.dumps(summary)
            return data

        with mock.patch.object(Path, "read_text", changed):
            with self.assertRaises(M.AuditError):
                M.analyze()

    def test_zero_length_gap_is_rejected_even_if_declared_total_is_preserved(self):
        def mutate(summary):
            gaps = [row for row in summary["gap_rows"]
                    if row["ownership_category"] == "unresolved"]
            removed = gaps[0]["bytes"]
            gaps[0]["end"] = gaps[0]["start"]
            gaps[0]["bytes"] = 0
            gaps[1]["bytes"] += removed

        self._assert_summary_mutation_rejected(mutate)

    def test_overlapping_gap_intervals_are_rejected(self):
        def mutate(summary):
            gaps = [row for row in summary["gap_rows"]
                    if row["ownership_category"] == "unresolved"]
            gaps[1]["start"] = gaps[0]["start"]
            gaps[1]["end"] = gaps[1]["start"] + gaps[1]["bytes"]

        self._assert_summary_mutation_rejected(mutate)

    def test_gap_extent_and_declared_size_must_agree(self):
        def mutate(summary):
            gap = next(row for row in summary["gap_rows"]
                       if row["ownership_category"] == "unresolved")
            gap["end"] -= 1

        self._assert_summary_mutation_rejected(mutate)


if __name__ == "__main__": unittest.main()
