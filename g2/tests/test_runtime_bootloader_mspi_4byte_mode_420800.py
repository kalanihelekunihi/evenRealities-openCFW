from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_4byte_mode_420800.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_4byte_mode_host.c"


class Mspi4ByteModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "fixture.dylib" if sys.platform == "darwin" else "fixture.so"
        cls.library_path = Path(cls.temporary.name) / suffix
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
             "-Wall", "-Wextra", "-Werror", str(FIXTURE),
             *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
             "-o", str(cls.library_path)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.lib.open_cfw_4byte_mode_fixture_config.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_4byte_mode_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_4byte_mode_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_4byte_mode_420800.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_4byte_mode_fixture_reset()

    def value(self, field: int) -> int:
        return self.lib.open_cfw_4byte_mode_fixture_value(field)

    def test_authenticated_stock_body_and_caller(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10800:0x1086C]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
            (108, "717b79259ef6b857ffeb0d87f6488ad7616de5e478960b5f311963b989fc9cee"))
        self.assertEqual(blob[0x10926:0x1092A].hex(), "fff76bff")

    def test_mode_bit_and_zero_initialized_read(self) -> None:
        self.lib.open_cfw_4byte_mode_fixture_config(0, 0x20)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_4byte_mode_420800(), 1)
        self.assertEqual(tuple(self.value(i) for i in range(4)), (0x15, 1, 0, 0))
        self.assertEqual((self.value(7), self.value(8)), (1, 0))
        self.lib.open_cfw_4byte_mode_fixture_config(0, 0xFF)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_4byte_mode_420800(), 1)

    def test_three_byte_mode_logs_and_returns_zero(self) -> None:
        self.lib.open_cfw_4byte_mode_fixture_config(0, 0xDF)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_4byte_mode_420800(), 0)
        self.assertEqual(tuple(self.value(i) for i in range(4, 7)),
            (0x3B8, 0x00432D0C, 0x00433524))
        self.assertEqual((self.value(7), self.value(8)), (1, 1))

    def test_read_failure_is_logged_and_raw_status_is_returned(self) -> None:
        self.lib.open_cfw_4byte_mode_fixture_config(9, 0x20)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_4byte_mode_420800(), 9)
        self.assertEqual(tuple(self.value(i) for i in range(4, 7)),
            (0x3B0, 0x00433814, 0x00433524))
        self.assertEqual((self.value(7), self.value(8)), (1, 1))

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "target.o"
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "--target=arm-none-eabi",
             "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
             "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-c",
             str(SOURCE), "-o", str(output)], check=True, capture_output=True)
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
