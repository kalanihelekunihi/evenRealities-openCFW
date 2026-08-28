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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_read_420f70.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_read_host.c"


class MspiReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "mspi-read.dylib" if sys.platform == "darwin" else "mspi-read.so"
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
        cls.lib.open_cfw_mspi_read_fixture_config.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_mspi_read_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_mspi_read_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_read_420f70.argtypes = [
            ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32
        ]
        cls.lib.open_cfw_bootloader_mspi_read_420f70.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_mspi_read_fixture_reset()
        self.buffer = (ctypes.c_uint8 * 64)()

    def value(self, field: int) -> int:
        return self.lib.open_cfw_mspi_read_fixture_value(field)

    def events(self) -> tuple[int, ...]:
        return tuple(self.value(64 + i) for i in range(self.value(32)))

    def call(self, address: int, length: int) -> int:
        return self.lib.open_cfw_bootloader_mspi_read_420f70(
            address, ctypes.cast(self.buffer, ctypes.c_void_p), length
        )

    def test_authenticated_stock_body_gap_pool_and_caller(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10F70:0x10FF2]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (130, "ce201805b566c9d5c4a70d675e0bdb145133d2771bc9098e4255245a8d6067e3"),
        )
        self.assertEqual(
            (len(blob[0x10F6A:0x10F70]), hashlib.sha256(blob[0x10F6A:0x10F70]).hexdigest()),
            (6, "86d14b79fc1438915684e8f5b80873e3458147a166ffdaa3a0d42aa9588c690f"),
        )
        self.assertEqual(
            (len(blob[0x10FF2:0x110C8]), hashlib.sha256(blob[0x10FF2:0x110C8]).hexdigest()),
            (214, "21ac43cfda25ec0bc55b6df8e70c3341923392c939cf989b96f0945e7b151ba3"),
        )
        self.assertEqual(blob[0x112EE:0x112F2].hex(), "fff73ffe")

    def test_validation_short_circuits(self) -> None:
        self.lib.open_cfw_mspi_read_fixture_config(0, 0)
        self.assertEqual(self.call(0, 1), 6)
        self.assertEqual(self.events(), ())

        self.setUp()
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_read_420f70(0, None, 1), 6)
        self.assertEqual(self.call(0, 0), 6)
        self.assertEqual(self.call(0x02000000, 1), 5)
        self.assertEqual(self.events(), ())

    def test_success_descriptor_order_and_ignored_wait_status(self) -> None:
        self.lib.open_cfw_mspi_read_fixture_config(1, 17)
        self.assertEqual(self.call(0x01234567, 0x31), 0)
        self.assertEqual(self.events(), (1, 2, 3, 4, 5))
        self.assertEqual(self.value(3), 1)
        self.assertEqual(self.value(4), 1)
        self.assertEqual(self.value(5), 0x12345678)
        self.assertEqual(self.value(6), 1000000)
        self.assertEqual((self.value(7), self.value(8), self.value(9)), (0x31, 1, 0x01234567))
        self.assertEqual((self.value(10), self.value(11), self.value(12)), (1, 0x6C, 1))
        self.assertEqual(self.value(13), ctypes.addressof(self.buffer) & 0xFFFFFFFF)
        self.assertEqual(self.value(14), 0)

    def test_hal_failure_is_returned_and_guard_is_released(self) -> None:
        self.lib.open_cfw_mspi_read_fixture_config(2, 9)
        self.assertEqual(self.call(0x100, 4), 9)
        self.assertEqual(self.events(), (1, 2, 3, 4, 5))

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "mspi-read-target.o"
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
