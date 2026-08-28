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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_xip_config_41ff34.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_xip_config_host.c"
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


class MspiXipConfigTests(unittest.TestCase):
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
        cls.library.open_cfw_mspi_xip_fixture_byte.argtypes = [ctypes.c_uint32]
        cls.library.open_cfw_mspi_xip_fixture_byte.restype = ctypes.c_uint32
        cls.library.open_cfw_mspi_xip_fixture_observed.argtypes = [ctypes.c_uint32]
        cls.library.open_cfw_mspi_xip_fixture_observed.restype = ctypes.c_size_t
        cls.library.open_cfw_mspi_xip_fixture_config_address.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_stock_body_callers_literals_and_control_seam(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0xFF34:0xFF60]
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "384a53a67910d2378b5f063ef45d4521d16c91098921a933f7a4a1d679eabe76",
        )
        self.assertEqual(
            tuple(
                address
                for address in range(BASE, BASE + len(blob) - 3, 2)
                if thumb_bl_target(blob, address) == 0x0041FF34
            ),
            (0x004203B0, 0x00420ED6, 0x00420F36),
        )
        self.assertEqual(int.from_bytes(blob[0x10A04:0x10A08], "little"), 0x2000023C)
        self.assertEqual(int.from_bytes(blob[0x10874:0x10878], "little"), 0x200270DC)
        self.assertEqual(thumb_bl_target(blob, 0x0041FF5A), 0x004251C0)

    def test_low_byte_mode_update_and_exact_control_arguments(self) -> None:
        for value, expected in ((1, 8), (0, 0), (2, 0), (0x101, 8)):
            with self.subTest(value=value):
                self.library.open_cfw_mspi_xip_fixture_reset()
                self.library.open_cfw_bootloader_mspi_xip_config_41ff34(value)
                self.assertEqual(self.library.open_cfw_mspi_xip_fixture_count(), 1)
                self.assertEqual(self.library.open_cfw_mspi_xip_fixture_byte(5), expected)
                self.assertEqual(
                    [self.library.open_cfw_mspi_xip_fixture_byte(i) for i in range(20) if i != 5],
                    [0xA0 + i for i in range(20) if i != 5],
                )
                self.assertEqual(
                    [self.library.open_cfw_mspi_xip_fixture_observed(i) for i in range(2)],
                    [0x2468, 16],
                )
                self.assertEqual(
                    self.library.open_cfw_mspi_xip_fixture_observed(2),
                    self.library.open_cfw_mspi_xip_fixture_config_address(),
                )

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "mspi-xip.o"
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
