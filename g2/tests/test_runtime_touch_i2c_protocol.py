#!/usr/bin/env python3
"""Behavior and target-build tests for touch-controller I2C source."""

from __future__ import annotations

import ctypes
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/touch/runtime_touch_i2c_protocol.c"
FIXTURE = ROOT / "tests/fixtures/touch_i2c_protocol_host.c"


class TouchI2cProtocolSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="open-cfw-touch-i2c-")
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("touch_i2c" + suffix)
        command = ["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror"]
        command += ["-dynamiclib"] if platform.system() == "Darwin" else ["-shared", "-fPIC"]
        command += [str(FIXTURE), "-o", str(library)]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        for name in (
            "open_cfw_test_touch_init_commands",
            "open_cfw_test_touch_report_persistence",
            "open_cfw_test_touch_event_fifo_power",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_command_surface(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_init_commands(), 0xFF)

    def test_report_and_deferred_persistence(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_report_persistence(), 0x1F)

    def test_event_fifo_and_power_contracts(self) -> None:
        self.assertEqual(self.lib.open_cfw_test_touch_event_fifo_power(), 0x0F)

    def test_freestanding_cortex_m0plus_compile(self) -> None:
        clang = shutil.which("clang")
        self.assertIsNotNone(clang)
        with tempfile.TemporaryDirectory(prefix="open-cfw-touch-target-") as tmp:
            obj = Path(tmp) / "touch.o"
            subprocess.run(
                [
                    clang, "--target=thumbv6m-none-eabi", "-mthumb",
                    "-mcpu=cortex-m0plus", "-O2", "-ffreestanding",
                    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                    "-Wall", "-Wextra", "-Werror", "-I" + str(SOURCE.parent),
                    "-c", str(SOURCE), "-o", str(obj),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
            )
            self.assertGreater(obj.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
