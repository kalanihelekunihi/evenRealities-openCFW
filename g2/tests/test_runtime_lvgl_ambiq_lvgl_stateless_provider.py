#!/usr/bin/env python3
"""Hostile-input and exact target-closure gates for stateless LVGL providers."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_stateless_provider.c"
)
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_stateless_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"

PROVIDER_SYMBOLS = {
    "lv_array_at", "lv_array_init_from_buf", "lv_draw_buf_flush_cache",
    "lv_draw_buf_invalidate_cache", "lv_draw_image_dsc_init",
    "lv_font_get_glyph_bitmap", "lv_freetype_is_outline_font",
    "lv_freetype_outline_get_scale", "lv_image_buf_get_transformed_area",
    "lv_memcpy", "lv_memset",
}


class LVGLStatelessProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-stateless-provider-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_hostile_host_oracle_is_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        command = [
            self.clang, "-std=gnu11", "-O1", "-g", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-DLV_CONF_SKIP=1", "-DLV_COLOR_DEPTH=8",
            "-DLV_USE_OS=LV_OS_NONE", "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CLIB",
            "-DLV_USE_FREETYPE=1", "-DLV_USE_VECTOR_GRAPHIC=1",
            "-DLV_USE_MATRIX=1", "-DLV_USE_FLOAT=1", "-DLV_USE_LOG=0",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
            "-I", str(ROOT / "third_party/lvgl"),
            "-I", str(ROOT / "third_party/freetype/include"),
            str(SOURCE), str(FIXTURE), "-o", str(executable),
        ]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        environment = dict(os.environ)
        environment["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        subprocess.run(
            [str(executable)], cwd=ROOT, env=environment, check=True,
            capture_output=True, text=True,
        )

    def test_manifest_pins_target_abi_and_zero_import_provider(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_stateless_provider"]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_lvgl_stateless_provider.o",
            "size": 5_412,
            "sha256": "6b1b93bad33f4710a7ec8987765b43d0fc90e0786801009eca36e7325fa5da73",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-stateless-provider.o",
            "size": 6_692,
            "sha256": "bcebd4a63cc1366be7ab0006fdab5f31e6645a3583c4aa9a0d72d9ea9ce932a4",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_stateless_provider_abi.o",
            "size": 908,
            "sha256": "3e99b5d4ca068929d9e7e8dcae18e326da666b04c77b24589462c760b02f76b1",
        })
        self.assertEqual(set(provider["required_exports"]), PROVIDER_SYMBOLS)
        self.assertEqual(set(provider["all_external_exports"]), PROVIDER_SYMBOLS)
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["external_relocations"], {})
        self.assertEqual(provider["fixed_address_import_count"], 0)
        self.assertEqual(provider["closed_residual_symbol_count"], 11)
        self.assertEqual(provider["closed_consumer_relocation_count"], 28)
        self.assertEqual(set(provider["indirect_callback_boundaries"]), {
            "lv_draw_buf_flush_cache", "lv_draw_buf_invalidate_cache",
        })
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_every_closed_symbol_has_an_exact_ambiq_branch_relocation(self) -> None:
        provider = json.loads(MANIFEST.read_text(encoding="utf-8"))[
            "local_lvgl_stateless_provider"
        ]
        relocations = provider["closed_consumer_relocations"]
        self.assertEqual(set(relocations), PROVIDER_SYMBOLS)
        self.assertEqual(
            sum(row["relocation_count"] for rows in relocations.values() for row in rows),
            28,
        )
        for symbol, owners in relocations.items():
            self.assertTrue(owners, symbol)
            for row in owners:
                self.assertGreater(row["relocation_count"], 0, symbol)
                self.assertTrue(
                    set(row["relocation_types"]).issubset(
                        {"R_ARM_THM_CALL", "R_ARM_THM_JUMP24"}
                    ),
                    symbol,
                )
        self.assertEqual(
            relocations["lv_array_init_from_buf"][0]["relocation_types"],
            {"R_ARM_THM_CALL": 1, "R_ARM_THM_JUMP24": 1},
        )

    def test_authenticated_source_and_residual_accounting_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        upstream = report["local_lvgl_stateless_provider"]["authenticated_upstream"]
        self.assertEqual(
            upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa"
        )
        self.assertEqual(upstream["tree"], "2c76db856ec570f3ee12565181e5cf52bdd33d78")
        self.assertEqual(len(upstream["source_blobs"]), 8)
        self.assertEqual(upstream["license"], "MIT")
        self.assertEqual(report["missing_provider_count"], 0)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertTrue(PROVIDER_SYMBOLS.isdisjoint(missing))


if __name__ == "__main__":
    unittest.main()
