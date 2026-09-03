#!/usr/bin/env python3
"""Hostile-input and target-ABI gates for the isolated LVGL mutex provider."""

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
SOURCE = RUNTIME / "lvgl_ambiq_lvgl_mutex_provider.c"
HOST_CONFIG = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_mutex_provider_host_config.h"
HOST_FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_lvgl_mutex_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"
SYMBOLS = {"lv_mutex_delete", "lv_mutex_init", "lv_mutex_lock", "lv_mutex_unlock"}


class LVGLMutexProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-mutex-provider-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_hostile_and_provider_forwarding_oracle_is_sanitizer_clean(self) -> None:
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

    def test_manifest_pins_exact_abi_and_fixed_provider_closure(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_mutex_provider"]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_lvgl_mutex_provider.o", "size": 1_776,
            "sha256": "e8fc442adba6730f9d00ee07a2b67e57f711831b4f2f92328c1ad620349390a6",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-mutex-provider.o", "size": 2_168,
            "sha256": "5067d94d102f8f6ce7090534a482657761ddee527f796db2cb330bedb36baf3a",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_lvgl_mutex_provider_abi.o", "size": 2_056,
            "sha256": "2067a9388bfeac43fe5ac2594c8bbdd35047b913cf3c5cb28ff442f319736d64",
        })
        self.assertEqual(set(provider["required_exports"]), SYMBOLS)
        self.assertEqual(set(provider["all_external_exports"]), SYMBOLS)
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["external_relocations"], {})
        self.assertEqual(provider["fixed_address_import_count"], 6)
        self.assertEqual(set(provider["fixed_address_imports"]), {
            "0x004416D7", "0x00441711", "0x00441751",
            "0x00441EA3", "0x004420D1", "0x004420E9",
        })
        self.assertEqual(provider["abi_probe_external_relocations"], {
            symbol: {"R_ARM_THM_JUMP24": 1} for symbol in SYMBOLS
        })
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_consumer_and_sync_provider_residual_boundaries_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_lvgl_mutex_provider"]
        relocations = provider["closed_consumer_relocations"]
        self.assertEqual(set(relocations), SYMBOLS)
        self.assertEqual(provider["closed_consumer_relocation_count"], 4)
        self.assertTrue(all(
            row["relocation_count"] > 0
            for owners in relocations.values()
            for row in owners
        ))
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["commit"], "344c7c318047b7348e1be8572a9fd4260c251cfa")
        self.assertEqual(upstream["freertos_commit"], "def7d2df2b0506d3d249334974f51e427c17a41c")
        self.assertEqual(len(upstream["source_git_blobs"]), 3)
        self.assertEqual(report["missing_provider_count"], 0)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertTrue(SYMBOLS.isdisjoint(missing))
        self.assertTrue({
            "lv_thread_sync_delete", "lv_thread_sync_init",
            "lv_thread_sync_signal", "lv_thread_sync_wait",
        }.isdisjoint(missing))


if __name__ == "__main__":
    unittest.main()
