#!/usr/bin/env python3
"""Verify the authenticated TinyFrame snapshot and recovered G2 ABI."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party" / "tinyframe"
PROBE = ROOT / "tests" / "fixtures" / "tinyframe_layout_probe.c"


class TinyFrameSnapshotTests(unittest.TestCase):
    def test_offline_snapshot_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SNAPSHOT / "verify_snapshot.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("snapshot verification passed", result.stdout)
        self.assertIn("eb75483e..a29167a", result.stdout)

    def test_cortex_m55_short_enum_layout_matches_g2_offsets(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not clang:
            self.skipTest("clang is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-tinyframe-") as tmp:
            obj = Path(tmp) / "tinyframe-layout.o"
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-std=c11",
                    "-ffreestanding",
                    "-fshort-enums",
                    "-I",
                    str(SNAPSHOT / "g2-compat"),
                    "-I",
                    str(SNAPSHOT / "g2-config"),
                    "-I",
                    str(SNAPSHOT),
                    "-c",
                    str(PROBE),
                    "-o",
                    str(obj),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue(obj.exists())

    def test_pristine_core_compiles_with_recovered_config(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not clang:
            self.skipTest("clang is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-tinyframe-core-") as tmp:
            obj = Path(tmp) / "TinyFrame.o"
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-Oz",
                    "-std=c11",
                    "-ffreestanding",
                    "-fshort-enums",
                    "-ffunction-sections",
                    "-fdata-sections",
                    "-fno-builtin",
                    "-fno-ident",
                    "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables",
                    "-I",
                    str(SNAPSHOT / "g2-compat"),
                    "-I",
                    str(SNAPSHOT / "g2-config"),
                    "-I",
                    str(SNAPSHOT),
                    "-c",
                    str(SNAPSHOT / "TinyFrame.c"),
                    "-o",
                    str(obj),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            data = obj.read_bytes()
            self.assertTrue(data.startswith(b"\x7fELF"))
            self.assertGreater(len(data), 10000)


if __name__ == "__main__":
    unittest.main()
