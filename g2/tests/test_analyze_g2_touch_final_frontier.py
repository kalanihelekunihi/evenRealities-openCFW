# SPDX-License-Identifier: MIT
"""Fail-closed tests for final Touch function and physical-byte typing."""

import importlib.util
import csv
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
        self.assertEqual(metrics["typed_code_complement_bytes"], 15854)
        self.assertEqual(metrics["typed_noncode_bytes"], 3588)
        self.assertEqual(metrics["typed_noncode_partition"], {
            "vectors": 192, "strings": 1640, "config_and_tables": 1756,
        })
        self.assertEqual(len(self.result["physical_rows"]), 13)
        self.assertEqual(len({row["address_set_sha256"]
                              for row in self.result["physical_rows"]}), 13)
        self.assertEqual(sum(row["bytes"] for row in self.result["physical_rows"]),
                         34464)
        typed = [row for row in self.result["physical_rows"]
                 if row["category"].startswith("typed_")]
        self.assertEqual(sum(row["bytes"] for row in typed), 19442)
        self.assertTrue(all(row["unresolved_sub_boundary"] for row in typed))
        self.assertTrue(all(row["owner_or_category"] for row in typed))
        self.assertTrue(self.result["physical_derivation"]
                        ["instruction_rows_are_not_summed_for_physical_buckets"])
        self.assertEqual(metrics["candidate_union_address_set_sha256"],
                         M.EXPECTED_CANDIDATE_ADDRESS_SHA256)
        self.assertEqual(metrics["candidate_union_content_sha256"],
                         M.EXPECTED_CANDIDATE_CONTENT_SHA256)

    def test_candidate_union_is_not_blanket_mit_or_output_ownership(self):
        candidate = next(
            row for row in self.result["physical_rows"]
            if row["category"] == "project_source_candidate"
        )
        self.assertNotEqual(candidate["owner_or_category"],
                            "OpenCFW clean-room source candidates")
        self.assertNotEqual(candidate["license_status"], "MIT")
        self.assertIn("MIXED semantic routes", candidate["license_status"])
        self.assertIn("NOASSERTION", candidate["license_status"])
        self.assertIn("not production ELF ownership",
                      candidate["unresolved_sub_boundary"])

    def test_candidate_provenance_is_disjoint_licensed_and_conservative(self):
        provenance = self.result["candidate_provenance"]
        rows = self.result["candidate_provenance_rows"]
        self.assertEqual(sum(row["bytes"] for row in rows), 14510)
        self.assertEqual(provenance["candidate_bytes"], 14510)
        self.assertEqual(provenance["subrow_overlap_bytes"], 0)
        self.assertTrue(provenance["semantic_stock_address_candidates_only"])
        self.assertFalse(provenance["production_elf_ownership"])
        self.assertFalse(provenance[
            "stock_address_to_linked_output_identity_proven"])
        self.assertEqual(provenance["stock_byte_redistribution_authority"],
                         "NOASSERTION")
        self.assertFalse(provenance["eula_vendor_source_included"])
        self.assertFalse(provenance[
            "nonproduction_source_image_production_routed"])
        self.assertEqual(len({row["address_set_sha256"] for row in rows}),
                         len(rows))
        self.assertTrue(all(row["source_route_license"] in
                            M.ROUTE_LICENSES | {"NOASSERTION"}
                            for row in rows))
        self.assertTrue(all(row["semantic_stock_address_candidate_only"]
                            for row in rows))
        self.assertTrue(all(not row["admitted_body_linked_to_stock_address"]
                            for row in rows))
        self.assertTrue(all(not row["production_elf_ownership"]
                            for row in rows))
        self.assertTrue(all(row["stock_byte_license_authority"] ==
                            "NOASSERTION" for row in rows))
        self.assertTrue(all(not row["eula_vendor_source_included"]
                            for row in rows))
        self.assertFalse(any("linked_tu" in row["category"] for row in rows))

    def test_cat2_body_is_identified_not_linked_and_eula_is_excluded(self):
        rows = {row["category"]: row
                for row in self.result["candidate_provenance_rows"]}
        cat2 = rows["apache_cat2_upstream_body_identified_not_linked"]
        self.assertFalse(cat2[
            "translation_unit_present_in_nonproduction_source_image"])
        self.assertFalse(cat2["admitted_body_linked_to_stock_address"])
        critical = rows[
            "apache_critical_adapter_nonproduction_source_image_tu_semantic_route"
        ]
        self.assertTrue(critical[
            "translation_unit_present_in_nonproduction_source_image"])
        self.assertFalse(critical["admitted_body_linked_to_stock_address"])
        eeprom = rows[
            "project_mit_emeeprom_clean_room_nonproduction_source_image_tu_semantic_route"
        ]
        self.assertIn("EULA comparison source excluded",
                      eeprom["excluded_source_boundaries"])
        self.assertFalse(eeprom["eula_vendor_source_included"])

    def test_unlicensed_claim_and_source_spdx_mismatch_are_rejected(self):
        with self.assertRaises(M.AuditError):
            M._candidate_claim({
                "entry": "0x0002", "license": "", "source": "missing.c",
            }, "synthetic.tsv", {})
        with self.assertRaises(M.AuditError):
            M._require_source_spdx(
                "components/shared/touch/runtime_touch_policy_helpers.c",
                "Apache-2.0",
            )

    def test_overlapping_provenance_subrows_are_rejected(self):
        with self.assertRaises(M.AuditError):
            M._assert_disjoint_partition({"first": {1}, "second": {1}}, {1})

    def test_current_and_final_summaries_are_identical_at_boundary(self):
        current = json.loads((M.MANIFEST_DIR /
            "g2-touch-current-source-readiness-summary.json").read_text())
        final = json.loads((M.MANIFEST_DIR /
            "g2-touch-final-classification-summary.json").read_text())
        self.assertEqual(current["whole_blob_bucket_bytes"],
                         final["metrics"]["whole_blob_bucket_bytes"])
        self.assertEqual(current["physical_bucket_digest"],
                         final["metrics"]["physical_bucket_digest"])
        self.assertEqual(current["candidate_provenance"],
                         final["candidate_provenance"])
        self.assertEqual(current["generation_receipt"],
                         final["generation_receipt"])
        self.assertEqual(current["generation_receipt"]
                         ["logical_manifest_count"], 5)
        self.assertEqual(len(current["generation_receipt"]
                             ["rendered_outputs"]), 5)
        analysis_inputs = current["generation_receipt"]["analysis_inputs"]
        self.assertGreaterEqual(analysis_inputs["path_count"], 60)
        self.assertEqual(analysis_inputs["path_count"],
                         len(analysis_inputs["path_sha256"]))
        self.assertEqual(analysis_inputs, final["analysis_inputs"])
        self.assertTrue(current["semantic_stock_address_candidates_only"])
        self.assertFalse(current["candidate_source_is_production_elf_ownership"])
        self.assertEqual(current["stock_byte_redistribution_authority"],
                         "NOASSERTION")
        self.assertTrue(current["classification_complete"])
        self.assertEqual(current["authoritative_batch"], 26)

    def test_checked_candidate_provenance_manifest_has_no_license_holes(self):
        with M.CANDIDATE_PROVENANCE.open(newline="") as handle:
            rows = list(csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t",
            ))
        self.assertTrue(rows)
        self.assertEqual(sum(int(row["bytes"]) for row in rows), 14510)
        self.assertTrue(all(row["source_route_license"]
                            for row in rows))
        self.assertTrue(all(row["stock_byte_license_authority"] ==
                            "NOASSERTION" for row in rows))
        self.assertTrue(all(row["production_elf_ownership"] == "false"
                            for row in rows))
        self.assertTrue(all(row["admitted_body_linked_to_stock_address"] ==
                            "false" for row in rows))

    def test_checked_receipts_match_one_rendered_generation(self):
        self.assertEqual(M.check_manifests(self.result),
                         list(M._manifest_payloads(self.result)))

    def test_only_final_classifier_writes_current_summary(self):
        for analyzer in M.TOOLS.glob("analyze_g2_touch_*admission*.py"):
            self.assertNotIn(
                "current.write_text",
                analyzer.read_text(encoding="utf-8"),
                analyzer.name,
            )

    def test_policy_is_software_only_and_not_production_routed(self):
        self.assertEqual(self.result["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.result["hardware_blocker"],
                         "blocked by unavailable physical evidence")
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
