#!/usr/bin/env python3
"""Hostile, ABI/import, and residual gates for the FreeType event setter."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_freetype_event_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_freetype_event_provider_host.c"
HOST_CONFIG = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_freetype_event_provider_host_config.h"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLFreeTypeEventProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-freetype-event-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_null_context_and_callback_storage_oracle_is_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        command = [
            self.clang, "-std=gnu11", "-O1", "-g", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-DLV_CONF_SKIP=1", "-DLV_COLOR_DEPTH=8",
            "-DLV_USE_FREETYPE=1", "-DLV_USE_VECTOR_GRAPHIC=1",
            "-DLV_USE_MATRIX=1", "-DLV_USE_FLOAT=1", "-DLV_USE_LOG=0",
            "-DLV_USE_OS=LV_OS_NONE", "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CLIB",
            "-include", str(HOST_CONFIG),
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
            "-I", str(ROOT / "third_party/lvgl"),
            "-I", str(ROOT / "third_party/lvgl/src"),
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

    def test_manifest_pins_target_abi_import_and_aggregate_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_freetype_event_provider"]
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-freetype-event-provider.o",
            "size": 1_208,
            "sha256": "f4d90b85f22b784d3922cc16b7cb58c5f3df8c1c1b937e2a44332498eb07774e",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_freetype_event_provider_abi.o",
            "size": 1_040,
            "sha256": "cd6de046286a8765255f6a844a7f845289fd6e6ef33283f3b83439d277e0201e",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-global-freetype-event-aggregate.o",
            "size": 1_340,
            "sha256": "1ab0eb432566d8c19d5bcf2e5621fda099d532adc123297014f480465e9ffa5a",
        })
        self.assertEqual(provider["required_exports"], ["lv_freetype_outline_add_event"])
        self.assertEqual(provider["elf_undefined_symbols"], ["lv_global"])
        self.assertEqual(provider["external_relocations"], {
            "lv_global": {"R_ARM_THM_MOVT_ABS": 1, "R_ARM_THM_MOVW_ABS_NC": 1},
        })
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(provider["closed_consumer_relocation_count"], 1)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_authenticated_source_and_residual_boundary_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_freetype_event_provider"]
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(set(upstream["source_git_blobs"]), {
            "src/libs/freetype/lv_freetype_outline.c",
            "src/libs/freetype/lv_freetype.c",
            "src/libs/freetype/lv_freetype.h",
            "src/libs/freetype/lv_freetype_private.h",
        })
        self.assertEqual(report["missing_provider_count"], 0)
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertNotIn("lv_freetype_outline_add_event", missing)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )


if __name__ == "__main__":
    unittest.main()
