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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_bitmap_update_421632.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_bitmap_update_host.c"


class BootloaderBitmapUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "bitmap-update.dylib" if sys.platform == "darwin" else "bitmap-update.so"
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
        cls.lib.open_cfw_bitmap_update_fixture_clear.argtypes = []
        cls.lib.open_cfw_bitmap_update_fixture_get.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_bitmap_update_fixture_get.restype = ctypes.c_uint32
        cls.lib.open_cfw_bitmap_update_fixture_set.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.update = cls.lib.open_cfw_bootloader_bitmap_update_421632
        cls.update.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        cls.update.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_bitmap_update_fixture_clear()

    def test_authenticated_complete_body_table_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x11632:0x116B2]
        self.assertEqual(len(body), 128)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "bc7fc361719841b4cd3b48adad0bb774fe817371892b0a9cbe4e8744c5ec2a8e",
        )
        self.assertEqual(blob[0x12210:0x12214].hex(), "746e0220")
        self.assertEqual(blob[0x116B2:0x116B4].hex(), "38b5")

    def test_set_clear_and_two_word_boundaries(self) -> None:
        for bit in (0, 31, 32, 56):
            self.assertEqual(self.update(3, bit, 1), 0)
        self.assertEqual(self.lib.open_cfw_bitmap_update_fixture_get(3, 0), 0x80000001)
        self.assertEqual(self.lib.open_cfw_bitmap_update_fixture_get(3, 1), 0x01000001)
        self.assertEqual(self.update(3, 31, 0), 0)
        self.assertEqual(self.update(3, 32, 0), 0)
        self.assertEqual(self.lib.open_cfw_bitmap_update_fixture_get(3, 0), 1)
        self.assertEqual(self.lib.open_cfw_bitmap_update_fixture_get(3, 1), 0x01000000)

    def test_validation_and_low_byte_contract(self) -> None:
        self.lib.open_cfw_bitmap_update_fixture_set(0, 0, 0xA5A5A5A5)
        for selector, bit in ((7, 0), (255, 0), (0, 57), (0, 255)):
            self.assertEqual(self.update(selector, bit, 1), 6)
            self.assertEqual(self.lib.open_cfw_bitmap_update_fixture_get(0, 0), 0xA5A5A5A5)
        self.assertEqual(self.update(0x100, 0x100, 0x100), 0)
        self.assertEqual(self.lib.open_cfw_bitmap_update_fixture_get(0, 0), 0xA5A5A5A4)
        self.assertEqual(self.update(0x106, 0x138, 0x101), 0)
        self.assertEqual(self.lib.open_cfw_bitmap_update_fixture_get(6, 1), 0x01000000)

    def test_updates_preserve_unselected_bits_and_enabled_is_boolean(self) -> None:
        self.lib.open_cfw_bitmap_update_fixture_set(2, 0, 0xAAAAAAAA)
        self.assertEqual(self.update(2, 4, 0x100), 0)
        self.assertEqual(self.lib.open_cfw_bitmap_update_fixture_get(2, 0), 0xAAAAAAAA)
        self.assertEqual(self.update(2, 4, 0x101), 0)
        self.assertEqual(self.lib.open_cfw_bitmap_update_fixture_get(2, 0), 0xAAAAAABA)
        self.assertEqual(self.update(2, 5, 0), 0)
        self.assertEqual(self.lib.open_cfw_bitmap_update_fixture_get(2, 0), 0xAAAAAA9A)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).is_file():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-bitmap-update.o")
            subprocess.run(
                [
                    compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                    "-c", str(SOURCE), "-o", str(output),
                ],
                check=True, capture_output=True,
            )
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
