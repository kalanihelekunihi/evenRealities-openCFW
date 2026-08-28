from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_bit_run_helpers_41ff60.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_bit_run_helpers_host.c"
BASE = 0x00410000


def thumb_bl_target(blob: bytes, address: int) -> int | None:
    offset = address - BASE
    first = int.from_bytes(blob[offset : offset + 2], "little")
    second = int.from_bytes(blob[offset + 2 : offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    delta = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((first & 0x3FF) << 12)
        | ((second & 0x7FF) << 1)
    )
    if delta & (1 << 24):
        delta -= 1 << 25
    return address + 4 + delta


def expected_length(value: int) -> int:
    value &= 0xFFFFFFFF
    result = 0
    while value:
        value &= (value << 1) & 0xFFFFFFFF
        result += 1
    return result


def expected_center(value: int) -> int:
    value &= 0xFFFFFFFF
    current = 0
    best = 0
    center = 0
    in_run = False
    best_odd = 0
    finish = False
    for bit in range(32):
        if (value >> bit) & 1:
            in_run = True
            current += 1
        elif in_run:
            in_run = False
            finish = True
        if bit == 31 and in_run:
            finish = True
        if finish:
            if best < current:
                best = current
                center = (bit - 1 - (current >> 1)) & 0xFFFFFFFF
                best_odd = current & 1
            current = 0
            finish = False
    if center < 16:
        if value & (1 << 1):
            center = (center - best_odd) & 0xFFFFFFFF
    elif value & (1 << 30):
        center = (center + 1) & 0xFFFFFFFF
    return center


class BitRunHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "fixture.dylib" if sys.platform == "darwin" else "fixture.so"
        library_path = Path(cls.temporary.name) / suffix
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o",
                str(library_path),
            ],
            check=True,
        )
        cls.library = ctypes.CDLL(str(library_path))
        for name in ("length", "center"):
            function = getattr(cls.library, f"open_cfw_bit_run_fixture_{name}")
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_stock_bodies_and_callers(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(
            hashlib.sha256(blob[0xFF60:0xFF74]).hexdigest(),
            "93e9d3dc1df2d950f6d5c0bae26e198c166b5388c3a4a69f9999715358fc4ad2",
        )
        self.assertEqual(
            hashlib.sha256(blob[0xFF74:0x10002]).hexdigest(),
            "3c89f5f441c8c6b0163697b7eb6f2bafe5a4ff6092b294191a5200ae6fa679ed",
        )
        callers = lambda target: tuple(
            address
            for address in range(BASE, BASE + len(blob) - 3, 2)
            if thumb_bl_target(blob, address) == target
        )
        self.assertEqual(callers(0x0041FF60), (0x004200BE,))
        self.assertEqual(callers(0x0041FF74), (0x00420158,))

    def test_length_and_center_match_the_recovered_contract(self) -> None:
        values = [
            0,
            1,
            2,
            3,
            0xFFFFFFFF,
            0x80000000,
            0x40000000,
            0xC0000000,
            0x0000000E,
            0x00FF0F00,
            0x55555555,
            0xAAAAAAAA,
        ]
        generator = random.Random(0x41FF60)
        values.extend(generator.getrandbits(32) for _ in range(2048))
        for value in values:
            with self.subTest(value=f"0x{value:08X}"):
                self.assertEqual(
                    self.library.open_cfw_bit_run_fixture_length(value),
                    expected_length(value),
                )
                self.assertEqual(
                    self.library.open_cfw_bit_run_fixture_center(value),
                    expected_center(value),
                )

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "bit-run.o"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-target",
                "arm-none-eabi",
                "-mcpu=cortex-m55",
                "-mthumb",
                "-std=c11",
                "-Oz",
                "-ffreestanding",
                "-fno-builtin",
                "-ffunction-sections",
                "-fdata-sections",
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
                "-fropi",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-c",
                str(SOURCE),
                "-o",
                str(output),
            ],
            check=True,
            capture_output=True,
        )


if __name__ == "__main__":
    unittest.main()
