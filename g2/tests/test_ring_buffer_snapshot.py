#!/usr/bin/env python3
"""Verify the Ring-Buffer snapshot and isolated Cortex-M55 compile probe."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party/ring-buffer"
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


EXPECTED_TEXT_SIZES = {
    ".text.ring_buffer_init": 40,
    ".text.ring_buffer_queue": 38,
    ".text.ring_buffer_is_full": 18,
    ".text.ring_buffer_queue_arr": 26,
    ".text.ring_buffer_dequeue": 32,
    ".text.ring_buffer_is_empty": 12,
    ".text.ring_buffer_dequeue_arr": 48,
    ".text.ring_buffer_peek": 34,
    ".text.ring_buffer_num_items": 12,
}


class RingBufferSnapshotTests(unittest.TestCase):
    def test_offline_snapshot_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SNAPSHOT / "verify_snapshot.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("snapshot verification passed", result.stdout)

    def test_apple_clang_cortex_m55_compile_profile(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not clang:
            self.skipTest("clang is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-ring-buffer-") as tmp:
            obj = Path(tmp) / "ringbuffer.o"
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
                    str(SNAPSHOT / "ringbuffer.c"),
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
                if str(section["name"]).startswith(".text.ring_buffer")
            }
            self.assertEqual(observed, EXPECTED_TEXT_SIZES)
            retained = sum(
                observed[f".text.{name}"]
                for name in (
                    "ring_buffer_is_empty",
                    "ring_buffer_is_full",
                    "ring_buffer_init",
                    "ring_buffer_queue",
                    "ring_buffer_queue_arr",
                    "ring_buffer_dequeue",
                    "ring_buffer_dequeue_arr",
                )
            )
            self.assertEqual(retained, 214)


if __name__ == "__main__":
    unittest.main()
