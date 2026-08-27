from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_callback_41639a_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_callback_41639a.c"
RUN_BASE = 0x00410000
ENTRY = 0x0041639A


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
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


class BootloaderRuntimeCallback41639aTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-runtime-callback.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        word = ctypes.c_size_t
        cls.lib.open_cfw_test_callback_reset.argtypes = [word, word]
        cls.lib.open_cfw_bootloader_runtime_callback_41639a.argtypes = [word]
        cls.lib.open_cfw_bootloader_runtime_callback_41639a.restype = None
        cls.lib.open_cfw_test_callback_retained_owner.restype = word
        cls.lib.open_cfw_test_callback_retained_calls.restype = ctypes.c_uint
        cls.lib.open_cfw_test_callback_calls.restype = ctypes.c_uint
        cls.lib.open_cfw_test_callback_argument.restype = word

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_entry_and_registered_ingress(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x639A:0x63B2]
        self.assertEqual(
            (len(body), hashlib.sha256(body).hexdigest()),
            (24, "17d06f6db0e1d0bded2fd9f0bb6742fbb1a933eb67061eb9c4cb7079545f596b"),
        )
        self.assertEqual(image.count(struct.pack("<I", ENTRY | 1)), 1)
        self.assertEqual(image[0x69A0:0x69A4], struct.pack("<I", ENTRY | 1))
        self.assertEqual(image[0x6452:0x6456].hex(), "dff84c05")
        self.assertEqual(image[0x646A:0x646E].hex(), "dff83405")
        direct = tuple(
            address
            for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
            if decode_bl(image, address) == ENTRY
        )
        self.assertEqual(direct, ())

    def test_null_record_returns_after_one_retained_query(self) -> None:
        self.lib.open_cfw_test_callback_reset(0, 0x1234)
        self.lib.open_cfw_bootloader_runtime_callback_41639a(0xABCDEF)
        self.assertEqual(self.lib.open_cfw_test_callback_retained_calls(), 1)
        self.assertEqual(self.lib.open_cfw_test_callback_retained_owner(), 0xABCDEF)
        self.assertEqual(self.lib.open_cfw_test_callback_calls(), 0)

    def test_even_and_flagged_records_invoke_exact_callback_argument(self) -> None:
        for result_kind in (1, 2):
            with self.subTest(result_kind=result_kind):
                self.lib.open_cfw_test_callback_reset(result_kind, 0x12345678)
                self.lib.open_cfw_bootloader_runtime_callback_41639a(7)
                self.assertEqual(self.lib.open_cfw_test_callback_retained_calls(), 1)
                self.assertEqual(self.lib.open_cfw_test_callback_calls(), 1)
                self.assertEqual(self.lib.open_cfw_test_callback_argument(), 0x12345678)

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "runtime-callback.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True, capture_output=True, text=True,
        )


if __name__ == "__main__":
    unittest.main()
