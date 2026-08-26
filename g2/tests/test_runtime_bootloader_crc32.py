from __future__ import annotations

import binascii
import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_crc32.c"
HEADER = ROOT / "components/bootloader/core_overlay/runtime_crc32.h"
FIXTURE = ROOT / "tests/fixtures/bootloader_crc32_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"


class BootloaderCrc32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "crc32.dylib"
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall", "-Wextra", "-Werror", "-dynamiclib", str(FIXTURE), "-o", str(cls.library)], check=True, capture_output=True, text=True)
        cls.function = ctypes.CDLL(str(cls.library)).open_cfw_bootloader_crc32_fixture
        cls.function.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        cls.function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def call(self, initial: int, data: bytes) -> int:
        storage = (ctypes.c_uint8 * max(1, len(data)))()
        if data:
            storage[:len(data)] = data
        return int(self.function(initial, storage, len(data)))

    def test_standard_and_incremental_semantics(self) -> None:
        cases = (b"", b"123456789", bytes(range(256)), b"openCFW\x00G2")
        for data in cases:
            with self.subTest(length=len(data)):
                expected = binascii.crc32(data, 0) ^ 0xFFFFFFFF
                self.assertEqual(self.call(0xFFFFFFFF, data), expected)
        first = self.call(0x13579BDF, b"split-")
        self.assertEqual(self.call(first, b"update"), self.call(0x13579BDF, b"split-update"))

    def test_authenticated_stock_entry_and_table(self) -> None:
        blob = OFFICIAL.read_bytes()
        entry = blob[0x57C0:0x57F8]
        table = blob[0x2174C:0x2178C]
        self.assertEqual((len(entry), hashlib.sha256(entry).hexdigest()), (56, "acba42ebe6d52e7d353fe1cd586fb79cea530e243d2ffaeaf1019f7548dc20be"))
        self.assertEqual(int.from_bytes(table[32:36], "little"), 0xEDB88320)
        self.assertEqual(len(table), 64)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "crc32-arm.o"
        subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output)], check=True, capture_output=True, text=True)
        self.assertGreater(output.stat().st_size, 0)
        self.assertIn("open_cfw_bootloader_crc32", HEADER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
