#!/usr/bin/env python3
"""Hostile-input and exact target-closure gates for the LVGL utility provider."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_core_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_core_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"

PROVIDER_SYMBOLS = {
    "lv_area_get_height", "lv_area_get_width", "lv_area_increase",
    "lv_area_intersect", "lv_area_is_in", "lv_area_move", "lv_area_set",
    "lv_area_set_height", "lv_area_set_width", "lv_color_format_get_bpp",
    "lv_event_get_code", "lv_event_get_param", "lv_matrix_transform_point",
    "lv_matrix_translate",
}


class LVGLCoreProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-core-provider-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_hostile_host_oracle_is_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        command = [
            self.clang, "-std=gnu11", "-O1", "-g", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-DLV_CONF_SKIP=1", "-DLV_COLOR_DEPTH=8",
            "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1", "-DLV_USE_FLOAT=1",
            "-DLV_USE_LOG=0", "-DLV_USE_OS=LV_OS_NONE",
            "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CLIB",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
            "-I", str(ROOT / "third_party/lvgl"), str(SOURCE), str(FIXTURE),
            "-o", str(executable),
        ]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        environment = dict(os.environ)
        environment["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        subprocess.run(
            [str(executable)], cwd=ROOT, env=environment, check=True,
            capture_output=True, text=True,
        )

    def test_manifest_pins_exact_target_abi_and_zero_import_provider(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_core_provider"]
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-core-provider.o",
            "size": 7_452,
            "sha256": "9342103b5ae256c72221216d754d21020a92218fbd3024d7e17303ed6ef7111a",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_core_provider_abi.o",
            "size": 896,
            "sha256": "f194076301eaed4ecabf74b3d4df75e227f443c1b33d945ee9b545cdb66d71e8",
        })
        self.assertEqual(set(provider["required_exports"]), PROVIDER_SYMBOLS)
        self.assertEqual(set(provider["all_external_exports"]), PROVIDER_SYMBOLS)
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["external_relocations"], {})
        self.assertEqual(provider["fixed_address_import_count"], 0)
        self.assertEqual(provider["closed_residual_symbol_count"], 14)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_every_closed_symbol_has_a_real_ambiq_consumer_relocation(self) -> None:
        provider = json.loads(MANIFEST.read_text(encoding="utf-8"))[
            "local_lvgl_core_provider"
        ]
        relocations = provider["closed_consumer_relocations"]
        self.assertEqual(set(relocations), PROVIDER_SYMBOLS)
        for symbol, owners in relocations.items():
            self.assertTrue(owners, symbol)
            self.assertGreater(sum(row["relocation_count"] for row in owners), 0, symbol)
            self.assertTrue(all("R_ARM_THM_CALL" in row["relocation_types"] for row in owners))

    def test_authenticated_source_tree_and_residual_accounting_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        upstream = report["local_lvgl_core_provider"]["authenticated_upstream"]
        self.assertEqual(
            upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa"
        )
        self.assertEqual(
            upstream["tree"], "2c76db856ec570f3ee12565181e5cf52bdd33d78"
        )
        self.assertEqual(len(upstream["source_blobs"]), 5)
        self.assertEqual(upstream["license"], "MIT")
        self.assertEqual(report["missing_provider_count"], 0)
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertTrue(PROVIDER_SYMBOLS.isdisjoint(missing))
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )


if __name__ == "__main__":
    unittest.main()
