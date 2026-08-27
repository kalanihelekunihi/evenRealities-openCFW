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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_easylogger_transport_41b854.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_easylogger_transport_host.c"
RUN_BASE = 0x00410000
FUNCTIONS = (
    (
        0x0041B854,
        0x0041B862,
        "d46fae4c767497230f0f9b6c050033b824887d7e59dd06e893eee604bbb9c59d",
        (0x0041A694,),
    ),
    (
        0x0041F918,
        0x0041F9B6,
        "363f18ceab0127d6da1b90de353495e370f50bce9631ee5ffbc83c2d725a2a95",
        (0x0041B85C,),
    ),
)


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
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((first & 0x3FF) << 12)
        | ((second & 0x7FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


class BootloaderEasyloggerTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / (
            "easylogger_transport.dylib"
            if sys.platform == "darwin"
            else "easylogger_transport.so"
        )
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_stock_bodies_and_direct_callers(self) -> None:
        image = OFFICIAL.read_bytes()
        for start, end, expected_sha, expected_callers in FUNCTIONS:
            with self.subTest(address=hex(start)):
                body = image[start - RUN_BASE:end - RUN_BASE]
                self.assertEqual(hashlib.sha256(body).hexdigest(), expected_sha)
                callers = tuple(
                    address
                    for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                    if decode_bl(image, address) == start
                )
                self.assertEqual(callers, expected_callers)

    def test_channel_descriptor_polling_and_driver_semantics(self) -> None:
        for name in (
            "rejects_invalid_channels",
            "driver_routes_channel_one",
            "descriptor_and_polling",
            "start_failure_and_timeout",
        ):
            with self.subTest(case=name):
                function = getattr(
                    self.loaded, f"open_cfw_test_easylogger_transport_{name}"
                )
                function.restype = ctypes.c_uint32
                self.assertEqual(function(), 1)

    def test_source_seams_and_freestanding_target_compile(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        for token in (
            "0x20000454U", "28U", "24U", "25U", "56U", "52U",
            "0x00415FF5U", "0x0041F919U", "0x004233E9U", "0x0041F9E7U",
            "1000U", "10U",
        ):
            self.assertIn(token, text)
        output = Path(self.temporary.name) / "easylogger_transport.o"
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
