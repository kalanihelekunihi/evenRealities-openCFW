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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_low_level_init_420254.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_low_level_init_host.c"
BASE = 0x00410000


def thumb_bl_target(blob: bytes, address: int) -> int | None:
    offset = address - BASE
    first = int.from_bytes(blob[offset : offset + 2], "little")
    second = int.from_bytes(blob[offset + 2 : offset + 4], "little")
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


class MspiLowLevelInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "fixture.dylib" if sys.platform == "darwin" else "fixture.so"
        cls.library_path = Path(cls.temporary.name) / suffix
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
             "-Wall", "-Wextra", "-Werror", str(FIXTURE),
             *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
             "-o", str(cls.library_path)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.lib.open_cfw_bootloader_mspi_low_level_init_420254.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_void_p),
        ]
        cls.lib.open_cfw_bootloader_mspi_low_level_init_420254.restype = ctypes.c_uint32
        cls.lib.open_cfw_low_init_fixture_status.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_low_init_fixture_active.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_low_init_fixture_call.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_low_init_fixture_call.restype = ctypes.c_size_t
        cls.lib.open_cfw_low_init_fixture_log.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_low_init_fixture_log.restype = ctypes.c_uint32
        cls.lib.open_cfw_low_init_fixture_state.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_low_init_fixture_state.restype = ctypes.c_uint32
        cls.lib.open_cfw_low_init_fixture_state_address.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_low_init_fixture_reset()

    def invoke(self, config=None):
        output = ctypes.c_void_p()
        pointer = config if config is not None else None
        result = self.lib.open_cfw_bootloader_mspi_low_level_init_420254(
            1, pointer, ctypes.byref(output))
        return result, output.value

    def test_authenticated_stock_body_caller_literals_and_seams(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10254:0x10476]
        self.assertEqual(len(body), 546)
        self.assertEqual(hashlib.sha256(body).hexdigest(),
                         "a3c3fab2d311bebbeb0a655aca6ee81a0afaf790008ca5bd11f23b05802bcb94")
        self.assertEqual(
            tuple(address for address in range(BASE, BASE + len(blob) - 3, 2)
                  if thumb_bl_target(blob, address) == 0x00420254),
            (0x00420480,),
        )
        expected_calls = {
            0x0042029A: 0x00424A5A, 0x004202AC: 0x00426808,
            0x004202EE: 0x00424AF0, 0x0042032E: 0x00424BE4,
            0x00420378: 0x00425066, 0x004203B0: 0x0041FF34,
            0x004203B8: 0x0041FADC, 0x004203C0: 0x0041D90E,
            0x004203CC: 0x00426506, 0x004203E0: 0x00426450,
            0x0042040E: 0x0041FDDE, 0x00420414: 0x0041FDC0,
            0x00420418: 0x0041B8E0,
        }
        for site, target in expected_calls.items():
            self.assertEqual(thumb_bl_target(blob, site), target)
        for offset, value in ((0x10874, 0x200270DC), (0x10B04, 0x20026FD0),
                              (0x10C20, 0x200F4C00), (0x10C28, 0x20000224)):
            self.assertEqual(int.from_bytes(blob[offset:offset + 4], "little"), value)
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
                         (10627, "e5170727ba0e6fbc412ccc2dc1a845f777a66c1bd10eba3248db041bde31548d"))

    def test_success_order_default_configuration_and_publication(self) -> None:
        result, output = self.invoke()
        self.assertEqual(result, 0)
        self.assertEqual(output, self.lib.open_cfw_low_init_fixture_state_address())
        self.assertEqual(self.lib.open_cfw_low_init_fixture_call_count(), 13)
        self.assertEqual([self.lib.open_cfw_low_init_fixture_call(i, 0) for i in range(13)],
                         [0, 1, 2, 3, 4, 10, 11, 6, 7, 8, 12, 13, 9,])
        self.assertEqual([self.lib.open_cfw_low_init_fixture_state(i) for i in range(4)],
                         [1, 16, 0x2468, 1])
        self.assertEqual(self.lib.open_cfw_low_init_fixture_call(6, 1), 1)
        self.assertEqual(self.lib.open_cfw_low_init_fixture_call(6, 2), 16)
        self.assertEqual(self.lib.open_cfw_low_init_fixture_call(8, 2), 0x1A80)
        self.assertEqual(self.lib.open_cfw_low_init_fixture_call(10, 1), 21)
        self.assertEqual(self.lib.open_cfw_low_init_fixture_call(10, 2), 4)
        self.assertEqual(self.lib.open_cfw_low_init_fixture_log_count(), 1)
        self.assertEqual([self.lib.open_cfw_low_init_fixture_log(0, i) for i in range(3)],
                         [3, 0x27A, 0x00432A74])

    def test_custom_config_busy_and_failure_cleanup_contracts(self) -> None:
        custom = (ctypes.c_uint8 * 24)(*range(24))
        custom[8] = 0x55
        result, _ = self.invoke(custom)
        self.assertEqual(result, 0)
        self.assertEqual(self.lib.open_cfw_low_init_fixture_state(1), 0x55)

        self.lib.open_cfw_low_init_fixture_reset()
        self.lib.open_cfw_low_init_fixture_active(1)
        result, _ = self.invoke()
        self.assertEqual(result, 0xFFFFFFFF)
        self.assertEqual(self.lib.open_cfw_low_init_fixture_call_count(), 0)

        for operation, status, expected, log_line, deinit in (
            (0, 7, 7, None, False), (1, 7, 1, 0x22A, False),
            (2, 7, 7, 0x233, True), (3, 7, 7, 0x23F, True),
            (4, 7, 7, 0x246, True), (7, 7, 1, None, False),
            (8, 7, 1, 0x269, False),
        ):
            with self.subTest(operation=operation):
                self.lib.open_cfw_low_init_fixture_reset()
                self.lib.open_cfw_low_init_fixture_status(operation, status)
                result, _ = self.invoke()
                self.assertEqual(result, expected)
                operations = [self.lib.open_cfw_low_init_fixture_call(i, 0)
                              for i in range(self.lib.open_cfw_low_init_fixture_call_count())]
                self.assertEqual(5 in operations, deinit)
                if log_line is None:
                    self.assertEqual(self.lib.open_cfw_low_init_fixture_log_count(), 0)
                else:
                    self.assertEqual(self.lib.open_cfw_low_init_fixture_log(0, 1), log_line)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "mspi-low-level-init.o"
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-target", "arm-none-eabi",
             "-mcpu=cortex-m55", "-mthumb", "-std=c11", "-Oz", "-ffreestanding",
             "-fno-builtin", "-ffunction-sections", "-fdata-sections",
             "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
             "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output)],
            check=True, capture_output=True,
        )


if __name__ == "__main__":
    unittest.main()
