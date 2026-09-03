#!/usr/bin/env python3
"""Behavior and target-compile gates for LVGL layer allocation."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_lvgl_layer_alloc_provider.c"
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_layer_alloc_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLLayerAllocProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-layer-alloc-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_allocation_clear_and_failure_rules_are_sanitizer_clean(self) -> None:
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

    def test_manifest_pins_target_abi_import_and_pending_log_boundary(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_layer_alloc_provider"]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_lvgl_layer_alloc_provider.o", "size": 2_504,
            "sha256": "df5ffc50377217d3092404482844e1614b34205b4f4e1bfe0484930befb59a78",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-layer-alloc-provider.o", "size": 2_836,
            "sha256": "cc24714099180a2d1d52825f24689441a34d6fa1892d705f350f621a26c2970d",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_layer_alloc_provider_abi.o", "size": 1_024,
            "sha256": "fda4c2622abe8479c932c4254000757ce5e0dce9234fbc6ece72ea71fc3fb03a",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-layer-alloc-aggregate.o", "size": 34_452,
            "sha256": "29ed9dc41094587281f79597c610fc30271d6fe38340c4b577d84638a4b81007",
        })
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertTrue(provider["transitive_source_closed"])
        self.assertEqual(provider["closed_consumer_relocation_count"], 1)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_authenticated_source_and_residual_boundary_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_layer_alloc_provider"]
        self.assertEqual(provider["authenticated_upstream"]["commit"],
                         "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(report["missing_provider_count"], 0)
        self.assertNotIn("lv_draw_layer_alloc_buf", {
            row["symbol"] for row in report["missing_provider_ledger"]
        })
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )


if __name__ == "__main__":
    unittest.main()
