#!/usr/bin/env python3
"""Hostile, ABI/import, and residual gates for draw-buffer create/reshape."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_buf_shape_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_draw_buf_shape_provider_host.c"
HOST_CONFIG = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_draw_buf_shape_provider_host_config.h"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLDrawBufferShapeProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-draw-buf-shape-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_hostile_geometry_callbacks_and_failures_are_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        command = [
            self.clang, "-std=gnu11", "-O1", "-g", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-DLV_CONF_SKIP=1", "-DLV_COLOR_DEPTH=8",
            "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1", "-DLV_USE_FLOAT=1",
            "-DLV_USE_LOG=0", "-DLV_USE_OS=LV_OS_NONE",
            "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CLIB", "-include", str(HOST_CONFIG),
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
            "-I", str(ROOT / "third_party/lvgl"),
            "-I", str(ROOT / "third_party/lvgl/src"),
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

    def test_manifest_pins_target_abi_import_and_aggregate_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_draw_buf_shape_provider"]
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-buf-shape-provider.o",
            "size": 2_296,
            "sha256": "2cf520c1f7d814e9594f93520b638d15e107128c1882fadabff3342eb5448933",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_draw_buf_shape_provider_abi.o",
            "size": 1_412,
            "sha256": "eb117a909d01a5efbb549229431835ef54748ff9b8581e6b521beb11518388dc",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-buf-shape-aggregate.o",
            "size": 4_780,
            "sha256": "286aa21ed029d21e21428beccfa082c8044e2019d7d7403c5f3529b512f6e9c5",
        })
        self.assertEqual(provider["required_exports"], [
            "lv_draw_buf_create", "lv_draw_buf_reshape",
        ])
        self.assertEqual(provider["elf_undefined_symbols"], [
            "lv_free", "lv_global", "lv_malloc_zeroed",
        ])
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(provider["closed_consumer_relocation_count"], 4)
        self.assertEqual(set(provider["indirect_callback_boundaries"]), {
            "buf_malloc_cb", "buf_free_cb", "align_pointer_cb", "width_to_stride_cb",
        })
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_authenticated_source_and_residual_boundary_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_draw_buf_shape_provider"]
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(set(upstream["source_git_blobs"]), {
            "src/draw/lv_draw_buf.c", "src/draw/lv_draw_buf.h",
            "src/draw/lv_draw_buf_private.h", "src/core/lv_global.h",
        })
        self.assertEqual(report["missing_provider_count"], 0)
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertNotIn("lv_draw_buf_create", missing)
        self.assertNotIn("lv_draw_buf_reshape", missing)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )


if __name__ == "__main__":
    unittest.main()
