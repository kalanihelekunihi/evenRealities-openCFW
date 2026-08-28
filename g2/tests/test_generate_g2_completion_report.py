# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_g2_completion_report as generator


class G2CompletionReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = generator.build_outputs()
        cls.assessment = json.loads(
            cls.outputs[generator.ASSESSMENT_NAME].decode("utf-8"))

    def test_committed_report_is_exactly_reproducible(self) -> None:
        for name, expected in self.outputs.items():
            self.assertEqual((generator.REPORT_DIR / name).read_bytes(), expected)
        self.assertEqual(generator.write_outputs(generator.REPORT_DIR, check=True), [])

    def test_component_and_package_ledgers_conserve_every_byte(self) -> None:
        for row in self.assessment["components"]:
            self.assertEqual(sum(row["buckets"].values()), row["size"])
        aggregate = self.assessment["aggregate"]
        package = self.assessment["package"]
        self.assertEqual(sum(aggregate["buckets"].values()),
                         aggregate["component_payload_bytes"])
        self.assertEqual(aggregate["component_payload_bytes"] +
                         package["generated_envelope_bytes"],
                         package["expected_size"])
        self.assertTrue(package["conservation"][
            "matches_expected_package_size"])

    def test_distinct_readiness_and_authority_claims_are_not_collapsed(self) -> None:
        buckets = self.assessment["aggregate"]["buckets"]
        self.assertEqual(set(buckets), {
            "production_source", "generated_or_reconstructible",
            "candidate_source_not_routed", "typed_retained_or_external",
            "unclassified",
        })
        gates = self.assessment["gates"]
        self.assertTrue(gates["byte_accounting_complete"])
        self.assertTrue(gates["classification_complete"])
        self.assertFalse(gates["source_complete"])
        self.assertTrue(gates["source_ownership_quality_clean"])
        self.assertTrue(gates["project_license_policy_clean"])
        self.assertFalse(gates["binary_redistribution_authority_resolved"])
        self.assertFalse(gates["release_authorized"])

    def test_touch_chain_and_license_audit_are_live(self) -> None:
        touch = self.assessment["touch_admission"]
        self.assertGreater(touch["authoritative_batch"], 0)
        self.assertGreater(touch["admission_batches"], 0)
        self.assertGreater(touch["cumulative_candidate_instruction_bytes"], 0)
        self.assertFalse(touch["production_routed"])
        license_data = self.assessment["licensing"]
        self.assertTrue(license_data["source_metadata_clean"])
        self.assertEqual(license_data["source_errors"], 0)
        self.assertIn("MIT", license_data["source_license_counts"])
        self.assertEqual(
            set(license_data["unresolved_binary_authority"]),
            {row["component_id"] for row in
             license_data["binary_redistribution_authority"]},
        )

    def test_transitive_classification_and_overlay_inputs_are_pinned(self) -> None:
        recorded = {row["path"] for row in self.assessment["source_inputs"]}
        expected_touch = {
            path.relative_to(generator.ROOT).as_posix()
            for path in (generator.ROOT / "tools/manifests").glob(
                "g2-touch-*-admission-summary.json")
        }
        self.assertTrue(expected_touch)
        self.assertLessEqual(expected_touch, recorded)
        self.assertLessEqual({
            "components/apollo_main/core_overlay/overlay.json",
            "components/bootloader/core_overlay/overlay.json",
            "tools/manifests/g2-touch-final-classification-summary.json",
            "tools/manifests/g2-case-register-primitives-admission-summary.json",
            "tools/manifests/g2-case-register-transforms-admission-summary.json",
            "tools/manifests/g2-case-final-classification-summary.json",
            "tools/manifests/g2-production-raw-encoding-quality-summary.json",
            "tools/analyze_g2_production_raw_encoding_quality.py",
            "tools/manifests/g2-project-license-normalization.tsv",
            "tools/manifests/g2-project-license-normalization-summary.json",
            "tools/manifests/g2-project-mit-normalization-scope-paths.txt",
            "tools/manifests/g2-project-mit-normalization-research-and-wrapper.txt",
            "tools/analyze_g2_project_license_normalization.py",
        }, recorded)

    def test_raw_instruction_transcription_is_an_explicit_release_gate(self) -> None:
        quality = self.assessment["source_ownership_quality"]
        self.assertTrue(quality["clean"])
        self.assertEqual(
            quality["source_owned_bytes_currently_overstated"], 0)
        self.assertEqual(quality["semantic_literal_bytes"], 16)

    def test_project_license_policy_is_an_explicit_release_gate(self) -> None:
        policy = self.assessment["project_license_policy"]
        self.assertTrue(policy["clean"])
        self.assertEqual(policy["project_owned_normalization_targets"], 460)
        self.assertEqual(policy["project_owned_gpl_records_pending_mit"], 0)
        self.assertEqual(policy["upstream_gpl_records_preserved"], 1)

    def test_hardware_policy_is_exact_and_generator_is_device_inert(self) -> None:
        self.assertEqual(self.assessment["hardware_validation"],
                         generator.HARDWARE_STATUS)
        self.assertEqual(self.assessment["hardware_operations"], [])
        self.assertEqual(self.assessment["gates"]["hardware_validation"],
                         generator.HARDWARE_STATUS)
        self.assertEqual(self.assessment["gates"]["hardware_operations"], [])
        for content in self.outputs.values():
            text = content.decode("utf-8").lower()
            self.assertNotIn("hardware was unavailable", text)
            self.assertNotIn("unavailable hardware", text)

    def test_alternate_output_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary) / "assessment"
            self.assertEqual(generator.write_outputs(output_dir, check=False), [])
            for name, expected in self.outputs.items():
                self.assertEqual((output_dir / name).read_bytes(), expected)
            self.assertEqual(generator.write_outputs(output_dir, check=True), [])


if __name__ == "__main__":
    unittest.main()
