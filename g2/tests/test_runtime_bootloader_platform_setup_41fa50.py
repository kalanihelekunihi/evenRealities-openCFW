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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_platform_setup_41fa50.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_platform_setup_host.c"
RUN_BASE = 0x00410000
START = 0x0041FA50
END = 0x0041FA98
STOCK_SHA256 = "fa00cb13624ecad4499a72574fa77edf5fc20471e6e6602cdae20441c7745f6f"


def decode_bl(blob: bytes, address: int) -> int | None:
    offset = address - RUN_BASE
    first = int.from_bytes(blob[offset:offset + 2], "little")
    second = int.from_bytes(blob[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22) |
        ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


class BootloaderPlatformSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / (
            "platform_setup.dylib" if sys.platform == "darwin"
            else "platform_setup.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin"
                  else ["-shared", "-fPIC"]),
                "-o", str(cls.library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_body_and_caller(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[START - RUN_BASE:END - RUN_BASE]
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        callers = tuple(
            address
            for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
            if decode_bl(image, address) == START
        )
        self.assertEqual(callers, (0x0041B87E,))

    def test_order_arguments_float_and_configuration_copy(self) -> None:
        function = self.loaded.open_cfw_test_platform_setup
        function.restype = ctypes.c_uint32
        self.assertEqual(function(), 1)

    def test_source_seams_and_freestanding_target_compile(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        for token in (
            "0x00433A9CU", "0x0041FA99U", "0x0041C4B5U",
            "0x0041C86DU", "0x0041CA2DU", "0x004156ADU",
            "0x00422417U", "0x004222A1U", "25.0F",
            'pcs("aapcs-vfp")',
        ):
            self.assertIn(token, text)
        output = Path(self.temporary.name) / "platform_setup.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-fropi",
                "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                "-o", str(output),
            ],
            check=True, capture_output=True, text=True,
        )
        self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
