# SPDX-License-Identifier: MIT
"""Tests for bounded relocated touch semantic/provider and byte typing."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_relocated_semantics.py"
S = importlib.util.spec_from_file_location("g2_touch_relocated_semantics", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchRelocatedSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["semantic_rows"]}

    def test_all_223_rows_have_a_bounded_batch(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["semantic_rows"], 223)
        self.assertEqual(metrics["batch_counts"], {
            "application_startup_clean_room": 99,
            "capsense_cat2_mixed": 55,
            "cat2_pdl": 54,
            "emeeprom_eula": 10,
            "runtime": 4,
            "system_handoff_mixed": 1,
        })
        self.assertEqual(len(self.rows), 223)

    def test_no_batch_is_misrepresented_as_project_source(self):
        self.assertEqual(self.result["metrics"]["concrete_project_source_rows"], 0)
        self.assertTrue(all(not row["concrete_project_source"]
                            for row in self.rows.values()))
        self.assertIn("No newly batched row is concrete project source",
                      self.result["source_rule"])
        self.assertEqual(self.rows[0x4C08]["license"],
                         "LicenseRef-Infineon-EULA")
        self.assertEqual(self.rows[0x58F4]["license"], "Apache-2.0")

    def test_mixed_capsense_cat2_cluster_remains_unresolved(self):
        rows = [row for row in self.rows.values()
                if row["batch"] == "capsense_cat2_mixed"]
        self.assertEqual(len(rows), 55)
        self.assertTrue(all(row["name_status"] == "typed_batch_only"
                            for row in rows))
        self.assertTrue(all("EULA-or-Apache" in row["license"]
                            for row in rows))

    def test_exact_runtime_candidates_are_limited_and_named(self):
        self.assertEqual(self.result["metrics"]["exact_runtime_rows"], 4)
        self.assertEqual(
            {entry: self.rows[entry]["proposed_name"]
             for entry in M.RUNTIME_EXACT},
            {0x76AC: "exit_wrapper", 0x76E4: "__libc_init_array",
             0x7740: "_exit_halt", 0x7744: "runtime_init_stub"},
        )

    def test_linked_switch_tables_add_cases_not_false_functions(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["dispatch_case_entries"], 23)
        self.assertEqual({row["table_offset"] for row in self.result["dispatch_rows"]},
                         {0x7DC4, 0x81FC, 0x821C})
        self.assertEqual(metrics["final_code_partition"]
                         ["dispatch_case_instruction_candidate"], 482)

    def test_expanded_entries_are_pinned(self):
        self.assertEqual(self.result["metrics"]["expanded_function_entries"], 301)
        self.assertEqual(set(M.LINEAR_PROLOGUE_ENTRIES),
                         {0x0320, 0x29F8, 0x2CC6, 0x2D44, 0x2D78,
                          0x2DEA, 0x35EC, 0x3780, 0x7750})

    def test_final_physical_partition_is_exhaustive(self):
        expected = {
            "cfg_instruction_candidate": 27674,
            "dispatch_case_instruction_candidate": 482,
            "referenced_literal_data": 1964,
            "residual_arch_nop_padding": 8,
            "residual_legacy_nop_padding": 126,
            "residual_return_tail": 4,
            "residual_typed_data": 60,
            "residual_zero_halfword_alignment_or_data": 46,
        }
        self.assertEqual(self.result["metrics"]["final_code_partition"], expected)
        self.assertEqual(sum(expected.values()), 30364)
        self.assertEqual(sum(row["bytes"] for row in self.result["byte_rows"]),
                         30364)
        self.assertEqual(self.result["remaining_opacity"]["byte_unclassified"], 0)
        self.assertEqual(self.result["remaining_opacity"]
                         ["byte_semantically_ambiguous"], 46)

    def test_prior_1584_bytes_are_fully_accounted(self):
        expected = {
            "cfg_instruction_candidate": 782,
            "dispatch_case_instruction_candidate": 482,
            "referenced_literal_data": 76,
            "residual_arch_nop_padding": 8,
            "residual_legacy_nop_padding": 126,
            "residual_return_tail": 4,
            "residual_typed_data": 60,
            "residual_zero_halfword_alignment_or_data": 46,
        }
        self.assertEqual(self.result["metrics"]["prior_1584_partition"], expected)
        self.assertEqual(sum(expected.values()), 1584)

    def test_all_72_overlap_bytes_resolve_as_literal_data(self):
        self.assertEqual(self.result["metrics"]["resolved_prior_ambiguous_bytes"],
                         72)
        self.assertEqual(sum(row["bytes"] for row in self.result["ambiguity_rows"]),
                         72)
        self.assertTrue(all(row["resolution"] ==
                            "referenced_literal_data_precedence"
                            for row in self.result["ambiguity_rows"]))

    def test_digests_and_software_only_mode_are_pinned(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["semantic_digest"],
                         "84fd01c5d0b8fe7ad0d1784e03c10f179ecdad90fcde2cf8cc863bd118b45864")
        self.assertEqual(metrics["byte_digest"],
                         "e8cd2af0475a22c070e04962a51977a370b12cc5ce6c86a271e686a10393df58")
        self.assertIn("no hardware", self.result["analysis_mode"])

    def test_manifest_writes_are_deterministic(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                first = M.write_manifests(self.result)
                first_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in first}
                second = M.write_manifests(M.analyze())
                second_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in second}
                self.assertEqual(first_hashes, second_hashes)
                self.assertEqual(set(first_hashes), {
                    "g2-touch-relocated-semantic-batches.tsv",
                    "g2-touch-relocated-final-byte-types.tsv",
                    "g2-touch-relocated-ambiguity-resolution.tsv",
                    "g2-touch-relocated-semantic-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
