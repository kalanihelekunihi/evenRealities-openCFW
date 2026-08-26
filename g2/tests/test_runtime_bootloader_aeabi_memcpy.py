from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_aeabi_memcpy.c"
HEADER = ROOT / "components/bootloader/core_overlay/runtime_aeabi_memcpy.h"
FIXTURE = ROOT / "tests/fixtures/bootloader_aeabi_memcpy_host.c"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"


class BootloaderAeabiMemcpyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "memcpy-host.dylib"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall",
                "-Wextra", "-Werror", "-dynamiclib", str(FIXTURE), "-o",
                str(cls.library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_bootloader_memcpy_fixture.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_every_bounded_length_and_unaligned_offsets(self) -> None:
        for count in range(65):
            for source_offset, destination_offset in ((0, 0), (1, 3), (3, 1)):
                with self.subTest(count=count, source=source_offset, destination=destination_offset):
                    source = (ctypes.c_ubyte * 72)(*[(index * 37 + 11) & 0xFF for index in range(72)])
                    destination = (ctypes.c_ubyte * 72)(*([0xA5] * 72))
                    self.lib.open_cfw_bootloader_memcpy_fixture(
                        ctypes.cast(ctypes.byref(destination, destination_offset), ctypes.POINTER(ctypes.c_ubyte)),
                        ctypes.cast(ctypes.byref(source, source_offset), ctypes.POINTER(ctypes.c_ubyte)),
                        count,
                    )
                    self.assertEqual(
                        bytes(destination[destination_offset:destination_offset + count]),
                        bytes(source[source_offset:source_offset + count]),
                    )
                    self.assertEqual(bytes(destination[:destination_offset]), b"\xA5" * destination_offset)
                    self.assertEqual(bytes(destination[destination_offset + count:]), b"\xA5" * (72 - destination_offset - count))

    def test_authenticated_stock_span(self) -> None:
        blob = OFFICIAL.read_bytes()
        start = 0x0041568C - 0x00410000
        body = blob[start:0x00415732 - 0x00410000]
        self.assertEqual(len(body), 166)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd",
        )

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "memcpy-arm.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-Wall",
                "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True, capture_output=True, text=True,
        )
        self.assertGreater(output.stat().st_size, 0)
        self.assertIn("open_cfw_bootloader_aeabi_memcpy", HEADER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
