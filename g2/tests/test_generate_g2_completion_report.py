# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


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
        self.assertTrue(gates["dual_profile_ownership_reconciliation"])
        self.assertTrue(gates["functional_software_gap_rows_zero"])
        self.assertTrue(gates["functional_hardware_rows_explicitly_blocked"])
        self.assertTrue(
            gates["functional_proprietary_rows_explicitly_blocked"])
        self.assertTrue(
            gates["candidate_artifacts_complete_and_hardware_blocked"])
        self.assertFalse(gates["binary_redistribution_authority_resolved"])
        self.assertFalse(gates["release_authorized"])

    def test_nine_domain_functional_ledger_is_semantically_closed(self) -> None:
        ledger = self.assessment["functional_capability_ledger"]
        self.assertEqual(set(ledger["domain_counts"]),
                         set(generator.CAPABILITY_DOMAINS))
        self.assertEqual(ledger["row_count"], 185)
        self.assertEqual(ledger["totals"], {
            "implemented-in-source": 152,
            "software-gap": 0,
            "hardware-dependent": 19,
            "proprietary-blocked": 14,
        })
        self.assertEqual(ledger["software_gap_rows"], 0)
        self.assertTrue(ledger["software_gap_gate"])
        self.assertEqual(ledger["hardware_marked_rows"], 130)
        self.assertEqual(ledger["hardware_rows_explicitly_blocked"], 130)
        self.assertTrue(ledger["hardware_blocker_wording_gate"])
        self.assertEqual(ledger["hardware_blocker_wording_failures"], [])
        self.assertEqual(ledger["proprietary_marked_rows"], 16)
        self.assertEqual(ledger["proprietary_rows_explicitly_blocked"], 16)
        self.assertTrue(ledger["proprietary_blocker_wording_gate"])
        self.assertEqual(ledger["proprietary_blocker_wording_failures"], [])

    def test_candidate_images_are_compilable_and_exactly_hardware_blocked(
            self) -> None:
        boundaries = self.assessment["candidate_admission_boundaries"]
        self.assertEqual(set(boundaries), {"touch", "case"})
        self.assertEqual(
            sum(row["candidate_bytes"] for row in boundaries.values()),
            self.assessment["aggregate"]["buckets"]
            ["candidate_source_not_routed"],
        )
        self.assertEqual(boundaries["touch"]["candidate_bytes"], 14_510)
        self.assertEqual(boundaries["touch"]["source_translation_units"], 31)
        self.assertEqual(boundaries["touch"]["candidate_source_functions"], 178)
        self.assertEqual(
            boundaries["touch"]["blocker_class"],
            "hardware-dependent-resident-abi",
        )
        self.assertEqual(boundaries["case"]["candidate_bytes"], 14_886)
        self.assertEqual(boundaries["case"]["source_translation_units"], 8)
        self.assertEqual(boundaries["case"]["candidate_source_functions"], 222)
        self.assertEqual(
            boundaries["case"]["blocker_class"],
            "hardware-dependent-board-routing",
        )
        for row in boundaries.values():
            self.assertEqual(row["remaining_callable_software_functions"], 0)
            self.assertEqual(row["undefined_symbols"], 0)
            self.assertTrue(row["software_link_complete"])
            self.assertTrue(row["software_package_complete"])
            self.assertFalse(row["production_routed"])
            self.assertFalse(row["physical_board_services_routed"])
            self.assertEqual(
                row["hardware_validation"], generator.HARDWARE_STATUS)
            self.assertEqual(row["hardware_operations"], [])

    def test_checked_dual_profile_companion_is_publicly_bound(self) -> None:
        ownership = self.assessment["dual_profile_ownership"]
        self.assertTrue(ownership["checked"])
        self.assertEqual(ownership["companion_schema_version"], 4)
        self.assertEqual(
            ownership["per_byte_ownership_policy"],
            {
                "all_profiles_mask_complete": False,
                "linux_per_byte_ownership_mask_complete": False,
                "qualification": (
                    "Linux aggregate buckets and typed-mixed spans are exact, "
                    "but no Linux per-byte source/generated/retained ownership "
                    "is fabricated"
                ),
                "sole_current_authority_profile": "apple-clang",
            },
        )
        companion = generator.ROOT / ownership["companion"]
        self.assertEqual(
            hashlib.sha256(companion.read_bytes()).hexdigest(),
            ownership["companion_sha256"],
        )
        self.assertFalse(ownership["per_byte_ownership_mask_complete"])
        self.assertEqual(
            ownership["sole_current_per_byte_ownership_authority_profile"],
            "apple-clang",
        )
        self.assertIn("Linux coarse spans", ownership["limitation"])
        expected = {
            "apple-clang": (
                4750780,
                "f2842600b84f303c40d2d299761c1abc0a7083acc05f2d378be9a045b0d9a846",
                4749836,
                0,
                120246,
            ),
            "linux-clang": (
                4750764,
                "e534ffe034360b24fffc3d7fc50988234fc48ae20f6e8afa8be2507247c8cd39",
                4749820,
                0,
                3359246,
            ),
        }
        for profile, values in expected.items():
            row = ownership["profiles"][profile]
            self.assertEqual(row["package_size"], values[0])
            self.assertEqual(row["package_sha256"], values[1])
            self.assertEqual(row["component_payload_bytes"], values[2])
            self.assertEqual(row["aggregate_buckets"]["unclassified"], values[3])
            self.assertEqual(row["internal_component_container_bytes"], 300)
            self.assertEqual(row["outer_evenota_envelope_bytes"], 944)
            self.assertEqual(
                row["bytes_requiring_address_label_reconciliation"], values[4]
            )
            self.assertEqual(
                sum(row["aggregate_buckets"].values()),
                row["component_payload_bytes"],
            )
        self.assertTrue(ownership["profiles"]["apple-clang"]
                        ["per_byte_ownership_mask_complete"])
        self.assertFalse(ownership["profiles"]["linux-clang"]
                         ["per_byte_ownership_mask_complete"])
        self.assertIn("aggregate totals", ownership["profiles"]["linux-clang"]
                      ["per_byte_ownership_authority"])

    def test_touch_chain_and_license_audit_are_live(self) -> None:
        touch = self.assessment["touch_admission"]
        self.assertGreater(touch["authoritative_batch"], 0)
        self.assertGreater(touch["admission_batches"], 0)
        self.assertGreater(touch["cumulative_candidate_instruction_bytes"], 0)
        self.assertFalse(touch["production_routed"])
        provenance = touch["candidate_provenance"]
        self.assertEqual(provenance["candidate_bytes"], 14_510)
        self.assertEqual(provenance["subrow_overlap_bytes"], 0)
        self.assertTrue(provenance["semantic_stock_address_candidates_only"])
        self.assertFalse(provenance["production_elf_ownership"])
        self.assertEqual(
            provenance["stock_byte_redistribution_authority"], "NOASSERTION")
        self.assertEqual(
            touch["candidate_provenance_manifest"],
            "g2-touch-final-source-candidate-provenance.tsv",
        )
        self.assertEqual(touch["analysis_input_count"], 69)
        self.assertEqual(
            touch["generation_receipt_sha256"],
            "08273958361436eca0a774812de8ca917d6d724d2de836a9f745737d86467aa9",
        )
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
            "tools/manifests/g2-touch-final-source-candidate-provenance.tsv",
            "tools/manifests/g2-case-register-primitives-admission-summary.json",
            "tools/manifests/g2-case-register-transforms-admission-summary.json",
            "tools/manifests/g2-case-final-classification-summary.json",
            "tools/manifests/g2-production-raw-encoding-quality-summary.json",
            "tools/analyze_g2_production_raw_encoding_quality.py",
            "tools/manifests/g2-project-license-normalization.tsv",
            "tools/manifests/g2-project-license-normalization-summary.json",
            "tools/manifests/g2-project-mit-normalization-scope-paths.txt",
            "tools/manifests/g2-project-mit-normalization-research-and-wrapper.txt",
            "tools/manifests/em9305-final-source-readiness.tsv",
            "tools/manifests/em9305-final-source-readiness-summary.json",
            "tools/analyze_g2_project_license_normalization.py",
            "tools/analyze_g2_dual_profile_ownership.py",
            "tools/analyze_g2_touch_final_frontier.py",
            "tools/manifests/g2-dual-profile-ownership.json",
            "tools/open_cfw.py",
        }, recorded)

    def test_all_readiness_receipts_are_direct_currentness_inputs(self) -> None:
        receipts = (
            generator.readiness.TOUCH_SOURCE_IMAGE,
            generator.readiness.EM9305_FINAL_LEDGER,
            generator.readiness.EM9305_FINAL_SUMMARY,
            generator.readiness.TOUCH_CANDIDATE_PROVENANCE,
            generator.readiness.CASE_SOURCE_IMAGE,
            generator.readiness.NEMAVG_STROKE_CAPS,
            generator.readiness.CLKMGR_DIVIDERS,
            generator.readiness.PT_SOURCE,
            generator.readiness.CASE_SEMANTIC_LEAVES,
            generator.readiness.CASE_PURE_HELPERS,
            generator.readiness.CASE_REGISTER_POLICIES,
        )
        self.assertEqual(len(receipts), len(set(receipts)))
        self.assertLessEqual(set(receipts), set(generator.DIRECT_INPUTS))
        recorded = {
            row["path"]: row for row in self.assessment["source_inputs"]
        }
        for receipt in receipts:
            relative = receipt.relative_to(generator.ROOT).as_posix()
            self.assertEqual(recorded[relative], generator._input_record(receipt))

    def test_source_input_count_is_the_current_dynamic_union(self) -> None:
        dual_records = generator._bound_dual_input_records(
            generator.dual_ownership.analyze())
        touch_records = generator._bound_touch_input_records(
            generator.readiness.analyze())
        expected_paths = {
            path.relative_to(generator.ROOT).as_posix()
            for path in generator.DIRECT_INPUTS
        } | {row["path"] for row in dual_records} | {
            row["path"] for row in touch_records
        }
        recorded_paths = {
            row["path"] for row in self.assessment["source_inputs"]
        }
        self.assertEqual(len(expected_paths), 166)
        self.assertEqual(recorded_paths, expected_paths)
        self.assertEqual(len(self.assessment["source_inputs"]),
                         len(expected_paths))

    def test_touch_generation_receipt_inputs_are_publicly_bound(self) -> None:
        live = generator.readiness.analyze()
        touch_records = generator._bound_touch_input_records(live)
        self.assertEqual(len(touch_records), 69)
        recorded = {
            row["path"]: row for row in self.assessment["source_inputs"]
        }
        for row in touch_records:
            self.assertEqual(recorded[row["path"]], row)

    def test_readiness_receipt_identity_drift_changes_assessment(self) -> None:
        target = generator.readiness.CLKMGR_DIVIDERS
        original_input_record = generator._input_record

        def drifted_input_record(path: Path) -> dict[str, object]:
            row = original_input_record(path)
            if path == target:
                row = dict(row)
                row["sha256"] = "0" * 64
            return row

        with mock.patch.object(
            generator, "_input_record", side_effect=drifted_input_record
        ):
            changed = generator.build_outputs()
        self.assertNotEqual(
            changed[generator.ASSESSMENT_NAME],
            self.outputs[generator.ASSESSMENT_NAME],
        )

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
            # macOS exposes /var as a system symlink to /private/var; hand the
            # no-follow report writer the canonical temporary parent.
            output_dir = Path(temporary).resolve() / "assessment"
            self.assertEqual(generator.write_outputs(output_dir, check=False), [])
            for name, expected in self.outputs.items():
                self.assertEqual((output_dir / name).read_bytes(), expected)
            self.assertEqual(generator.write_outputs(output_dir, check=True), [])


