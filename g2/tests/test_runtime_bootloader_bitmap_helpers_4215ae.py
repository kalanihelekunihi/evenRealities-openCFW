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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_bitmap_helpers_4215ae.c"
POPCOUNT = ROOT / "components/bootloader/core_overlay/runtime_popcount_421584.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_bitmap_helpers_host.c"


class BootloaderBitmapHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "bitmap.dylib" if sys.platform == "darwin" else "bitmap.so"
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
        cls.lib.open_cfw_bitmap_fixture_clear.argtypes = []
        cls.lib.open_cfw_bitmap_fixture_set.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.any = cls.lib.open_cfw_bootloader_bitmap_any_4215ae
        cls.test = cls.lib.open_cfw_bootloader_bitmap_test_4215dc
        cls.count = cls.lib.open_cfw_bootloader_bitmap_count_4215fe
        for function in (cls.any, cls.count):
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32
        cls.test.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.test.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_bitmap_fixture_clear()

    def test_authenticated_complete_bodies_table_and_callers(self) -> None:
        blob = OFFICIAL.read_bytes()
        spans = (
            (0x115AE, 0x115DC, "11a6cf814c1a66760a988880dac541c55419e26aa1f4c7ef2de27b9a0d7e019f"),
            (0x115DC, 0x115FE, "8dc0a88874cc74f9148e7ae8b6e70f50b7cd1f732db5b74982a8abcccb1bd6f5"),
            (0x115FE, 0x11632, "2c98fb87af946ccd169b0e0f8225c9455b682478941053f2a25da7ac6e23c689"),
        )
        for start, end, digest in spans:
            self.assertEqual(hashlib.sha256(blob[start:end]).hexdigest(), digest)
        self.assertEqual(blob[0x12210:0x12214].hex(), "746e0220")
        self.assertEqual(blob[0x1161C:0x11620].hex(), "fff7b2ff")

    def test_any_and_selector_low_byte_contract(self) -> None:
        self.assertEqual(self.any(7), 0)
        self.lib.open_cfw_bitmap_fixture_set(7, 1, 0x80000000)
        self.assertEqual(self.any(7), 1)
        self.assertEqual(self.any(0x107), 1)
        self.lib.open_cfw_bitmap_fixture_set(7, 1, 0)
        self.lib.open_cfw_bitmap_fixture_set(7, 0, 1)
        self.assertEqual(self.any(7), 1)

    def test_bit_lookup_uses_low_bit_byte_and_two_word_layout(self) -> None:
        self.lib.open_cfw_bitmap_fixture_set(3, 0, 0x80000001)
        self.lib.open_cfw_bitmap_fixture_set(3, 1, 0x80000001)
        for bit in (0, 31, 32, 63):
            self.assertEqual(self.test(3, bit), 1)
        for bit in (1, 30, 33, 62):
            self.assertEqual(self.test(3, bit), 0)
        self.assertEqual(self.test(0x103, 0), 1)

    def test_count_sums_both_words_and_returns_low_byte(self) -> None:
        self.lib.open_cfw_bitmap_fixture_set(9, 0, 0xFFFFFFFF)
        self.lib.open_cfw_bitmap_fixture_set(9, 1, 0x80000001)
        self.assertEqual(self.count(9), 34)
        self.assertEqual(self.count(0x109), 34)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).is_file():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-bitmap.o")
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
