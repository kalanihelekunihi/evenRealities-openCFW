#!/usr/bin/env python3
"""Verify the DaveGamble/cJSON snapshot and its Cortex-M55 compile probe."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party/cJSON"
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


EXPECTED_PUBLIC_SECTIONS = {
    ".text.cJSON_Parse",
    ".text.cJSON_ParseWithOpts",
    ".text.cJSON_Delete",
    ".text.cJSON_GetObjectItem",
    ".text.cJSON_GetArraySize",
    ".text.cJSON_GetArrayItem",
    ".text.cJSON_IsArray",
}


class CjsonSnapshotTests(unittest.TestCase):
    def test_offline_snapshot_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SNAPSHOT / "verify_snapshot.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("snapshot verification passed", result.stdout)
        self.assertIn("production: excluded", result.stdout)

    def test_production_exclusion_decision_is_explicit(self) -> None:
        import json

        provenance = json.loads((SNAPSHOT / "PROVENANCE.json").read_text(encoding="utf-8"))
        boundary = provenance["g2_boundary"]
        self.assertFalse(boundary["production_routed"])
        self.assertIn("production-excluded", boundary["production_decision"])
        self.assertEqual(boundary["linked_functions"], 21)
        self.assertEqual(boundary["stock_body_bytes"], 2572)
        self.assertEqual(boundary["stock_span"], "[0x004D798C,0x004D83D8)")

    def test_apple_clang_cortex_m55_compile_profile(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not clang:
            self.skipTest("clang is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-cjson-") as tmp:
            obj = Path(tmp) / "cjson.o"
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-Oz",
                    "-std=c11",
                    "-ffunction-sections",
                    "-fdata-sections",
                    "-fno-builtin",
                    "-fno-ident",
                    "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables",
                    "-nostdinc",
                    "-I",
                    str(SNAPSHOT / "g2-compat"),
                    "-I",
                    str(SNAPSHOT),
                    "-c",
                    str(SNAPSHOT / "cJSON.c"),
                    "-o",
                    str(obj),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            _data, sections = apollo_overlay.parse_elf32(obj)
            observed = {
                str(section["name"]): int(section["size"])
                for section in sections
                if str(section["name"]) in EXPECTED_PUBLIC_SECTIONS
            }
            self.assertEqual(set(observed), EXPECTED_PUBLIC_SECTIONS)
            self.assertTrue(all(size > 0 for size in observed.values()))


if __name__ == "__main__":
    unittest.main()