class G2CompletionReportStaticSafetyTests(unittest.TestCase):
    """Exercise report bindings without invoking the package-dependent audit."""

    def test_analyzer_closure_and_source_complete_definition_are_explicit(self) -> None:
        generator._verify_direct_analyzer_import_closure()
        self.assertEqual(len(generator.DIRECT_ANALYZER_INPUTS), 28)
        paths = {
            path.relative_to(generator.ROOT).as_posix()
            for path in generator.DIRECT_INPUTS
        }
        self.assertLessEqual({
            "tools/analyze_em9305_source_readiness.py",
            "tools/analyze_gx8002_source_readiness.py",
            "tools/apply_g2_canonical_observations.py",
            "tools/analyze_g2_dual_profile_ownership.py",
            "tools/analyze_g2_touch_final_frontier.py",
        }, paths)
        for bucket in ("candidate", "retained/external", "unclassified"):
            self.assertIn(bucket, generator.SOURCE_COMPLETE_DEFINITION)

    def test_functional_ledger_gap_and_hardware_wording_fail_closed(self) -> None:
        source = generator.CAPABILITY_LEDGER.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary).resolve() / "ledger.md"
            software_gap = source.replace(
                "| Protocol | 62 | 0 | 3 | 5 |",
                "| Protocol | 61 | 1 | 3 | 5 |",
                1,
            ).replace(
                "| implemented-in-source / hardware-deferred |",
                "| software-gap |",
                1,
            )
            path.write_text(software_gap, encoding="utf-8")
            report = generator._functional_capability_ledger(path)
            self.assertEqual(report["software_gap_rows"], 1)
            self.assertFalse(report["software_gap_gate"])

            missing_block = source.replace(
                "physical case execution is blocked by unavailable physical evidence",
                "physical case execution is pending",
                1,
            )
            path.write_text(missing_block, encoding="utf-8")
            report = generator._functional_capability_ledger(path)
            self.assertFalse(report["hardware_blocker_wording_gate"])
            self.assertEqual(len(report["hardware_blocker_wording_failures"]), 1)

            missing_proprietary_block = source.replace(
                "resident image is blocked by unavailable proprietary inputs",
                "resident image is pending",
                1,
            )
            path.write_text(missing_proprietary_block, encoding="utf-8")
            report = generator._functional_capability_ledger(path)
            self.assertFalse(report["proprietary_blocker_wording_gate"])
            self.assertEqual(
                len(report["proprietary_blocker_wording_failures"]), 1)

    def test_dual_profile_private_receipts_are_exact_direct_inputs(self) -> None:
        expected = generator._input_record(
            generator.ROOT / "tools/generate_g2_completion_report.py"
        )
        report = {
            "profiles": {
                "test-profile": {
                    "main_observation": {"observation_reports": [expected]},
                    "boot_provider": {"report": expected},
                    "package": {
                        "package_report": expected,
                        "flash_plan": expected,
                    },
                }
            }
        }
        self.assertEqual(
            generator._bound_dual_input_records(report), [expected]
        )
        changed = json.loads(json.dumps(report))
        changed["profiles"]["test-profile"]["package"][
            "flash_plan"
        ]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            generator.ReportError, "direct input identity changed"
        ):
            generator._bound_dual_input_records(changed)

    def test_report_reads_and_writes_reject_links_and_hardlinks(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="completion-report-path-safety-",
            dir=generator.ROOT / "tests",
        ) as temporary:
            root = Path(temporary)
            target = root / "target.json"
            target.write_bytes(b"preserve\n")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaisesRegex(generator.ReportError, "opened safely"):
                generator._read_regular_path_once(link, label="test input")
            with self.assertRaisesRegex(generator.ReportError, "opened safely"):
                generator._atomic_write_output(link, b"replacement\n")
            self.assertEqual(target.read_bytes(), b"preserve\n")

            link.unlink()
            hardlink = root / "hardlink.json"
            os.link(target, hardlink)
            with self.assertRaisesRegex(
                generator.ReportError, "not an independent regular file"
            ):
                generator._atomic_write_output(target, b"replacement\n")
            self.assertEqual(target.read_bytes(), b"preserve\n")

            hardlink.unlink()
            output = root / "output/report.json"
            generator._atomic_write_output(output, b"complete\n")
            self.assertEqual(output.read_bytes(), b"complete\n")


if __name__ == "__main__":
    unittest.main()
