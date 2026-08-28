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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_driver_init_420476.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_driver_init_host.c"
BASE = 0x00410000


def thumb_bl_target(blob: bytes, address: int) -> int | None:
    offset = address - BASE
    first = int.from_bytes(blob[offset:offset + 2], "little")
    second = int.from_bytes(blob[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    delta = ((sign << 24) | (i1 << 23) | (i2 << 22) |
             ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1))
    if delta & (1 << 24):
        delta -= 1 << 25
    return address + 4 + delta


class MspiDriverInitTests(unittest.TestCase):
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
        cls.lib.open_cfw_bootloader_mspi_driver_init_420476.restype = ctypes.c_uint32
        cls.lib.open_cfw_driver_init_fixture_status.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_driver_init_fixture_identifier.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_driver_init_fixture_record.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_driver_init_fixture_record.restype = ctypes.c_uint32
        cls.lib.open_cfw_driver_init_fixture_log.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_driver_init_fixture_log.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_driver_init_fixture_reset()

    def records(self):
        count = self.lib.open_cfw_driver_init_fixture_record_count()
        return [(self.lib.open_cfw_driver_init_fixture_record(i, 0),
                 self.lib.open_cfw_driver_init_fixture_record(i, 1))
                for i in range(count)]

    def logs(self):
        count = self.lib.open_cfw_driver_init_fixture_log_count()
        return [tuple(self.lib.open_cfw_driver_init_fixture_log(i, f)
                      for f in range(4)) for i in range(count)]

    def test_authenticated_stock_body_calls_literals_and_source(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10476:0x1052A]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
                         (180, "5be1a86e4e5b4c50b9d8eac9043747caec7abd1ad916fc13ceace39fa5ddb662"))
        calls = {
            0x00420480: 0x00420254, 0x004204A6: 0x004176CE,
            0x004204AE: 0x0041F9D8, 0x004204B2: 0x0042052A,
            0x004204B6: 0x00420F10, 0x004204BA: 0x004201BA,
            0x004204BE: 0x00420F10, 0x004204C4: 0x0042059E,
            0x004204EA: 0x004176CE, 0x0042050E: 0x004176CE,
            0x00420512: 0x00420890, 0x00420518: 0x00420C5C,
            0x0042051C: 0x0041FE62, 0x00420520: 0x0041FE28,
        }
        for site, target in calls.items():
            self.assertEqual(thumb_bl_target(blob, site), target)
        self.assertEqual(int.from_bytes(blob[0x10C40:0x10C44], "little"), 0x200270D8)
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
                         (5602, "65a390f2c770079f4255ea489cc02bc0f593674de7688d3fb550f201ebc8785f"))

    def test_success_order_identifier_and_logs(self) -> None:
        self.lib.open_cfw_driver_init_fixture_identifier(0x00123456)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_driver_init_420476(), 0)
        self.assertEqual(self.records(), [(0, 0), (1, 10), (2, 0), (3, 0),
                                          (4, 0), (3, 0), (5, 0), (6, 0),
                                          (7, 1), (8, 0), (9, 0)])
        self.assertEqual(self.logs(), [(3, 0x292, 0x00433AD8, 0x00123456)])

    def test_initializer_and_identifier_failures_short_circuit(self) -> None:
        self.lib.open_cfw_driver_init_fixture_status(0, 7)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_driver_init_420476(), 7)
        self.assertEqual(self.records(), [(0, 0)])
        self.assertEqual(self.logs(), [(1, 0x284, 0x004337E4, 7)])

        self.lib.open_cfw_driver_init_fixture_reset()
        self.lib.open_cfw_driver_init_fixture_status(5, 9)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_driver_init_420476(), 9)
        self.assertEqual([item[0] for item in self.records()], [0, 1, 2, 3, 4, 3, 5])
        self.assertEqual(self.logs(), [(1, 0x28E, 0x00433AC4, 9)])

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
