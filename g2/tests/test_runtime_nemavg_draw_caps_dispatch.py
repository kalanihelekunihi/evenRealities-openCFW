#!/usr/bin/env python3
"""Host and Cortex-M55 gates for the source-owned NemaVG cap coordinator."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "components/apollo_main/core_overlay/"
    "runtime_nemavg_draw_caps_dispatch.c"
)
FIXTURE = ROOT / "tests/fixtures/runtime_nemavg_draw_caps_dispatch_host.c"


class NemaVGDrawCapsDispatchTests(unittest.TestCase):
    def test_host_behavior_and_target_contract(self) -> None:
        compiler = shutil.which("clang")
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(
            prefix="open-cfw-nemavg-draw-caps-"
        ) as directory:
            output = Path(directory)
            host = output / "host"
            subprocess.run(
                [
                    compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                    str(FIXTURE), "-o", str(host),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [str(host)], check=True, capture_output=True, text=True
            )

            target = output / "dispatch.o"
            subprocess.run(
                [
                    compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-ffreestanding", "-fno-builtin", "-Oz",
                    "-std=c11", "-Wall", "-Wextra", "-Werror", "-c",
                    str(SOURCE), "-o", str(target),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            undefined_lines = subprocess.run(
                ["nm", "-u", str(target)], check=True,
                capture_output=True, text=True,
            ).stdout.splitlines()
            undefined = {
                line.split()[-1] for line in undefined_lines if line.split()
            }
            self.assertEqual(
                undefined,
                {
                    "open_cfw_retained_nemavg_draw_end_cap",
                    "open_cfw_retained_nemavg_draw_start_cap",
                    "open_cfw_retained_nemavg_set_error",
                },
            )

    def test_source_is_semantic_c_with_exact_context_contract(self) -> None:
        text = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: MIT", text)
        self.assertIn("0x20074F04", text)
        self.assertIn("0x114", text)
        self.assertIn("0x118", text)
        self.assertNotIn("__asm", text)
        self.assertNotIn(".byte", text)


if __name__ == "__main__":
    unittest.main()
