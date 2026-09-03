#!/usr/bin/env python3
"""Hostile-input and exact target gates for the Ambiq target-runtime tranche."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_target_runtime_provider.c"
)
FIXTURE = ROOT / "tests/fixtures/lvgl_ambiq_target_runtime_provider_host.c"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"

PROVIDER_SYMBOLS = {
    "__aeabi_d2lz", "__aeabi_f2ulz", "__aeabi_memcpy4", "memcpy", "memset",
}


class TargetRuntimeProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="lvgl-target-runtime-")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_hostile_and_sampled_host_oracle_is_sanitizer_clean(self) -> None:
        executable = Path(self.temporary.name) / "host-oracle"
        subprocess.run([
            self.clang, "-std=gnu11", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
            "-fno-builtin", "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
            "-I", str(ROOT / "third_party/lvgl-ambiq-backend/g2-runtime"),
            str(SOURCE), str(FIXTURE), "-o", str(executable),
        ], cwd=ROOT, check=True, capture_output=True, text=True)
        environment = dict(os.environ)
        environment["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        subprocess.run(
            [str(executable)], cwd=ROOT, env=environment, check=True,
            capture_output=True, text=True,
        )

    def test_manifest_pins_target_abi_and_zero_import_provider(self) -> None:
        provider = json.loads(MANIFEST.read_text(encoding="utf-8"))[
            "local_target_runtime_provider"
        ]
        self.assertEqual(provider["target_source_artifact"], {
            "path": "lvgl_ambiq_target_runtime_provider.o",
            "size": 2_308,
            "sha256": "2a43b8130fe85d3e2b27e25efa386ac92f466fb83de85c6f6c083b9643a92a88",
        })
        self.assertEqual(provider["abi_probe_artifact"], {
            "path": "lvgl_ambiq_target_runtime_provider_abi.o",
            "size": 1_648,
            "sha256": "918bd5ffff80d2240c8924c7b299f80a286d1c13002a656a5a9acb670c805c4b",
        })
        self.assertEqual(provider["artifact"], {
            "path": "lvgl-ambiq-target-runtime-provider.o",
            "size": 2_736,
            "sha256": "c009f816e4d59547783e88272d77bf9fccaf765f5d66d6339fc3296ca4256bf7",
        })
        self.assertEqual(set(provider["required_exports"]), PROVIDER_SYMBOLS)
        self.assertEqual(set(provider["all_external_exports"]), PROVIDER_SYMBOLS)
        self.assertEqual(provider["elf_undefined_symbols"], [])
        self.assertEqual(provider["external_relocations"], {})
        self.assertEqual(provider["fixed_address_import_count"], 0)
        self.assertTrue(provider["hard_float_to_aeabi_base_pcs_marshalling_verified"])
        self.assertEqual(provider["abi_probe_external_relocations"], {
            "__aeabi_d2lz": {"R_ARM_THM_JUMP24": 1},
            "__aeabi_f2ulz": {"R_ARM_THM_JUMP24": 1},
        })
        self.assertTrue(provider["source_admitted"])
        self.assertFalse(provider["production_overlay_registered"])
        self.assertFalse(provider["hardware_qualified"])

    def test_every_closed_symbol_has_a_pinned_consumer(self) -> None:
        provider = json.loads(MANIFEST.read_text(encoding="utf-8"))[
            "local_target_runtime_provider"
        ]
        relocations = provider["closed_consumer_relocations"]
        self.assertEqual(set(relocations), PROVIDER_SYMBOLS)
        self.assertEqual(provider["closed_consumer_relocation_count"], 21)
        self.assertEqual(
            sum(row["relocation_count"] for rows in relocations.values() for row in rows),
            21,
        )
        for symbol, owners in relocations.items():
            self.assertTrue(owners, symbol)
            self.assertTrue(all(row["relocation_count"] > 0 for row in owners), symbol)

    def test_upstream_algorithm_boundary_and_residual_are_exact(self) -> None:
        report = json.loads(MANIFEST.read_text(encoding="utf-8"))
        provider = report["local_target_runtime_provider"]
        upstream = provider["authenticated_upstream"]
        self.assertEqual(upstream["repository"], "https://github.com/llvm/llvm-project.git")
        self.assertEqual(upstream["tag"], "llvmorg-20.1.8")
        self.assertEqual(upstream["commit"], "87f0227cb60147a26a1eeb4fb06e3b505e9c7261")
        self.assertEqual(upstream["license"], "Apache-2.0 WITH LLVM-exception")
        self.assertEqual(len(upstream["algorithmic_sources"]), 4)
        self.assertEqual(report["missing_provider_count"], 0)
        self.assertEqual(
            report["maximal_scoped_candidate_closure"]["expected_residual_symbol_digest"],
            "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        )
        missing = {row["symbol"] for row in report["missing_provider_ledger"]}
        self.assertTrue(PROVIDER_SYMBOLS.isdisjoint(missing))


if __name__ == "__main__":
    unittest.main()
