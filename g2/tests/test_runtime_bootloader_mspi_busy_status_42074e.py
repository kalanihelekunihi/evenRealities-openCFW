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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_busy_status_42074e.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_busy_status_host.c"


class MspiBusyStatusTests(unittest.TestCase):
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
        cls.lib.open_cfw_busy_status_fixture_config.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_busy_status_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_busy_status_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_busy_status_42074e.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_busy_status_fixture_reset()

    def value(self, field: int) -> int:
        return self.lib.open_cfw_busy_status_fixture_value(field)

    def test_authenticated_stock_body_and_source(self) -> None:
        body = OFFICIAL.read_bytes()[0x1074E:0x107A2]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
                         (84, "33e47f7e0bf37502f2f2dd20196d15b67a1f3ef336cd48538ac99f6ceed0e6e5"))

    def test_clear_and_busy_status_bits(self) -> None:
        self.lib.open_cfw_busy_status_fixture_config(0, 0x00)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_busy_status_42074e(), 0)
        self.assertEqual(tuple(self.value(i) for i in range(4)),
                         (0x05, 1, 0, 0))
        self.assertEqual((self.value(7), self.value(8)), (1, 0))

        self.lib.open_cfw_busy_status_fixture_reset()
        self.lib.open_cfw_busy_status_fixture_config(0, 0x80)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_busy_status_42074e(), 1)
        self.lib.open_cfw_busy_status_fixture_config(0, 0xFF)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_busy_status_42074e(), 1)
        self.lib.open_cfw_busy_status_fixture_config(0, 0x7F)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_busy_status_42074e(), 0)

    def test_read_failure_is_logged_and_returned(self) -> None:
        self.lib.open_cfw_busy_status_fixture_config(9, 0x80)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_busy_status_42074e(), 9)
        self.assertEqual((self.value(7), self.value(8)), (1, 1))
        self.assertEqual(tuple(self.value(i) for i in range(4)),
                         (0x05, 1, 0, 0))
        self.assertEqual(tuple(self.value(i) for i in range(4, 7)),
                         (0x376, 0x00433508, 0x00433B00))

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
