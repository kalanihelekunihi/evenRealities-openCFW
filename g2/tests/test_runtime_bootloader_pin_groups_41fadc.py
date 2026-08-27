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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_pin_groups_41fadc.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_pin_groups_host.c"
RUN_BASE = 0x00410000
START = 0x0041FADC
END = 0x0041FCF6
STOCK_SHA256 = "5fa7352e1bdc3dffcdda275c9fe7102d92c41fbc2a6384e407f6a68e920a35ce"


def decode_bl(blob: bytes, address: int) -> int | None:
    offset = address - RUN_BASE
    first = int.from_bytes(blob[offset:offset + 2], "little")
    second = int.from_bytes(blob[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22) |
                 ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


class BootloaderPinGroupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / (
            "pin_groups.dylib" if sys.platform == "darwin" else "pin_groups.so"
        )
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
             "-Wall", "-Wextra", "-Werror", str(FIXTURE),
             *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
             "-o", str(cls.library)],
            check=True, capture_output=True, text=True,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_body_and_callers(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[START - RUN_BASE:END - RUN_BASE]
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        self.assertEqual(
            tuple(address for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                  if decode_bl(image, address) == START),
            (0x004203B8, 0x00420E84),
        )

    def test_group_order_arguments_truncation_and_noops(self) -> None:
        function = self.loaded.open_cfw_test_pin_groups
        function.restype = ctypes.c_uint32
        self.assertEqual(function(), 1)

    def test_source_seams_and_freestanding_target_compile(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        for token in ("0x20000000U", "0x0041D92DU", "0xC7U", "0x68U"):
            self.assertIn(token, text)
        output = Path(self.temporary.name) / "pin_groups.o"
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-target", "arm-none-eabi",
             "-mcpu=cortex-m55", "-mthumb", "-std=c11", "-Oz",
             "-ffreestanding", "-fno-builtin", "-ffunction-sections",
             "-fdata-sections", "-fno-unwind-tables",
             "-fno-asynchronous-unwind-tables", "-fropi", "-Wall", "-Wextra",
             "-Werror", "-c", str(SOURCE), "-o", str(output)],
            check=True, capture_output=True, text=True,
        )
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
