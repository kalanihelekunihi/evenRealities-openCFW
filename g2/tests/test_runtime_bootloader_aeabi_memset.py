from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_aeabi_memset.c"
HEADER = ROOT / "components/bootloader/core_overlay/runtime_aeabi_memset.h"
FIXTURE = ROOT / "tests/fixtures/bootloader_aeabi_memset_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"


class BootloaderAeabiMemsetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "memset-host.dylib"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-Wall", "-Wextra", "-Werror", "-dynamiclib",
                str(FIXTURE), "-o", str(cls.library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_bootloader_memset_fixture.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t, ctypes.c_int
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_zero_length_does_not_touch_destination(self) -> None:
        data = (ctypes.c_ubyte * 4)(1, 2, 3, 4)
        self.lib.open_cfw_bootloader_memset_fixture(data, 0, 0xAA)
        self.assertEqual(bytes(data), b"\x01\x02\x03\x04")

    def test_low_byte_is_repeated_for_every_count(self) -> None:
        for count in range(0, 65):
            with self.subTest(count=count):
                data = (ctypes.c_ubyte * 68)(*([0x55] * 68))
                self.lib.open_cfw_bootloader_memset_fixture(data, count, 0x1A7)
                self.assertEqual(bytes(data[:count]), b"\xA7" * count)
                self.assertEqual(bytes(data[count:]), b"\x55" * (68 - count))

    def test_authenticated_stock_span(self) -> None:
        blob = OFFICIAL.read_bytes()
        start = 0x0041560C - 0x00410000
        body = blob[start : start + 102]
        self.assertEqual(len(body), 102)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "34da1a99d5cb56ca41cfaff98190ced2a7767f53cd95c53c504009566e9ca10a",
        )

    def test_source_is_c_and_freestanding_target_compiles(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        self.assertIn("while (count != 0U)", text)
        self.assertIn("SPDX-License-Identifier: MIT", text)
        output = Path(self.temporary.name) / "memset-arm.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(output.stat().st_size, 0)
        self.assertIn("open_cfw_bootloader_aeabi_memset", HEADER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
