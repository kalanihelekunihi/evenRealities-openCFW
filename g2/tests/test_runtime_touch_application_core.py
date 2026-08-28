#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Behavior and target-build tests for the Touch application core."""

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
SOURCE = TOUCH / "runtime_touch_application_core.c"
FIXTURE = ROOT / "tests/fixtures/touch_application_core_host.c"


class TouchApplicationCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory(prefix="open-cfw-touch-app-core-")
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("touch_app_core" + suffix)
        command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror"]
        command += ["-dynamiclib"] if platform.system() == "Darwin" else ["-shared", "-fPIC"]
        command += [str(FIXTURE), "-o", str(library)]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_touch_application_data_core.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_touch_application_run_core.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_touch_application_core_null_guards.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_data_pipeline_order_and_results(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_application_data_core(), 0xF)

    def test_top_level_run_cleanup_and_timeout(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_application_run_core(), 0x7)

    def test_missing_contracts_fail_closed(self) -> None:
        self.assertEqual(
            self.lib.open_cfw_test_touch_application_core_null_guards(), 0)

    def test_freestanding_cortex_m0plus_compile(self) -> None:
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        output = Path(self.temp.name) / "touch-app-core.o"
        subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], cwd=ROOT, check=True, capture_output=True)
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
