# SPDX-License-Identifier: MIT
from __future__ import annotations

import unittest
from pathlib import Path

from tools import analyze_g2_pt_protocol_source as analyzer


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = analyzer.analyze()

    def test_full_command_binding(self):
        self.assertEqual(self.r["software"]["bound_commands"], 66)
        self.assertTrue(self.r["software"]["handler_surface_complete"])
        self.assertEqual(self.r["software"]["missing_commands"], 0)

    def test_target_link(self):
        self.assertEqual(self.r["software"]["target_undefined_symbols"], 0)
        self.assertEqual(self.r["software"]["apollo510_undefined_symbols"], 0)
        self.assertEqual(self.r["software"]["cortex_m0plus_undefined_symbols"], 0)
        self.assertEqual(self.r["software"]["translation_units"], 14)
        self.assertEqual(self.r["software"]["target_text_bytes"], 19126)
        self.assertEqual(self.r["software"]["target_rodata_bytes"], 1177)
        self.assertEqual(self.r["software"]["target_data_bytes"], 0)
        self.assertEqual(self.r["software"]["target_bss_bytes"], 0)
        self.assertEqual(self.r["software"]["target_loadable_bytes"], 20303)
        self.assertEqual(
            self.r["software"]["production_text_placement_free_bytes"], 4314)
        self.assertEqual(
            self.r["software"]["production_text_placement_shortfall_bytes"],
            15989,
        )
        self.assertEqual(
            self.r["software"]["production_ram_binding_remaining_bytes"], 0)
        self.assertEqual(
            self.r["software"]["production_in_place_loadable_bytes"], 20348)
        self.assertTrue(self.r["software"]["production_placement_complete"])

    def test_ownership_and_stock_accounting(self):
        self.assertEqual(self.r["ownership"]["license"], "MIT")
        self.assertEqual(self.r["ownership"]["source_files"], 28)
        self.assertEqual(self.r["ownership"]["stock_machine_code_bytes_in_source"], 0)
        self.assertEqual(
            self.r["ownership"]["retained_vendor_data_bytes_embedded_in_source"],
            0,
        )
        self.assertEqual(self.r["evidence"]["stock_function_body_bytes"], 32866)
        self.assertTrue(self.r["evidence"]["corpus_ledger_verified"])

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
        self.assertEqual(software["board_source_routed_service_bindings"], 43)
        self.assertEqual(software["board_retained_service_bindings"], 40)
        self.assertEqual(
            software["board_retained_provider_candidate_bindings"], 40)
        self.assertEqual(
            software["board_top_level_retained_provider_bindings_remaining"], 0)
        self.assertEqual(
            software["board_retained_provider_bindings_remaining"], 23)
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
        self.assertTrue(software["board_second_order_abis_verified"])
        self.assertEqual(software["board_second_order_callable_bindings"], 60)
        callable_census = software["board_second_order_callable_census"]
        self.assertEqual(len(callable_census), 60)
        self.assertEqual(
            sum(item["category"] == "source_overlay_callable"
                for item in callable_census),
            21,
        )
        self.assertEqual(
            sum(item["category"] == "source_local_callable"
                for item in callable_census),
            16,
        )
        self.assertEqual(
            sum(item["category"] == "retained_callable"
                for item in callable_census),
            23,
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
            21,
        )
        self.assertEqual(
            software[
                "board_second_order_source_overlay_callable_unique_addresses"
            ],
            21,
        )
        self.assertEqual(
            software["board_second_order_source_local_callable_bindings"], 16)
        self.assertEqual(
            software["board_second_order_source_callable_bindings"], 37)
        self.assertEqual(
            software["board_second_order_retained_callable_bindings"], 23)
        self.assertEqual(
            software["board_second_order_retained_callable_unique_addresses"],
            21,
        )
        self.assertEqual(software["board_second_order_data_bindings"], 46)
        data_census = software["board_second_order_data_census"]
        self.assertEqual(len(data_census), 46)
        self.assertEqual(
            len({item["runtime_address"] for item in data_census}), 44)
        self.assertTrue(all(
            item["ownership"] == "supported_retained_external_abi"
            for item in data_census
        ))
        self.assertEqual(
            software["board_second_order_data_unique_addresses"], 44)
        self.assertEqual(software["board_second_order_data_source_owned"], 0)
        self.assertEqual(
            software["board_second_order_retained_data_bindings"], 46)
        self.assertEqual(
            software["board_second_order_data_categories"],
            {
                "external_xip_bound": 2,
                "external_xip_data": 2,
                "immutable_flash_data": 2,
                "peripheral_mmio": 3,
                "retained_callback_entry": 2,
                "runtime_sram_data": 35,
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
            self.assertTrue(analyzer.analyze()["software"]["production_routed"])
        finally:
            if hidden.exists():
                hidden.rename(report)


if __name__ == "__main__":
    unittest.main()
