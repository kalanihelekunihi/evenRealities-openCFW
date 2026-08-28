#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Behavior and target-build tests for final Touch platform completion."""

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
SOURCE = TOUCH / "runtime_touch_platform_completion.c"
FIXTURE = ROOT / "tests/fixtures/touch_platform_completion_host.c"


class TouchPlatformCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None: raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory(prefix="open-cfw-touch-platform-final-")
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("touch_platform_final" + suffix)
        command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror"]
        command += ["-dynamiclib"] if platform.system() == "Darwin" else ["-shared", "-fPIC"]
        command += [str(FIXTURE), "-o", str(library)]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        for name in ("runtime", "mapping_profiles", "register_builder", "completion_null_guards"):
            getattr(cls.lib, "open_cfw_test_touch_platform_" + name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_selected_runtime_fault_and_handoff(self):
        self.assertEqual(self.lib.open_cfw_test_touch_platform_runtime(), 0xF)

    def test_source_owned_mapping_and_profiles(self):
        self.assertEqual(self.lib.open_cfw_test_touch_platform_mapping_profiles(), 0x3)

    def test_register_image_builder(self):
        self.assertEqual(self.lib.open_cfw_test_touch_platform_register_builder(), 1)

    def test_missing_contracts_fail_closed(self):
        self.assertEqual(self.lib.open_cfw_test_touch_platform_completion_null_guards(), 0)

    def test_freestanding_cortex_m0plus_compile(self):
        clang = shutil.which("clang")
        if clang is None: self.skipTest("clang unavailable")
        output = Path(self.temp.name) / "touch-platform-final.o"
        subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], cwd=ROOT, check=True, capture_output=True)
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__": unittest.main()
