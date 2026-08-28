from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memory_exchange_423864.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_memory_exchange_host.c"


class BootloaderMemoryExchangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("mx.dylib" if sys.platform == "darwin" else "mx.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.swap = cls.lib.open_cfw_bootloader_memory_swap_423864
        cls.swap.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        cls.swap.restype = None
        cls.rotate = cls.lib.open_cfw_bootloader_memory_rotate3_4238ba
        cls.rotate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        cls.rotate.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_authenticated_bodies_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(
            hashlib.sha256(blob[0x13864:0x138BA]).hexdigest(),
            "ad7509b25a0cfd0245ca73f96c5c84c4ed321d6676a184c9a4b00fca46658e08",
        )
        self.assertEqual(
            hashlib.sha256(blob[0x138BA:0x13928]).hexdigest(),
            "15ab5faaa76530e6ce93f1d9ece7899858802f1eb5a6a1cb42287c8966aba239",
        )
        self.assertEqual(
            hashlib.sha256(blob[0x13928:0x13972]).hexdigest(),
            "6e7615d2123f9cf87dcb9d1823cfe5613687eaae88ce8b5f88664c205d012e09",
        )

    def test_swap_zero_small_threshold_and_chunked_sizes(self) -> None:
        for size in (0, 1, 17, 63, 64, 127, 128, 129, 257):
            left_values = bytes((index * 3 + 1) & 0xFF for index in range(300))
            right_values = bytes((index * 5 + 2) & 0xFF for index in range(300))
            left = (ctypes.c_uint8 * 300).from_buffer_copy(left_values)
            right = (ctypes.c_uint8 * 300).from_buffer_copy(right_values)
            self.swap(left, right, size)
            self.assertEqual(bytes(left), right_values[:size] + left_values[size:])
            self.assertEqual(bytes(right), left_values[:size] + right_values[size:])

    def test_rotate_zero_small_threshold_and_chunked_sizes(self) -> None:
        for size in (0, 1, 31, 63, 64, 127, 128, 193, 257):
            first_values = bytes((index + 11) & 0xFF for index in range(300))
            second_values = bytes((index * 3 + 17) & 0xFF for index in range(300))
            third_values = bytes((index * 7 + 23) & 0xFF for index in range(300))
            first = (ctypes.c_uint8 * 300).from_buffer_copy(first_values)
            second = (ctypes.c_uint8 * 300).from_buffer_copy(second_values)
            third = (ctypes.c_uint8 * 300).from_buffer_copy(third_values)
            self.rotate(first, second, third, size)
            self.assertEqual(bytes(first), third_values[:size] + first_values[size:])
            self.assertEqual(bytes(second), first_values[:size] + second_values[size:])
            self.assertEqual(bytes(third), second_values[:size] + third_values[size:])

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-mx.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
