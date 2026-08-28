#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Behavior and target-build tests for Touch platform wrappers."""

from __future__ import annotations

import ctypes
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
SOURCE = TOUCH / "runtime_touch_platform_wrappers.c"
FIXTURE = ROOT / "tests/fixtures/touch_platform_wrappers_host.c"


class TouchPlatformWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory(prefix="open-cfw-touch-platform-")
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("touch_platform" + suffix)
        command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror"]
        command += ["-dynamiclib"] if platform.system() == "Darwin" else ["-shared", "-fPIC"]
        command += [str(FIXTURE), "-o", str(library)]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_touch_platform_wrappers.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_touch_platform_null_guards.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_all_recovered_wrapper_semantics(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_platform_wrappers(), 0xFFF)

    def test_absent_provider_fails_closed(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_platform_null_guards(), 0)

    def test_freestanding_cortex_m0plus_compile(self) -> None:
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        output = Path(self.temp.name) / "touch-platform.o"
        subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], cwd=ROOT, check=True, capture_output=True)
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
