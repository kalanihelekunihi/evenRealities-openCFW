#!/usr/bin/env python3
"""Sequence, ABI/import, and residual gates for draw-dispatch requests."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_draw_dispatch_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_draw_dispatch_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLDrawDispatchProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-draw-dispatch-")
        cls.stubs = Path(cls.temporary.name) / "stubs"
        cls.stubs.mkdir()
        (cls.stubs / "FreeRTOS.h").write_text(
            "#ifndef TEST_FREERTOS_H\n#define TEST_FREERTOS_H\n"
            "#include <stdint.h>\ntypedef int BaseType_t;\n"
            "typedef unsigned int UBaseType_t;\ntypedef uint32_t TickType_t;\n"
            "typedef void * TaskHandle_t;\ntypedef void * SemaphoreHandle_t;\n"
            "#define portMAX_DELAY UINT32_MAX\n#endif\n",
            encoding="ascii",
        )
        (cls.stubs / "task.h").write_text(
            "#ifndef TEST_TASK_H\n#define TEST_TASK_H\n#include \"FreeRTOS.h\"\n#endif\n",
            encoding="ascii",
        )
        (cls.stubs / "semphr.h").write_text(
            "#ifndef TEST_SEMPHR_H\n#define TEST_SEMPHR_H\n#include \"FreeRTOS.h\"\n#endif\n",
            encoding="ascii",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_exact_two_signal_sequence_is_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        command = [
            self.clang, "-std=gnu11", "-O1", "-g", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-DLV_CONF_SKIP=1", "-DLV_COLOR_DEPTH=8",
            "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1", "-DLV_USE_FLOAT=1",
            "-DLV_USE_LOG=1", "-DLV_LOG_LEVEL=LV_LOG_LEVEL_WARN",
            "-DLV_USE_OS=LV_OS_FREERTOS", "-DLV_USE_FREERTOS_TASK_NOTIFY=1",
            "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CLIB",
            "-I", str(self.stubs),
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

    def test_manifest_pins_target_abi_import_and_deferred_dependency(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_draw_dispatch_provider"]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_lvgl_draw_dispatch_provider.o",
            "size": 1_084,
            "sha256": "3521e40f536ed4c3e39ebbabc8396c6052272f5ebed0907ad617cf1256015766",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-dispatch-provider.o",
            "size": 1_248,
            "sha256": "5add8d9b27247a4d2e059cbf5783f6f9961de975adb4509e594641fef235ee62",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_draw_dispatch_provider_abi.o",
            "size": 1_048,
            "sha256": "f4172c6054d14694ae3aef4cc92905c9084a662bc20d2f1dc411376233e8cbdc",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-dispatch-aggregate.o",
            "size": 1_380,
            "sha256": "ec5f9f6e2f0e97781e0b8f29065b9a93134126451a71bcd64b20f611ced21990",
        })
        self.assertEqual(provider["elf_undefined_symbols"], [
            "lv_global", "lv_thread_sync_signal",
        ])
        self.assertEqual(provider["external_relocations"], {
            "lv_global": {"R_ARM_THM_MOVT_ABS": 1, "R_ARM_THM_MOVW_ABS_NC": 1},
            "lv_thread_sync_signal": {"R_ARM_THM_CALL": 1, "R_ARM_THM_JUMP24": 1},
        })
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [
            "lv_thread_sync_signal",
        ])
        self.assertEqual(provider["transitive_residual_dependencies"], [
            "lv_thread_sync_signal",
        ])
        self.assertTrue(provider["dependency_admitted"])
        self.assertEqual(
            provider["transitive_dependency_provider"],
            "local_lvgl_thread_sync_signal_provider",
        )
        self.assertEqual(provider["closed_consumer_relocations"], {
            "lv_draw_dispatch_request": [{
                "object": "lv_draw_ambiq.o", "relocation_count": 1,
                "relocation_types": {"R_ARM_THM_CALL": 1},
            }],
        })
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_authenticated_source_and_residual_boundary_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_draw_dispatch_provider"]
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(set(upstream["source_git_blobs"]), {
            "src/draw/lv_draw.c", "src/draw/lv_draw.h",
            "src/draw/lv_draw_private.h", "src/core/lv_global.h",
            "src/osal/lv_os.h",
        })
        self.assertEqual(report["missing_provider_count"], 11)
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertNotIn("lv_draw_dispatch_request", missing)
        self.assertNotIn("lv_thread_sync_signal", missing)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "f9d7f5b3fc8db9a19441ec0c4991ac9161c0ae46583e56c2a2298f2794732744",
        )


if __name__ == "__main__":
    unittest.main()
