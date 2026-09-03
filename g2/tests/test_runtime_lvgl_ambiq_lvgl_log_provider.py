#!/usr/bin/env python3
"""Behavior and target-compile gates for LVGL callback logging."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_log_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_log_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLLogProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-log-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_callback_formatting_and_filtering_are_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        command = [
            self.clang, "-std=gnu11", "-O1", "-g", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-DLV_CONF_SKIP=1", "-DLV_COLOR_DEPTH=8",
            "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1", "-DLV_USE_FLOAT=1",
            "-DLV_USE_LOG=1", "-DLV_LOG_LEVEL=LV_LOG_LEVEL_WARN",
            "-DLV_LOG_PRINTF=0", "-DLV_LOG_USE_TIMESTAMP=1",
            "-DLV_LOG_USE_FILE_LINE=1", "-DLV_USE_OS=LV_OS_NONE",
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

    def test_manifest_pins_formatter_runtime_and_aggregate_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_log_provider"]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_lvgl_log_provider.o", "size": 1_816,
            "sha256": "5bc00237d7f54ccfb7eb55d839f95a626ffdaa286e2f60f40d424c4603847fe5",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-log-provider.o", "size": 2_016,
            "sha256": "a1ca277a5c1d44d73dc0b135ad91520383e76cef91ffa251f5ddc4234c1f6a4d",
        })
        self.assertEqual(provider["production_runtime_artifact"], {
            "path": "lvgl-ambiq-lvgl-log-runtime.o", "size": 13_964,
            "sha256": "99a67191cf82ecc37b0d6810613a268bf377280bfc4ea41a50fcf33c545e5dd6",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-log-aggregate.o", "size": 15_228,
            "sha256": "c19effb664c3984375b0de96ea6b5ea23b1f21c16d25849d4a7c6d0af5035ca0",
        })
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(provider["closed_consumer_relocation_count"], 67)
        self.assertEqual(provider["closed_transitive_relocation_count"], 1)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_authenticated_source_and_residual_boundary_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_log_provider"]
        self.assertEqual(provider["authenticated_upstream"]["commit"],
                         "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(report["missing_provider_count"], 0)
        self.assertNotIn("lv_log_add", {
            row["symbol"] for row in report["missing_provider_ledger"]
        })
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )


if __name__ == "__main__":
    unittest.main()
