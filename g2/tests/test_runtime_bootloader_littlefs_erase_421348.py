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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_littlefs_erase_421348.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_littlefs_erase_host.c"


class LittlefsEraseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "littlefs-erase.dylib" if sys.platform == "darwin" else "littlefs-erase.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library),
            ],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_littlefs_erase_fixture_status.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_littlefs_erase_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_littlefs_erase_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_littlefs_erase_421348.argtypes = [
            ctypes.c_void_p, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_littlefs_erase_421348.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_littlefs_erase_fixture_reset()

    def value(self, index: int) -> int:
        return self.lib.open_cfw_littlefs_erase_fixture_value(index)

    def invoke(self, block: int) -> int:
        return self.lib.open_cfw_bootloader_littlefs_erase_421348(None, block)

    def test_authenticated_body_gap_driver_log_and_configuration(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x11348:0x11372]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (42, "df1788d1db60223b7af5050ab14307a3bf27f30fc6d61917adee77f679b3b872"),
        )
        gap = blob[0x11372:0x113D4]
        self.assertEqual(
            (len(gap), hashlib.sha256(gap).hexdigest()),
            (98, "69c23d9c23df577cb63407fd0899c61afc102f15fc1a38f710fde8d829b71d2b"),
        )
        self.assertEqual(blob[0x11354:0x11358].hex(), "fff758fb")
        self.assertEqual(blob[0x11364:0x11368].hex(), "f4f723fe")
        self.assertEqual(int.from_bytes(blob[0x113D0:0x113D4], "little"), 0x00432568)
        config = blob[0x21070:0x210A0]
        self.assertEqual(int.from_bytes(config[12:16], "little"), 0x00421349)

    def test_success_forwards_stock_partition_address(self) -> None:
        self.assertEqual(self.invoke(3), 0)
        self.assertEqual((self.value(0), self.value(1)), (0x01403000, 0))

    def test_device_failure_logs_complete_tuple_and_maps_to_lfs_err_io(self) -> None:
        self.lib.open_cfw_littlefs_erase_fixture_status(9)
        self.assertEqual(self.invoke(0x2A), -5)
        self.assertEqual(self.value(1), 1)
        self.assertEqual(
            tuple(self.value(index) for index in range(2, 5)),
            (0x2A, 0x0142A000, 9),
        )

    def test_address_calculation_preserves_stock_32_bit_wrap(self) -> None:
        self.assertEqual(self.invoke(0xFFF00), 0)
        self.assertEqual(self.value(0), 0x01300000)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "littlefs-erase-target.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-Oz", "-ffreestanding", "-fno-builtin",
                "-Wall", "-Wextra", "-Werror",
                "-c", str(SOURCE), "-o", str(output),
            ],
            check=True, capture_output=True,
        )
        self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
