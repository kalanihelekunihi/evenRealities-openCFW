#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Regression tests for the fail-closed CFF size experiment."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
TOOL = G2 / "tools/analyze_g2_freetype_cff_size_optimization.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-size-optimization.json"
CFF_MAP = G2 / "tools/manifests/g2-freetype-cff-function-map.json"


def load_tool():
    spec = importlib.util.spec_from_file_location("g2_cff_size_opt_test", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeTypeCffSizeOptimizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_tool()
        cls.report = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_complete_source_policy_and_public_roots_are_unchanged(self) -> None:
        source = self.report["source_and_policy"]
        self.assertEqual(source["complete_stock_map"], {
            "functions": 101,
            "callable_bytes": 16_718,
            "physical_bytes": 16_924,
            "unresolved_callable_bytes": 0,
        })
        self.assertEqual(source["source_inventory"]["files"], 17)
        self.assertEqual(source["source_inventory"]["bytes"], 269_028)
        self.assertEqual(source["source_files_modified_for_optimization"], 0)
        self.assertEqual(source["preprocessor_definitions_added_for_optimization"], [])
        self.assertEqual(source["additional_source_branch_eliminations_admitted"], 0)
        candidate = self.report["selected_candidate"]
        self.assertEqual(candidate["name"], "size-oz")
        self.assertFalse(candidate["lto_used"])
        self.assertFalse(candidate["section_gc_used"])
        self.assertFalse(candidate["constant_merging_used"])
        self.assertFalse(candidate["abi_or_feature_definitions_changed"])
        self.assertEqual(candidate["public_exports"], [
            "cff_driver_class",
            "open_cfw_freetype_cff_get_darkening_parameters",
            "open_cfw_freetype_cff_get_hinting_engine",
            "open_cfw_freetype_cff_get_no_stem_darkening",
            "open_cfw_freetype_cff_set_darkening_parameters",
            "open_cfw_freetype_cff_set_hinting_engine",
            "open_cfw_freetype_cff_set_no_stem_darkening",
        ])
        self.assertEqual(candidate["complete_map_coverage"], {
            "source_functions": 101,
            "materialized_named_functions": 81,
            "inlined_only_functions": 20,
            "address_taken_callback_relocations": 58,
            "distinct_callback_targets": 55,
            "public_roots": 7,
            "rooted_section_gc_binary_is_byte_identical": True,
            "proof": (
                "clang inline remarks cover exactly the 20 nonmaterialized "
                "map names; all 81 emitted map functions survive GC rooted "
                "at cff_driver_class and the six adapter exports"
            ),
        })

        mapped = {
            row["symbol"]
            for row in json.loads(CFF_MAP.read_text(encoding="utf-8"))["functions"]
        }
        self.assertEqual(len(mapped), 101)
        for profile in candidate["profiles"].values():
            final = profile["final"]
            materialized = set(final["materialized_complete_map_symbol_names"])
            inlined = set(final["inlined_only_complete_map_symbol_names"])
            self.assertEqual((len(materialized), len(inlined)), (81, 20))
            self.assertTrue(materialized.isdisjoint(inlined))
            self.assertEqual(materialized | inlined, mapped)
            self.assertEqual(final["complete_map_source_behavior_covered"], 101)

    def test_dual_profile_oz_closes_only_the_byte_capacity_threshold(self) -> None:
        expected = {
            "apple-clang": {
                "sections": (15_482, 16, 4_918, 0, 0),
                "loadable": 20_416,
                "flat": 20_430,
                "margins": (1_290, 1_276),
                "binary_sha256": (
                    "f851e50ce0defa8bf3692addd785c12348cb8e310e20e950f1979b08b716b612"
                ),
                "relocations": (579, 132),
            },
            "linux-clang": {
                "sections": (15_430, 16, 4_918, 0, 0),
                "loadable": 20_364,
                "flat": 20_378,
                "margins": (1_342, 1_328),
                "binary_sha256": (
                    "4ed0d388d71c16017db60f18381bb89164759000620d97fee3ab738faeae85b6"
                ),
                "relocations": (576, 138),
            },
        }
        for name, profile in self.report["selected_candidate"]["profiles"].items():
            final = profile["final"]
            sections = final["sections"]
            self.assertEqual(
                tuple(sections[key]["size"] for key in (
                    "text", "arm_exidx", "rodata", "data", "bss"
                )),
                expected[name]["sections"],
            )
            self.assertEqual(final["loadable_bytes"], expected[name]["loadable"])
            self.assertEqual(final["flat_binary_bytes"], expected[name]["flat"])
            self.assertEqual(
                (final["legal_capacity_loadable_margin"],
                 final["legal_capacity_flat_binary_margin"]),
                expected[name]["margins"],
            )
            self.assertTrue(final["byte_capacity_fit"])
            self.assertEqual(final["undefined_symbols"], [])
            self.assertEqual(final["relocations"]["total"], 0)
            self.assertEqual(final["static_ram_bytes"], 0)
            self.assertEqual(
                profile["objects"]["final_binary"]["sha256"],
                expected[name]["binary_sha256"],
            )
            closure = profile["provider_closed"]
            self.assertEqual(
                (closure["relocations"]["total"],
                 closure["relocations"]["external"]),
                expected[name]["relocations"],
            )
            self.assertEqual(closure["import_count"], 36)

        self.assertEqual(self.report["routing"], {
            "byte_capacity_threshold_closed": True,
            "exact_scatter_placement_proven": False,
            "production_route_permitted": False,
            "module_class_pointer_patch_permitted": False,
            "firmware_image_emitted": False,
        })

    def test_every_address_taken_callback_and_new_import_are_closed(self) -> None:
        provider = self.report["retained_compiler_runtime_provider"]
        self.assertEqual(provider["binding"], "0x00439BE4")
        self.assertEqual(provider["source_leaf"], "0x007C29F8")
        self.assertEqual(provider["source_leaf_bytes"], 152)
        self.assertTrue(provider["current_package_route_authenticated"])
        for profile in self.report["selected_candidate"]["profiles"].values():
            self.assertEqual(profile["source_callback_roots"], {
                "available_before_lto": True,
                "relocations": 58,
                "distinct_targets": 55,
                "records_sha256": (
                    "dd4e5d792b4ba5b5ca5e42c399b05b3a482b224d0166194ec65d9ef077199211"
                ),
            })
            helper = profile["compiler_runtime_import"]
            self.assertEqual(helper["binding"], "0x00439BE4")
            self.assertEqual(helper["source_relocations"], 1)
            self.assertEqual(helper["records"], [{
                "section": ".rel.text.cff_ps_get_font_info",
                "offset": 26,
                "type": "R_ARM_THM_CALL",
                "symbol": "__aeabi_memcpy",
            }])

    def test_os_gc_lto_and_constant_merging_are_bounded(self) -> None:
        variants = self.report["variants"]
        expected_loadable = {
            "baseline-o2": (26_780, 26_712),
            "size-os": (22_144, 22_368),
            "size-oz": (20_416, 20_364),
            "size-oz-gc": (20_416, 20_364),
            "size-oz-lto-gc": (20_252, 20_244),
            "size-oz-lto-gc-merge": (20_252, 20_244),
        }
        for variant, values in expected_loadable.items():
            profiles = variants[variant]["profiles"]
            self.assertEqual(
                (profiles["apple-clang"]["final"]["loadable_bytes"],
                 profiles["linux-clang"]["final"]["loadable_bytes"]),
                values,
            )
        conclusions = self.report["optimization_conclusions"]
        self.assertFalse(conclusions["os_closes_byte_capacity"])
        self.assertTrue(conclusions["oz_closes_byte_capacity"])
        self.assertEqual(
            conclusions["section_gc_additional_bytes_saved_after_complete_roots"], 0
        )
        self.assertTrue(conclusions["lto_closes_byte_capacity"])
        self.assertFalse(conclusions["lto_selected"])
        self.assertEqual(
            conclusions["constant_merging_additional_bytes_saved_after_lto"], 0
        )
        self.assertFalse(conclusions["source_level_feature_elimination_used"])

    def test_hostile_contract_and_input_mutations_fail_closed(self) -> None:
        for mutation in ("callback", "import", "capacity", "routing"):
            hostile = copy.deepcopy(self.report)
            profiles = hostile["selected_candidate"]["profiles"]
            if mutation == "callback":
                profiles["apple-clang"]["source_callback_roots"][
                    "distinct_targets"
                ] -= 1
            elif mutation == "import":
                profiles["linux-clang"]["compiler_runtime_import"][
                    "binding"
                ] = None
            elif mutation == "capacity":
                profiles["apple-clang"]["final"]["byte_capacity_fit"] = False
            else:
                hostile["routing"]["production_route_permitted"] = True
            with self.subTest(mutation=mutation):
                with self.assertRaises(self.module.OptimizationError):
                    self.module.validate_selected_contract(hostile)

        with tempfile.TemporaryDirectory(prefix="opencfw-cff-size-hostile-") as raw:
            changed = Path(raw) / "capacity.json"
            body = bytearray(self.module.CAPACITY.read_bytes())
            body[len(body) // 2] ^= 1
            changed.write_bytes(body)
            with self.assertRaisesRegex(
                self.module.OptimizationError, "input pin drift"
            ):
                self.module.analyze(input_overrides={
                    self.module.CAPACITY: changed,
                })

        with self.assertRaisesRegex(
            self.module.OptimizationError, "public export root set drift"
        ):
            self.module.analyze(required_exports=tuple(
                self.module.load_module(self.module.BUILDER).REQUIRED_EXPORTS[:-1]
            ))

    def test_checked_manifest_and_cli_are_deterministic(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--check-manifest"],
            cwd=G2, check=True, capture_output=True, text=True,
        )
        self.assertEqual(json.loads(completed.stdout), self.report)


if __name__ == "__main__":
    unittest.main()
