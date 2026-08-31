# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/analyze_g2_liblc3_service_audio_route.py"
SPEC = importlib.util.spec_from_file_location("g2_liblc3_service_route", TOOL)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Liblc3ServiceAudioRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = MODULE.read_json(MODULE.CONFIG)
        cls.image = MODULE.resolve(
            cls.config["stock_evidence"]["official_component"]["path"]
        ).read_bytes()
        cls.report = MODULE.analyze()

    def test_exact_stock_entries_and_complete_context_ingress(self) -> None:
        stock = self.report["stock_abi"]
        self.assertEqual(
            [(row["address"], row["size"]) for row in stock["entries"]],
            [(0x0057A926, 26), (0x0057A940, 568)])
        self.assertEqual(stock["whole_image_setup_ingress_count"], 4)
        self.assertEqual(stock["whole_image_encode_ingress_count"], 5)
        self.assertEqual(
            [row["start"] for row in stock["contexts"]],
            [0x20106A7C, 0x201074C0, 0x20107F04, 0x20108948])
        self.assertTrue(stock["contexts_nonoverlapping"])
        self.assertEqual(stock["context_total_bytes"], 10512)

    def test_transition_contract_is_one_way_bounded_and_alias_safe(self) -> None:
        contract = self.report["transition_contract"]
        self.assertEqual(contract["stock_configuration_bytes_copied_before_transition"], 24)
        self.assertEqual(contract["stock_encoder_pointer_offset"], 24)
        self.assertTrue(contract["stock_encoder_pointer_must_be_zero"])
        self.assertTrue(contract["one_way_lazy_transition"])
        self.assertTrue(contract["explicit_stock_setup_resets_codec"])
        self.assertTrue(contract["failed_setup_restores_stock_header"])
        self.assertFalse(contract["plan_query_reinitializes_encoder"])
        self.assertTrue(contract["completed_prefix_preserved_on_provider_failure"])
        self.assertTrue(contract["state_pcm_output_and_count_aliases_rejected"])

    def test_dual_profiles_reproduce_and_replay_every_relocation(self) -> None:
        for profile in self.report["profiles"].values():
            self.assertTrue(profile["byte_reproducible_two_builds"])
            self.assertTrue(profile["all_relocations_applied_at_synthetic_layout"])
            self.assertEqual(profile["sections"]["table_rodata"]["size"], 404)
            self.assertEqual(len(profile["imports"]), 11)
            self.assertEqual(len(profile["entry_veneers"]), 2)
            self.assertTrue(all(row["kind"] == "Thumb-2 B.W tail branch"
                                for row in profile["entry_veneers"]))

    def test_capacity_and_routing_remain_fail_closed(self) -> None:
        self.assertEqual(
            self.report["profiles"]["apple-clang"]["capacity"]["shortfall"],
            34084)
        self.assertEqual(
            self.report["profiles"]["linux-clang"]["capacity"]["shortfall"],
            35204)
        routing = self.report["routing"]
        self.assertFalse(routing["production_patch_bytes_emitted"])
        self.assertFalse(routing["production_placement"])
        self.assertFalse(routing["service_audio_routed"])
        self.assertFalse(routing["firmware_image_emitted"])
        self.assertFalse(routing["hardware_operations"])

    def test_hostile_stock_entry_ingress_and_context_drift_reject(self) -> None:
        mutations = []
        wrong_entry = copy.deepcopy(self.config["stock_evidence"])
        wrong_entry["entries"][0]["prologue_hex"] = "00000000"
        mutations.append(wrong_entry)
        missing_ingress = copy.deepcopy(self.config["stock_evidence"])
        missing_ingress["ingress"]["SVC_Lc3EncodeMono"].pop()
        mutations.append(missing_ingress)
        wrong_context = copy.deepcopy(self.config["stock_evidence"])
        wrong_context["context_literal_cells"][0]["context_index"] = 1
        mutations.append(wrong_context)
        overlap = copy.deepcopy(self.config["stock_evidence"])
        overlap["contexts"][1] -= 4
        mutations.append(overlap)
        wrong_pointer = copy.deepcopy(self.config["stock_evidence"])
        wrong_pointer["stock_encoder_pointer_offset"] = 20
        mutations.append(wrong_pointer)
        for mutation in mutations:
            with self.subTest(mutation=mutations.index(mutation)):
                with self.assertRaises(MODULE.RouteAuditError):
                    MODULE.validate_stock_evidence(mutation, self.image)

    def test_hostile_production_promotion_and_source_pin_reject(self) -> None:
        promoted = copy.deepcopy(self.config)
        promoted["routing"]["service_audio_routed"] = True
        with self.assertRaises(MODULE.RouteAuditError):
            MODULE.validate_static_config(promoted)
        wrong_source = copy.deepcopy(self.config)
        wrong_source["sources"]["shim"]["sha256"] = "0" * 64
        with self.assertRaises(MODULE.RouteAuditError):
            MODULE.validate_static_config(wrong_source)


if __name__ == "__main__":
    unittest.main()
