#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Behavior and target-build tests for the clean-room Touch Em_EEPROM."""

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
SOURCE = TOUCH / "runtime_touch_emeeprom_clean_room.c"
FIXTURE = ROOT / "tests/fixtures/touch_emeeprom_clean_room_host.c"


class TouchEmEepromCleanRoomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None: raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory(prefix="open-cfw-touch-eeprom-")
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("touch_eeprom" + suffix)
        command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror"]
        command += ["-dynamiclib"] if platform.system() == "Darwin" else ["-shared", "-fPIC"]
        command += [str(FIXTURE), "-o", str(library)]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_touch_eeprom_simple.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_touch_eeprom_extended.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_touch_eeprom_primitives.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_touch_eeprom_null_guards.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_simple_mode_read_write_erase(self):
        self.assertEqual(self.lib.open_cfw_test_touch_eeprom_simple(), 0x1F)

    def test_extended_mode_wear_sequence_and_crc_fallback(self):
        self.assertEqual(self.lib.open_cfw_test_touch_eeprom_extended(), 0x1F)

    def test_crc_geometry_and_validation(self):
        self.assertEqual(self.lib.open_cfw_test_touch_eeprom_primitives(), 1)

    def test_missing_contracts_fail_closed(self):
        self.assertEqual(self.lib.open_cfw_test_touch_eeprom_null_guards(), 0)

    def test_freestanding_cortex_m0plus_compile(self):
        clang = shutil.which("clang")
        if clang is None: self.skipTest("clang unavailable")
        output = Path(self.temp.name) / "touch-eeprom.o"
        subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(SOURCE), "-o", str(output),
        ], cwd=ROOT, check=True, capture_output=True)
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__": unittest.main()
