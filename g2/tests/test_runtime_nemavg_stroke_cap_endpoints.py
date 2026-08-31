#!/usr/bin/env python3
"""Host and Cortex-M55 checks for source-owned NemaVG cap endpoints."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_nemavg_stroke_cap_endpoints.c"
FIXTURE = ROOT / "tests/fixtures/runtime_nemavg_stroke_cap_endpoints_host.c"
INCLUDE = SOURCE.parent
APPLE_CLANG = Path(
    "/Applications/Xcode-beta.app/Contents/Developer/Toolchains/"
    "XcodeDefault.xctoolchain/usr/bin/clang"
)
APPLE_NM = APPLE_CLANG.with_name("llvm-nm")


class NemaVGStrokeCapEndpointTests(unittest.TestCase):
    def test_host_geometry_and_fail_closed_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="open-cfw-nemavg-endpoint-") as tmp:
            executable = Path(tmp) / "endpoint-host"
            subprocess.run(
                [
                    "cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-fno-strict-aliasing", "-I", str(INCLUDE), str(FIXTURE),
                    "-lm", "-o", str(executable),
                ],
                check=True,
            )
            subprocess.run([str(executable)], check=True)

    def test_cortex_m55_object_has_only_authenticated_providers(self) -> None:
        if not APPLE_CLANG.is_file() or not APPLE_NM.is_file():
            self.skipTest("reviewed Apple Clang toolchain is unavailable")
        with tempfile.TemporaryDirectory(prefix="open-cfw-nemavg-endpoint-") as tmp:
            object_path = Path(tmp) / "endpoints.o"
            subprocess.run(
                [
                    str(APPLE_CLANG), "--target=arm-none-eabi",
                    "-mcpu=cortex-m55", "-mthumb", "-mfpu=fp-armv8",
                    "-mfloat-abi=hard", "-Oz", "-ffreestanding",
                    "-fno-builtin", "-fno-jump-tables", "-fomit-frame-pointer",
                    "-mno-unaligned-access", "-ffunction-sections",
                    "-fdata-sections", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi", "-mllvm",
                    "-enable-machine-outliner=never", "-Wall", "-Wextra",
                    "-Werror", "-fno-ident", "-c", str(SOURCE),
                    "-o", str(object_path),
                ],
                check=True,
            )
            undefined = {
                line.strip().split()[-1]
                for line in subprocess.run(
                    [str(APPLE_NM), "-u", str(object_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.splitlines()
                if line.strip()
            }
            self.assertEqual(
                undefined,
                {
                    "open_cfw_retained_nemavg_calculate_steps",
                    "open_cfw_retained_nemavg_cos",
                    "open_cfw_retained_nemavg_enable_aa",
                    "open_cfw_retained_nemavg_raster_quad",
                    "open_cfw_retained_nemavg_raster_triangle",
                    "open_cfw_retained_nemavg_raster_triangle_fan",
                    "open_cfw_retained_nemavg_restore_aa",
                    "open_cfw_retained_nemavg_set_error",
                    "open_cfw_retained_nemavg_sin",
                    "open_cfw_retained_nemavg_sqrt",
                },
            )


if __name__ == "__main__":
    unittest.main()
