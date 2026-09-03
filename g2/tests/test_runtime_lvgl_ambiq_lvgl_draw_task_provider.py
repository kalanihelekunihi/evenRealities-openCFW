#!/usr/bin/env python3
"""Behavior and target-compile gates for draw-task selection."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_task_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_draw_task_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLDrawTaskProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-draw-task-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_selection_rules_are_sanitizer_clean(self) -> None:
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
        subprocess.run([str(executable)], cwd=ROOT, env=environment, check=True,
                       capture_output=True, text=True)

    def test_manifest_pins_target_abi_import_and_aggregate_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_draw_task_provider"]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_lvgl_draw_task_provider.o", "size": 1_276,
            "sha256": "146ae1cf94aa234607c3b5d6d6e8bb383b6d7906e8014ce648d5ddd937c03456",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-task-provider.o", "size": 1_448,
            "sha256": "3b103e71b599e201f56362e973fda7f3f9ef8569a819a39947423d8dfbf451a5",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_draw_task_provider_abi.o", "size": 1_020,
            "sha256": "97577f4542bf3f075c51db1b8c5ee4f2248ff0f933eb5b97d52c6acf8a808d86",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-task-aggregate.o", "size": 8_344,
            "sha256": "d6620afbb9c02d0bcb81617531f9a0c1730c74c22ab614b120dda591d3a799cf",
        })
        self.assertEqual(provider["elf_undefined_symbols"], ["lv_area_intersect", "lv_global"])
        self.assertEqual(provider["external_relocations"], {
            "lv_area_intersect": {"R_ARM_THM_CALL": 1},
            "lv_global": {"R_ARM_THM_MOVT_ABS": 1, "R_ARM_THM_MOVW_ABS_NC": 1},
        })
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(provider["closed_consumer_relocation_count"], 1)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_authenticated_source_and_residual_boundary_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_draw_task_provider"]
        self.assertEqual(provider["authenticated_upstream"]["commit"],
                         "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(report["missing_provider_count"], 0)
        self.assertNotIn("lv_draw_get_available_task", {
            row["symbol"] for row in report["missing_provider_ledger"]
        })
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )


if __name__ == "__main__":
    unittest.main()
