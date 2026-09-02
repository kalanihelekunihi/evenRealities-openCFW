#!/usr/bin/env python3

from __future__ import annotations

import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_bootloader_post_mspi_frontier.py"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_interrupt_power_426536.S"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("post_mspi_frontier", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load post-MSPI analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PostMspiFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.result = cls.module.audit()

    def test_exhaustive_partition_has_no_unclassified_bytes(self) -> None:
        classification = self.result["classification"]
        self.assertTrue(classification["exhaustive"])
        self.assertEqual(classification["row_count"], 272)
        self.assertEqual(classification["unclassified_bytes"], 0)
        self.assertEqual(
            sum(item["bytes"] for item in classification["by_disposition"].values()),
            57_153,
        )

    def test_candidate_queue_is_empty_and_unresolved_queue_is_bounded(self) -> None:
        classes = self.result["classification"]["by_disposition"]
        self.assertNotIn("cross_image_exact_source_candidate", classes)
        self.assertEqual(classes["source_owned_production"],
                         {"spans": 187, "bytes": 26_720})
        self.assertEqual(
            classes["typed_unresolved_executable"],
            {"spans": 0, "bytes": 0},
        )
        self.assertEqual(classes["typed_nonentry_mixed_or_data"],
                         {"spans": 67, "bytes": 30_121})

    def test_admitted_ambiq_functions_are_exact_production_source(self) -> None:
        admission = self.result["admission"]
        self.assertTrue(admission["production_routed"])
        self.assertEqual(admission["license"], "BSD-3-Clause")
        self.assertEqual(admission["source_owned_bytes"], 26_720)
        functions = list(admission["functions"].values())
        self.assertEqual([item["bytes"] for item in functions], [712, 1_014])
        self.assertEqual([item["address_coupled_difference_bytes"] for item in functions], [20, 29])
        self.assertEqual([len(item["provider_edges"]) for item in functions], [8, 12])

    def test_memset_wrapper_is_compiled_c_with_a_bounded_tail(self) -> None:
        wrapper = self.result["admission"]["memset_wrapper"]
        self.assertEqual(wrapper["source_bytes"], 18)
        self.assertEqual(wrapper["retained_unreachable_tail_bytes"], 2)
        self.assertEqual(len(wrapper["direct_call_sites"]), 7)
        self.assertIn(0x004201C4, wrapper["direct_call_sites"])
        self.assertEqual(wrapper["provider"], 0x0041560C)
        self.assertEqual(
            self.result["classification"]["by_disposition"]["retained_unreachable_tail"],
            {"spans": 16, "bytes": 284},
        )

    def test_hfadj_leaf_is_compiled_c_with_authenticated_mmio_semantics(self) -> None:
        hfadj = self.result["admission"]["clkgen_hfadj_enable"]
        self.assertEqual(hfadj["source_bytes"], 24)
        self.assertEqual(hfadj["retained_unreachable_tail_bytes"], 2)
        self.assertEqual(hfadj["register"], 0x40004044)
        self.assertEqual(
            hfadj["direct_call_sites"],
            [0x00421DE2, 0x00421E18, 0x00421E7E],
        )

    def test_hfadj_config_is_source_routed_through_a_bounded_cave(self) -> None:
        config = self.result["admission"]["clkgen_hfadj_config"]
        self.assertEqual(config["stock_bytes"], 12)
        self.assertEqual(config["source_cave_bytes"], 16)
        self.assertEqual(config["source_cave_start"], 0x00426C28)
        self.assertEqual(config["register"], 0x40004020)
        self.assertEqual(
            config["direct_call_sites"],
            [0x0042176E, 0x0042177E, 0x00421DF6],
        )

    def test_hfadj_disable_is_source_routed_through_a_bounded_cave(self) -> None:
        disable = self.result["admission"]["clkgen_hfadj_disable"]
        self.assertEqual(disable["stock_bytes"], 14)
        self.assertEqual(disable["source_cave_bytes"], 20)
        self.assertEqual(disable["source_cave_start"], 0x00426C38)
        self.assertEqual(disable["register"], 0x40004020)
        self.assertEqual(
            disable["direct_call_sites"],
            [0x00421764, 0x0042178E],
        )

    def test_dual_switch_is_compiled_c_with_bounded_tail_and_provider(self) -> None:
        dual = self.result["admission"]["dual_switch"]
        self.assertEqual(dual["source_bytes"], 56)
        self.assertEqual(dual["retained_unreachable_tail_bytes"], 8)
        self.assertEqual(dual["register"], 0x40004044)
        self.assertEqual(dual["status_register"], 0x40004030)
        self.assertEqual(dual["poll_mask"], 0x01000000)
        self.assertEqual(dual["provider"], 0x0041D246)
        self.assertEqual(
            dual["direct_call_sites"],
            [0x00421FB4, 0x00421FDE, 0x004220A4],
        )

    def test_clkgen_config_is_source_routed_with_exact_register_contract(self) -> None:
        config = self.result["admission"]["clkgen_config"]
        self.assertEqual(config["stock_bytes"], 82)
        self.assertEqual(config["source_cave_bytes"], 84)
        self.assertEqual(config["source_cave_start"], 0x00415BFC)
        self.assertEqual(config["control_register"], 0x40004020)
        self.assertEqual(config["mode_register"], 0x4000404C)
        self.assertEqual(config["divider_register"], 0x40004048)
        self.assertEqual(config["direct_call_sites"], [0x00421928, 0x00421FC6])

    def test_clkgen_disable_is_source_routed_with_exact_register_contract(self) -> None:
        disable = self.result["admission"]["clkgen_disable"]
        self.assertEqual(disable["stock_bytes"], 14)
        self.assertEqual(disable["source_cave_bytes"], 20)
        self.assertEqual(disable["source_cave_start"], 0x00415C50)
        self.assertEqual(disable["register"], 0x40004050)
        self.assertEqual(disable["direct_call_sites"], [0x0042191E, 0x00422082])

    def test_float_gcd_is_source_routed_with_bounded_provider_contract(self) -> None:
        gcd = self.result["admission"]["float_gcd"]
        self.assertEqual(gcd["stock_bytes"], 106)
        self.assertEqual(gcd["source_cave_bytes"], 92)
        self.assertEqual(gcd["source_cave_start"], 0x00415C64)
        self.assertEqual(gcd["provider"], 0x00427C90)
        self.assertEqual(gcd["main_analogue"], 0x0053937C)
        self.assertEqual(gcd["identical_bytes"], 102)
        self.assertEqual(gcd["direct_call_sites"], [0x00426DCE, 0x0042706C])

    def test_float_ratio_is_source_routed_with_bounded_encoding_contract(self) -> None:
        ratio = self.result["admission"]["float_ratio"]
        self.assertEqual(ratio["stock_bytes"], 248)
        self.assertEqual(ratio["source_cave_bytes"], 252)
        self.assertEqual(ratio["source_cave_start"], 0x00415CD4)
        self.assertEqual(ratio["main_analogue"], 0x005393E8)
        self.assertEqual(ratio["identical_bytes"], 230)
        self.assertEqual(ratio["direct_call_sites"], [0x00426FC8])
        self.assertEqual(len(ratio["provider_edges"]), 7)
        self.assertEqual(ratio["provider_edges"][0]["target_address"], 0x00426D48)

    def test_float_multiplier_is_source_routed_with_hard_float_contract(self) -> None:
        multiplier = self.result["admission"]["float_multiplier"]
        self.assertEqual(multiplier["stock_bytes"], 190)
        self.assertEqual(multiplier["source_cave_bytes"], 192)
        self.assertEqual(multiplier["source_cave_start"], 0x00415DE4)
        self.assertEqual(multiplier["main_analogue"], 0x005394E0)
        self.assertEqual(multiplier["identical_bytes"], 173)
        self.assertEqual(multiplier["direct_call_sites"], [0x00426FE6])
        self.assertEqual(len(multiplier["provider_edges"]), 5)
        self.assertEqual(
            [item["target_address"] for item in multiplier["provider_edges"]],
            [0x00427DD0, 0x00427CCC, 0x00427D98,
             0x00427C90, 0x00427C90],
        )

    def test_production_source_is_reviewable_mnemonic_assembly(self) -> None:
        source = SOURCE.read_text()
        self.assertNotIn(".byte", source)
        self.assertNotIn(".short", source)
        self.assertNotIn(".word", source)
        self.assertIn(".syntax unified", source)
        self.assertIn("ABI r0=pHandle", source)
        self.assertEqual(
            self.result["admission"]["upstream_commit"],
            "5efc0228528a8adce5eae0d226fac85d2551eb3b",
        )

    def test_literal_pools_remain_typed_official_data(self) -> None:
        rows = list(csv.DictReader(CENSUS.read_text().splitlines(), delimiter="\t"))
        pools = [row for row in rows if row["kind"] == "literal_pool"]
        self.assertEqual([(row["start"], row["end"], int(row["size"])) for row in pools], [
            ("0x004267fe", "0x00426808", 10),
            ("0x00426bfe", "0x00426c10", 18),
        ])
        self.assertTrue(all(row["disposition"] == "retained_typed_data" for row in pools))

    def test_both_reviewed_compilers_emit_the_same_bodies(self) -> None:
        self.assertTrue(self.result["profiles"]["apple-clang"].startswith("Apple clang version 21.0.0"))
        self.assertEqual(self.result["profiles"]["linux-clang"], "Homebrew clang version 22.1.8")

    def test_syspll_deinitialize_is_exact_in_place_production_c(self) -> None:
        deinitialize = self.result["admission"]["syspll_deinitialize"]
        self.assertEqual(deinitialize["stock_bytes"], 80)
        self.assertEqual(
            deinitialize["source_in_place_bytes_by_profile"],
            {"apple-clang": 80, "linux-clang": 80},
        )
        self.assertEqual(
            deinitialize["direct_call_sites"],
            [0x00422198, 0x00422266],
        )
        self.assertEqual(
            [item["target_address"] for item in deinitialize["provider_edges"]],
            [0x004273DC, 0x0041CAE8, 0x0041CAA2],
        )
        self.assertEqual(deinitialize["handle_magic"], 0x01504C30)
        self.assertEqual(deinitialize["main_analogue"], 0x00539944)
        self.assertEqual(deinitialize["identical_bytes"], 74)

    def test_syspll_enable_is_source_routed_in_authenticated_body_space(self) -> None:
        enable = self.result["admission"]["syspll_enable"]
        self.assertEqual(enable["stock_bytes"], 124)
        self.assertEqual(enable["source_cave_start"], 0x00427364)
        self.assertEqual(
            enable["source_cave_bytes_by_profile"],
            {"apple-clang": 84, "linux-clang": 84},
        )
        self.assertEqual(enable["direct_call_sites"], [0x0042217E])
        self.assertEqual(enable["handle_magic"], 0x01504C30)
        self.assertEqual(enable["vrctrl_address"], 0x40020060)
        self.assertEqual(enable["pllctl0_address"], 0x400204D8)
        self.assertEqual(enable["main_analogue"], 0x00539994)
        self.assertEqual(enable["identical_bytes"], 118)

    def test_syspll_disable_is_exact_in_place_production_source(self) -> None:
        disable = self.result["admission"]["syspll_disable"]
        self.assertEqual(disable["stock_bytes"], 48)
        self.assertEqual(
            disable["source_bytes_by_profile"],
            {"apple-clang": 48, "linux-clang": 48},
        )
        self.assertEqual(disable["direct_call_sites"], [0x00422260, 0x0042733C])
        self.assertEqual(disable["handle_magic"], 0x01504C30)
        self.assertEqual(disable["pllctl0_address"], 0x400204D8)
        self.assertEqual(disable["main_analogue"], 0x00539A10)
        self.assertEqual(disable["identical_bytes"], 44)

    def test_syspll_configure_is_source_routed_in_authenticated_body_space(self) -> None:
        configure = self.result["admission"]["syspll_configure"]
        self.assertEqual(configure["stock_bytes"], 278)
        self.assertEqual(configure["source_cave_start"], 0x00427410)
        self.assertEqual(
            configure["source_cave_bytes_by_profile"],
            {"apple-clang": 240, "linux-clang": 240},
        )
        self.assertEqual(configure["direct_call_sites"], [0x00422170])
        self.assertEqual(
            configure["provider_edges"],
            [{"offset": 0xEE, "target_address": 0x0041AC92}],
        )
        self.assertEqual(configure["handle_magic"], 0x01504C30)
        self.assertEqual(configure["pllctl0_address"], 0x400204D8)
        self.assertEqual(configure["plldiv0_address"], 0x400204DC)
        self.assertEqual(configure["plldiv1_address"], 0x400204E0)
        self.assertEqual(configure["main_analogue"], 0x00539A40)
        self.assertEqual(configure["identical_bytes"], 267)

    def test_live_boot_accounting_conserves_the_stock_owned_domain(self) -> None:
        component = self.result["boot_component"]
        self.assertEqual(component["source_owned_bytes"], 59_009)
        self.assertEqual(component["source_owned_cave_bytes"], 2_594)
        self.assertEqual(component["opaque_base_bytes"], 87_985)
        self.assertEqual(component["source_owned_in_place_bytes"], 41_190)
        self.assertEqual(component["generated_patch_site_bytes"], 16_830)
        self.assertEqual(
            component["source_owned_bytes"] + component["opaque_base_bytes"] +
            component["generated_alignment_bytes"],
            147_010,
        )

    def test_mode_apply_is_exact_source_with_pinned_routes_and_state(self) -> None:
        mode = self.result["admission"]["mode_apply"]
        self.assertEqual((mode["start"], mode["end_exclusive"]),
                         (0x0042FF00, 0x0042FFF2))
        self.assertEqual(mode["source_bytes_by_profile"],
                         {"apple-clang": 242, "linux-clang": 242})
        self.assertEqual(mode["direct_call_sites"], [0x0042FFF8])
        self.assertEqual(mode["state_address"], 0x200270D0)
        self.assertEqual(mode["aggregate_modes"], [6, 7, 9])
        self.assertEqual(len(mode["provider_edges"]), 8)
        self.assertEqual(mode["hardware_validation"],
                         "blocked by unavailable physical evidence")

    def test_platform_finish_is_exact_bounded_eight_slot_lifecycle(self) -> None:
        finish = self.result["admission"]["platform_finish"]
        self.assertEqual((finish["start"], finish["end_exclusive"]),
                         (0x00430502, 0x00430610))
        self.assertEqual(finish["source_bytes_by_profile"],
                         {"apple-clang": 270, "linux-clang": 270})
        self.assertEqual(finish["direct_call_sites"], [0x004301EC])
        self.assertEqual((finish["slot_count"], finish["interrupt_number"]),
                         (8, 10))
        self.assertEqual(finish["main_analogue"], 0x0050423A)
        self.assertEqual(finish["identical_main_bytes"], 196)
        self.assertEqual(len(finish["provider_edges"]), 12)
        self.assertEqual(len(finish["shared_literals"]), 7)

        descriptor = self.result["admission"]["descriptor_register"]
        self.assertEqual((descriptor["start"], descriptor["end_exclusive"]),
                         (0x00430280, 0x004303BC))
        self.assertEqual(descriptor["source_bytes_by_profile"],
                         {"apple-clang": 316, "linux-clang": 316})
        self.assertEqual(descriptor["direct_call_sites"], [0x004301DC])
        self.assertEqual(descriptor["main_analogue"], 0x0053A454)
        self.assertEqual(descriptor["identical_main_bytes"], 285)
        self.assertEqual(descriptor["supported_types"], [1, 2, 4])
        self.assertEqual((descriptor["descriptor_stride"],
                          descriptor["interrupt_mask_words"]), (12, 7))

        composer = self.result["admission"]["hardware_state_compose"]
        self.assertEqual((composer["start"], composer["end_exclusive"]),
                         (0x0042BDF0, 0x0042BF4E))
        self.assertEqual(composer["source_bytes_by_profile"],
                         {"apple-clang": 350, "linux-clang": 350})
        self.assertEqual(composer["direct_call_sites"], [])
        self.assertEqual(composer["stored_pointer"], 0x0041D164)
        self.assertEqual(composer["main_analogue"], 0x005A1C18)
        self.assertEqual(composer["identical_main_bytes"], 313)
        self.assertEqual(composer["config_read_count"], 3)
        self.assertEqual(len(composer["provider_edges"]), 4)
        self.assertEqual(composer["hardware_validation"],
                         "blocked by unavailable physical evidence")

        crc = self.result["admission"]["dfu_image_crc_check"]
        self.assertEqual((crc["start"], crc["end_exclusive"]),
                         (0x0042D890, 0x0042D9F0))
        self.assertEqual(crc["source_bytes_by_profile"],
                         {"apple-clang": 352, "linux-clang": 352})
        self.assertEqual(crc["direct_call_sites"], [0x0042DFF6])
        self.assertEqual(len(crc["provider_edges"]), 12)
        self.assertEqual(len(crc["shared_literals"]), 11)
        self.assertEqual((crc["header_bytes_skipped"],
                          crc["payload_size_mask"]), (8, 0x00FFFFFF))
        self.assertTrue(crc["short_reads_are_logged"])

        init = self.result["admission"]["hardware_context_initialize"]
        self.assertEqual((init["start"], init["end_exclusive"]),
                         (0x0042E8D0, 0x0042EA32))
        self.assertEqual(init["source_bytes_by_profile"],
                         {"apple-clang": 354, "linux-clang": 354})
        self.assertEqual(init["direct_call_sites"], [0x00430016])
        self.assertEqual(init["main_analogue"], 0x0055D94C)
        self.assertEqual(init["identical_main_bytes"], 339)
        self.assertEqual((init["slot_stride"], init["primary_profile_words"],
                          init["secondary_profile_words"]), (72, 3, 2))
        self.assertEqual(len(init["provider_edges"]), 5)
        self.assertEqual(len(init["shared_literals"]), 11)

        registers = self.result["admission"]["state_register_initialize"]
        self.assertEqual((registers["start"], registers["end_exclusive"]),
                         (0x0042D3BC, 0x0042D562))
        self.assertEqual(registers["source_bytes_by_profile"],
                         {"apple-clang": 422, "linux-clang": 422})
        self.assertEqual(registers["direct_call_sites"], [0x0042D59C])
        self.assertEqual(registers["main_analogue"], 0x005A05E0)
        self.assertEqual(registers["identical_main_bytes"], 414)
        self.assertEqual(registers["delay_sequence_us"], [5, 10])
        self.assertEqual(registers["power_mask"], 0xF0000000)
        self.assertEqual(len(registers["provider_edges"]), 2)
        self.assertEqual(len(registers["shared_literals"]), 16)

        program = self.result["admission"]["dfu_payload_program"]
        self.assertEqual((program["start"], program["end_exclusive"]),
                         (0x0042DAE8, 0x0042DC90))
        self.assertEqual(program["source_bytes_by_profile"],
                         {"apple-clang": 424, "linux-clang": 424})
        self.assertEqual(program["direct_call_sites"], [0x0042E004])
        self.assertEqual(len(program["provider_edges"]), 14)
        self.assertEqual(len(program["shared_literals"]), 13)
        self.assertEqual((program["header_bytes_skipped"],
                          program["payload_size_mask"]), (32, 0x00FFFFFF))
        self.assertTrue(program["indirect_program_callback"])

        bringup = self.result["admission"]["platform_bringup"]
        self.assertEqual((bringup["start"], bringup["end_exclusive"]),
                         (0x00430000, 0x004301D6))
        self.assertEqual(bringup["source_bytes_by_profile"],
                         {"apple-clang": 470, "linux-clang": 470})
        self.assertEqual(bringup["direct_call_sites"], [0x004301E4])
        self.assertEqual(len(bringup["provider_edges"]), 23)
        self.assertEqual(len(bringup["shared_literals"]), 16)
        self.assertEqual((bringup["measurement_attempts"],
                          bringup["measurement_scale_numerator"],
                          bringup["measurement_scale_shift"]), (3, 0x4A6, 12))

        task = self.result["admission"]["dfu_service_task"]
        self.assertEqual((task["start"], task["end_exclusive"]),
                         (0x0042DE58, 0x0042E104))
        self.assertEqual(task["source_bytes_by_profile"],
                         {"apple-clang": 684, "linux-clang": 684})
        self.assertEqual(task["direct_call_sites"], [0x0042E1CC])
        self.assertEqual(len(task["provider_edges"]), 29)
        self.assertEqual(len(task["shared_literals"]), 20)
        self.assertEqual((task["header_bytes"], task["queue_command"],
                          task["vector_ready_mask"]), (32, 1, 0x20000000))

        state_one = self.result["admission"]["state_event_one_value"]
        self.assertEqual((state_one["start"], state_one["end_exclusive"]),
                         (0x0042D104, 0x0042D3BC))
        self.assertEqual(state_one["source_bytes_by_profile"],
                         {"apple-clang": 696, "linux-clang": 696})
        self.assertEqual(state_one["direct_call_sites"], [0x0042D5A6])
        self.assertEqual((state_one["main_analogue"],
                          state_one["identical_main_bytes"]),
                         (0x005A0328, 684))
        self.assertEqual(len(state_one["provider_edges"]), 3)
        self.assertEqual(len(state_one["shared_literals"]), 16)
        self.assertEqual(state_one["delay_sequences_us"],
                         {"active": [5, 10], "nonactive": [15]})

        decode = self.result["admission"]["hardware_state_decode"]
        self.assertEqual((decode["start"], decode["end_exclusive"]),
                         (0x0042B6B8, 0x0042B9BA))
        self.assertEqual(decode["source_bytes_by_profile"],
                         {"apple-clang": 770, "linux-clang": 770})
        self.assertEqual(decode["direct_call_sites"], [0x0042BCEC])
        self.assertEqual((decode["main_analogue"],
                          decode["identical_main_bytes"]),
                         (0x005A13E8, 738))
        self.assertEqual(len(decode["provider_edges"]), 0)
        self.assertEqual(len(decode["shared_literals"]), 8)
        self.assertEqual((decode["portable_cases"], decode["primary_values"],
                          decode["secondary_values"]), (16384, 24, 12))

        transition = self.result["admission"]["spotmgr_state_transition"]
        self.assertEqual((transition["start"], transition["end_exclusive"]),
                         (0x0042B294, 0x0042B69C))
        self.assertEqual(transition["source_bytes_by_profile"],
                         {"apple-clang": 1032, "linux-clang": 1032})
        self.assertEqual(transition["direct_call_sites"], [0x0042BD14])
        self.assertEqual((transition["main_analogue"],
                          transition["identical_main_bytes"]),
                         (0x005A0FC4, 996))
        self.assertEqual(len(transition["provider_edges"]), 12)
        self.assertEqual(len(transition["shared_literals"]), 15)
        self.assertEqual(transition["transition_delays"], [50, 200, 2000])
        self.assertEqual(transition["special_states"], [1, 5, 8, 12, 14, 15, 17])

    def test_spotmgr_transition_is_exact_in_place_production_source(self) -> None:
        transition = self.result["admission"]["spotmgr_transition_sequence_2b"]
        self.assertEqual(transition["start"], 0x00428378)
        self.assertEqual(transition["end_exclusive"], 0x004283E2)
        self.assertEqual(
            transition["source_bytes_by_profile"],
            {"apple-clang": 106, "linux-clang": 106},
        )
        self.assertEqual(transition["direct_call_sites"], [0x0042A05C])
        self.assertEqual(transition["provider"], 0x0041D1C0)
        self.assertEqual(len(transition["shared_literals"]), 9)
        self.assertEqual(
            transition["shared_literals"][0],
            {"address": 0x00428A90, "value": 0x200270B4},
        )

    def test_spotmgr_transition_7b_is_exact_bounded_production_source(self) -> None:
        transition = self.result["admission"]["spotmgr_transition_sequence_7b"]
        self.assertEqual(transition["start"], 0x00428A94)
        self.assertEqual(transition["end_exclusive"], 0x00428BA8)
        self.assertEqual(
            transition["source_bytes_by_profile"],
            {"apple-clang": 276, "linux-clang": 276},
        )
        self.assertEqual(transition["direct_call_sites"], [0x0042A068])
        self.assertEqual(len(transition["provider_edges"]), 5)
        self.assertEqual(
            [item["target_address"] for item in transition["provider_edges"]],
            [0x0041D1C0, 0x0041D1C0, 0x0041D1C0, 0x0041D21C,
             0x0041D1C0],
        )
        self.assertEqual(len(transition["shared_literals"]), 12)
        self.assertEqual(transition["poll_limit_us"], 20)

    def test_spotmgr_factory_trim_loader_is_exact_indexed_source(self) -> None:
        loader = self.result["admission"]["spotmgr_factory_trim_loader"]
        self.assertEqual(loader["start"], 0x00429DA4)
        self.assertEqual(loader["end_exclusive"], 0x00429DF6)
        self.assertEqual(
            loader["source_bytes_by_profile"],
            {"apple-clang": 82, "linux-clang": 82},
        )
        self.assertEqual(loader["direct_call_sites"], [0x0042A042])
        self.assertEqual(loader["main_analogue"], 0x005A3E24)
        self.assertEqual(len(loader["shared_literals"]), 5)

    def test_spotmgr_factory_trim_readiness_has_exact_stored_ingress(self) -> None:
        wrapper = self.result["admission"]["spotmgr_factory_trim_readiness"]
        self.assertEqual(wrapper["start"], 0x0042A036)
        self.assertEqual(wrapper["end_exclusive"], 0x0042A04A)
        self.assertEqual(wrapper["stored_entry_pointer"], 0x0041D15C)
        self.assertEqual(wrapper["provider"], 0x00429DA4)
        self.assertEqual(wrapper["main_analogue"], 0x005A40B6)

    def test_spotmgr_timer_irq_extent_and_critical_edges_are_exact(self) -> None:
        service = self.result["admission"]["spotmgr_timer_irq_service"]
        self.assertEqual(service["start"], 0x0042A04A)
        self.assertEqual(service["end_exclusive"], 0x0042A078)
        self.assertEqual(service["corrected_prior_end_exclusive"], 0x0042A074)
        self.assertEqual(service["stored_entry_pointer"], 0x0041D160)
        self.assertEqual(len(service["direct_call_sites"]), 24)
        self.assertEqual(service["direct_call_sites"][0], 0x00427F62)
        self.assertEqual(service["direct_call_sites"][-1], 0x00429FFA)
        self.assertEqual(
            [item["target_address"] for item in service["provider_edges"]],
            [0x0041B8EC, 0x00428378, 0x00428A94, 0x0041CCD6],
        )

    def test_spotmgr_buck_deepsleep_classifier_is_exact_and_bounded(self) -> None:
        classifier = self.result["admission"][
            "spotmgr_buck_deepsleep_classifier"
        ]
        self.assertEqual(classifier["start"], 0x0042A08C)
        self.assertEqual(classifier["end_exclusive"], 0x0042A19C)
        self.assertEqual(
            classifier["source_bytes_by_profile"],
            {"apple-clang": 272, "linux-clang": 272},
        )
        self.assertEqual(classifier["direct_call_sites"], [0x0042AA7A])
        self.assertEqual(classifier["provider"], 0x0041F3F0)
        self.assertEqual(classifier["main_analogue"], 0x005A410C)
        self.assertEqual(classifier["identical_main_bytes"], 253)
        self.assertEqual(classifier["timer_count"], 16)
        self.assertEqual(
            classifier["timer_clock_ranges"],
            [[0, 6], [19, 25], [0x100, 0x1E0]],
        )
        self.assertEqual(len(classifier["shared_literals"]), 5)

        scan = self.result["admission"]["spotmgr_buck_deepsleep_scan"]
        self.assertEqual((scan["start"], scan["end_exclusive"]),
                         (0x0042AEF0, 0x0042B010))
        self.assertEqual(scan["source_bytes_by_profile"],
                         {"apple-clang": 288, "linux-clang": 288})
        self.assertEqual(scan["direct_call_sites"], [0x0042BC08])
        self.assertEqual(scan["provider"], 0x0041F3F0)
        self.assertEqual(scan["main_analogue"], 0x005A0C20)
        self.assertEqual(scan["identical_main_bytes"], 284)
        self.assertEqual(scan["host_cases_tested"], 100_000)

        effects = self.result["admission"]["spotmgr_state_transition_effects"]
        self.assertEqual((effects["start"], effects["end_exclusive"]),
                         (0x0042B014, 0x0042B068))
        self.assertEqual(effects["direct_call_sites"],
                         [0x0042BCB0, 0x0042BD26])
        self.assertEqual(effects["main_analogue"], 0x005A0D44)
        self.assertEqual(effects["exact_main_bytes"], 84)
        self.assertEqual(effects["cleared_power_control_mask"], 0x10048)
        self.assertEqual(effects["state_pairs_tested"], 65_536)

        transition = self.result["admission"]["spotmgr_power_transition_trims"]
        self.assertEqual((transition["start"], transition["end_exclusive"]),
                         (0x0042B06C, 0x0042B294))
        self.assertEqual(transition["direct_call_sites"],
                         [0x0042B2DA, 0x0042B348, 0x0042B65C])
        self.assertEqual(len(transition["provider_edges"]), 2)
        self.assertEqual(transition["main_analogue"], 0x005A0D9C)
        self.assertEqual(transition["identical_main_bytes"], 540)
        self.assertEqual(transition["route_cases_tested"], 10_500)
        self.assertEqual(transition["temporary_trim_widths"], [10, 6])

        helpers = self.result["admission"]["rounded_divider_helpers"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in helpers], [52, 20])
        self.assertEqual([item["main_analogue"] for item in helpers],
                         [0x0055BF1C, 0x0055BF50])
        self.assertEqual([item["direct_call_sites"] for item in helpers],
                         [[0x0042C394, 0x0042C3C8], [0x0042C3B2]])

        clock = self.result["admission"]["hardware_clock_encode"]
        self.assertEqual(clock["source_bytes_by_profile"],
                         {"apple-clang": 376, "linux-clang": 376})
        self.assertEqual(clock["direct_call_sites"], [0x0042CCB0])
        self.assertEqual(clock["main_analogue"], 0x0055BF64)
        self.assertEqual(clock["identical_main_bytes"], 370)
        self.assertEqual([edge["target_address"]
                          for edge in clock["provider_edges"]],
                         [0x0042C222, 0x0042C256, 0x0042C222])
        self.assertEqual(clock["source_clock_hz"], 96_000_000)
        self.assertEqual(clock["maximum_exponent"], 7)

        apply = self.result["admission"]["hardware_event_apply"]
        self.assertEqual(apply["source_bytes_by_profile"],
                         {"apple-clang": 368, "linux-clang": 368})
        self.assertEqual(apply["direct_call_sites"],
                         [0x0042C7D0, 0x0042C92A])
        self.assertEqual(apply["main_analogue"], 0x0055BDAC)
        self.assertEqual(apply["identical_main_bytes"], 361)
        self.assertEqual(apply["provider_edges"],
                         [{"offset": 0xC8, "target_address": 0x0041D1C0}])
        self.assertEqual((apply["drain_event_mask"], apply["pulse_event_mask"]),
                         (0x800, 0x210))

        state_services = self.result["admission"]["state_range_services"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in state_services], [172, 264, 96])
        self.assertEqual([item["main_analogue"] for item in state_services],
                         [0x005A001C, 0x005A00FC, 0x005A0786])
        self.assertEqual([item["direct_call_sites"] for item in state_services],
                         [[0x0042CECC, 0x0042D5E0], [0x0042D5B0], []])
        self.assertEqual(state_services[2]["stored_pointer"], 0x0041D184)
        self.assertEqual([len(item["provider_edges"]) for item in state_services],
                         [0, 3, 4])

        classifier = self.result["admission"]["state_event_zero"]
        self.assertEqual((classifier["start"], classifier["end_exclusive"]),
                         (0x0042CFE0, 0x0042D0F2))
        self.assertEqual(classifier["source_bytes_by_profile"],
                         {"apple-clang": 274, "linux-clang": 274})
        self.assertEqual(classifier["direct_call_sites"], [0x0042D58C])
        self.assertEqual(classifier["main_analogue"], 0x005A0204)
        self.assertEqual(classifier["identical_main_bytes"], 271)
        self.assertEqual(classifier["channel_count"], 16)
        self.assertEqual(classifier["classified_ranges"],
                         [[0, 6], [19, 25], [256, 480]])

        primitives = self.result["admission"]["miscellaneous_primitives"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in primitives], [62, 6, 18, 52, 32])
        self.assertEqual([item["direct_call_sites"] for item in primitives],
                         [[0x0042D8A8, 0x0042DB2E, 0x0042DED8],
                          [0x0042DD6A], [0x0042E08C, 0x0042E0F8],
                          [0x0042D936, 0x0042D99C], [0x0042DE50]])

        register_helpers = self.result["admission"]["register_helpers"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in register_helpers],
                         [66, 60, 56, 68, 46, 28, 36, 30])
        self.assertEqual([item["direct_call_sites"] for item in register_helpers],
                         [[0x0042C570], [0x0042C796, 0x0042C8CE],
                          [0x004305CC], [0x0043061C], [0x0043062E],
                          [0x0043036E], [0x0043035E], [0x004305D2]])
        self.assertTrue(all(item["hardware_validation"] ==
                            "blocked by unavailable physical evidence"
                            for item in register_helpers))

        adapters = self.result["admission"]["command_queue_adapters"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in adapters], [62, 46, 12])
        self.assertEqual([item["direct_call_sites"] for item in adapters],
                         [[0x0042C5D0], [0x0042C93E, 0x0042CAA4],
                          [0x0042C94A, 0x0042CBE0]])
        self.assertEqual([item["provider_edge"]["target_address"]
                          for item in adapters],
                         [0x00427794, 0x00427878, 0x004278C8])

        descriptor = self.result["admission"]["hardware_descriptor_publish"]
        self.assertEqual(descriptor["source_bytes_by_profile"],
                         {"apple-clang": 108, "linux-clang": 108})
        self.assertEqual(descriptor["direct_call_sites"], [0x0042C7EC])
        self.assertEqual(descriptor["published_field_order"], [0, 1, 4, 2, 3, 5])
        self.assertEqual(descriptor["hardware_validation"],
                         "blocked by unavailable physical evidence")

        claim = self.result["admission"]["hardware_context_claim"]
        self.assertEqual(claim["source_bytes_by_profile"],
                         {"apple-clang": 114, "linux-clang": 114})
        self.assertEqual(claim["direct_call_sites"], [0x00430514])
        self.assertEqual(claim["main_analogue"], 0x0055C2BC)
        self.assertEqual(claim["identical_main_bytes"], 110)
        self.assertEqual(claim["handle_magic"], 0x123456)
        self.assertEqual(claim["context_stride"], 0x8A8)
        self.assertEqual(claim["status_codes"],
                         {"success": 0, "index": 5, "output": 6,
                          "claimed": 7})

        enable = self.result["admission"]["hardware_context_enable"]
        self.assertEqual(enable["source_bytes_by_profile"],
                         {"apple-clang": 258, "linux-clang": 258})
        self.assertEqual(enable["direct_call_sites"], [0x0043056C])
        self.assertEqual(enable["main_analogue"], 0x0055C32E)
        self.assertEqual(enable["identical_main_bytes"], 246)
        self.assertEqual([edge["target_address"]
                          for edge in enable["provider_edges"]],
                         [0x0042C034, 0x0042C3E2, 0x0041D246])
        self.assertEqual(enable["rollback_mask"], 0x11)

        event = self.result["admission"]["hardware_event_service"]
        self.assertEqual(event["source_bytes_by_profile"],
                         {"apple-clang": 648, "linux-clang": 648})
        self.assertEqual(event["direct_call_sites"], [0x00430636])
        self.assertEqual(event["main_analogue"], 0x0055C558)
        self.assertEqual(event["identical_main_bytes"], 621)
        self.assertEqual(len(event["provider_edges"]), 9)
        self.assertEqual(event["event_apply_mask"], 0x4A7C)
        self.assertEqual(event["register_200_mask"], 0xFFFFFBFE)

        config = self.result["admission"]["hardware_config_transaction"]
        self.assertEqual(config["source_bytes_by_profile"],
                         {"apple-clang": 684, "linux-clang": 684})
        self.assertEqual(config["direct_call_sites"],
                         [0x004304EC, 0x00430552])
        self.assertEqual(config["main_analogue"], 0x0055C7E8)
        self.assertEqual(config["identical_main_bytes"], 657)
        self.assertEqual(len(config["provider_edges"]), 7)
        self.assertEqual(config["snapshot_register_count"], 13)
        self.assertEqual(config["supported_modes"], [0, 1, 2])

        instance = self.result["admission"]["hardware_instance_configure"]
        self.assertEqual(instance["source_bytes_by_profile"],
                         {"apple-clang": 380, "linux-clang": 380})
        self.assertEqual(instance["direct_call_sites"], [0x00430562])
        self.assertEqual(instance["main_analogue"], 0x0055CA94)
        self.assertEqual(instance["identical_main_bytes"], 352)
        self.assertEqual(instance["provider_edges"],
                         [{"offset": 0x7C, "target_address": 0x0042C26A}])
        self.assertEqual(instance["supported_modes"], [0, 1])
        self.assertEqual(instance["fixed_rates_hz"],
                         [100_000, 400_000, 1_000_000])
        self.assertEqual(instance["maximum_instances"], 8)
        self.assertEqual(instance["slot_count"], 4)

        retry = self.result["admission"]["hardware_config_retry"]
        self.assertEqual(retry["source_bytes_by_profile"],
                         {"apple-clang": 116, "linux-clang": 116})
        self.assertEqual(retry["direct_call_sites"], [0x00430576])
        self.assertEqual(retry["main_analogue"], 0x005041C6)
        self.assertEqual(retry["identical_main_bytes"], 98)
        self.assertEqual([edge["target_address"] for edge in retry["provider_edges"]],
                         [0x0041D92C, 0x0041D92C, 0x0041F9D8, 0x0042C988])
        self.assertEqual((retry["maximum_attempts"], retry["retry_delay_us"],
                          retry["timeout_status"]), (1000, 10, 4))

        profile = self.result["admission"]["hardware_profile_apply"]
        self.assertEqual(profile["source_bytes_by_profile"],
                         {"apple-clang": 142, "linux-clang": 142})
        self.assertEqual(profile["direct_call_sites"], [0x004300B6])
        self.assertEqual(profile["main_analogue"], 0x0055DAE4)
        self.assertEqual(profile["identical_main_bytes"], 140)
        self.assertEqual(profile["provider_edges"],
                         [{"offset": 0x2E, "target_address": 0x004222F0}])
        self.assertEqual((profile["profile_fields"], profile["published_register"]),
                         (7, 0x40038000))

        controls = self.result["admission"]["runtime_control_wrappers"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in controls], [8, 10, 10, 22, 18])
        self.assertEqual([item["direct_call_sites"] for item in controls],
                         [[0x0042DD1E], [0x0042DD16], [0x0042DD26],
                          [0x0042DD2C], [0x0042E1D4]])
        self.assertEqual([len(item["provider_edges"]) for item in controls],
                         [1, 1, 1, 2, 2])

        event_controls = self.result["admission"]["event_control_wrappers"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in event_controls], [14, 22, 20])
        self.assertEqual([item["direct_call_sites"] for item in event_controls],
                         [[0x0042E30A], [], [0x0042E1DE]])
        self.assertEqual([item["provider_edge"]["target_address"]
                          for item in event_controls],
                         [0x0042E2A2, 0x00416200, 0x0041652E])

        services = self.result["admission"]["runtime_control_services"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in services], [80, 72, 84, 60])
        self.assertEqual([item["direct_call_sites"] for item in services],
                         [[], [0x0042E2F2], [0x0042E508],
                          [0x0042F268, 0x0042F2D4, 0x0042F336, 0x0042F37E]])
        self.assertEqual(services[0]["stored_pointer"], 0x0041D16C)
        self.assertTrue(all(item["hardware_validation"] ==
                            "blocked by unavailable physical evidence"
                            for item in services))

        loop = self.result["admission"]["event_service_loop"]
        self.assertEqual((loop["start"], loop["end_exclusive"]),
                         (0x0042E2F8, 0x0042E39A))
        self.assertEqual(loop["stored_pointer"], 0x0042E48C)
        self.assertEqual(loop["wait_timeout"], 60_000)
        self.assertEqual(len(loop["provider_edges"]), 14)

        event_runtime = self.result["admission"]["event_runtime_services"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in event_runtime], [262, 66, 108])
        self.assertEqual([item["direct_call_sites"] for item in event_runtime],
                         [[0x0042E27A], [], [0x0042E79C]])
        self.assertEqual([len(item["provider_edges"]) for item in event_runtime],
                         [9, 2, 3])

        orchestration = self.result["admission"]["control_orchestration"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in orchestration], [84, 74])
        self.assertEqual(orchestration[0]["stored_pointer"], 0x0042E174)
        self.assertEqual(orchestration[1]["direct_call_sites"],
                         [0x0042DE9A, 0x0042DF0C, 0x0042E00A])

        publish = self.result["admission"]["runtime_context_publish"]
        self.assertEqual((publish["start"], publish["end_exclusive"]),
                         (0x0042DCA2, 0x0042DD14))
        self.assertEqual(publish["direct_call_sites"],
                         [0x0042E33A, 0x0042E364])
        self.assertEqual(publish["event_mask"], 0x00400000)

        late = self.result["admission"]["late_runtime_wrappers"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in late], [12, 34, 40, 40, 44, 62])
        self.assertEqual(late[4]["end_exclusive"], 0x00430B3C)
        self.assertEqual(late[5]["stored_pointer"], 0x00433448)
        self.assertEqual([len(item["provider_edges"]) for item in late],
                         [1, 1, 2, 2, 2, 8])

        noops = self.result["admission"]["noop_callbacks"]
        self.assertEqual([item["start"] for item in noops],
                         [0x0042DD98, 0x0042E276, 0x0042E39A])
        self.assertTrue(all(item["semantic_effect"] == "none" for item in noops))
        self.assertEqual([item["direct_call_sites"] for item in noops],
                         [[0x0042DD22], [0x0042E302], [0x0042E36C]])

        startup = self.result["admission"]["startup_services"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in startup], [10, 16, 24, 34])
        self.assertEqual([item["main_analogue"] for item in startup],
                         [0x005E4228, 0x005E4232, 0x005E4254, 0x005E4270])
        self.assertEqual([item["direct_call_sites"] for item in startup],
                         [[0x0043297C], [], [0x00432924], [0x0043294C]])
        self.assertEqual(startup[1]["stored_entry_pointer"], 0x00410004)
        self.assertEqual([len(item["provider_edges"]) for item in startup],
                         [0, 1, 2, 0])

        runtime = self.result["admission"]["startup_runtime"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in runtime], [30, 32, 14])
        self.assertEqual([item["main_analogue"] for item in runtime],
                         [0x005E4294, 0x005E42B4, 0x005E42DC])
        self.assertEqual([item["identical_main_bytes"] for item in runtime],
                         [27, 32, 11])
        self.assertEqual([item["direct_call_sites"] for item in runtime],
                         [[0x00432950], [0x00432984], [0x00432996]])
        self.assertEqual([len(item["provider_edges"]) for item in runtime],
                         [4, 0, 1])

        alignment = self.result["admission"]["alignment_dispatch"]
        self.assertEqual((alignment["start"], alignment["end_exclusive"]),
                         (0x0042E4F4, 0x0042E50E))
        self.assertEqual(alignment["direct_call_sites"],
                         [0x0042DE42, 0x00430B30])
        self.assertEqual(alignment["main_analogue"], 0x004D0A2C)
        self.assertEqual(alignment["error_code"], 0x08000140)
        self.assertEqual((alignment["required_length_alignment"],
                          alignment["required_destination_alignment"]), (16, 4))
        self.assertEqual(alignment["portable_rejection_classes"], 63)

        guarded = self.result["admission"]["guarded_call_cleanup"]
        self.assertEqual((guarded["start"], guarded["end_exclusive"]),
                         (0x0042E8A4, 0x0042E8C2))
        self.assertEqual(guarded["direct_call_sites"], [0x0042E4D0])
        self.assertEqual(guarded["main_analogue"], 0x00541B7C)
        self.assertEqual(guarded["control_base"], 0x40014008)
        self.assertEqual(guarded["status_address"], 0x40014024)
        self.assertEqual(guarded["ordered_cleanup_writes"], [
            {"offset": 0, "value": 0xC3},
            {"offset": 0x1C, "value": 0},
            {"offset": 0, "value": 0},
        ])

        transfer = self.result["admission"]["register_profile_transfer"]
        self.assertEqual((transfer["start"], transfer["end_exclusive"]),
                         (0x0042F020, 0x0042F14E))
        self.assertEqual(transfer["source_bytes_by_profile"],
                         {"apple-clang": 302, "linux-clang": 302})
        self.assertEqual(transfer["direct_call_sites"],
                         [0x00430068, 0x004301BE])
        self.assertEqual(transfer["main_analogue"], 0x0055E09C)
        self.assertEqual(transfer["identical_main_bytes"], 292)
        self.assertEqual(transfer["supported_operations"], [0, 1, 2])
        self.assertEqual(transfer["profile_words"], 13)

        profile = self.result["admission"]["event_value_profile"]
        self.assertEqual((profile["start"], profile["end_exclusive"]),
                         (0x0042F204, 0x0042F2FA))
        self.assertEqual(profile["source_bytes_by_profile"],
                         {"apple-clang": 246, "linux-clang": 246})
        self.assertEqual(profile["direct_call_sites"], [0x0042F3C0])
        self.assertEqual(profile["main_analogue"], 0x0059FBAC)
        self.assertEqual(profile["identical_main_bytes"], 234)
        self.assertEqual(profile["settle_delay_cycles"], 15)
        self.assertEqual(len(profile["shared_literals"]), 12)

        event = self.result["admission"]["event_dispatch"]
        self.assertEqual((event["start"], event["end_exclusive"]),
                         (0x0042F38E, 0x0042F3DA))
        self.assertEqual(event["stored_entry_pointer"], 0x0041D1B4)
        self.assertEqual([edge["target_address"] for edge in event["provider_edges"]],
                         [0x0042F2FA, 0x0042F204])
        self.assertEqual(event["main_analogue"], 0x0059FD36)
        self.assertEqual((event["event_values_tested"],
                          event["event_selector_width_bits"]), (256, 8))

        services = self.result["admission"]["hardware_handle_services"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in services], [54, 54, 56, 42])
        self.assertEqual([item["main_analogue"] for item in services],
                         [0x0055DAAE, 0x0055DBF0, 0x0055DC26, 0x0055DC5E])
        self.assertEqual([item["direct_call_sites"] for item in services],
                         [[0x004301C4], [0x00430084],
                          [0x0043010C], [0x00430150]])

        command = self.result["admission"]["hardware_handle_command"]
        self.assertEqual((command["start"], command["end_exclusive"]),
                         (0x0042EFF4, 0x0042F014))
        self.assertEqual(command["direct_call_sites"], [0x00430112])
        self.assertEqual(command["main_analogue"], 0x0055E070)
        self.assertEqual((command["command_value"], command["command_address"]),
                         (55, 0x40038008))

        hardware = self.result["admission"]["hardware_configuration_enumeration"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in hardware], [340, 108, 388])
        self.assertEqual([item["main_analogue"] for item in hardware],
                         [0x0055DC88, 0x0055DE7C, 0x0055DEEC])
        self.assertEqual([item["direct_call_sites"] for item in hardware],
                         [[0x00430040], [0x0042EECA, 0x0042EFD0], [0x00430142]])
        self.assertEqual([len(item["provider_edges"]) for item in hardware],
                         [0, 0, 2])

    def test_spotmgr_internal_power_domain_marker_is_exact(self) -> None:
        marker = self.result["admission"]["spotmgr_internal_power_domain"]
        self.assertEqual(marker["start"], 0x0042A19C)
        self.assertEqual(marker["end_exclusive"], 0x0042A1B2)
        self.assertEqual(
            marker["source_bytes_by_profile"],
            {"apple-clang": 22, "linux-clang": 22},
        )
        self.assertEqual(marker["direct_call_sites"], [0x0042AAF4])
        self.assertEqual(marker["main_analogue"], 0x005A421C)
        self.assertEqual(marker["shared_flag"], 0x200271B0)
        self.assertEqual(marker["requested_deep_sleep_state"], 2)
        self.assertEqual(marker["prior_high_performance_state"], 1)

    def test_spotmgr_power_ton_selector_is_exact_and_fully_ingressed(self) -> None:
        selector = self.result["admission"]["spotmgr_power_ton_adjust"]
        self.assertEqual(selector["start"], 0x0042A1BC)
        self.assertEqual(selector["end_exclusive"], 0x0042A2A4)
        self.assertEqual(
            selector["source_bytes_by_profile"],
            {"apple-clang": 232, "linux-clang": 232},
        )
        self.assertEqual(len(selector["direct_call_sites"]), 19)
        self.assertEqual(selector["direct_call_sites"][0], 0x00427F18)
        self.assertEqual(selector["direct_call_sites"][-1], 0x0042A4DA)
        self.assertEqual(selector["main_analogue"], 0x005A423C)
        self.assertEqual(selector["identical_main_bytes"], 218)
        self.assertEqual(selector["power_state_8_forced_ton_state"], 7)
        self.assertEqual(selector["vddc_output_bit_offset"], 25)
        self.assertEqual(selector["vddf_output_bit_offset"], 8)
        self.assertEqual(len(selector["shared_literals"]), 4)

    def test_spotmgr_state_transition_sequence_is_exact_and_fully_ingressed(self) -> None:
        selector = self.result["admission"]["spotmgr_state_transition_sequence"]
        self.assertEqual(selector["start"], 0x0042A2B4)
        self.assertEqual(selector["end_exclusive"], 0x0042A43A)
        self.assertEqual(
            selector["source_bytes_by_profile"],
            {"apple-clang": 390, "linux-clang": 390},
        )
        self.assertEqual(
            selector["direct_call_sites"],
            [0x0042A462, 0x0042A492, 0x0042A524],
        )
        self.assertEqual(
            selector["provider_edge"],
            {"offset": 0x12, "target_address": 0x004156AC},
        )
        self.assertEqual(selector["main_analogue"], 0x005A4334)
        self.assertEqual(selector["identical_main_bytes"], 384)
        self.assertEqual(selector["transition_table_address"], 0x00433498)
        self.assertEqual(selector["valid_state_pairs_tested"], 400)

    def test_spotmgr_temperature_transition_dispatcher_is_exact(self) -> None:
        dispatcher = self.result["admission"][
            "spotmgr_temperature_transition_separate"
        ]
        self.assertEqual(dispatcher["start"], 0x0042A43A)
        self.assertEqual(dispatcher["end_exclusive"], 0x0042A4BC)
        self.assertEqual(
            dispatcher["source_bytes_by_profile"],
            {"apple-clang": 130, "linux-clang": 130},
        )
        self.assertEqual(dispatcher["direct_call_sites"], [0x0042A4F2, 0x0042A518])
        self.assertEqual(
            dispatcher["provider_edges"],
            [
                {"offset": 0x28, "target_address": 0x0042A2B4},
                {"offset": 0x58, "target_address": 0x0042A2B4},
            ],
        )
        self.assertEqual(dispatcher["callback_table_pointer"], 0x20000158)
        self.assertEqual(dispatcher["main_analogue"], 0x005A44BA)
        self.assertEqual(dispatcher["identical_main_bytes"], 126)

    def test_spotmgr_power_trims_router_is_exact(self) -> None:
        router = self.result["admission"]["spotmgr_power_trims_update"]
        self.assertEqual(router["start"], 0x0042A4BC)
        self.assertEqual(router["end_exclusive"], 0x0042A546)
        self.assertEqual(
            router["source_bytes_by_profile"],
            {"apple-clang": 138, "linux-clang": 138},
        )
        self.assertEqual(router["direct_call_sites"], [0x0042AB52])
        self.assertEqual(len(router["provider_edges"]), 4)
        self.assertEqual(router["callback_table_pointer"], 0x20000158)
        self.assertEqual(router["main_analogue"], 0x005A453C)
        self.assertEqual(router["identical_main_bytes"], 136)
        self.assertEqual(router["routes_tested"], 800)

    def test_spotmgr_power_state_classifier_is_exact(self) -> None:
        classifier = self.result["admission"]["spotmgr_power_state_determine"]
        self.assertEqual(classifier["start"], 0x0042A550)
        self.assertEqual(classifier["end_exclusive"], 0x0042A85E)
        self.assertEqual(
            classifier["source_bytes_by_profile"],
            {"apple-clang": 782, "linux-clang": 782},
        )
        self.assertEqual(classifier["direct_call_sites"], [0x0042AB2A])
        self.assertEqual(classifier["provider_edges"], [])
        self.assertEqual(len(classifier["shared_literals"]), 8)
        self.assertEqual(classifier["main_analogue"], 0x005A45D0)
        self.assertEqual(classifier["identical_main_bytes"], 750)
        self.assertEqual(classifier["host_cases_tested"], 40_960)

    def test_spotmgr_dispatch_entries_hidden_in_mixed_span_are_exact(self) -> None:
        update = self.result["admission"]["spotmgr_power_state_update"]
        self.assertEqual((update["start"], update["end_exclusive"]),
                         (0x0042A878, 0x0042AB6E))
        self.assertEqual(update["source_bytes_by_profile"],
                         {"apple-clang": 758, "linux-clang": 758})
        self.assertEqual(update["dispatch_pointer_site"], 0x0041D150)
        self.assertEqual(len(update["provider_edges"]), 6)
        profile = self.result["admission"]["spotmgr_profile_apply"]
        self.assertEqual((profile["start"], profile["end_exclusive"]),
                         (0x0042AB7C, 0x0042ABB2))
        self.assertEqual(profile["source_bytes_by_profile"],
                         {"apple-clang": 54, "linux-clang": 54})
        self.assertEqual(profile["dispatch_pointer_site"], 0x0041D158)
        initializer = self.result["admission"]["spotmgr_init"]
        self.assertEqual((initializer["start"], initializer["end_exclusive"]),
                         (0x0042ABBC, 0x0042AC4E))
        self.assertEqual(initializer["source_bytes_by_profile"],
                         {"apple-clang": 146, "linux-clang": 146})
        self.assertEqual(initializer["dispatch_pointer_site"], 0x0041D14C)
        self.assertEqual(len(initializer["provider_edges"]), 4)
        temperature = self.result["admission"]["spotmgr_temperature_init"]
        self.assertEqual((temperature["start"], temperature["end_exclusive"]),
                         (0x0042AC54, 0x0042ACA4))
        self.assertEqual(temperature["dispatch_pointer_site"], 0x0041D154)
        self.assertEqual(len(temperature["provider_edges"]), 3)
        ranges = self.result["admission"]["spotmgr_temperature_range"]
        self.assertEqual(ranges["main_analogue"], 0x005A0A70)
        self.assertEqual(ranges["direct_call_sites"], [0x0042BB68])
        trims = self.result["admission"]["spotmgr_trim_helpers"]
        self.assertEqual([item["source_bytes_by_profile"]["apple-clang"]
                          for item in trims], [108, 72, 48])
        self.assertEqual([item["main_analogue"] for item in trims],
                         [0x005A0AE8, 0x005A0B54, 0x005A0B9C])
        commit = self.result["admission"]["spotmgr_trim_commit"]
        self.assertEqual((commit["start"], commit["end_exclusive"]),
                         (0x0042AE9C, 0x0042AEEC))
        self.assertEqual(commit["source_bytes_by_profile"],
                         {"apple-clang": 80, "linux-clang": 80})
        self.assertEqual(commit["dispatch_pointer_site"], 0x0041D17C)
        self.assertEqual(len(commit["provider_edges"]), 4)

    def test_queue_family_is_source_routed_with_exact_abi_and_callers(self) -> None:
        queue = self.result["admission"]["queue_family"]
        self.assertEqual(queue["abi_bytes"], 24)
        self.assertEqual(queue["critical_provider"], 0x0041B8EC)
        self.assertEqual(
            queue["upstream_source_sha256"],
            "2ca55e34d5b9d4843e32ce0ab24e312bde580716c708c7f017adcd0a12dbd1e4",
        )
        functions = queue["functions"]
        self.assertEqual(functions["queue_init"]["stock_bytes"], 24)
        self.assertEqual(functions["queue_item_add"]["stock_bytes"], 94)
        self.assertEqual(functions["queue_item_get"]["stock_bytes"], 90)
        self.assertEqual(
            functions["queue_init"]["direct_call_sites"],
            [0x00422E04, 0x00422E20],
        )
        self.assertEqual(
            functions["queue_item_add"]["source_cave_bytes_by_profile"],
            {"apple-clang": 88, "linux-clang": 88},
        )
        self.assertEqual(
            functions["queue_item_get"]["source_cave_bytes_by_profile"],
            {"apple-clang": 86, "linux-clang": 86},
        )

    def test_memmove_is_source_routed_with_overlap_and_provider_topology(self) -> None:
        memmove = self.result["admission"]["memmove"]
        self.assertEqual(memmove["stock_bytes"], 150)
        self.assertEqual(memmove["source_cave_start"], 0x004276C0)
        self.assertEqual(
            memmove["source_cave_bytes_by_profile"],
            {"apple-clang": 50, "linux-clang": 50},
        )
        self.assertEqual(memmove["direct_call_sites"], [0x0042395A])
        self.assertEqual(memmove["copy_provider"], 0x0041568C)
        self.assertEqual(memmove["main_analogue"], 0x00439710)
        self.assertEqual(memmove["identical_bytes"], 146)
        self.assertEqual(memmove["alignment_bytes"], 2)

    def test_cmdq_update_indices_is_source_routed_with_exact_epoch_semantics(self) -> None:
        update = self.result["admission"]["cmdq_update_indices"]
        self.assertEqual(update["stock_bytes"], 64)
        self.assertEqual(update["source_cave_start"], 0x00427758)
        self.assertEqual(
            update["source_cave_bytes_by_profile"],
            {"apple-clang": 44, "linux-clang": 44},
        )
        self.assertEqual(
            update["direct_call_sites"],
            [0x00427944, 0x00427A7C, 0x00427AF2],
        )
        self.assertEqual(update["critical_provider"], 0x0041B8EC)
        self.assertEqual(update["main_analogue"], 0x00538D18)
        self.assertEqual(update["identical_bytes"], 61)
        self.assertEqual(
            update["upstream_source_sha256"],
            "60aa2126ca01cd72f746a92d6f34a13e909fdab24ebfab6d6b0a70b026d8fa83",
        )

    def test_cmdq_public_services_are_dual_profile_in_place_source(self) -> None:
        services = self.result["admission"]["cmdq_public_services"]
        self.assertEqual(len(services), 11)
        self.assertEqual(sum(item["source_bytes_by_profile"]["apple-clang"]
                             for item in services), 1_056)
        self.assertEqual(sum(item["retained_unreachable_tail_bytes"]
                             for item in services), 204)
        self.assertEqual(services[0]["start"], 0x00427794)
        self.assertEqual(services[-1]["stock_end_exclusive"], 0x00427C80)
        self.assertEqual(
            services[3]["direct_call_sites"],
            [0x00425D8A, 0x00425E26, 0x00425FDA],
        )
        self.assertEqual(services[6]["source_bytes_by_profile"],
                         {"apple-clang": 104, "linux-clang": 108})

    def test_syspll_lock_wait_is_source_routed_with_exact_poll_contract(self) -> None:
        lock_wait = self.result["admission"]["syspll_lock_wait"]
        self.assertEqual(lock_wait["stock_bytes"], 102)
        self.assertEqual(lock_wait["source_cave_start"], 0x00427528)
        self.assertEqual(
            lock_wait["source_cave_bytes_by_profile"],
            {"apple-clang": 88, "linux-clang": 88},
        )
        self.assertEqual(lock_wait["direct_call_sites"], [0x00422202])
        self.assertEqual(
            lock_wait["provider_edges"],
            [{"offset": 0x60, "target_address": 0x0041D246}],
        )
        self.assertEqual(lock_wait["handle_magic"], 0x01504C30)
        self.assertEqual(lock_wait["pllctl0_address"], 0x400204D8)
        self.assertEqual(lock_wait["plldiv1_address"], 0x400204E0)
        self.assertEqual(lock_wait["pllstat_address"], 0x400204E4)
        self.assertEqual(lock_wait["main_analogue"], 0x00539B56)
        self.assertEqual(lock_wait["identical_bytes"], 96)

    def test_cli_is_machine_readable_and_software_only(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["hardware_validation"], "blocked by unavailable physical evidence")
        self.assertEqual(result["hardware_operations"], [])
        self.assertNotIn("flashing", result)


if __name__ == "__main__":
    unittest.main()
