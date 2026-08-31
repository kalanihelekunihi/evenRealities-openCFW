#!/usr/bin/env python3
"""Hostile, ABI, dependency-link, and residual gates for draw-buffer destroy."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_buf_lifecycle_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_draw_buf_lifecycle_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLDrawBufferLifecycleProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-draw-buf-life-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_hostile_descriptor_and_callback_oracle_is_sanitizer_clean(self) -> None:
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

    def test_manifest_pins_target_abi_dependency_and_aggregate_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_draw_buf_lifecycle_provider"]
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-buf-lifecycle-provider.o",
            "size": 1_192,
            "sha256": "4b633e5f8f0b2fe765678d8525317aa4c8df3e10d4c22a5e216baeb6393888ca",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_draw_buf_lifecycle_provider_abi.o",
            "size": 1_036,
            "sha256": "a65afe066d348288c6cde31b6e7839e7ce2f550ea243e0220b7b4ad2873aab32",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-heap-lifecycle-aggregate.o",
            "size": 3_584,
            "sha256": "ee9e7d0d5419d12a70e3707b99bac1b6bc4ce79c536aa811d3a027ea7c303823",
        })
        self.assertEqual(provider["required_exports"], ["lv_draw_buf_destroy"])
        self.assertEqual(provider["elf_undefined_symbols"], ["lv_free"])
        self.assertEqual(provider["external_relocations"], {
            "lv_free": {"R_ARM_THM_JUMP24": 2},
        })
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(provider["fixed_address_import_count"], 0)
        self.assertEqual(provider["closed_consumer_relocation_count"], 4)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_authenticated_source_and_residual_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_draw_buf_lifecycle_provider"]
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(set(upstream["source_git_blobs"]), {
            "src/draw/lv_draw_buf.c", "src/draw/lv_draw_buf.h",
        })
        self.assertEqual(report["missing_provider_count"], 11)
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertNotIn("lv_draw_buf_destroy", missing)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "f9d7f5b3fc8db9a19441ec0c4991ac9161c0ae46583e56c2a2298f2794732744",
        )


if __name__ == "__main__":
    unittest.main()
