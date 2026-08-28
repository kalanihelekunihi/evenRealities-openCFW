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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_enter_4byte_mode_420890.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_enter_4byte_mode_host.c"


class MspiEnter4ByteModeTests(unittest.TestCase):
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
        cls.lib.open_cfw_enter_4byte_fixture_config.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_enter_4byte_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_enter_4byte_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_enter_4byte_mode_420890.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_enter_4byte_fixture_reset()

    def config(self, field: int, value: int) -> None:
        self.lib.open_cfw_enter_4byte_fixture_config(field, value)

    def value(self, field: int) -> int:
        return self.lib.open_cfw_enter_4byte_fixture_value(field)

    def events(self) -> tuple[int, ...]:
        return tuple(self.value(9 + i) for i in range(self.value(8)))

    def test_authenticated_stock_body_gap_and_caller(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10890:0x10978]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
            (232, "ad4285ffa57c4bd7999a6b83f2bb9569b6bb85e40ef419b42bde4514d3f7e50c"))
        gap = blob[0x1086C:0x10890]
        self.assertEqual((len(gap), hashlib.sha256(gap).hexdigest()),
            (36, "bd568192057107608070c8993444e0e2bdc34243a5ddf9972040371697be4eca"))
        self.assertEqual(blob[0x10512:0x10516].hex(), "00f0bdf9")

    def test_unavailable_and_initial_busy_mappings(self) -> None:
        self.config(0, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_enter_4byte_mode_420890(), 2)
        self.assertEqual(self.events(), ())
        self.setUp(); self.config(1, 9)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_enter_4byte_mode_420890(), 3)
        self.assertEqual(self.events(), (1, 6))
        self.assertEqual(tuple(self.value(i) for i in range(5, 8)),
            (0x3C8, 0x00433CE8, 0x004331C0))

    def test_enable_and_command_failures_return_raw_status(self) -> None:
        self.config(2, 7)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_enter_4byte_mode_420890(), 7)
        self.assertEqual(self.events(), (1, 2, 6))
        self.assertEqual(tuple(self.value(i) for i in range(5, 8)),
            (0x3CF, 0x00431ED8, 0x004331C0))
        self.setUp(); self.config(3, 8)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_enter_4byte_mode_420890(), 8)
        self.assertEqual(self.events(), (1, 2, 3, 6))
        self.assertEqual(tuple(self.value(i) for i in range(5, 8)),
            (0x3D6, 0x004331E0, 0x004331C0))

    def test_command_post_wait_and_verify_quirks(self) -> None:
        self.config(4, 99)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_enter_4byte_mode_420890(), 0)
        self.assertEqual(self.events(), (1, 2, 3, 1, 4, 5))
        self.assertEqual(tuple(self.value(i) for i in range(5)), (0xB7, 0, 0, 1, 0))
        self.setUp(); self.config(5, 0)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_enter_4byte_mode_420890(), 1)
        self.assertEqual(self.events(), (1, 2, 3, 1, 4, 6))
        self.assertEqual(tuple(self.value(i) for i in range(5, 8)),
            (0x3DE, 0x00433200, 0x004331C0))
        self.setUp(); self.config(5, 77)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_enter_4byte_mode_420890(), 0)

    def test_disable_failure_and_success_order(self) -> None:
        self.config(6, 11)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_enter_4byte_mode_420890(), 11)
        self.assertEqual(self.events(), (1, 2, 3, 1, 4, 5, 6))
        self.assertEqual(tuple(self.value(i) for i in range(5, 8)),
            (0x3E4, 0x0043382C, 0x004331C0))
        self.setUp()
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_enter_4byte_mode_420890(), 0)
        self.assertEqual(self.events(), (1, 2, 3, 1, 4, 5))

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
