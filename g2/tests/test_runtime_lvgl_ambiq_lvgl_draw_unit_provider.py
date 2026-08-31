#!/usr/bin/env python3
"""State, ABI/import, and residual gates for draw-unit creation."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_unit_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_draw_unit_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLDrawUnitProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-draw-unit-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_hostile_extent_failure_and_head_insertion_are_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        command = [
            self.clang, "-std=gnu11", "-O1", "-g", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-DLV_CONF_SKIP=1", "-DLV_COLOR_DEPTH=8",
            "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1", "-DLV_USE_FLOAT=1",
            "-DLV_USE_LOG=0", "-DLV_USE_OS=LV_OS_NONE",
            "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CLIB",
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
        provider = report["local_lvgl_draw_unit_provider"]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_lvgl_draw_unit_provider.o",
            "size": 1_108,
            "sha256": "0e4477b7ccd8baaf853d17c4a6725ba4e53075d472cc9a828e5f329b6228cdfd",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-unit-provider.o",
            "size": 1_260,
            "sha256": "67c6f571e7d904438deccaa9de331449a59cecdf9d26ab78c618dbaf96489206",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_draw_unit_provider_abi.o",
            "size": 1_028,
            "sha256": "ee45e95ecb3515d8f7b9031c70fb7e33c2947ec010901c21c9144d6d5c9233ee",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-unit-aggregate.o",
            "size": 3_768,
            "sha256": "7ca28abfb72e6413ac30afc2ae7bd7b3f55b4e58815f62af8e113ae35c07cb09",
        })
        self.assertEqual(provider["elf_undefined_symbols"], [
            "lv_global", "lv_malloc_zeroed",
        ])
        self.assertEqual(provider["external_relocations"], {
            "lv_global": {"R_ARM_THM_MOVT_ABS": 1, "R_ARM_THM_MOVW_ABS_NC": 1},
            "lv_malloc_zeroed": {"R_ARM_THM_CALL": 1},
        })
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(provider["closed_consumer_relocations"], {
            "lv_draw_create_unit": [{
                "object": "lv_draw_ambiq.o", "relocation_count": 1,
                "relocation_types": {"R_ARM_THM_CALL": 1},
            }],
        })
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_authenticated_source_and_residual_boundary_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_draw_unit_provider"]
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(set(upstream["source_git_blobs"]), {
            "src/draw/lv_draw.c", "src/draw/lv_draw.h",
            "src/draw/lv_draw_private.h", "src/core/lv_global.h",
            "src/stdlib/lv_mem.h",
        })
        self.assertEqual(report["missing_provider_count"], 11)
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertNotIn("lv_draw_create_unit", missing)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "f9d7f5b3fc8db9a19441ec0c4991ac9161c0ae46583e56c2a2298f2794732744",
        )


if __name__ == "__main__":
    unittest.main()
