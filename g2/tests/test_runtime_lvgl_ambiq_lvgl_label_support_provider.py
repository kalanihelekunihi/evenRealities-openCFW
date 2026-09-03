#!/usr/bin/env python3
"""Behavior gate for source-owned LVGL label support leaves."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_label_support_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_label_support_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLLabelSupportProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-label-support-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_geometry_and_color_leaves_are_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        command = [
            self.clang, "-std=gnu11", "-O1", "-g", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-DLV_CONF_SKIP=1", "-DLV_COLOR_DEPTH=8",
            "-DLV_USE_VECTOR_GRAPHIC=1", "-DLV_USE_MATRIX=1", "-DLV_USE_FLOAT=1",
            "-DLV_USE_LOG=1", "-DLV_LOG_LEVEL=LV_LOG_LEVEL_WARN",
            "-DLV_USE_OS=LV_OS_NONE", "-DLV_USE_STDLIB_MALLOC=LV_STDLIB_CLIB",
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

    def test_manifest_pins_zero_undefined_label_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_label_provider"]
        self.assertEqual(provider["cluster_artifact"], {
            "path": "lvgl-ambiq-lvgl-label-cluster.o", "size": 18_472,
            "sha256": "2502cfe99b1c16732031b7e409d9ec416fd70d392fd071fd4fb80e5455862e1f",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-label-aggregate.o", "size": 49_412,
            "sha256": "81dad58e17c0beb4e5721229f73e8d935c29a1791c26c1635c2279c7b26daad5",
        })
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(provider["closed_consumer_relocation_count"], 1)
        self.assertEqual(provider["closed_residual_symbol_count"], 1)
        self.assertNotIn("lv_draw_label_iterate_characters", {
            row["symbol"] for row in report["missing_provider_ledger"]
        })
        maximal = report["maximal_scoped_candidate_closure"]
        self.assertEqual(maximal["expected_residual_symbol_count"], 0)
        self.assertEqual(maximal["expected_residual_symbol_digest"],
                         "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945")
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])


if __name__ == "__main__":
    unittest.main()
