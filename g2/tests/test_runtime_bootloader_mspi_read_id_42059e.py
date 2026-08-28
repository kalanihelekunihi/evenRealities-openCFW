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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_read_id_42059e.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_read_id_host.c"


class MspiReadIdTests(unittest.TestCase):
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
        cls.lib.open_cfw_read_id_fixture_response.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_read_id_fixture_value.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_read_id_fixture_value.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_mspi_read_id_42059e.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.open_cfw_bootloader_mspi_read_id_42059e.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_read_id_fixture_reset()

    def values(self):
        return tuple(self.lib.open_cfw_read_id_fixture_value(i) for i in range(4))

    def test_authenticated_stock_body(self) -> None:
        body = OFFICIAL.read_bytes()[0x1059E:0x105F4]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()),
                         (86, "76375cc441140c585f955d99008ebaf467fb7eb54882cc857cff55b7aaa0f48e"))

    def test_success_packs_three_big_endian_jedec_bytes(self) -> None:
        self.lib.open_cfw_read_id_fixture_response(0, 0xC23925)
        identifier = ctypes.c_uint32(0xFFFFFFFF)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_read_id_42059e(
            ctypes.byref(identifier)), 0)
        self.assertEqual(identifier.value, 0xC23925)
        self.assertEqual(self.values(), (0x9F, 3, 0, 0))

    def test_failure_logs_and_preserves_output(self) -> None:
        self.lib.open_cfw_read_id_fixture_response(7, 0xC23925)
        identifier = ctypes.c_uint32(0xA5A5A5A5)
        self.assertEqual(self.lib.open_cfw_bootloader_mspi_read_id_42059e(
            ctypes.byref(identifier)), 7)
        self.assertEqual(identifier.value, 0xA5A5A5A5)
        self.assertEqual(self.values(), (0x9F, 3, 0x2D8, 0x00433AEC))

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
