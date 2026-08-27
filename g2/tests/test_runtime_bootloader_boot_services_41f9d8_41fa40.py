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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_boot_services_41f9d8.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_boot_services_host.c"
RUN_BASE = 0x00410000
FUNCTIONS = (
    (
        0x0041F9D8,
        0x0041F9E6,
        "f9d267ca0fe9273e71065d8d35b31cf4d296067d79e9787d7635113ae2ab6676",
        (0x0041B866, 0x004204AE, 0x00420560, 0x00420598, 0x004304CE),
    ),
    (
        0x0041F9E6,
        0x0041F9EE,
        "dddd4579356bb2192ab70e96b40e55aed4767132acd66a48667053c1045ec591",
        (
            0x0041D324, 0x0041D33C, 0x0041D34A, 0x0041D362, 0x0041D372,
            0x0041D388, 0x0041D398, 0x0041D3B0, 0x0041D3C8, 0x0041D3DE,
            0x0041F98A, 0x004207AC, 0x004207E0,
        ),
    ),
    (
        0x0041F9F0,
        0x0041F9F8,
        "c4fc4b65a098dcd475fdd6b5d696b5e7e3957c2af7e722653ea39798d642e3ad",
        (),
    ),
    (
        0x0041F9F8,
        0x0041FA40,
        "bc69f5a1adfd743601ee6cfc46e0397fa7ab4dfd46176d3d4b626f8361cccf22",
        (0x0041B86A,),
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


class BootloaderBootServicesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / (
            "boot_services.dylib" if sys.platform == "darwin" else "boot_services.so"
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

    def test_authenticated_bodies_callers_literals_and_table(self) -> None:
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
        self.assertEqual(
            struct.unpack_from("<I", image, 0x0041FA4C - RUN_BASE)[0],
            0x0041F9F1,
        )
        records = tuple(
            struct.unpack_from("<II", image, address - RUN_BASE)
            for address in range(0x00433440, 0x00433460, 8)
        )
        self.assertEqual(
            records,
            (
                (0x004301D7, 1),
                (0x0043194D, 1),
                (0x00415591, 25),
                (0x0041FD71, 26),
            ),
        )

    def test_delay_compare_sort_dispatch_and_cap_semantics(self) -> None:
        for name in (
            "delays", "comparator", "sorted_dispatch", "count_cap", "empty_table",
        ):
            with self.subTest(case=name):
                function = getattr(self.loaded, f"open_cfw_test_boot_services_{name}")
                function.restype = ctypes.c_uint32
                self.assertEqual(function(), 1)

    def test_source_seams_and_freestanding_target_compile(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        for token in (
            "0x00433440U", "0x00433460U", "0x20022E00U",
            "0x0041D1C1U", "0x0041568DU", "0x00423D09U",
            "1000U", "256U", "8U",
        ):
            self.assertIn(token, text)
        output = Path(self.temporary.name) / "boot_services.o"
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
