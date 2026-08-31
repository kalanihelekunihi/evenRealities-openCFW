#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Regression tests for the fail-closed CFF placement/link census."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
TOOL = G2 / "tools/analyze_g2_freetype_cff_placement_link.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-placement-link.json"
PROVIDER = (
    G2 / "components/shared/freetype_cff/runtime_freetype_cff_import_providers.c"
)
HOST_FIXTURE = G2 / "tests/fixtures/freetype_cff_import_providers_host.c"


def load_tool():
    spec = importlib.util.spec_from_file_location(
        "g2_freetype_cff_placement_link_test", TOOL
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeTypeCffPlacementLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_tool()
        cls.report = cls.module.analyze()

    def test_dual_profile_sections_exports_imports_and_relocations_are_exact(self) -> None:
        profiles = self.report["deterministic_link"]["profiles"]
        expected = {
            "apple-clang": {
                "sections": (20_718, 680, 4_918, 0, 0),
                "span": 26_318,
                "relocations": (610, 355, 255),
                "link_sha256": (
                    "371e7af55006fae42b100ae535bed45ebf6b695c5fff2c6e5075b40bcd79f137"
                ),
            },
            "linux-clang": {
                "sections": (20_650, 680, 4_918, 0, 0),
                "span": 26_250,
                "relocations": (608, 353, 255),
                "link_sha256": (
                    "49768aa0410f7a54c704c8cb722b8840cb090871bb2bce77e07410546d4d6c24"
                ),
            },
        }
        for name, profile in profiles.items():
            sections = profile["sections"]
            self.assertEqual(
                tuple(sections[key]["size"] for key in (
                    "text", "arm_exidx", "rodata", "data", "bss"
                )),
                expected[name]["sections"],
            )
            self.assertEqual(
                profile["required_aligned_flash_span"], expected[name]["span"]
            )
            relocations = profile["relocations"]
            self.assertEqual(
                (relocations["total"], relocations["internal"],
                 relocations["external"]),
                expected[name]["relocations"],
            )
            self.assertEqual(
                profile["objects"]["relocatable_link"]["sha256"],
                expected[name]["link_sha256"],
            )
            self.assertEqual(len(profile["imports"]), 45)
            self.assertEqual(len(profile["required_exports"]), 7)
            self.assertIn("cff_driver_class", profile["defined_global_symbols"])
            self.assertEqual(profile["static_ram_bytes"], 0)

    def test_final_links_close_every_import_and_relocation(self) -> None:
        profiles = self.report["deterministic_link"]["profiles"]
        expected = {
            "apple-clang": (624, 412, 212, 26_794,
                            "09c131cce2987d9689fbacf652f5e07f3df2e570db208531b8c0e621a5c2f09e"),
            "linux-clang": (622, 410, 212, 26_726,
                            "ec4c7c35dd797440bd41f4c19f21d8dacaab4c2826d24fe382a437e95d7c3f37"),
        }
        for name, profile in profiles.items():
            closure = profile["provider_closure"]
            final = profile["finalized"]
            self.assertEqual(
                (closure["relocations"]["total"],
                 closure["relocations"]["internal"],
                 closure["relocations"]["external"]),
                expected[name][:3],
            )
            self.assertEqual(closure["source_owned_original_relocations"], 43)
            self.assertEqual(closure["retained_original_relocations"], 212)
            self.assertEqual(profile["relocations"]["external"], 255)
            self.assertEqual(final["undefined_symbols"], [])
            self.assertEqual(final["relocations"]["total"], 0)
            self.assertEqual(profile["objects"]["final_binary"], {
                "size": expected[name][3], "sha256": expected[name][4],
            })

    def test_candidate_flash_fits_but_current_flash_plan_conflicts(self) -> None:
        capacity = self.report["capacity"]
        self.assertEqual(capacity["authenticated_current_flash_interval"], {
            "start": 0x007ECA44,
            "end_exclusive": 0x007FE000,
            "bytes": 71_100,
            "authority": (
                "canonical core artifact end plus package-protected update record"
            ),
        })
        self.assertEqual(
            capacity["profiles"]["apple-clang"]["remaining_bytes"], 44_306
        )
        self.assertEqual(
            capacity["profiles"]["linux-clang"]["remaining_bytes"], 44_374
        )
        self.assertEqual(self.report["imports"]["authenticated_retained_count"], 35)
        self.assertEqual(self.report["imports"]["source_owned_count"], 10)
        self.assertEqual(self.report["imports"]["source_owned_bindings"], [
            "FT_Property_Get", "FT_Property_Set", "FT_Stream_Pos",
            "memcmp", "memcpy", "memset", "strcmp", "strlen", "strncmp",
            "strstr",
        ])
        self.assertEqual(self.report["imports"]["unresolved"], [])
        plan = self.report["flash_plan"]
        self.assertEqual(plan["candidate_interval_overlap_regions"], 477)
        self.assertEqual(plan["candidate_interval_occupied_bytes"], 66_678)
        self.assertEqual(plan["planned_apollo_end_exclusive"], 0x007FCEBA)
        self.assertEqual(plan["bytes_before_update_record"], 4_422)
        self.assertEqual(plan["profiles"]["apple-clang"]["shortfall"], 22_372)
        self.assertEqual(plan["profiles"]["linux-clang"]["shortfall"], 22_304)
        self.assertFalse(self.report["routing"]["production_route_feasible_now"])
        self.assertFalse(self.report["routing"]["firmware_image_emitted"])

    def test_minimal_registration_consumer_contract_is_bounded(self) -> None:
        contract = self.report["minimal_registration_consumer_contract"]
        self.assertEqual(contract["stock_default_module_table"], "0x0073EEF8")
        self.assertEqual(contract["cff_slot_address"], "0x0073EF00")
        self.assertEqual(contract["stock_cff_driver_class"], "0x006DCB74")
        self.assertEqual(contract["required_replacement_symbol"], "cff_driver_class")
        self.assertEqual(contract["required_pointer_patch_count"], 1)
        self.assertEqual(contract["expected_stock_little_endian_hex"], "74cb6d00")
        self.assertEqual(
            contract["profile_replacements"]["apple-clang"]
            ["replacement_little_endian_hex"], "d4207f00"
        )
        self.assertEqual(
            contract["profile_replacements"]["linux-clang"]
            ["replacement_little_endian_hex"], "90207f00"
        )
        self.assertEqual(contract["retained_lvgl_consumer_patch_count"], 0)
        self.assertEqual(len(self.report["blockers"]), 3)
        self.assertFalse(self.report["evidence_bounds"]["production_placement_claimed"])
        self.assertFalse(self.report["evidence_bounds"]["hardware_validation_performed"])

    def test_source_owned_import_providers_execute_on_host(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-cff-provider-host-") as d:
            output = Path(d) / "provider-host"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-O2", "-fno-builtin",
                "-Wall", "-Wextra", "-Werror", "-DFT2_BUILD_LIBRARY",
                "-I", str(G2 / "research/candidates/freetype/g2_config"),
                "-I", str(G2 / "third_party/freetype/g2-config"),
                "-I", str(G2 / "third_party/freetype/include"),
                "-I", str(G2 / "third_party/freetype"),
                "-I", str(G2 / "components/shared/freetype_cff"),
                str(PROVIDER), str(HOST_FIXTURE), "-o", str(output),
            ], check=True, capture_output=True, text=True)
            subprocess.run([str(output)], check=True)

    def test_checked_in_manifest_and_cli_are_deterministic(self) -> None:
        self.assertEqual(json.loads(MANIFEST.read_text()), self.report)
        result = subprocess.run(
            [sys.executable, str(TOOL), "--check-manifest"],
            cwd=G2, check=True, capture_output=True, text=True,
        )
        self.assertEqual(json.loads(result.stdout), self.report)

    def test_hostile_base_map_and_capacity_receipt_mutations_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-cff-placement-hostile-") as d:
            temporary = Path(d)
            base = temporary / "base-map.json"
            base_data = json.loads(self.module.BASE_MAP.read_text())
            base_data["functions"][0]["symbol"] = "hostile_symbol"
            base.write_text(json.dumps(base_data), encoding="utf-8")
            original_base = self.module.BASE_MAP
            self.module.BASE_MAP = base
            try:
                with self.assertRaisesRegex(
                    self.module.PlacementError, "base-map pin drift"
                ):
                    self.module._base_bindings(set(
                        self.report["deterministic_link"]["profiles"]
                        ["apple-clang"]["imports"]
                    ))
            finally:
                self.module.BASE_MAP = original_base

            config = temporary / "overlay.json"
            config_data = json.loads(self.module.CORE_CONFIG.read_text())
            config_data["profiles"]["apple-clang"]["base_component"]["size"] -= 1
            config.write_text(json.dumps(config_data), encoding="utf-8")
            with self.assertRaisesRegex(
                self.module.PlacementError, "component receipt drift"
            ):
                self.module._capacity(
                    self.report["deterministic_link"]["profiles"],
                    core_config_path=config,
                    core_artifact_path=self.module.CORE_ARTIFACT,
                )

            flash_plan = temporary / "flash-plan.json"
            flash_plan_data = bytearray(self.module.FLASH_PLAN.read_bytes())
            flash_plan_data[100] ^= 1
            flash_plan.write_bytes(flash_plan_data)
            original_plan = self.module.FLASH_PLAN
            self.module.FLASH_PLAN = flash_plan
            try:
                with self.assertRaisesRegex(
                    self.module.PlacementError, "flash-plan receipt drift"
                ):
                    self.module._flash_plan(
                        self.report["deterministic_link"]["profiles"]
                    )
            finally:
                self.module.FLASH_PLAN = original_plan


if __name__ == "__main__":
    unittest.main()
