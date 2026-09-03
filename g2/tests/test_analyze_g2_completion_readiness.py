from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_completion_readiness as analyzer


class G2CompletionReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = analyzer.analyze()

    def test_every_shipped_component_is_present(self) -> None:
        self.assertEqual(set(self.report["components"]), {
            "apollo_main", "apollo_bootloader", "codec", "ble_em9305",
            "touch", "case",
        })

    def test_every_component_and_aggregate_conserve_bytes(self) -> None:
        for component in self.report["components"].values():
            self.assertEqual(sum(component["buckets"].values()), component["size"])
            self.assertEqual(component["hardware_operations"], [])
        aggregate = self.report["aggregate"]
        self.assertEqual(sum(aggregate["buckets"].values()),
                         aggregate["component_payload_bytes"])
        self.assertEqual(aggregate["component_payload_bytes"] +
                         aggregate["package_envelope_bytes"],
                         aggregate["package_bytes"])

    def test_open_boundaries_are_derived_fail_closed(self) -> None:
        self.assertTrue(self.report["gates"]["byte_accounting_complete"])
        aggregate = self.report["aggregate"]
        self.assertEqual(self.report["gates"]["classification_complete"],
                         not aggregate["unclassified_components"])
        self.assertEqual(self.report["gates"]["source_complete"],
                         not aggregate["source_incomplete_components"])
        self.assertEqual(aggregate["buckets"]["unclassified"], sum(
            row["buckets"]["unclassified"]
            for row in self.report["components"].values()))

    def test_touch_rapid_admission_chain_is_reflected(self) -> None:
        touch = self.report["components"]["touch"]
        progress = touch["details"]
        self.assertGreater(progress["authoritative_batch"], 0)
        self.assertGreater(progress["admission_batches"], 0)
        self.assertGreater(progress["cumulative_candidate_instruction_bytes"], 0)
        current = analyzer._read(analyzer.TOUCH_CURRENT)
        if current.get("classification_complete", False):
            final = analyzer._read(analyzer.TOUCH_FINAL)
            self.assertEqual(current["whole_blob_bucket_bytes"],
                             final["metrics"]["whole_blob_bucket_bytes"])
            self.assertEqual(current["physical_bucket_digest"],
                             final["metrics"]["physical_bucket_digest"])
            self.assertEqual(touch["buckets"]["unclassified"], 0)
            self.assertEqual(
                touch["buckets"]["candidate_source_not_routed"],
                current["whole_blob_bucket_bytes"]["project_source_candidate"])
        else:
            baseline = analyzer._read(analyzer.TOUCH_SUMMARY)["metrics"][
                "whole_blob_bucket_bytes"]["project_source_candidate"]
            self.assertEqual(
                touch["buckets"]["candidate_source_not_routed"],
                baseline + progress["cumulative_candidate_instruction_bytes"],
            )

    def test_touch_candidate_provenance_is_disjoint_mixed_license_evidence(
            self) -> None:
        touch = self.report["components"]["touch"]
        rows = analyzer._touch_candidate_provenance_rows()
        provenance = touch["details"]["candidate_provenance"]
        self.assertEqual(
            [row["category"] for row in rows],
            list(analyzer.TOUCH_CANDIDATE_ROUTE_ORDER),
        )
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 14_510)
        self.assertEqual(provenance["candidate_bytes"], 14_510)
        self.assertEqual(provenance["subrow_count"], len(rows))
        self.assertEqual(provenance["subrow_overlap_bytes"], 0)
        self.assertEqual(provenance["row_digest"], hashlib.sha256(json.dumps(
            rows, sort_keys=True, separators=(",", ":")
        ).encode()).hexdigest())
        self.assertEqual(
            provenance["manifest"],
            "g2-touch-final-source-candidate-provenance.tsv",
        )
        self.assertTrue(provenance["semantic_stock_address_candidates_only"])
        self.assertFalse(provenance["production_elf_ownership"])
        self.assertFalse(
            provenance["stock_address_to_linked_output_identity_proven"])
        self.assertEqual(
            provenance["stock_byte_redistribution_authority"], "NOASSERTION")
        self.assertFalse(provenance["eula_vendor_source_included"])
        self.assertFalse(
            provenance["nonproduction_source_image_production_routed"])
        self.assertEqual(
            touch["buckets"]["candidate_source_not_routed"],
            provenance["candidate_bytes"],
        )

    def test_touch_candidate_provenance_rows_fail_closed(self) -> None:
        rows = analyzer._touch_candidate_provenance_rows()
        with self.assertRaisesRegex(
                analyzer.AuditError, "category order or membership"):
            analyzer._validate_touch_candidate_provenance_rows(rows[:-1])
        overclaimed = deepcopy(rows)
        overclaimed[0]["production_elf_ownership"] = True
        with self.assertRaisesRegex(
                analyzer.AuditError, "overclaims stock-address ownership"):
            analyzer._validate_touch_candidate_provenance_rows(overclaimed)
        unlicensed = deepcopy(rows)
        non_overlap = next(
            row for row in unlicensed
            if row["category"] != analyzer.TOUCH_CANDIDATE_OVERLAP_CATEGORY
        )
        non_overlap["source_route_license"] = "NOASSERTION"
        with self.assertRaisesRegex(
                analyzer.AuditError, "non-overlap candidate mixes"):
            analyzer._validate_touch_candidate_provenance_rows(unlicensed)

    def test_touch_generation_receipt_binds_every_analysis_input(self) -> None:
        current = analyzer._read(analyzer.TOUCH_CURRENT)
        final = analyzer._read(analyzer.TOUCH_FINAL)
        receipt = analyzer._touch_generation_receipt(current, final)
        inputs = receipt["analysis_inputs"]
        self.assertEqual(inputs["path_count"], 69)
        self.assertEqual(len(inputs["path_sha256"]), 69)
        self.assertEqual(
            inputs["aggregate_sha256"],
            "314622feca33964631d7f7ee69168cd6659b91e598bc9f554f05b995e8abc31a",
        )
        self.assertEqual(receipt["logical_manifest_count"], 5)
        self.assertEqual(set(receipt["rendered_outputs"]), {
            "g2-touch-current-source-readiness-summary.json:core",
            "g2-touch-final-classification-summary.json:core",
            "g2-touch-final-frontier.tsv",
            "g2-touch-final-physical-byte-buckets.tsv",
            "g2-touch-final-source-candidate-provenance.tsv",
        })
        self.assertEqual(
            self.report["components"]["touch"]["details"]
            ["generation_receipt"],
            receipt,
        )

    def test_touch_generation_receipt_disagreement_fails_closed(self) -> None:
        current = analyzer._read(analyzer.TOUCH_CURRENT)
        final = analyzer._read(analyzer.TOUCH_FINAL)
        changed = deepcopy(final)
        changed["generation_receipt"]["analysis_inputs"]["path_count"] = 68
        with self.assertRaisesRegex(
                analyzer.AuditError, "generation receipts disagree"):
            analyzer._touch_generation_receipt(current, changed)

    def test_licensing_and_hardware_policy_remain_honest(self) -> None:
        self.assertTrue(self.report["gates"]["source_metadata_clean"])
        unresolved = self.report["licensing"]["unresolved_binary_authority"]
        self.assertEqual(
            self.report["gates"]["binary_redistribution_authority_resolved"],
            not unresolved)
        self.assertEqual(self.report["gates"]["release_authorized"],
                         not unresolved and
                         self.report["gates"]["source_metadata_clean"] and
                         self.report["gates"]["source_ownership_quality_clean"] and
                         self.report["gates"]["project_license_policy_clean"])
        self.assertEqual(self.report["gates"]["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.report["gates"]["hardware_blocker"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.report["gates"]["hardware_operations"], [])

    def test_raw_instruction_transcription_source_ownership_gate_is_clean(self) -> None:
        quality = self.report["source_ownership_quality"]
        self.assertTrue(self.report["gates"]["source_ownership_quality_clean"])
        self.assertTrue(quality["clean"])
        self.assertEqual(
            quality["source_owned_bytes_currently_overstated"], 0)
        self.assertEqual(quality["raw_instruction_transcription_bytes"], 0)
        self.assertEqual(quality["semantic_literal_bytes"], 16)

    def test_project_owned_sources_pass_mit_policy_gate(self) -> None:
        policy = self.report["project_license_policy"]
        self.assertTrue(self.report["gates"]["project_license_policy_clean"])
        self.assertTrue(policy["clean"])
        self.assertEqual(policy["project_owned_normalization_targets"], 460)
        self.assertEqual(policy["project_owned_records_normalized_mit"], 460)
        self.assertEqual(policy["project_owned_gpl_records_pending_mit"], 0)
        self.assertEqual(policy["overlay_records_pending_mit"], 0)
        self.assertEqual(
            policy["distributed_project_mit_normalization_targets"], 919)
        self.assertEqual(
            policy["community_controller_and_adapter_source_files"], 112)
        self.assertEqual(
            policy["community_project_mit_compatible_source_files"], 109)
        self.assertEqual(
            policy["community_touch_apache_source_files_preserved"], 3)
        self.assertEqual(policy["touch_source_image_project_mit_files"], 9)
        self.assertEqual(policy["touch_source_image_package_files"], 6)
        self.assertEqual(policy["touch_source_image_support_files"], 3)
        self.assertEqual(policy["case_source_image_project_mit_files"], 7)
        self.assertEqual(policy["case_source_image_package_files"], 5)
        self.assertEqual(policy["case_source_image_support_files"], 2)
        self.assertEqual(policy["em9305_source_image_project_mit_files"], 19)
        self.assertEqual(policy["em9305_source_image_package_files"], 11)
        self.assertEqual(policy["em9305_source_image_support_files"], 8)
        self.assertEqual(policy["pt_protocol_project_mit_files"], 28)
        self.assertEqual(policy["upstream_gpl_records_preserved"], 1)

    def test_case_final_frontier_is_reflected(self) -> None:
        case = self.report["components"]["case"]
        final = analyzer._read(analyzer.CASE_FINAL)
        self.assertEqual(case["details"]["register_primitive_candidate_bytes"],
                         120)
        self.assertEqual(case["details"]["register_primitive_candidate_functions"],
                         13)
        self.assertEqual(case["details"]["register_transform_candidate_bytes"],
                         96)
        self.assertEqual(case["details"]["register_transform_candidate_functions"],
                         5)
        self.assertEqual(case["details"]["semantic_leaf_candidate_bytes"], 14208)
        self.assertEqual(case["details"]["semantic_leaf_candidate_functions"], 189)
        self.assertEqual(case["details"]["pure_helper_candidate_bytes"], 248)
        self.assertEqual(case["details"]["pure_helper_candidate_functions"], 7)
        self.assertEqual(case["details"]["register_policy_candidate_bytes"], 214)
        self.assertEqual(case["details"]["register_policy_candidate_functions"], 8)
        self.assertEqual(case["details"]["register_candidate_bytes"], 14886)
        self.assertEqual(case["details"]["register_candidate_functions"], 222)
        self.assertTrue(final["classification_complete"])
        self.assertEqual(case["buckets"]["candidate_source_not_routed"],
                         final["metrics"]["whole_blob_bucket_bytes"]
                         ["project_source_candidate"])
        self.assertEqual(case["buckets"]["typed_retained_or_external"],
                         final["metrics"]["whole_blob_bucket_bytes"]
                         ["typed_external_or_unsupported"])
        self.assertEqual(case["buckets"]["unclassified"], 0)
        self.assertTrue(case["details"]["software_image_link_complete"])
        self.assertTrue(case["details"]["software_even_package_complete"])
        self.assertFalse(case["details"]["physical_board_services_routed"])
        self.assertEqual(
            case["details"]["candidate_admission_blocker_class"],
            "hardware-dependent-board-routing",
        )
        self.assertEqual(
            case["details"]["candidate_admission_hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(
            case["details"]["candidate_admission_hardware_operations"], [],
        )
        self.assertEqual(case["details"]["source_image_translation_units"], 8)
        self.assertEqual(case["details"]["source_image_undefined_symbols"], 0)
        self.assertEqual(case["details"]["candidate_source_functions"], 222)
        self.assertEqual(
            case["details"]["remaining_callable_software_functions"], 0)
        self.assertEqual(case["details"]["physical_bucket_digest"],
                         final["metrics"]["physical_bucket_digest"])
        self.assertEqual(case["hardware_validation"],
                         "blocked by unavailable physical evidence")

    def test_pt_protocol_source_progress_is_reflected(self) -> None:
        main = self.report["components"]["apollo_main"]
        details = main["details"]
        self.assertTrue(details["pt_protocol_handler_surface_complete"])
        self.assertEqual(details["pt_protocol_candidate_stock_body_bytes"],
                         32866)
        self.assertEqual(details["pt_protocol_target_loadable_bytes"], 22643)
        self.assertEqual(details["pt_protocol_target_bss_bytes"], 0)
        self.assertEqual(
            details["pt_protocol_production_text_placement_free_bytes"], 72740)
        self.assertEqual(
            details["pt_protocol_production_text_placement_shortfall_bytes"],
            0,
        )
        self.assertEqual(
            details["pt_protocol_production_ram_binding_remaining_bytes"], 0)
        self.assertTrue(details["pt_protocol_production_placement_complete"])
        self.assertEqual(
            details["pt_protocol_retained_provider_candidate_bindings"], 40)
        self.assertEqual(
            details[
                "pt_protocol_retained_provider_candidate_stock_body_bytes"],
            3402,
        )
        self.assertEqual(
            details["pt_protocol_top_level_retained_provider_bindings_remaining"],
            4,
        )
        self.assertEqual(
            details["pt_protocol_retained_provider_bindings_remaining"], 13)
        self.assertFalse(details["pt_protocol_board_source_complete"])
        self.assertEqual(
            details["pt_protocol_second_order_callable_bindings"], 81)
        self.assertEqual(
            details["pt_protocol_second_order_source_overlay_callable_bindings"],
            29,
        )
        self.assertEqual(
            details["pt_protocol_second_order_source_local_callable_bindings"],
            39,
        )
        self.assertEqual(
            details["pt_protocol_second_order_source_callable_bindings"], 68)
        self.assertEqual(
            details["pt_protocol_second_order_retained_callable_bindings"], 13)
        self.assertEqual(
            details[
                "pt_protocol_second_order_retained_callable_unique_addresses"],
            13,
        )
        self.assertEqual(
            details["pt_protocol_second_order_data_bindings"], 97)
        self.assertEqual(
            details["pt_protocol_second_order_data_unique_addresses"], 94)
        self.assertEqual(
            details["pt_protocol_second_order_data_source_owned"], 0)
        self.assertEqual(
            details["pt_protocol_second_order_retained_data_bindings"], 97)
        self.assertEqual(
            details["pt_protocol_second_order_data_categories"],
            {
                "external_xip_bound": 2,
                "external_xip_data": 2,
                "immutable_flash_data": 33,
                "peripheral_mmio": 5,
                "retained_callback_entry": 2,
                "runtime_sram_data": 53,
            },
        )
        self.assertTrue(details[
            "pt_protocol_second_order_retained_boundaries_deliberately_supported"
        ])
        self.assertEqual(details["pt_protocol_stock_layout_data_bindings"], 53)
        self.assertEqual(
            details[
                "pt_protocol_stock_layout_data_immutable_flash_bindings"], 17)
        self.assertEqual(
            details["pt_protocol_stock_layout_data_runtime_sram_bindings"], 36)
        self.assertTrue(
            details["pt_protocol_stock_layout_data_deliberately_supported"])
        self.assertFalse(details["pt_protocol_stock_layout_data_software_gap"])
        self.assertEqual(details["pt_protocol_bound_commands"], 66)
        self.assertEqual(details["pt_protocol_target_undefined_symbols"], 0)
        self.assertTrue(details["pt_protocol_provider_adapters_complete"])
        self.assertTrue(details["pt_protocol_platform_backend_contract_complete"])
        self.assertTrue(details["pt_protocol_stock_abi_entry_complete"])
        self.assertTrue(details["pt_protocol_production_bootstrap_complete"])
        self.assertTrue(details["pt_protocol_platform_backend_production_bound"])
        self.assertTrue(details["pt_protocol_production_routed"])
        self.assertEqual(
            main["buckets"]["candidate_source_not_routed"], 0)

    def test_nemavg_stroke_cap_source_progress_is_reflected(self) -> None:
        main = self.report["components"]["apollo_main"]
        details = main["details"]
        self.assertEqual(details["nemavg_stroke_cap_candidate_functions"], 0)
        self.assertEqual(details["nemavg_stroke_cap_candidate_bytes"], 0)
        self.assertEqual(
            details["nemavg_stroke_cap_source_routed_functions"], 3)
        self.assertEqual(
            details["nemavg_stroke_cap_source_routed_stock_bytes"], 6614)
        self.assertEqual(
            details["nemavg_stroke_cap_retained_unpatched_functions"], 0)
        self.assertEqual(
            details["nemavg_stroke_cap_retained_unpatched_stock_bytes"], 0)
        self.assertTrue(details["nemavg_stroke_cap_production_routed"])
        self.assertFalse(
            details["nemavg_stroke_cap_endpoint_stock_entries_unpatched"])
        self.assertEqual(
            main["buckets"]["candidate_source_not_routed"], 0)

    def test_clock_manager_divider_source_progress_is_reflected(self) -> None:
        main = self.report["components"]["apollo_main"]
        boot = self.report["components"]["apollo_bootloader"]
        for component in (main, boot):
            details = component["details"]
            self.assertEqual(details["clkmgr_divider_source_functions"], 2)
            self.assertEqual(details["clkmgr_divider_source_stock_bytes"], 52)
            self.assertTrue(details["clkmgr_divider_production_routed"])
            self.assertNotIn("clkmgr_divider_candidate_bytes", details)
        self.assertEqual(
            boot["buckets"]["candidate_source_not_routed"], 0)

    def test_apollo_boundaries_are_disjoint_and_current(self) -> None:
        main = self.report["components"]["apollo_main"]
        details = main["details"]
        self.assertEqual(main["release_blocking_bytes"], 3_061_168)
        self.assertEqual(details["release_readiness_partition"], {
            "candidate_source_not_routed": 0,
            "typed_retained_or_external": 3_061_168,
        })
        self.assertEqual(details["unanchored_frontier_partition"], {
            "candidate_source_not_routed": 0,
            "typed_retained_unanchored_without_candidate": 596_170,
        })
        self.assertEqual(details["controlled_label_reconciliation_bytes"], 21_544)
        self.assertFalse(details["controlled_label_reconciliation_additive"])
        self.assertEqual(details["overlapping_object_closure_evidence"], {
            "bytes": 885_418,
            "additive_to_disjoint_release_totals": False,
        })

        boot = self.report["components"]["apollo_bootloader"]
        complement = boot["details"]["retained_complement"]
        self.assertEqual(complement["component_bytes"], 163_840)
        self.assertEqual(complement["intervals"], 901)
        self.assertEqual(complement["retained_official_bytes"], 87_985)
        self.assertEqual(
            complement["bytes_by_address_status"]["source_compiled"],
            59_009,
        )
        self.assertEqual(
            complement["retained_official_bytes"],
            boot["buckets"]["typed_retained_or_external"],
        )

    def test_external_component_detail_is_not_overclaimed(self) -> None:
        codec = self.report["components"]["codec"]
        detail = codec["details"]["external_provider_detail"]
        self.assertEqual(detail["bytes_by_class"], {
            "opaque_executable": 190_912,
            "opaque_runtime_data": 5_124,
            "opaque_npu_commands": 9_164,
            "proprietary_model_data": 120_800,
        })
        self.assertEqual(detail["bytes"], 326_000)
        self.assertFalse(detail["open_source_available"])
        self.assertFalse(codec["details"]
                         ["external_provider_claims_open_availability"])

        em = self.report["components"]["ble_em9305"]
        self.assertEqual(em["size"], 212_984)
        self.assertEqual(em["buckets"]["production_source"], 1_174)
        self.assertEqual(em["buckets"]["generated_or_reconstructible"], 1_226)
        self.assertEqual(em["buckets"]["candidate_source_not_routed"], 0)
        self.assertEqual(em["buckets"]["typed_retained_or_external"], 210_584)
        self.assertTrue(em["details"]["candidate_production_routed"])
        self.assertTrue(em["production_routed"])
        self.assertFalse(em["source_complete"])
        receipts = em["details"]["final_source_readiness_receipts"]
        self.assertEqual(receipts["manifest_count"], 2)
        self.assertEqual(receipts["residual_span_count"], 175)
        self.assertEqual(receipts["residual_bytes"], 33_658)
        self.assertEqual(receipts["hardware_operations"], [])
        self.assertEqual(em["details"]["hardware_operations"], [])
        self.assertEqual(
            receipts["ledger"]["sha256"],
            analyzer.EM9305_FINAL_LEDGER_SHA256,
        )
        self.assertEqual(
            receipts["summary"]["sha256"],
            analyzer.EM9305_FINAL_SUMMARY_SHA256,
        )

        touch = self.report["components"]["touch"]
        self.assertEqual(touch["details"]["typed_code_complement_bytes"], 15_854)
        self.assertEqual(touch["details"]["typed_noncode_partition"], {
            "vectors": 192,
            "strings": 1_640,
            "config_and_tables": 1_756,
        })

    def test_touch_source_image_link_gate_is_reflected(self) -> None:
        details = self.report["components"]["touch"]["details"]
        self.assertTrue(details["software_image_link_complete"])
        self.assertTrue(details["software_fwpk_package_complete"])
        self.assertFalse(details["physical_board_services_routed"])
        self.assertEqual(
            details["candidate_admission_blocker_class"],
            "hardware-dependent-resident-abi",
        )
        self.assertEqual(
            details["candidate_admission_hardware_validation"],
            "blocked by unavailable physical evidence",
        )
        self.assertEqual(details["candidate_admission_hardware_operations"], [])
        self.assertEqual(details["source_image_translation_units"], 31)
        self.assertEqual(details["source_image_undefined_symbols"], 0)
        self.assertEqual(details["candidate_source_functions"], 178)
        self.assertEqual(details["remaining_callable_software_functions"], 0)
        self.assertLessEqual(details["source_image_raw_flash_bytes"], 65536)


if __name__ == "__main__":
    unittest.main()
