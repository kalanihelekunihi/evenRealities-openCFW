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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_read_transfer_4205f4.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_read_transfer_host.c"


class MspiReadTransferTests(unittest.TestCase):
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
        cls.lib.open_cfw_read_transfer_fixture_config.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_read_transfer_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_read_transfer_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_read_transfer_4205f4.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_void_p, ctypes.c_uint32]
        cls.lib.open_cfw_bootloader_mspi_read_transfer_4205f4.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_read_transfer_fixture_reset()

    def value(self, field: int) -> int:
        return self.lib.open_cfw_read_transfer_fixture_value(field)

    def call(self, instruction=0x12345, address=0x123456, present=1,
             buffer=0x20001000, length=17):
        return self.lib.open_cfw_bootloader_mspi_read_transfer_4205f4(
            instruction, address, present, buffer, length)

    def test_authenticated_stock_body_and_source(self) -> None:
        body = OFFICIAL.read_bytes()[0x105F4:0x1069E]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
                         (170, "7fe24d8d1ac2fda0dcce1f4e7d4364b2bbe3df283c05000ab32d357de04a6749"))

    def test_validation_short_circuits(self) -> None:
        self.lib.open_cfw_read_transfer_fixture_config(0, 0)
        self.assertEqual(self.call(), 2)
        self.assertEqual(self.value(12), 0)
        self.lib.open_cfw_read_transfer_fixture_config(1, 0)
        self.assertEqual(self.call(buffer=None), 6)
        self.assertEqual(self.call(length=0), 6)
        self.assertEqual(self.call(address=0x02000000, present=0), 5)
        self.assertEqual(self.value(12), 0)

    def test_descriptor_and_success_contract(self) -> None:
        self.assertEqual(self.call(), 0)
        self.assertEqual(tuple(self.value(i) for i in range(11)),
                         (0x1234, 17, 0, 1, 0x123456, 1, 0x2345, 1,
                          0, 0x20001000, 1000000))
        self.assertEqual((self.value(12), self.value(13)), (1, 0))
        self.lib.open_cfw_read_transfer_fixture_reset()
        self.assertEqual(self.call(address=0x123456, present=0), 0)
        self.assertEqual((self.value(3), self.value(4)), (0, 0))

    def test_hal_failure_is_logged_and_returned(self) -> None:
        self.lib.open_cfw_read_transfer_fixture_config(1, 9)
        self.assertEqual(self.call(), 9)
        self.assertEqual((self.value(12), self.value(13)), (1, 1))
        self.assertEqual((self.value(6), self.value(4), self.value(1), self.value(11)),
                         (0x2345, 0x123456, 17, 9))

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
