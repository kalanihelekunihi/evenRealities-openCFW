#!/usr/bin/env python3
"""Hostile, ABI/fixed-call, and residual gates for LVGL sync signaling."""

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

    def test_hostile_lazy_pending_waiter_and_race_paths_are_sanitizer_clean(self) -> None:
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
            "size": 984,
            "sha256": "311b0db237f5051bce92970186641d2771c29e0a1c382387ede9c204af84909d",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-thread-sync-signal-provider.o",
            "size": 1_140,
            "sha256": "48251997ef18222cd29f8397f049ad5ca3c20b95b789d8917bbb03632db69269",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_thread_sync_signal_provider_abi.o",
            "size": 1_044,
            "sha256": "9895a3e05c4f9405ac0aabf7cb0c09d32946d8a7d13340fccb567d81be513787",
        })
        self.assertEqual(provider["aggregate_link_artifact"], {
            "path": "lvgl-ambiq-lvgl-thread-sync-signal-aggregate.o",
            "size": 1_836,
            "sha256": "4d9ee85c604f6ad3f18a8d547fad3a775f326d2f2cf9c866cc144e1c330bb79b",
        })
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["external_relocations"], {})
        self.assertEqual(provider["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(provider["fixed_address_imports"], {
            "0x004420D1": "source-owned vPortEnterCritical Thumb entry",
            "0x004420E9": "source-owned vPortExitCritical Thumb entry",
            "0x00455C49": "source-owned xTaskGenericNotify Thumb entry",
        })
        self.assertEqual(provider["closed_consumer_relocation_count"], 2)
        self.assertEqual(provider["closed_transitive_relocation_count"], 2)
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
        self.assertEqual(report["missing_provider_count"], 11)
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertNotIn("lv_thread_sync_signal", missing)
        self.assertIn("lv_thread_sync_wait", missing)
        self.assertTrue(report["local_lvgl_draw_dispatch_provider"]["dependency_admitted"])
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "f9d7f5b3fc8db9a19441ec0c4991ac9161c0ae46583e56c2a2298f2794732744",
        )


if __name__ == "__main__":
    unittest.main()
