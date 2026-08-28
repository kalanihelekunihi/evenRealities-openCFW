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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_timing_auto_4201ba.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_timing_auto_host.c"
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


class MspiTimingAutoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "fixture.dylib" if sys.platform == "darwin" else "fixture.so"
        path = Path(cls.temporary.name) / suffix
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
                str(path),
            ],
            check=True,
        )
        cls.library = ctypes.CDLL(str(path))
        cls.library.open_cfw_mspi_timing_auto_fixture_set_result.argtypes = [
            ctypes.c_size_t,
            ctypes.c_uint32,
        ]
        cls.library.open_cfw_mspi_timing_auto_fixture_active.argtypes = [
            ctypes.c_size_t
        ]
        cls.library.open_cfw_mspi_timing_auto_fixture_active.restype = ctypes.c_uint32
        cls.library.open_cfw_mspi_timing_auto_fixture_log.argtypes = [ctypes.c_size_t]
        cls.library.open_cfw_mspi_timing_auto_fixture_log.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_stock_body_caller_literals_and_seams(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x101BA:0x10254]
        self.assertEqual(len(body), 154)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "a31a24975e2a7de11d5a42b05db91799e7e9656bca2cc22112867efdf9f2b9b7",
        )
        self.assertEqual(
            tuple(
                address
                for address in range(BASE, BASE + len(blob) - 3, 2)
                if thumb_bl_target(blob, address) == 0x004201BA
            ),
            (0x004204BA,),
        )
        self.assertEqual(thumb_bl_target(blob, 0x004201C4), 0x00426C10)
        self.assertEqual(thumb_bl_target(blob, 0x004201CA), 0x00420002)
        self.assertEqual(thumb_bl_target(blob, 0x00420210), 0x004176CE)
        self.assertEqual(thumb_bl_target(blob, 0x0042024C), 0x004176CE)
        for address, value in (
            (0x00420A04, 0x2000023C),
            (0x00420978, 0x00431540),
            (0x00420ADC, 0x00433CD8),
            (0x00420AF8, 0x00430BD0),
            (0x00420AFC, 0x004337B4),
            (0x00420B00, 0x00430C4C),
        ):
            offset = address - BASE
            self.assertEqual(int.from_bytes(blob[offset : offset + 4], "little"), value)

    def test_success_publishes_scanned_configuration_and_logs_it(self) -> None:
        self.library.open_cfw_mspi_timing_auto_fixture_reset()
        values = [3, 1, 2, 9, 14, 8]
        for index, value in enumerate(values):
            self.library.open_cfw_mspi_timing_auto_fixture_set_result(index, value)
        self.library.open_cfw_mspi_timing_auto_fixture_run()
        self.assertEqual(self.library.open_cfw_mspi_timing_auto_fixture_scan_count(), 1)
        self.assertEqual(
            [self.library.open_cfw_mspi_timing_auto_fixture_active(i) for i in range(6)],
            values,
        )
        self.assertEqual(
            [self.library.open_cfw_mspi_timing_auto_fixture_active(i) for i in (6, 7)],
            [0xA6, 0xA7],
        )
        self.assertEqual(self.library.open_cfw_mspi_timing_auto_fixture_log_count(), 1)
        self.assertEqual(
            [self.library.open_cfw_mspi_timing_auto_fixture_log(i) for i in range(9)],
            [2, 0x1F3, 0x430BD0, *values],
        )
        self.assertEqual(self.library.open_cfw_mspi_timing_auto_fixture_log(11), 6)

    def test_failure_preserves_active_configuration_and_logs_fallback(self) -> None:
        self.library.open_cfw_mspi_timing_auto_fixture_reset()
        self.library.open_cfw_mspi_timing_auto_fixture_set_status(7)
        self.library.open_cfw_mspi_timing_auto_fixture_run()
        active = [0xA0 + index for index in range(6)]
        self.assertEqual(
            [self.library.open_cfw_mspi_timing_auto_fixture_active(i) for i in range(6)],
            active,
        )
        self.assertEqual(
            [self.library.open_cfw_mspi_timing_auto_fixture_log(i) for i in range(9)],
            [1, 0x1FB, 0x430C4C, *active],
        )

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "timing-auto.o"
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
