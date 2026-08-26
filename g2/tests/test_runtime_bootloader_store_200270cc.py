from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_store_200270cc.c"
HEADER = ROOT / "components/bootloader/core_overlay/runtime_store_200270cc.h"
FIXTURE = ROOT / "tests/fixtures/bootloader_store_200270cc_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"


class BootloaderStore200270ccTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "store-200270cc.dylib"
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall", "-Wextra", "-Werror", "-dynamiclib", str(FIXTURE), "-o", str(cls.library)], check=True, capture_output=True, text=True)
        cls.function = ctypes.CDLL(str(cls.library)).open_cfw_bootloader_store_200270cc_fixture
        cls.function.argtypes = [ctypes.c_uint32]
        cls.function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_full_word_store(self) -> None:
        for value in (0, 1, 0xFFFFFFFF, 0x12345678):
            with self.subTest(value=value):
                self.assertEqual(self.function(value), value)

    def test_authenticated_stock_entry_and_sram_literal(self) -> None:
        blob = OFFICIAL.read_bytes()
        entry = blob[0x583C:0x5844]
        self.assertEqual((len(entry), hashlib.sha256(entry).hexdigest()), (8, "8bee0f65c10cb18c0d50f225275e41e44c54b0c06cdaef05017cccf89162d0f8"))
        self.assertEqual(int.from_bytes(blob[0x5FDC:0x5FE0], "little"), 0x200270CC)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "store-arm.o"
        subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output)], check=True, capture_output=True, text=True)
        self.assertGreater(output.stat().st_size, 0)
        self.assertIn("open_cfw_bootloader_store_200270cc", HEADER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
