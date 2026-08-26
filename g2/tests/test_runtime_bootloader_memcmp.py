from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_memcmp.c"
HEADER = ROOT / "components/bootloader/core_overlay/runtime_memcmp.h"
FIXTURE = ROOT / "tests/fixtures/bootloader_memcmp_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"


class BootloaderMemcmpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "memcmp-host.dylib"
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall", "-Wextra", "-Werror", "-dynamiclib", str(FIXTURE), "-o", str(cls.library)],
            check=True, capture_output=True, text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_bootloader_memcmp_fixture.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint]
        cls.lib.open_cfw_bootloader_memcmp_fixture.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def compare(self, left: bytes, right: bytes, count: int, left_offset: int = 0, right_offset: int = 0) -> int:
        lhs = (ctypes.c_ubyte * len(left)).from_buffer_copy(left)
        rhs = (ctypes.c_ubyte * len(right)).from_buffer_copy(right)
        return self.lib.open_cfw_bootloader_memcmp_fixture(
            ctypes.cast(ctypes.byref(lhs, left_offset), ctypes.POINTER(ctypes.c_ubyte)),
            ctypes.cast(ctypes.byref(rhs, right_offset), ctypes.POINTER(ctypes.c_ubyte)),
            count,
        )

    def test_zero_equal_and_first_difference_sign(self) -> None:
        baseline = bytes((index * 19 + 7) & 0xFF for index in range(72))
        self.assertEqual(self.compare(baseline, baseline, 0), 0)
        for count in range(65):
            self.assertEqual(self.compare(baseline, baseline, count), 0)
        for position in (0, 1, 3, 31, 63):
            left = bytearray(baseline)
            right = bytearray(baseline)
            left[position], right[position] = 0xF1, 0x12
            self.assertGreater(self.compare(left, right, position + 1), 0)
            self.assertLess(self.compare(right, left, position + 1), 0)
            if position:
                self.assertEqual(self.compare(left, right, position), 0)

    def test_unaligned_inputs(self) -> None:
        left = b"x" + bytes(range(64)) + b"tail"
        right = b"yz" + bytes(range(64)) + b"tail"
        self.assertEqual(self.compare(left, right, 64, 1, 2), 0)

    def test_authenticated_stock_span(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x5758:0x57C0]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (104, "33e09969a8e4f7ca9290ef4678d252c217a5d031eb362f8d6c5ad656424d4154"),
        )

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "memcmp-arm.o"
        subprocess.run(
            ["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output)],
            check=True, capture_output=True, text=True,
        )
        self.assertGreater(output.stat().st_size, 0)
        self.assertIn("open_cfw_bootloader_memcmp", HEADER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
