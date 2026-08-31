#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Regression tests for the exact CFF -Oz scatter relocation replay."""

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
TOOL = G2 / "tools/analyze_g2_freetype_cff_scatter_link.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-scatter-link.json"


def load_tool():
    spec = importlib.util.spec_from_file_location("g2_cff_scatter_test", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeTypeCffScatterLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_tool()
        cls.report = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_only_authenticated_same_entry_intervals_are_consumed(self) -> None:
        ownership = self.report["ownership"]
        self.assertEqual(ownership["conditional_stock_cff_envelope"], {
            "start": "0x005ABEF8",
            "end_exclusive": "0x005B0114",
            "bytes": 16_924,
            "sha256": (
                "58b8b5e4c1b801d7ac4c6883dc8afeccd7cf370e3e9cccdf95f938e20b91358b"
            ),
            "current_plan_owner": "official_blob",
            "replacement_condition": (
                "same-entry atomic module-class pointer replacement must make "
                "the old CFF class and callbacks unreachable"
            ),
        })
        self.assertEqual(ownership["direct_application_tail"], {
            "start": "0x007FCEBA",
            "end_exclusive": "0x007FE000",
            "bytes": 4_422,
            "current_plan_collision_rows": 0,
        })
        self.assertEqual(ownership["scattered_table_words_consumed"], 0)
        self.assertEqual(ownership["bootloader_partition_bytes_consumed"], 0)
        self.assertEqual(
            ownership["protected_update_record_bytes_consumed"], 0
        )
        self.assertTrue(ownership["byte_exact_plan_and_package_evidence"])

    def test_dual_profile_ranges_section_hashes_and_slack_are_exact(self) -> None:
        expected = {
            "apple-clang": {
                "loadable": 20_416,
                "slack": (622, 300, 930),
                "elf": "d11b4b1fffb0328cbf0adb532a753745089ea33cfa22f1489a3d408375f70d3f",
                "script": "cec79f423de6759afd7618b12c30df01f860ff1e10875e068d434f8c20d6e0cb",
                "ranges": [
                    ("0x005ABEF8", "0x005AD22E", 4_918,
                     "af26a89e31bd570876eb6525feca32796170b4e1d126d30c7c9a475ca5c87761"),
                    ("0x005AD230", "0x005AFEA6", 11_382,
                     "875b144a03be6535cbda9d925aaec7db2a17f088376d2f300e0e38c2b154bd26"),
                    ("0x007FCEC0", "0x007FDEC4", 4_100,
                     "a27cfc1302153a5bc2f2e2253d7d3e9eb8dd75fdae0c66426c898bc46376ccb0"),
                    ("0x007FDEC4", "0x007FDED4", 16,
                     "c7f38a59fd9b7e9eca1ba1e07f3de5b1c3b5f7eb5b6322638f42f668c62abd66"),
                ],
            },
            "linux-clang": {
                "loadable": 20_356,
                "slack": (682, 300, 990),
                "elf": "915a4c28c28c2173b074e09f2d2114498f3b7e412b53d163173ccbd749097fcd",
                "script": "b80cf9d9390d04460205a47302ff31954e3a4940cbf6ab4b595563440430e1a5",
                "ranges": [
                    ("0x005ABEF8", "0x005AD22E", 4_918,
                     "5c2f3b649f62d1d86f3c900498f4ba679dc9b0eb3bb46cf184e27fa5ccb268a2"),
                    ("0x005AD230", "0x005AFE6A", 11_322,
                     "257e531397359a887481018b7679a280250714be8bc07b56003900969cf57ee4"),
                    ("0x007FCEC0", "0x007FDEC4", 4_100,
                     "632fe6b5d869358279803fa7bb07f6717b5c2ab5706fafd38ac40a30e873f2f1"),
                    ("0x007FDEC4", "0x007FDED4", 16,
                     "c7f38a59fd9b7e9eca1ba1e07f3de5b1c3b5f7eb5b6322638f42f668c62abd66"),
                ],
            },
        }
        for name, profile in self.report["profiles"].items():
            self.assertEqual(profile["loadable_bytes"], expected[name]["loadable"])
            self.assertEqual(
                (profile["stock_envelope_unused_bytes"],
                 profile["tail_suffix_unused_bytes"],
                 profile["two_interval_unused_bytes"]),
                expected[name]["slack"],
            )
            self.assertEqual(profile["tail_prefix_alignment_bytes"], 6)
            self.assertEqual(profile["final_elf"]["sha256"], expected[name]["elf"])
            self.assertEqual(
                profile["partition"]["linker_script_sha256"],
                expected[name]["script"],
            )
            self.assertEqual(
                [(row["start"], row["end_exclusive"], row["bytes"],
                  row["sha256"]) for row in profile["sections"]],
                expected[name]["ranges"],
            )

    def test_all_relocations_callbacks_class_and_branches_are_closed(self) -> None:
        expected = {
            "apple-clang": (
                "5288d163b0472a8545a955b966ee73a6883e1d76145b1444369cbc2b17a250b5",
                "f7570851208f5f49b09f3f126a53dbcc80535ae506a26fea67c36ff206df7ad7",
            ),
            "linux-clang": (
                "f99b6d1ee168ecfd95d767de3caaf7a2f17fb6f31b3c2f629df42210a70fd169",
                "262b8e6789fc42d65934c0f3169cb52fd5f2e2135825700e79092025c92bf38f",
            ),
        }
        for name, profile in self.report["profiles"].items():
            self.assertEqual(profile["undefined_symbols"], [])
            self.assertEqual(profile["relocations"]["total"], 0)
            self.assertEqual(profile["binding_count"], 36)
            self.assertEqual(profile["bindings"]["__aeabi_memcpy"], "0x00439BE4")
            self.assertEqual(profile["cff_driver_class"], "0x005AC014")
            self.assertEqual(profile["cff_driver_class_bytes"], 96)
            self.assertEqual(profile["cff_driver_class_sha256"], expected[name][0])
            callbacks = profile["final_callback_bindings"]
            self.assertEqual(
                (callbacks["records"], callbacks["distinct_targets"]), (58, 55)
            )
            self.assertEqual(callbacks["records_sha256"], expected[name][1])
            self.assertTrue(
                callbacks["all_words_resolve_to_relocated_thumb_symbols"]
            )
            self.assertEqual(profile["materialized_complete_map_symbols"], 81)
            self.assertEqual(profile["widest_binding_domain_bytes"], 3_949_296)
            self.assertTrue(profile["range_compatible"])
            self.assertEqual(profile["linker_generated_veneers"], [])

    def test_patch_ota_and_route_contract_remain_fail_closed(self) -> None:
        self.assertEqual(self.report["module_class_patch_contract"], {
            "address": "0x0073EF00",
            "expected_stock_class": "0x006DCB74",
            "expected_stock_little_endian_hex": "74cb6d00",
            "replacement_class": "0x005AC014",
            "replacement_little_endian_hex": "14c05a00",
            "pointer_alignment": 4,
            "same_apollo_application_package_entry": True,
            "guarded_compare_before_write_required": True,
            "applied": False,
        })
        self.assertEqual(self.report["ota_and_package"], {
            "all_scatter_sections_and_pointer_patch_in_entry_id": 6,
            "cross_entry_mutations": 0,
            "cross_entry_ota_atomicity_required": False,
            "current_runtime_end_exclusive": "0x007FCEBA",
            "candidate_runtime_end_exclusive": "0x007FDED4",
            "component_growth_bytes": 4_122,
            "package_length_crc_and_flash_plan_regeneration_required": True,
            "candidate_component_or_package_emitted": False,
        })
        self.module.validate_route_boundary(self.report)

    def test_hostile_route_and_dependency_mutations_fail_closed(self) -> None:
        for mutation in ("patch", "relocation", "range", "route"):
            hostile = copy.deepcopy(self.report)
            if mutation == "patch":
                hostile["module_class_patch_contract"][
                    "expected_stock_little_endian_hex"
                ] = "00000000"
            elif mutation == "relocation":
                hostile["profiles"]["apple-clang"]["relocations"]["total"] = 1
            elif mutation == "range":
                hostile["profiles"]["linux-clang"]["range_compatible"] = False
            else:
                hostile["routing"]["production_route_permitted"] = True
            with self.subTest(mutation=mutation):
                with self.assertRaises(self.module.ScatterError):
                    self.module.validate_route_boundary(hostile)

        with tempfile.TemporaryDirectory(prefix="opencfw-cff-scatter-hostile-") as raw:
            changed = Path(raw) / "size.json"
            body = bytearray(self.module.SIZE_MANIFEST.read_bytes())
            body[len(body) // 2] ^= 1
            changed.write_bytes(body)
            with self.assertRaisesRegex(self.module.ScatterError, "input pin drift"):
                self.module.analyze(input_overrides={
                    self.module.SIZE_MANIFEST: changed,
                })

    def test_checked_manifest_and_cli_are_deterministic(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--check-manifest"],
            cwd=G2, check=True, capture_output=True, text=True,
        )
        self.assertEqual(json.loads(completed.stdout), self.report)


if __name__ == "__main__":
    unittest.main()
