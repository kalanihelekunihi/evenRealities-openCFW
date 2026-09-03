#!/usr/bin/env python3
"""Behavior and target-compile gates for image-decoder support leaves."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_decoder_support_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_decoder_support_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLDecoderSupportProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-decoder-support-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_support_leaves_are_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        command = [
            self.clang, "-std=gnu11", "-O1", "-g", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-DLV_CONF_SKIP=1", "-DLV_COLOR_DEPTH=8",
            "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1", "-DLV_USE_FLOAT=1",
            "-DLV_USE_LOG=1", "-DLV_LOG_LEVEL=LV_LOG_LEVEL_WARN",
            "-DLV_LOG_PRINTF=0", "-DLV_USE_OS=LV_OS_NONE",
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

    def test_manifest_pins_decoder_filesystem_cache_and_support_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_decoder_provider"]
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-decoder-aggregate.o", "size": 48_140,
            "sha256": "92f09f27f55e93c91107cb5bb517d086085583e4c74da87807a57d20a1650be1",
        })
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(provider["closed_consumer_relocation_count"], 9)
        self.assertEqual(provider["closed_residual_symbol_count"], 2)
        self.assertEqual(provider["authenticated_upstream"]["commit"],
                         "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertNotIn("lv_image_decoder_open", {
            row["symbol"] for row in report["missing_provider_ledger"]
        })
        self.assertNotIn("lv_image_decoder_close", {
            row["symbol"] for row in report["missing_provider_ledger"]
        })
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])


if __name__ == "__main__":
    unittest.main()
