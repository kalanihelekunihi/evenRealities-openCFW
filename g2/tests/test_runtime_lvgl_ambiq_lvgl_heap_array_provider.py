#!/usr/bin/env python3
"""Hostile-input, ABI, and target-link gates for the LVGL heap/array provider."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_heap_array_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_heap_array_provider_host.c"
HOST_CONFIG = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_heap_array_provider_host_config.h"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"
SYMBOLS = {
    "lv_array_deinit", "lv_array_push_back", "lv_free", "lv_malloc",
    "lv_malloc_zeroed",
}


class LVGLHeapArrayProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-heap-array-provider-")

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
            "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CLIB", "-include", str(HOST_CONFIG),
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

    def test_manifest_pins_exact_abi_import_and_consumer_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_heap_array_provider"]
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-heap-array-provider.o",
            "size": 3_060,
            "sha256": "e37759628d884e20f3c788d7b16e21997a667fddd8a6271e2cdd818a74661458",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_heap_array_provider_abi.o",
            "size": 2_472,
            "sha256": "028f1e607d6aac51df51f26535be9a42edc60475afa2e71c78deff7c3c81faba",
        })
        self.assertEqual(set(provider["required_exports"]), SYMBOLS)
        self.assertEqual(set(provider["all_external_exports"]), SYMBOLS)
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["external_relocations"], {})
        self.assertEqual(set(provider["fixed_address_imports"]), {
            "0x00474CD2", "0x00474D16", "0x00474D54",
        })
        self.assertEqual(provider["closed_consumer_relocation_count"], 41)
        self.assertEqual(set(provider["closed_consumer_relocations"]), SYMBOLS)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_residual_and_authenticated_source_bounds_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_heap_array_provider"]
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(upstream["tree"], "2c76db856ec570f3ee12565181e5cf52bdd33d78")
        self.assertEqual(len(upstream["source_git_blobs"]), 3)
        self.assertEqual(report["missing_provider_count"], 0)
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertTrue(SYMBOLS.isdisjoint(missing))
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )


if __name__ == "__main__":
    unittest.main()
