#!/usr/bin/env python3
"""Host and Cortex-M55 gates for the clean-room NemaVG cap candidate."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/lvgl/runtime_nemavg_stroke_caps_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_nemavg_stroke_caps_host.c"


class NemaVGStrokeCapsCandidateTests(unittest.TestCase):
    def test_host_behavior_and_target_object(self) -> None:
        compiler = shutil.which("clang")
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix="open-cfw-nemavg-caps-") as tmp:
            temporary = Path(tmp)
            host = temporary / "host"
            command = [
                compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), str(SOURCE), str(FIXTURE),
                "-lm", "-o", str(host),
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            subprocess.run([str(host)], check=True, capture_output=True, text=True)

            target = temporary / "caps.o"
            command = [
                compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-mfloat-abi=hard", "-ffreestanding",
                "-fno-builtin", "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(SOURCE.parent), "-c", str(SOURCE), "-o", str(target),
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertGreater(target.stat().st_size, 0)
            undefined = subprocess.run(
                ["nm", "-u", str(target)], check=True,
                capture_output=True, text=True,
            ).stdout.strip()
            self.assertEqual(undefined, "")

    def test_source_is_semantic_c(self) -> None:
        combined = SOURCE.read_text() + HEADER.read_text()
        self.assertEqual(combined.count("SPDX-License-Identifier: MIT"), 2)
        self.assertNotIn("__asm", combined)
        self.assertNotIn(".byte", combined)
        self.assertIn("open_cfw_nemavg_draw_start_cap", combined)
        self.assertIn("open_cfw_nemavg_draw_end_cap", combined)


if __name__ == "__main__":
    unittest.main()
