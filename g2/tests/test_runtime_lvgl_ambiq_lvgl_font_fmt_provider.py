#!/usr/bin/env python3
"""Hostile/reference, ABI, and residual gates for the fmt_txt provider."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_font_fmt_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_font_fmt_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLFontFmtProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-font-fmt-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_plain_compressed_and_hostile_oracle_is_sanitizer_clean(self) -> None:
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

    def test_manifest_pins_zero_import_target_abi_and_consumer(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_font_fmt_provider"]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_lvgl_font_fmt_provider.o",
            "size": 4_176,
            "sha256": "000a0c4bc5bd8ca6886b6a821f3cdbbbfd331d67a12b4a3a87e3581aaed6a8a4",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-font-fmt-provider.o",
            "size": 4_688,
            "sha256": "9d4333cf6277960f46d5ce5e0cb8ef0b49e203861bb275afbcf7e409a789ef66",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_font_fmt_provider_abi.o",
            "size": 1_016,
            "sha256": "adad17c030719f3bc67ab0b525ea303221fb941caeadc0ab87d053588bef195e",
        })
        self.assertEqual(provider["required_exports"], ["lv_font_get_bitmap_fmt_txt"])
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["external_relocations"], {})
        self.assertEqual(provider["closed_consumer_relocation_count"], 2)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_authenticated_algorithm_and_residual_boundary_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_font_fmt_provider"]
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(set(upstream["source_git_blobs"]), {
            "src/font/lv_font_fmt_txt.c", "src/font/lv_font_fmt_txt.h",
            "src/font/lv_font_fmt_txt_private.h", "src/draw/lv_draw_buf_private.h",
        })
        self.assertEqual(report["missing_provider_count"], 0)
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertNotIn("lv_font_get_bitmap_fmt_txt", missing)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )


if __name__ == "__main__":
    unittest.main()
