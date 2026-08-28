from __future__ import annotations

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
            policy["distributed_project_mit_normalization_targets"], 884)
        self.assertEqual(
            policy["community_controller_and_adapter_source_files"], 107)
        self.assertEqual(
            policy["community_project_mit_compatible_source_files"], 104)
        self.assertEqual(
            policy["community_touch_apache_source_files_preserved"], 3)
        self.assertEqual(policy["touch_source_image_project_mit_files"], 9)
        self.assertEqual(policy["touch_source_image_package_files"], 6)
        self.assertEqual(policy["touch_source_image_support_files"], 3)
        self.assertEqual(policy["case_source_image_project_mit_files"], 7)
        self.assertEqual(policy["case_source_image_package_files"], 5)
        self.assertEqual(policy["case_source_image_support_files"], 2)
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
        self.assertEqual(case["details"]["source_image_translation_units"], 8)
        self.assertEqual(case["details"]["source_image_undefined_symbols"], 0)
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
        self.assertEqual(details["pt_protocol_target_loadable_bytes"], 20303)
        self.assertEqual(details["pt_protocol_target_bss_bytes"], 0)
        self.assertEqual(
            details["pt_protocol_production_text_placement_free_bytes"], 4314)
        self.assertEqual(
            details["pt_protocol_production_text_placement_shortfall_bytes"],
            15989,
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
            0,
        )
        self.assertEqual(
            details["pt_protocol_retained_provider_bindings_remaining"], 23)
        self.assertFalse(details["pt_protocol_board_source_complete"])
        self.assertEqual(
            details["pt_protocol_second_order_callable_bindings"], 60)
        self.assertEqual(
            details["pt_protocol_second_order_source_overlay_callable_bindings"],
            21,
        )
        self.assertEqual(
            details["pt_protocol_second_order_source_local_callable_bindings"],
            16,
        )
        self.assertEqual(
            details["pt_protocol_second_order_retained_callable_bindings"], 23)
        self.assertEqual(
            details["pt_protocol_second_order_data_bindings"], 46)
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
            main["buckets"]["candidate_source_not_routed"], 6614)

    def test_nemavg_stroke_cap_source_progress_is_reflected(self) -> None:
        main = self.report["components"]["apollo_main"]
        details = main["details"]
        self.assertEqual(details["nemavg_stroke_cap_candidate_functions"], 3)
        self.assertEqual(details["nemavg_stroke_cap_candidate_bytes"], 6614)
        self.assertFalse(details["nemavg_stroke_cap_production_routed"])
        self.assertGreaterEqual(
            main["buckets"]["candidate_source_not_routed"], 6614)

    def test_clock_manager_divider_source_progress_is_reflected(self) -> None:
        main = self.report["components"]["apollo_main"]
        boot = self.report["components"]["apollo_bootloader"]
        for component in (main, boot):
            details = component["details"]
            self.assertEqual(details["clkmgr_divider_candidate_functions"], 2)
            self.assertEqual(details["clkmgr_divider_candidate_bytes"], 52)
            self.assertTrue(details["clkmgr_divider_production_routed"])
        self.assertEqual(
            boot["buckets"]["candidate_source_not_routed"], 0)

    def test_touch_source_image_link_gate_is_reflected(self) -> None:
        details = self.report["components"]["touch"]["details"]
        self.assertTrue(details["software_image_link_complete"])
        self.assertTrue(details["software_fwpk_package_complete"])
        self.assertEqual(details["source_image_translation_units"], 31)
        self.assertEqual(details["source_image_undefined_symbols"], 0)
        self.assertLessEqual(details["source_image_raw_flash_bytes"], 65536)


if __name__ == "__main__":
    unittest.main()
