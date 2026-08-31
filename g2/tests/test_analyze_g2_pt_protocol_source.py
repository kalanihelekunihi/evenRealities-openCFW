# SPDX-License-Identifier: MIT
from __future__ import annotations

import unittest
from pathlib import Path

from tools import analyze_g2_pt_protocol_source as analyzer


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = analyzer.analyze(enforce_canonical_pin=False)

    def test_full_command_binding(self):
        self.assertEqual(self.r["software"]["bound_commands"], 66)
        self.assertTrue(self.r["software"]["handler_surface_complete"])
        self.assertEqual(self.r["software"]["missing_commands"], 0)

    def test_target_link(self):
        self.assertEqual(self.r["software"]["target_undefined_symbols"], 0)
        self.assertEqual(self.r["software"]["apollo510_undefined_symbols"], 0)
        self.assertEqual(self.r["software"]["cortex_m0plus_undefined_symbols"], 0)
        self.assertEqual(self.r["software"]["translation_units"], 15)
        self.assertEqual(self.r["software"]["target_text_bytes"], 21466)
        self.assertEqual(self.r["software"]["target_rodata_bytes"], 1177)
        self.assertEqual(self.r["software"]["target_data_bytes"], 0)
        self.assertEqual(self.r["software"]["target_bss_bytes"], 0)
        self.assertEqual(self.r["software"]["target_loadable_bytes"], 22643)
        self.assertEqual(
            self.r["software"]["production_text_placement_free_bytes"], 72740)
        self.assertEqual(
            self.r["software"]["production_text_placement_shortfall_bytes"],
            0,
        )
        self.assertEqual(
            self.r["software"]["production_ram_binding_remaining_bytes"], 0)
        self.assertEqual(
            self.r["software"]["production_in_place_loadable_bytes"], 22696)
        self.assertTrue(self.r["software"]["production_placement_complete"])

    def test_ownership_and_stock_accounting(self):
        self.assertEqual(self.r["ownership"]["license"], "mixed")
        self.assertEqual(
            self.r["ownership"]["licenses"],
            {
                "MIT": "OpenCFW PT protocol and G2 wiring",
                "Apache-2.0": "Google/liblc3 encoder-setup adaptation",
            },
        )
        self.assertEqual(self.r["ownership"]["source_files"], 29)
        self.assertEqual(self.r["ownership"]["stock_machine_code_bytes_in_source"], 0)
        self.assertEqual(
            self.r["ownership"]["retained_vendor_data_bytes_embedded_in_source"],
            0,
        )
        self.assertEqual(self.r["evidence"]["stock_function_body_bytes"], 32866)
        self.assertTrue(self.r["evidence"]["corpus_ledger_verified"])

    def test_lc3_license_and_provenance_boundary_fails_closed(self):
        component = (
            Path(__file__).resolve().parents[1]
            / "components/apollo_main/core_overlay"
        )
        apache = (component / "pt_protocol_lc3_setup.c").read_text()
        mit_leaf = (
            component / "pt_protocol_board_leaf_candidates.c"
        ).read_text()
        analyzer.validate_lc3_license_boundary(apache, mit_leaf)
        mutations = (
            apache.replace("Apache-2.0", "MIT", 1),
            apache.replace("Copyright 2022 Google LLC", "", 1),
            apache.replace("third_party/liblc3/src/lc3.c", "", 1),
            apache.replace("third_party/liblc3/LICENSE", "", 1),
        )
        for mutated in mutations:
            with self.subTest(marker=mutated[:80]):
                with self.assertRaisesRegex(
                    RuntimeError, "license/provenance boundary changed"
                ):
                    analyzer.validate_lc3_license_boundary(mutated, mit_leaf)
        contaminated_leaf = (
            mit_leaf
            + "\nvoid *open_cfw_pt_lc3_setup_encoder(int a, int b, int c, "
            "void *d) { return d; }\n"
        )
        with self.assertRaisesRegex(
            RuntimeError, "license/provenance boundary changed"
        ):
            analyzer.validate_lc3_license_boundary(apache, contaminated_leaf)

    def test_software_integration_gate_is_routed(self):
        software = self.r["software"]
        self.assertEqual(software["provider_operation_count"], 56)
        self.assertEqual(software["provider_callback_count"], 58)
        self.assertTrue(software["provider_adapters_complete"])
        self.assertTrue(software["platform_backend_contract_complete"])
        self.assertTrue(software["stock_abi_entry_complete"])
        self.assertTrue(software["production_bootstrap_complete"])
        self.assertTrue(software["production_bootstrap_reachable"])
        self.assertTrue(software["board_calls_table_lifetime_contract"])
        self.assertEqual(software["board_operations_implemented"], 56)
        self.assertEqual(software["board_operations_remaining"], 0)
        self.assertEqual(software["board_host_operations_exercised"], 56)
        self.assertTrue(software["board_failure_semantics_exercised"])
        self.assertEqual(software["board_callback_count"], 83)
        self.assertEqual(software["board_service_bindings"], 83)
        self.assertTrue(software["board_function_binding_associations_verified"])
        self.assertTrue(software["board_function_abis_verified"])
        self.assertEqual(software["board_source_routed_service_bindings"], 39)
        self.assertEqual(software["board_retained_service_bindings"], 44)
        self.assertEqual(
            software["board_retained_provider_candidate_bindings"], 40)
        self.assertEqual(
            software["board_top_level_retained_provider_bindings_remaining"], 4)
        self.assertEqual(
            software["board_retained_provider_bindings_remaining"], 13)
        self.assertEqual(
            software["board_retained_provider_candidate_stock_body_bytes"],
            3402,
        )
        self.assertTrue(
            software["board_retained_provider_candidates_semantic_c"])
        self.assertTrue(
            software["board_retained_provider_candidates_production_routed"])
        self.assertFalse(software["board_retained_providers_source_owned"])
        self.assertFalse(software["board_source_complete"])
        self.assertFalse(software["board_second_order_abis_verified"])
        self.assertTrue(
            software["board_second_order_binding_inventory_verified"])
        self.assertEqual(software["board_second_order_callable_bindings"], 81)
        callable_census = software["board_second_order_callable_census"]
        self.assertEqual(len(callable_census), 81)
        self.assertEqual(
            sum(item["category"] == "source_overlay_callable"
                for item in callable_census),
            29,
        )
        self.assertEqual(
            sum(item["category"] == "source_local_callable"
                for item in callable_census),
            39,
        )
        self.assertEqual(
            sum(item["category"] == "retained_callable"
                for item in callable_census),
            13,
        )
        self.assertTrue(all(
            item["runtime_address"] == (item["thumb_pointer"] & ~1)
            for item in callable_census
            if item["category"] != "source_local_callable"
        ))
        self.assertTrue(all(
            (item["ownership"] == "source_owned") ==
            (item["target_function"] is not None)
            for item in callable_census
        ))
        self.assertEqual(
            software["board_second_order_callable_unique_addresses"], 42)
        self.assertEqual(
            software["board_second_order_source_overlay_callable_bindings"],
            29,
        )
        self.assertEqual(
            software[
                "board_second_order_source_overlay_callable_unique_addresses"
            ],
            29,
        )
        self.assertEqual(
            software["board_second_order_source_local_callable_bindings"], 39)
        self.assertEqual(
            software["board_second_order_source_callable_bindings"], 68)
        self.assertEqual(
            software["board_second_order_retained_callable_bindings"], 13)
        self.assertEqual(
            software["board_second_order_retained_callable_unique_addresses"],
            13,
        )
        trace = next(item for item in callable_census
                     if item["macro"] == "OPEN_CFW_PT_AUDIO_TRACE_LOG")
        self.assertEqual(trace["category"], "retained_callable")
        self.assertEqual(trace["runtime_address"], 0x0043CE9E)
        self.assertEqual(trace["abi"],
                         "void (*)(uint32_t, const char *, ...)")
        lens_transport = next(
            item for item in callable_census
            if item["macro"] == "OPEN_CFW_PT_LENS_SYNC_TRANSPORT")
        self.assertEqual(lens_transport["category"], "retained_callable")
        self.assertEqual(lens_transport["runtime_address"], 0x00464772)
        self.assertEqual(lens_transport["thumb_pointer"], 0x00464773)
        self.assertEqual(
            lens_transport["abi"],
            "int32_t (*)(uint16_t, const void *, uint32_t, uint32_t, "
            "uint8_t, uint8_t, uint32_t)",
        )
        lens_evidence = software[
            "board_postprocess_lens_sync_transport_evidence"]
        self.assertTrue(
            software[
                "board_postprocess_lens_sync_transport_abi_and_address_authenticated"
            ]
        )
        self.assertTrue(lens_evidence["authenticated"])
        self.assertEqual(lens_evidence["stock_wrapper_runtime_address"],
                         0x00464C36)
        self.assertEqual(lens_evidence["stock_transport_runtime_address"],
                         0x00464772)
        self.assertEqual(lens_evidence["stock_wrapper_transport_callsite"],
                         0x00464CB2)
        self.assertEqual(lens_evidence["stock_trailing_arguments"], [5, 2, 0])
        self.assertEqual(
            lens_evidence["stock_wrapper_signature"],
            "void FUN_00464c36(undefined2 param_1,undefined4 param_2,"
            "undefined2 param_3,undefined4 param_4);",
        )
        self.assertEqual(
            lens_evidence["stock_transport_signature"],
            "undefined4 FUN_00464772(undefined2 param_1,int param_2,uint "
            "param_3,undefined4 param_4,undefined1 param_5,byte param_6,"
            "undefined4 param_7);",
        )
        self.assertEqual(
            lens_evidence["stock_wrapper_call_expression"],
            "FUN_00464772(param_1,param_2,param_3,param_4,5,2,0);",
        )
        self.assertRegex(
            lens_evidence["authenticated_decomp_index_sha256"],
            r"^[0-9a-f]{64}$",
        )
        uart_evidence = software["board_uart_cache_maintenance_evidence"]
        self.assertTrue(
            software["board_uart_cache_maintenance_target_verified"])
        self.assertEqual(len(uart_evidence["dsb_runtime_addresses"]), 2)
        self.assertEqual(len(uart_evidence["isb_runtime_addresses"]), 1)
        self.assertEqual(uart_evidence["dmb_runtime_addresses"], [])
        self.assertTrue(uart_evidence["target_bytes_verified"])
        lc3_setup = next(
            item for item in callable_census
            if item["macro"] == "OPEN_CFW_PT_LC3_SETUP_ENCODER")
        self.assertEqual(lc3_setup["category"], "source_local_callable")
        self.assertIsNone(lc3_setup["runtime_address"])
        self.assertEqual(
            lc3_setup["target_function"],
            "open_cfw_pt_lc3_setup_encoder_bounded",
        )
        self.assertTrue(software["board_lc3_setup_boundary_authenticated"])
        self.assertEqual(software["board_lc3_setup_license"], "Apache-2.0")
        self.assertTrue(software["board_lc3_setup_source_routed"])
        self.assertTrue(software["board_lc3_setup_fail_closed"])
        self.assertEqual(
            software["board_lc3_setup_pending_software_gates"],
            [],
        )
        lc3_evidence = self.r["evidence"]["lc3_setup_boundary"]
        self.assertEqual(lc3_evidence["upstream"], "Google/liblc3")
        self.assertEqual(lc3_evidence["upstream_license"], "Apache-2.0")
        self.assertEqual(
            lc3_evidence["upstream_source"],
            "third_party/liblc3/src/lc3.c",
        )
        self.assertEqual(
            lc3_evidence["upstream_commit"],
            "96a3af0beb5487aca3b98a4b992a539a1f6d80d1",
        )
        self.assertEqual(
            lc3_evidence["upstream_license_path"],
            "third_party/liblc3/LICENSE",
        )
        self.assertEqual(
            lc3_evidence["abi"], "void *(*)(int, int, int, void *)"
        )
        self.assertEqual(lc3_evidence["stock_primary_runtime_address"],
                         0x0059123A)
        self.assertEqual(lc3_evidence["stock_primary_size"], 314)
        self.assertEqual(
            lc3_evidence["stock_primary_sha256"],
            "04f7f722ef30afdfae612d0f6622cb4811918c8a8f4dc30b1ee99f95f42572c8",
        )
        self.assertEqual(lc3_evidence["fixed_context_slot_bytes"], 0xA44)
        self.assertEqual(
            lc3_evidence["fixed_context_starts"],
            [0x20106A7C, 0x201074C0, 0x20107F04, 0x20108948],
        )
        self.assertEqual(lc3_evidence["next_allocation_start"], 0x2010938C)
        self.assertEqual(lc3_evidence["fixed_context_header_bytes"], 0x1C)
        self.assertEqual(lc3_evidence["fixed_context_storage_bytes"], 2600)
        self.assertEqual(
            lc3_evidence["configuration_safety"],
            "computed size must fit authenticated 2600-byte storage",
        )
        self.assertFalse(software["canonical_pin_enforced"])
        self.assertIsInstance(software["canonical_apple_profile_matches"], bool)
        self.assertEqual(software["board_second_order_data_bindings"], 97)
        data_census = software["board_second_order_data_census"]
        self.assertEqual(len(data_census), 97)
        self.assertEqual(
            len({item["runtime_address"] for item in data_census}), 94)
        self.assertTrue(all(
            item["ownership"] == "supported_retained_external_abi"
            for item in data_census
        ))
        self.assertEqual(
            software["board_second_order_data_unique_addresses"], 94)
        self.assertEqual(software["board_second_order_data_source_owned"], 0)
        self.assertEqual(
            software["board_second_order_retained_data_bindings"], 97)
        self.assertEqual(
            software["board_second_order_data_categories"],
            {
                "external_xip_bound": 2,
                "external_xip_data": 2,
                "immutable_flash_data": 33,
                "peripheral_mmio": 5,
                "retained_callback_entry": 2,
                "runtime_sram_data": 53,
            },
        )
        self.assertTrue(
            software[
                "board_second_order_retained_boundaries_deliberately_supported"
            ]
        )
        self.assertEqual(software["board_stock_layout_data_bindings"], 53)
        self.assertTrue(software["board_data_binding_associations_verified"])
        self.assertTrue(software["board_data_abis_and_extents_verified"])
        self.assertEqual(
            software["board_stock_layout_data_immutable_flash_bindings"], 17)
        self.assertEqual(
            software["board_stock_layout_data_runtime_sram_bindings"], 36)
        self.assertTrue(
            software["board_stock_layout_data_deliberately_supported"])
        self.assertFalse(software["board_stock_layout_data_software_gap"])
        self.assertFalse(software["board_stock_layout_data_source_owned"])
        self.assertTrue(software["board_apollo_binding_available"])
        self.assertTrue(software["platform_backend_production_bound"])
        self.assertTrue(software["production_routed"])
        self.assertEqual(len(software["production_ingress_sites"]), 3)
        for ingress in software["production_ingress_sites"]:
            self.assertNotIn("expected_hex", ingress)
            self.assertEqual(ingress["authenticated_size"], 4)
            self.assertRegex(ingress["authenticated_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(
            self.r["hardware"]["validation"],
            "blocked by unavailable physical evidence",
        )

    def test_analysis_is_independent_of_transient_core_build_report(self):
        report = (Path(__file__).resolve().parents[1] /
                  "components/apollo_main/core_overlay/build/build-report.json")
        hidden = report.with_suffix(".json.source-gate-hidden")
        if report.exists():
            report.rename(hidden)
        try:
            self.assertTrue(analyzer.analyze(
                enforce_canonical_pin=False)["software"]["production_routed"])
        finally:
            if hidden.exists():
                hidden.rename(report)


if __name__ == "__main__":
    unittest.main()
