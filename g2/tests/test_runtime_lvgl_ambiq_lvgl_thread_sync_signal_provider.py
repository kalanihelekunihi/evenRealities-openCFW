#!/usr/bin/env python3
"""Hostile, ABI/fixed-call, and residual gates for LVGL thread/sync OSAL."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"
SOURCE = RUNTIME / "lvgl_ambiq_lvgl_thread_sync_signal_provider.c"
HOST_CONFIG = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_thread_sync_signal_provider_host_config.h"
HOST_FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_thread_sync_signal_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"


class LVGLThreadSyncSignalProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-thread-sync-signal-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_hostile_thread_lifecycle_sync_and_race_paths_are_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        subprocess.run([
            self.clang, "-std=gnu11", "-O1", "-g", "-fshort-enums",
            "-Wall", "-Wextra", "-Werror", "-fsanitize=address,undefined",
            "-fno-omit-frame-pointer", "-include", str(HOST_CONFIG),
            "-I", str(RUNTIME), str(SOURCE), str(HOST_FIXTURE), "-o", str(executable),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        environment = dict(os.environ)
        environment["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        subprocess.run(
            [str(executable)], cwd=ROOT, env=environment, check=True,
            capture_output=True, text=True,
        )

    def test_manifest_pins_exact_abi_fixed_calls_and_aggregate_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_thread_sync_signal_provider"]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_lvgl_thread_sync_signal_provider.o",
            "size": 2_820,
            "sha256": "ea7b79666b87c9a5d23894183e7a68bc908ae20612d26998558352d1a618a7c1",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-thread-sync-signal-provider.o",
            "size": 3_592,
            "sha256": "ddbbc2988d6f974c109e0f5d826f24579a2251d7acb569414b05184cb35252da",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_thread_sync_signal_provider_abi.o",
            "size": 1_628,
            "sha256": "6c4cdc36d26040954239adb9caa26c86acf82bc2670a8c407a3fa9b3c7a16caa",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-thread-sync-signal-aggregate.o",
            "size": 4_288,
            "sha256": "4f82e5232652fd83555c7321d2743c14eb75e0b1b8de728df2db691fe1fe3e2c",
        })
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["external_relocations"], {})
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(provider["fixed_address_imports"], {
            "0x004420D1": "source-owned vPortEnterCritical Thumb entry",
            "0x004420E9": "source-owned vPortExitCritical Thumb entry",
            "0x0045589D": "source-owned xTaskGetCurrentTaskHandle Thumb entry",
            "0x00455FA9": "source-owned prvAddCurrentTaskToDelayedList Thumb entry",
            "0x00455C49": "source-owned xTaskGenericNotify Thumb entry",
            "0x004420BD": "source-owned vPortYield Thumb entry",
            "0x004548BB": "source-owned xTaskCreate Thumb entry",
            "0x00454AAF": "source-owned vTaskDelete Thumb entry",
        })
        self.assertEqual(provider["fixed_address_import_count"], 8)
        self.assertEqual(provider["closed_consumer_relocation_count"], 7)
        self.assertEqual(provider["closed_transitive_relocation_count"], 2)
        self.assertEqual(provider["closed_residual_symbol_count"], 6)
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_notify_mode_source_and_residual_boundary_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_thread_sync_signal_provider"]
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(upstream["freertos_commit"], "def7d2df2b0506d3d249334974f51e427c17a41c")
        self.assertEqual(upstream["notify_mode"], 1)
        self.assertEqual(set(upstream["source_git_blobs"]), {
            "src/osal/lv_freertos.c", "src/osal/lv_freertos.h",
            "src/osal/lv_os.h", "src/lv_conf_internal.h",
        })
        self.assertEqual(report["missing_provider_count"], 0)
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertTrue({
            "lv_thread_sync_init", "lv_thread_sync_wait",
            "lv_thread_sync_signal", "lv_thread_sync_delete",
        }.isdisjoint(missing))
        self.assertTrue({"lv_thread_init", "lv_thread_delete"}.isdisjoint(missing))
        self.assertTrue(report["local_lvgl_draw_dispatch_provider"]["dependency_admitted"])
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )


if __name__ == "__main__":
    unittest.main()
