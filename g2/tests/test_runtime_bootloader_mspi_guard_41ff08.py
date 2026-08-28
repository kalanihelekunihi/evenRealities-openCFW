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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_guard_41ff08.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_guard_host.c"
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


class MspiGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "fixture.dylib" if sys.platform == "darwin" else "fixture.so"
        cls.library_path = Path(cls.temporary.name) / suffix
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
                str(cls.library_path),
            ],
            check=True,
        )
        cls.library = ctypes.CDLL(str(cls.library_path))
        cls.library.open_cfw_mspi_guard_fixture_reset.argtypes = [ctypes.c_uint32]
        cls.library.open_cfw_mspi_guard_fixture_call.argtypes = [ctypes.c_uint32]
        cls.library.open_cfw_mspi_guard_fixture_call.restype = ctypes.c_uint32
        cls.library.open_cfw_mspi_guard_fixture_count.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def calls(self) -> list[int]:
        return [
            self.library.open_cfw_mspi_guard_fixture_call(index)
            for index in range(self.library.open_cfw_mspi_guard_fixture_count())
        ]

    def test_authenticated_stock_functions_callers_and_state_literal(self) -> None:
        blob = OFFICIAL.read_bytes()
        spans = (
            (0x0041FF08, 0x0041FF1E, "02963ef679faf897f9108a5e1526bd79eccabb28b11192d6325dfb4165ca0dc5", (0x00420A48, 0x00420B54, 0x00420F98)),
            (0x0041FF1E, 0x0041FF34, "ecb3a585f0f910e6428aa9a722ff0f2a621ca1d195b8fd8b4a9d4f2820f0dddd", (0x00420AD2, 0x00420C0C, 0x00420FE8)),
        )
        for start, end, expected_hash, expected_callers in spans:
            self.assertEqual(
                hashlib.sha256(blob[start - BASE : end - BASE]).hexdigest(),
                expected_hash,
            )
            self.assertEqual(
                tuple(
                    address
                    for address in range(BASE, BASE + len(blob) - 3, 2)
                    if thumb_bl_target(blob, address) == start
                ),
                expected_callers,
            )
        self.assertEqual(
            int.from_bytes(blob[0x10AE0 : 0x10AE4], "little"),
            0x200271C5,
        )

    def test_enter_always_acquires_and_conditionally_disables(self) -> None:
        self.library.open_cfw_mspi_guard_fixture_reset(0)
        self.library.open_cfw_bootloader_mspi_guard_enter_41ff08()
        self.assertEqual(self.calls(), [1, 2])

        self.library.open_cfw_mspi_guard_fixture_reset(1)
        self.library.open_cfw_bootloader_mspi_guard_enter_41ff08()
        self.assertEqual(self.calls(), [1])

    def test_exit_conditionally_enables_and_always_releases(self) -> None:
        self.library.open_cfw_mspi_guard_fixture_reset(0)
        self.library.open_cfw_bootloader_mspi_guard_exit_41ff1e()
        self.assertEqual(self.calls(), [3, 4])

        self.library.open_cfw_mspi_guard_fixture_reset(1)
        self.library.open_cfw_bootloader_mspi_guard_exit_41ff1e()
        self.assertEqual(self.calls(), [4])

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "mspi-guard.o"
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
