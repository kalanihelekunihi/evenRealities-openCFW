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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_write_latch_420984.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_write_latch_host.c"


class MspiWriteLatchTests(unittest.TestCase):
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
        cls.lib.open_cfw_write_latch_fixture_status.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_write_latch_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_write_latch_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_write_enable_420984.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_write_disable_4209c4.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_write_latch_fixture_reset()

    def values(self) -> tuple[int, ...]:
        return tuple(self.lib.open_cfw_write_latch_fixture_value(i) for i in range(11))

    def test_authenticated_stock_bodies_pools_and_callers(self) -> None:
        blob = OFFICIAL.read_bytes()
        spans = (
            (0x10984, 0x109BE, "e675df17f3a419b27b088cd7cd0c5785537fe730f597f894ba648e3a76afa3e5"),
            (0x109C4, 0x109FC, "f29c57daa25ee3108fe92b65e0076a21ac49af5ded9c735c33624e26e4400cd2"),
        )
        for start, end, digest in spans:
            body = blob[start:end]
            self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
                (end - start, digest))
        self.assertEqual(blob[0x10978:0x10984].hex(), "4015430084374300242a4300")
        self.assertEqual(blob[0x109BE:0x109C4].hex(), "00009c374300")
        self.assertEqual(blob[0x109FC:0x10A08].hex(), "00e100e018ed00e03c020020")
        callers = {
            0x108C6: "00f05df8", 0x10A66: "fff78dff",
            0x10B62: "fff70fff", 0x10CFA: "fff743fe",
            0x1094C: "00f03af8", 0x10AB8: "fff784ff",
            0x10B8C: "fff71aff",
        }
        for offset, encoding in callers.items():
            self.assertEqual(blob[offset:offset + 4].hex(), encoding)

    def test_write_enable_success_and_failure_contract(self) -> None:
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_write_enable_420984(), 0)
        self.assertEqual(self.values(), (1, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.setUp()
        self.lib.open_cfw_write_latch_fixture_status(17)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_write_enable_420984(), 17)
        self.assertEqual(self.values(),
            (1, 6, 0, 0, 0, 0, 1, 1, 0x3F2, 0x00432650, 0x00433220))

    def test_write_disable_success_and_failure_contract(self) -> None:
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_write_disable_4209c4(), 0)
        self.assertEqual(self.values(), (1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.setUp()
        self.lib.open_cfw_write_latch_fixture_status(23)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_write_disable_4209c4(), 23)
        self.assertEqual(self.values(),
            (1, 4, 0, 0, 0, 0, 1, 2, 0x3FE, 0x00432650, 0x00432D30))

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
