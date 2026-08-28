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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memory_rotate_front_423928.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_memory_rotate_front_host.c"


class BootloaderMemoryRotateFrontTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("mrf.dylib" if sys.platform == "darwin" else "mrf.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(output))
        cls.rotate = cls.lib.open_cfw_bootloader_memory_rotate_front_423928
        cls.rotate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        cls.rotate.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_authenticated_body_calls_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(hashlib.sha256(blob[0x13928:0x13972]).hexdigest(), "6e7615d2123f9cf87dcb9d1823cfe5613687eaae88ce8b5f88664c205d012e09")
        self.assertEqual(hashlib.sha256(blob[0x13972:0x139C2]).hexdigest(), "b6ec5384c9fd2cd9f993179c74e4993b5d85e6a0ea5c1b1533842d11fe4b76ff")

    def test_zero_small_threshold_and_multichunk_widths(self) -> None:
        for width in (0, 1, 17, 63, 64, 127, 128, 129, 257):
            body_size = 4 * width
            original = bytes((index * 13 + 7) & 0xFF for index in range(body_size + 19))
            buffer = (ctypes.c_uint8 * len(original)).from_buffer_copy(original)
            self.rotate(buffer, ctypes.byref(buffer, 3 * width), width)
            expected = original[3 * width:4 * width] + original[:3 * width] + original[4 * width:]
            self.assertEqual(bytes(buffer), expected)

    def test_first_element_is_a_noop_and_suffix_is_preserved(self) -> None:
        width = 193
        original = bytes((index * 9 + 5) & 0xFF for index in range(width + 37))
        buffer = (ctypes.c_uint8 * len(original)).from_buffer_copy(original)
        self.rotate(buffer, buffer, width)
        self.assertEqual(bytes(buffer), original)

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-mrf.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
