#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Regression tests for the fail-closed CFF flash-capacity solver."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
TOOL = G2 / "tools/analyze_g2_freetype_cff_capacity_solver.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-capacity-solver.json"


def load_tool():
    spec = importlib.util.spec_from_file_location(
        "g2_freetype_cff_capacity_solver_test", TOOL
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeTypeCffCapacitySolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_tool()
        cls.report = cls.module.analyze()

    def test_all_477_current_package_regions_are_closed(self) -> None:
        package = self.report["current_package"]
        self.assertEqual(package["apollo_payload_bytes"], 3_952_346)
        self.assertEqual(
            package["apollo_payload_sha256"],
            "dc578472f06af2d499b9cb771fc185df4f739a05de558098088b56da9a5e4ce0",
        )
        self.assertTrue(package["all_477_artifacts_match_package"])
        interval = self.report["candidate_interval"]
        self.assertEqual(interval["occupied_regions"], 477)
        self.assertEqual(interval["occupied_bytes"], 66_678)
        self.assertEqual(interval["directly_free_tail_bytes"], 4_422)
        self.assertEqual(interval["classification_bytes"], {
            "generated_alignment": 302,
            "source_compiled": 66_376,
        })
        self.assertEqual(interval["classification_full_row_bytes"], {
            "generated_alignment": 302,
            "source_compiled": 66_524,
        })
        self.assertEqual(interval["family_rows"], {
            "ambiqsuite": 82, "cordio": 333, "iar": 2,
            "s200": 8, "service": 52,
        })
        self.assertEqual(interval["family_bytes"], {
            "ambiqsuite": 16_274, "cordio": 38_988, "iar": 9_166,
            "s200": 588, "service": 1_662,
        })
        self.assertEqual(len(interval["regions"]), 477)
        self.assertTrue(all(
            row["artifact_and_package_bytes_match"] and
            not row["directly_reclaimable"]
            for row in interval["regions"]
        ))

    def test_optimistic_reclaim_bound_still_cannot_fit(self) -> None:
        reclaim = self.report["reclaim_audit"]
        self.assertEqual(reclaim["directly_reclaimable"]["bytes"], 0)
        self.assertEqual(reclaim["repack_only_generated_alignment"]["bytes"], 302)
        conditional = reclaim["conditionally_superseded_stock_cff"]
        self.assertEqual(conditional["callable_physical_envelope"]["bytes"], 16_924)
        self.assertEqual(
            conditional["authenticated_table_and_callback_words"]["bytes"], 364
        )
        self.assertEqual(
            conditional["authenticated_table_and_callback_words"]
            ["bytes_already_inside_callable_physical_envelope"], 4
        )
        self.assertEqual(
            conditional["authenticated_table_and_callback_words"]
            ["unique_bytes_beyond_callable_physical_envelope"], 360
        )
        self.assertEqual(conditional["bytes"], 17_284)
        self.assertFalse(conditional["currently_reclaimable"])
        bound = reclaim["optimistic_known_capacity_upper_bound"]
        self.assertEqual(bound["total"], 22_008)
        self.assertFalse(bound["feasible_for_any_profile"])
        self.assertEqual(
            self.report["minimal_blocker_set"]
            ["residual_after_all_known_optimistic_capacity"],
            {"apple-clang": 4_786, "linux-clang": 4_718},
        )

    def test_minimal_live_blockers_are_exact(self) -> None:
        expected_regions = [
            "ambiqsuite_ancc_profile_open-cfw-ancc-dispatch_source_text",
            "iar_format_input_source_closure",
            "iar_format_output_source_closure",
            "cordio_hci_evt_hciEvtProcessCmdCmpl_source_text",
        ]
        expected = {
            "apple-clang": (26_794, 22_372, 4_786),
            "linux-clang": (26_726, 22_304, 4_718),
        }
        for name, profile in self.report["profiles"].items():
            self.assertEqual(
                (profile["required_payload_bytes"], profile["current_shortfall"],
                 profile["shortfall_even_after_optimistic_upper_bound"]),
                expected[name],
            )
            lower = profile["byte_capacity_lower_bound"]
            self.assertEqual(
                lower["minimum_distinct_live_source_rows_by_byte_capacity"], 4
            )
            self.assertEqual(lower["selected_live_source_bytes"], 22_814)
            self.assertEqual([row["region"] for row in lower["rows"]], expected_regions)
            suffix = profile["contiguous_final_binary_blocker"]
            self.assertEqual(suffix["minimal_whole_region_suffix_start"], "0x007F7060")
            self.assertEqual(suffix["minimal_whole_region_suffix_rows"], 171)
            self.assertEqual(suffix["source_compiled_rows"], 121)
            self.assertEqual(suffix["generated_alignment_rows"], 50)
            self.assertEqual(suffix["occupied_bytes_that_require_displacement"], 24_154)
            self.assertEqual(suffix["first_live_region"], "iar_format_output_source_closure")
            self.assertTrue(suffix["contains_live_ancc_dispatch"])
            self.assertFalse(profile["placement_feasible"])

    def test_protected_boundary_and_route_remain_closed(self) -> None:
        self.assertEqual(self.report["protected_boundary"], {
            "start": "0x007FE000",
            "end_exclusive": "0x007FE010",
            "policy": "bootloader_owned_do_not_include_in_application_image",
            "reclaimable": False,
        })
        self.assertEqual(self.report["routing"], {
            "production_placement_feasible": False,
            "production_scatter_feasible": False,
            "module_class_pointer_patch_permitted": False,
            "firmware_image_emitted": False,
        })
        bounds = self.report["evidence_bounds"]
        self.assertFalse(bounds["conditional_capacity_counted_as_writable"])
        self.assertFalse(bounds["production_placement_claimed"])
        self.assertFalse(bounds["production_routing_claimed"])
        self.assertFalse(bounds["hardware_validation_performed"])

    def test_whole_address_space_and_scatter_bounds_are_exact(self) -> None:
        whole = self.report["whole_address_space"]
        application = whole["apollo_application"]
        self.assertEqual(application["rows"], 6_120)
        self.assertEqual(application["installed_bytes"], 3_952_314)
        self.assertEqual(application["internal_free_gaps"], 0)
        self.assertTrue(application["vector_and_first_region_occupied"])
        self.assertEqual(application["unproven_source_replaced_caves_admitted"], 0)
        self.assertEqual(application["row_status_counts"], {
            "generated_alignment": 897,
            "generated_source_data_replacement": 123,
            "generated_source_entry_replacement": 2_291,
            "generated_source_exact_load_image": 1,
            "generated_source_exact_replacement": 7,
            "official_blob": 810,
            "source_compiled": 1_989,
            "source_compiled_rodata": 2,
        })
        self.assertEqual(application["byte_status_counts"], {
            "generated_alignment": 1_888,
            "generated_source_data_replacement": 2_200,
            "generated_source_entry_replacement": 397_760,
            "generated_source_exact_load_image": 6,
            "generated_source_exact_replacement": 134,
            "official_blob": 3_123_044,
            "source_compiled": 425_682,
            "source_compiled_rodata": 1_600,
        })
        self.assertEqual(whole["even_bootloader"]["rows"], 330)
        self.assertEqual(whole["bootloader_partition_headroom"], {
            "start": "0x004368E0",
            "end_exclusive": "0x00438000",
            "bytes": 5_920,
            "classification": "outside-apollo-application-package-entry",
            "physically_empty_in_pinned_package": True,
            "application_placement_authority": False,
        })
        self.assertEqual(whole["legal_application_gap_count"], 1)
        self.assertEqual(whole["legal_application_gap_bytes"], 4_422)
        self.assertEqual(whole["physical_gap_count_below_update_record"], 2)
        self.assertEqual(whole["physical_gap_bytes_below_update_record"], 10_342)
        self.assertTrue(
            self.report["current_package"]
            ["all_6120_application_and_330_boot_rows_match_package"]
        )

        scatter = self.report["scatter_placement"]
        self.assertEqual(scatter["legal_application_capacity_upper_bound"], 21_706)
        self.assertEqual(scatter["relocation_forms"], [
            "R_ARM_ABS32", "R_ARM_PREL31", "R_ARM_THM_CALL",
            "R_ARM_THM_JUMP24", "R_ARM_THM_MOVT_ABS",
            "R_ARM_THM_MOVW_ABS_NC",
        ])
        self.assertEqual(scatter["widest_hypothetical_binding_domain_bytes"], 3_958_234)
        self.assertTrue(scatter["relocation_encodings_range_compatible"])
        self.assertTrue(scatter["data_pointer_encoding_range_compatible"])
        self.assertFalse(scatter["exact_scatter_link_attempted"])
        self.assertFalse(scatter["production_scatter_feasible"])
        expected = {
            "apple-clang": (26_780, 5_074, 5_088, 462),
            "linux-clang": (26_712, 5_006, 5_020, 530),
        }
        for name, values in scatter["profile_results"].items():
            minimum, minimum_short, binary_short, margin = expected[name]
            self.assertEqual(profile := values["minimum_loadable_section_bytes"], minimum)
            self.assertGreater(profile, scatter["legal_application_capacity_upper_bound"])
            self.assertEqual(values["legal_application_minimum_shortfall"], minimum_short)
            self.assertEqual(values["legal_application_final_binary_shortfall"], binary_short)
            hypothetical = values["hypothetical_cross_component"]
            self.assertTrue(hypothetical["section_shape_fits"])
            self.assertFalse(hypothetical["legal_component_ownership"])
            self.assertEqual(hypothetical["text_margin"], margin)

        references = self.report["reclaim_audit"][
            "stock_cff_external_reference_audit"
        ]
        self.assertEqual(references["direct_external_cff_call_edges"], 0)
        self.assertEqual(references["pointer_like_words"], 62)
        self.assertEqual(references["distinct_cff_targets"], 58)
        self.assertEqual(references["classification_counts"], {
            "authenticated-callback-slot": 18,
            "authenticated-compact-table": 40,
            "inside-cff-envelope": 3,
            "outside-authenticated-cff-data": 1,
        })
        self.assertEqual(
            references["instruction_collision"]["containing_function"],
            "0x004CD3AA",
        )

    def test_checked_manifest_and_cli_are_deterministic(self) -> None:
        self.assertEqual(json.loads(MANIFEST.read_text()), self.report)
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--check-manifest"],
            cwd=G2, check=True, capture_output=True, text=True,
        )
        self.assertEqual(json.loads(completed.stdout), self.report)

    def test_hostile_dependency_receipts_fail_closed(self) -> None:
        paths = {
            "flash_plan_path": self.module.FLASH_PLAN,
            "build_report_path": self.module.BUILD_REPORT,
            "package_path": self.module.PACKAGE,
            "cff_map_path": self.module.CFF_MAP,
            "ghidra_path": self.module.GHIDRA,
            "placement_path": self.module.PLACEMENT,
        }
        with tempfile.TemporaryDirectory(prefix="opencfw-cff-capacity-hostile-") as d:
            root = Path(d)
            for argument, original in paths.items():
                mutated = root / original.name
                payload = bytearray(original.read_bytes())
                payload[len(payload) // 2] ^= 1
                mutated.write_bytes(payload)
                arguments = dict(paths)
                arguments[argument] = mutated
                with self.subTest(argument=argument):
                    with self.assertRaisesRegex(
                        self.module.CapacityError, "input pin drift"
                    ):
                        self.module.analyze(**arguments)

    def test_hostile_artifact_and_interval_mutations_fail_closed(self) -> None:
        plan = json.loads(self.module.FLASH_PLAN.read_text())
        component_rows = [
            row for row in plan["flash_regions"]
            if row.get("component") in {"apollo_main", "apollo_bootloader"} and
            row.get("target") == "apollo510b_internal_mram"
        ]
        candidate_rows = [
            row for row in plan["flash_regions"]
            if row.get("component") == "apollo_main" and
            row["end_exclusive"] > self.module.CANDIDATE[0] and
            row["target_address"] < self.module.CANDIDATE[1]
        ]
        with tempfile.TemporaryDirectory(prefix="opencfw-cff-capacity-artifact-") as d:
            root = Path(d)
            for row in component_rows:
                source = self.module.ARTIFACT_ROOT / row["artifact"]
                target = root / row["artifact"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            hostile = root / candidate_rows[0]["artifact"]
            payload = bytearray(hostile.read_bytes())
            payload[0] ^= 1
            hostile.write_bytes(payload)
            with self.assertRaisesRegex(
                self.module.CapacityError, "component artifact/package drift"
            ):
                self.module.analyze(artifact_root=root)

        ordered = sorted(candidate_rows, key=lambda row: row["target_address"])
        hostile_rows = [dict(row) for row in ordered]
        hostile_rows[1]["target_address"] += 2
        with self.assertRaisesRegex(
            self.module.CapacityError, "unexpected free gap or overlap"
        ):
            self.module.validate_contiguous(
                hostile_rows, self.module.CANDIDATE[0], 0x007FCEBA
            )


if __name__ == "__main__":
    unittest.main()
