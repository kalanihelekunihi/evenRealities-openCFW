# SPDX-License-Identifier: MIT
"""Host and ARM admission checks for the freestanding division provider."""

from __future__ import annotations

import ctypes
import random
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/touch/runtime_touch_unsigned_division.c"
FIXTURE = ROOT / "tests/fixtures/touch_unsigned_division_host.c"
INCLUDE = ROOT / "components/shared/touch"


class TouchUnsignedDivisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "division.dylib"
        subprocess.run([
            "clang", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-dynamiclib", "-I", str(INCLUDE), str(SOURCE), str(FIXTURE),
            "-o", str(library),
        ], check=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.fixture_touch_divide.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.fixture_touch_divide.restype = ctypes.c_uint32
        cls.lib.fixture_touch_remainder.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.fixture_touch_remainder.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_edge_and_deterministic_random_values(self) -> None:
        pairs = [
            (0, 1), (1, 1), (0xFFFFFFFF, 1), (0xFFFFFFFF, 0xFFFFFFFF),
            (0xFFFFFFFF, 3), (0x80000000, 0x7FFFFFFF), (123456789, 1000),
        ]
        generator = random.Random(0x4732)
        pairs.extend((generator.randrange(1 << 32),
                      generator.randrange(1, 1 << 32)) for _ in range(500))
        for numerator, denominator in pairs:
            self.assertEqual(self.lib.fixture_touch_divide(numerator, denominator),
                             numerator // denominator)
            self.assertEqual(self.lib.fixture_touch_remainder(numerator, denominator),
                             numerator % denominator)

    def test_zero_denominator_is_fail_closed(self) -> None:
        self.assertEqual(self.lib.fixture_touch_divide(123, 0), 0)
        self.assertEqual(self.lib.fixture_touch_remainder(123, 0), 123)

    def test_freestanding_armv6m_compiles_without_runtime_references(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            obj = Path(directory) / "division.o"
            subprocess.run([
                "clang", "--target=armv6m-none-eabi", "-mcpu=cortex-m0plus",
                "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-Wall", "-Wextra", "-Werror", "-I", str(INCLUDE),
                "-c", str(SOURCE), "-o", str(obj),
            ], check=True)
            symbols = subprocess.run([
                "/opt/homebrew/opt/llvm/bin/llvm-nm", "-u", str(obj),
            ], check=True, text=True, capture_output=True).stdout.strip()
            self.assertEqual(symbols, "")


if __name__ == "__main__":
    unittest.main()
