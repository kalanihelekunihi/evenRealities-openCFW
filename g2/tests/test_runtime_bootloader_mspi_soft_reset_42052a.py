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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_soft_reset_42052a.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_soft_reset_host.c"


class MspiSoftResetTests(unittest.TestCase):
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
        cls.lib.open_cfw_soft_reset_fixture_status.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_soft_reset_fixture_event.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_soft_reset_fixture_event.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_soft_reset_fixture_reset()

    def events(self):
        return [tuple(self.lib.open_cfw_soft_reset_fixture_event(i, f)
                      for f in range(2))
                for i in range(self.lib.open_cfw_soft_reset_fixture_count())]

    def test_authenticated_stock_body_and_source(self) -> None:
        body = OFFICIAL.read_bytes()[0x1052A:0x1059E]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
                         (116, "ec592b1db3c6c381036d5c69d065056547b69d870025dd08aef11f34c2b350f0"))
        self.assertEqual((SOURCE.stat().st_size, hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
                         (3305, "ebe83fc0c63dc78e6c165f308dfd331eaf9cdc0a171c036a564f581d55bd3b47"))

    def test_command_delay_order_and_failure_only_logs(self) -> None:
        self.lib.open_cfw_bootloader_mspi_soft_reset_42052a()
        self.assertEqual(self.events(), [(0, 0x66), (1, 1), (0, 0x99), (1, 50)])

        self.lib.open_cfw_soft_reset_fixture_reset()
        self.lib.open_cfw_soft_reset_fixture_status(0, 7)
        self.lib.open_cfw_soft_reset_fixture_status(1, 9)
        self.lib.open_cfw_bootloader_mspi_soft_reset_42052a()
        self.assertEqual(self.events(), [(0, 0x66), (0x2C4, 0x004334EC),
                                         (1, 1), (0, 0x99),
                                         (0x2C9, 0x00432650), (1, 50)])

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
