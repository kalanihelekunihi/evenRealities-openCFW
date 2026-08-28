#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Behavior and target-build tests for touch sensing/gesture source."""

from __future__ import annotations

import ctypes
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/touch/runtime_touch_sensing.c"
FIXTURE = ROOT / "tests/fixtures/touch_sensing_host.c"


class TouchSensingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="open-cfw-touch-sensing-")
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("touch_sensing" + suffix)
        command = ["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror"]
        command += ["-dynamiclib"] if platform.system() == "Darwin" else ["-shared", "-fPIC"]
        command += [str(FIXTURE), "-o", str(library)]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        for name in ("open_cfw_test_touch_msc_scan",
                     "open_cfw_test_touch_power_transitions",
                     "open_cfw_test_touch_gestures"):
            getattr(cls.lib, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_authenticated_msc_loop_contract(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_msc_scan(), 0x1F)

    def test_all_observed_power_transitions(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_power_transitions(), 0x1F)

    def test_direction_long_press_fast_click_and_calibration(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_gestures(), 0x1F)

    def test_freestanding_cortex_m0plus_compile(self) -> None:
        clang = shutil.which("clang")
        self.assertIsNotNone(clang)
        with tempfile.TemporaryDirectory(prefix="open-cfw-touch-sensing-target-") as tmp:
            obj = Path(tmp) / "touch_sensing.o"
            subprocess.run([
                clang, "--target=thumbv6m-none-eabi", "-mthumb",
                "-mcpu=cortex-m0plus", "-O2", "-ffreestanding",
                "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                "-Wall", "-Wextra", "-Werror", "-I" + str(SOURCE.parent),
                "-c", str(SOURCE), "-o", str(obj),
            ], cwd=ROOT, check=True, capture_output=True)
            self.assertGreater(obj.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
