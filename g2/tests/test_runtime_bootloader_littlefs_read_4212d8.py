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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_littlefs_read_4212d8.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_littlefs_read_host.c"


class LittlefsReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "littlefs-read.dylib" if sys.platform == "darwin" else "littlefs-read.so"
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
        cls.lib.open_cfw_littlefs_read_fixture_status.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_littlefs_read_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_littlefs_read_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_littlefs_read_4212d8.argtypes = [
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_void_p, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_littlefs_read_4212d8.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_littlefs_read_fixture_reset()

    def value(self, index: int) -> int:
        return self.lib.open_cfw_littlefs_read_fixture_value(index)

    def invoke(self, block: int, offset: int, size: int) -> int:
        return self.lib.open_cfw_bootloader_littlefs_read_4212d8(
            None, block, offset, ctypes.c_void_p(0x12345678), size
        )

    def test_authenticated_body_successors_driver_log_and_configuration(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x112D8:0x11310]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (56, "26e2b4b9fe7f3389d15261fe01621eb3b37bfc4b9923ebfac70609216ac92a90"),
        )
        successor = blob[0x11310:0x11348]
        self.assertEqual(
            (len(successor), hashlib.sha256(successor).hexdigest()),
            (56, "6d46e88d2df85850b8ec35b4f55e5e0522884210c8bf5a3419e328599ffebf60"),
        )
        self.assertEqual(blob[0x112EE:0x112F2].hex(), "fff73ffe")
        self.assertEqual(blob[0x11302:0x11306].hex(), "f4f754fe")
        self.assertEqual(int.from_bytes(blob[0x113C8:0x113CC], "little"), 0x004317CC)
        config = blob[0x21070:0x210A0]
        self.assertEqual(int.from_bytes(config[4:8], "little"), 0x004212D9)

    def test_success_forwards_stock_address_buffer_and_size(self) -> None:
        self.assertEqual(self.invoke(3, 0x24, 0x80), 0)
        self.assertEqual(
            (self.value(0), self.value(1), self.value(2), self.value(3)),
            (0x01403024, 0x12345678, 0x80, 0),
        )

    def test_device_failure_logs_complete_tuple_and_maps_to_lfs_err_io(self) -> None:
        self.lib.open_cfw_littlefs_read_fixture_status(7)
        self.assertEqual(self.invoke(0x2A, 0x18, 0x100), -5)
        self.assertEqual(self.value(3), 1)
        self.assertEqual(
            tuple(self.value(index) for index in range(4, 9)),
            (0x2A, 0x18, 0x100, 0x0142A018, 7),
        )

    def test_address_calculation_preserves_stock_32_bit_wrap(self) -> None:
        self.assertEqual(self.invoke(0xFFF00, 0x40, 1), 0)
        self.assertEqual(self.value(0), 0x01300040)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "littlefs-read-target.o"
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
