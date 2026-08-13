#!/usr/bin/env python3
"""Guard the fail-closed EM9305 QP/C provenance audit."""

from __future__ import annotations

import importlib.util
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_em9305_qpc.py"
SDK_ORACLE_CHECKOUT = Path("/var/tmp/opencfw-em9305-sdk-oracle")


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_em9305_qpc", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Em9305QpcAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_controller_identity_and_record_are_pinned(self) -> None:
        identity = self.report["identity"]
        self.assertEqual(identity["architecture"], "Synopsys ARC EM7D / ARCompact")
        self.assertEqual(identity["application_size"], 210_888)
        self.assertEqual(len(self.report["modules"]), 8)

    def test_qk_discriminator_bounds_the_checked_release_interval(self) -> None:
        upstream = self.report["upstream"]
        self.assertEqual(upstream["portable_ancestry_floor_tag"], "v6.3.6")
        self.assertEqual(upstream["selected_release_tag"], "v6.5.1")
        self.assertEqual(
            upstream["selected_release_commit"],
            "416dcec8820b9cdb5827497e645d0d9375db53c6",
        )
        self.assertTrue(upstream["release_identification_proven"])
        self.assertEqual(upstream["compatible_ceiling_tag"], "v6.6.0+")
        self.assertEqual(upstream["first_excluded_tag"], "v6.7.0")
        self.assertFalse(upstream["exact_vendor_checkout_proven"])
        self.assertFalse(upstream["pre_v6_possible"])
        self.assertTrue(upstream["vendor_backport_or_cherry_pick_possible"])
        self.assertEqual(upstream["checked_tag_count"], 16)
        self.assertEqual(upstream["portable_source_epoch_count"], 10)
        self.assertEqual(upstream["stock_compatible_tag_count"], 7)
        self.assertEqual(upstream["stock_compatible_source_epoch_count"], 6)
        self.assertIsNone(upstream["source_epoch_audit"])
        self.assertIsNone(upstream["em9305_sdk_source_oracle"]["audit"])

    def test_assertion_cluster_and_retention_state_are_explicit(self) -> None:
        assertions = self.report["assertions"]
        self.assertEqual(assertions["handler"], 0x0031_17D8)
        self.assertEqual(len(assertions["direct_calls"]), 31)
        self.assertEqual(len(assertions["module_references"]), 22)
        self.assertEqual(assertions["portable_call_count"], 29)
        self.assertTrue(assertions["all_calls_assigned_to_module"])
        self.assertEqual(
            {call["module"] for call in assertions["direct_calls"]},
            {"MyApp", "WsfOs", "qk", "qf_dyn", "qf_act", "qep_hsm", "qf_actq", "qf_mem"},
        )
        self.assertEqual(assertions["qk_assertion_id"], 500)
        self.assertEqual(assertions["qk_macro_callsite_id"], 189)
        self.assertTrue(all(region["state"].endswith("stock_retained") for region in self.report["regions"]))
        self.assertEqual(self.report["recovery"]["production_source_replacement_percent"], 0)

    def test_raw_arc_scan_is_the_exhaustive_topology_authority(self) -> None:
        blob = self.analyzer.DEFAULT_IMAGE.read_bytes()
        observed = self.analyzer.scan_arc_bl_calls(blob, self.analyzer.ASSERT_HANDLER)
        expected = tuple(call[0] for call in self.analyzer.ASSERT_CALLS)
        self.assertEqual(observed, expected)

    def test_portable_assertion_constellation_matches_linked_modules(self) -> None:
        constellation = self.report["assertions"]["portable_constellation"]
        self.assertEqual(tuple(constellation["qf_actq"]["linked"]), (100, 110, 210, 310))
        self.assertEqual(tuple(constellation["qep_hsm"]["linked"]), (200, 210, 220, 400, 410, 510, 520))
        self.assertEqual(tuple(constellation["qk"]["linked"]), (300, 410, 500, 510))

    def test_recovered_qp_configuration_widths_are_explicit(self) -> None:
        config = self.report["configuration"]["recovered"]
        self.assertEqual(config["QF_MAX_ACTIVE"]["value"], 16)
        self.assertEqual(config["QF_MAX_TICK_RATE"]["value"], 0)
        self.assertEqual(config["QF_MAX_EPOOL"]["value"], 2)
        self.assertEqual(config["Q_SIGNAL_SIZE"]["value"], 2)
        self.assertEqual(config["QF_EQUEUE_CTR_SIZE"]["value"], 1)
        self.assertEqual(config["QF_MPOOL_SIZ_SIZE"]["value"], 2)
        self.assertEqual(config["QF_MPOOL_CTR_SIZE"]["value"], 2)
        self.assertEqual(config["QK_READY_SET_BITS"]["value"], 16)
        self.assertEqual(config["QACTIVE_SIZE"]["value"], 36)
        self.assertEqual(config["QK_ATTR_SIZE"]["value"], 8)
        self.assertTrue(all(item["confidence"] == "high" for item in config.values()))
        port = self.report["configuration"]["port_and_build"]
        self.assertFalse(port["Q_SPY"]["value"])
        self.assertIn("32-bit", port["QF_CRIT_STAT_TYPE"]["value"])
        self.assertEqual(port["QF_onStartup"]["value"], 0x0031_1154)
        self.assertEqual(port["QK_onIdle"]["value"], 0x0031_15E4)
        self.assertIn("ILINK sentinel", port["QK_onIdle_interrupt_race_guard"]["value"])
        self.assertIn("T-2022.09", port["ARC_toolchain"]["value"])
        self.assertIn("IRQHandler_SWI0", port["QK_port"]["value"])
        self.assertTrue(all(item["confidence"] == "high" for item in port.values()))

    def test_qk_idle_power_manager_boundary_and_call_are_pinned(self) -> None:
        power = self.report["power_management"]
        self.assertEqual(power["qk_on_idle"], 0x0031_15E4)
        self.assertEqual(power["sleep_manager"], 0x0031_26E0)
        self.assertEqual(power["sleep_manager_size"], 516)
        self.assertEqual(tuple(power["sleep_instructions"]), (0x0031_280E, 0x0031_2816))
        self.assertEqual(tuple(power["direct_callers"]), (0x0031_1610,))
        region = next(item for item in self.report["regions"] if item["name"] == "sleep_manager_go_to_sleep")
        self.assertEqual(region["size"], 516)
        self.assertEqual(region["state"], "sdk_symbol_identified_vendor_configured_stock_retained")
        self.assertEqual(power["sleep_manager_name"], "SLEEP_MANAGER_GoToSleep")
        self.assertEqual(power["rccal_callback"], 0x0031_28E4)
        self.assertEqual(power["rccal_callback_size"], 52)

    def test_qactive_post_stock_body_pins_the_portable_lineage_floor(self) -> None:
        region = next(
            item for item in self.report["regions"]
            if item["name"] == "qactive_post_candidate"
        )
        self.assertEqual(region["start"], 0x0031_0E28)
        self.assertEqual(region["size"], 188)
        self.assertEqual(self.report["upstream"]["last_earlier_incompatible_tag"], "v6.3.4")

    def test_unlinked_upstream_time_event_settings_are_not_invented(self) -> None:
        config = self.report["configuration"]
        not_observable = config["not_observable_from_linked_portable_corpus"]
        self.assertIn("QF_TIMEEVT_CTR_SIZE_and_layout", not_observable)
        self.assertNotIn("QF_MAX_TICK_RATE", config["unresolved"])
        self.assertNotIn(b"qf_time\0", self.analyzer.DEFAULT_IMAGE.read_bytes())

    def test_portable_function_boundaries_are_hash_pinned(self) -> None:
        functions = self.report["portable_functions"]
        self.assertEqual(len(functions), 22)
        self.assertEqual(sum(item["size"] for item in functions), 2_450)
        self.assertEqual(
            {item["module"] for item in functions},
            {"qf_qact", "qf_qeq", "qf_actq", "qf_act", "qf_dyn", "qep_hsm", "qk", "qf_mem"},
        )
        self.assertEqual(self.report["recovery"]["portable_function_bytes"], 2_450)

    def test_portable_and_remainder_ranges_exactly_partition_the_cluster(self) -> None:
        remainder = self.report["cluster_remainder_segments"]
        self.assertEqual(len(remainder), 26)
        self.assertEqual(sum(item["size"] for item in remainder), 602)
        self.assertEqual(self.report["recovery"]["cluster_remainder_bytes"], 602)
        self.assertTrue(self.report["recovery"]["cluster_partition_complete"])
        ranges = sorted(
            [(item["start"], item["end"]) for item in self.report["portable_functions"]]
            + [(item["start"], item["end"]) for item in remainder]
        )
        self.assertEqual(ranges[0][0], self.analyzer.QPC_CLUSTER[0])
        self.assertEqual(ranges[-1][1], self.analyzer.QPC_CLUSTER[1])
        self.assertTrue(all(left[1] == right[0] for left, right in zip(ranges, ranges[1:])))
        self.assertEqual(
            next(item for item in remainder if item["name"] == "q_on_assert")["state"],
            "source_oracle_identified_fully_reverse_engineered_stock_retained",
        )
        self.assertEqual(
            {item["name"] for item in remainder if "alignment" not in item["name"]},
            {
                "prot_timer_set_hw_trigger_enable_tail",
                "prot_timer_store_config",
                "prot_timer_update_restart_time",
                "qf_on_resume",
                "qf_on_resume_ext",
                "qf_on_resume_internal_hook",
                "qf_on_startup",
                "qf_on_startup_ext",
                "qf_on_startup_internal_hook",
                "qf_resume",
                "qk_on_idle",
                "qk_on_idle_ext",
                "qk_on_idle_internal_hook",
                "q_on_assert",
                "q_on_assert_ext_prefix",
            },
        )

    def test_sdk_archive_comparison_closes_qk_port_and_protocol_timer(self) -> None:
        archive = self.report["upstream"]["em9305_sdk_archive_comparison"]
        self.assertEqual(archive["archive_count"], 6)
        self.assertEqual(archive["confirmed_exact_function_count"], 98)
        self.assertEqual(archive["confirmed_exact_function_bytes"], 7_172)
        self.assertEqual(archive["unique_exact_function_count"], 92)
        self.assertEqual(archive["unique_exact_function_bytes"], 7_146)
        self.assertEqual(archive["qpc_known_address_matches"], 36)
        self.assertEqual(archive["qpc_known_address_candidates"], 39)
        functions = {item["name"]: item for item in self.report["sdk_identified_functions"]}
        self.assertEqual(functions["IRQHandler_SWI0"]["start"], 0x0030_251C)
        self.assertEqual(functions["BSP_Init"]["start"], 0x0030_2E80)
        self.assertEqual(functions["ProtTimer_StoreConfig"]["start"], 0x0031_0C08)
        self.assertEqual(functions["SLEEP_MANAGER_RCCAL_Callback"]["start"], 0x0031_28E4)
        self.assertEqual(self.report["recovery"]["anonymous_executable_cluster_bytes"], 0)
        self.assertEqual(self.report["recovery"]["bounded_cluster_identification_percent"], 100)

    def test_hook_pointer_table_and_callback_globals_are_hash_pinned(self) -> None:
        hooks = self.report["hooks"]
        self.assertEqual(hooks["pointer_table"]["start"], 0x0033_5B94)
        self.assertEqual(len(hooks["pointer_table"]["entries"]), 9)
        self.assertEqual(
            hooks["callback_globals"]["gQ_onAssertExt"],
            0x0080_FE1C,
        )
        region = next(item for item in self.report["regions"] if item["name"] == "q_on_assert_ext")
        self.assertEqual(region["size"], 16)

    @unittest.skipUnless(SDK_ORACLE_CHECKOUT.is_dir(), "pinned EM9305 SDK oracle checkout unavailable")
    def test_pinned_em9305_sdk_source_oracle(self) -> None:
        audit = self.analyzer.run_em9305_sdk_oracle_audit(SDK_ORACLE_CHECKOUT)
        self.assertEqual(audit["qp_version"], "6.5.1")
        self.assertEqual(audit["commit"], "e4412bc98d4e76d441d1226ca3696e53cfae5f54")
        self.assertFalse(audit["authoritative_vendor_checkout"])
        self.assertEqual(len(audit["files"]), 10)
        self.assertEqual(
            audit["files"]["libs/third_party/QPC/lib_QPC.a"]["kind"],
            "binary_archive",
        )

    @unittest.skipUnless(shutil.which("rizin"), "Rizin is not installed")
    def test_rizin_reproduces_exact_calls_and_qk_fingerprint(self) -> None:
        report = self.analyzer.analyze(with_rizin=True)
        self.assertEqual(report["rizin"]["exact_address_call_count"], 31)
        self.assertFalse(report["rizin"]["global_xrefs_authoritative"])
        self.assertEqual(len(report["rizin"]["qk_discriminator"]), 6)


if __name__ == "__main__":
    unittest.main()
