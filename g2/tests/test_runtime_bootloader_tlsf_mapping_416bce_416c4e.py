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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_tlsf_mapping_416bce.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_tlsf_mapping_host.c"

STOCK = (
    (0x6BCE, 0x6BF8, "8f24fcab6cfba7e90833e18751c03493d5a7f8d537c0b5c991e9a273990b2d99"),
    (0x6BF8, 0x6C26, "c1275ed4397a9e46d7c3fe8b57a6f7e434c5a4ac6764d3786235b05c6a401b79"),
    (0x6C26, 0x6C4E, "28f5a5f4c0ce20ce58272435bbb3791fc904e17324a44792ffd7f127ee9a5ab8"),
)


class BootloaderTlsfMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library_path = Path(cls.temporary.name) / (
            "tlsf_mapping.dylib" if sys.platform == "darwin" else "tlsf_mapping.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.adjust = cls.lib.open_cfw_bootloader_tlsf_adjust_request_size_416bce
        cls.adjust.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.adjust.restype = ctypes.c_uint32
        cls.insert = cls.lib.open_cfw_bootloader_tlsf_mapping_insert_416bf8
        cls.insert.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        cls.search = cls.lib.open_cfw_bootloader_tlsf_mapping_search_416c26
        cls.search.argtypes = cls.insert.argtypes

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def mapped(self, function, size):
        first = ctypes.c_int(-1)
        second = ctypes.c_int(-1)
        function(size, ctypes.byref(first), ctypes.byref(second))
        return first.value, second.value

    def test_authenticated_complete_stock_entries_and_callers(self):
        image = OFFICIAL.read_bytes()
        for start, end, expected_hash in STOCK:
            body = image[start:end]
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)

    def test_adjust_request_size_contract(self):
        self.assertEqual(self.adjust(0, 4), 0)
        self.assertEqual(self.adjust(1, 4), 12)
        self.assertEqual(self.adjust(12, 4), 12)
        self.assertEqual(self.adjust(13, 4), 16)
        self.assertEqual(self.adjust(0x3FFFFFFC, 4), 0x3FFFFFFC)
        self.assertEqual(self.adjust(0x3FFFFFFD, 4), 0)
        self.assertEqual(self.adjust(0x40000000, 4), 0)
        self.assertEqual(self.adjust(0xFFFFFFFF, 4), 12)

    def test_mapping_insert_contract(self):
        self.assertEqual(self.mapped(self.insert, 0), (0, 0))
        self.assertEqual(self.mapped(self.insert, 4), (0, 1))
        self.assertEqual(self.mapped(self.insert, 124), (0, 31))
        self.assertEqual(self.mapped(self.insert, 128), (1, 0))
        self.assertEqual(self.mapped(self.insert, 132), (1, 1))
        self.assertEqual(self.mapped(self.insert, 255), (1, 31))
        self.assertEqual(self.mapped(self.insert, 256), (2, 0))
        self.assertEqual(self.mapped(self.insert, 0x3FFFFFFF), (23, 31))

    def test_mapping_search_rounds_to_containing_class(self):
        self.assertEqual(self.mapped(self.search, 124), (0, 31))
        self.assertEqual(self.mapped(self.search, 128), (1, 0))
        self.assertEqual(self.mapped(self.search, 129), (1, 1))
        self.assertEqual(self.mapped(self.search, 132), (1, 1))
        self.assertEqual(self.mapped(self.search, 255), (2, 0))
        self.assertEqual(self.mapped(self.search, 257), (2, 1))

    def test_freestanding_target_compiles(self):
        output = Path(self.temporary.name) / "mapping.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
