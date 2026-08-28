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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_timing_scan_420002.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_timing_scan_host.c"
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


def expected_center(value: int) -> int:
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
    if center < 16 and value & 2:
        center = (center - best_odd) & 0xFFFFFFFF
    elif center >= 16 and value & (1 << 30):
        center = (center + 1) & 0xFFFFFFFF
    return center


class MspiTimingScanTests(unittest.TestCase):
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
        cls.library.open_cfw_mspi_timing_scan_fixture_set_mask.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.library.open_cfw_mspi_timing_scan_fixture_run.argtypes = [
            ctypes.POINTER(ctypes.c_uint8)
        ]
        cls.library.open_cfw_mspi_timing_scan_fixture_run.restype = ctypes.c_uint32
        cls.library.open_cfw_mspi_timing_scan_fixture_log.argtypes = [
            ctypes.c_size_t,
            ctypes.c_size_t,
        ]
        cls.library.open_cfw_mspi_timing_scan_fixture_log.restype = ctypes.c_size_t
        cls.library.open_cfw_mspi_timing_scan_fixture_table_byte.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.library.open_cfw_mspi_timing_scan_fixture_table_byte.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_stock_body_callers_and_retained_seams(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x10002:0x101BA]
        self.assertEqual(len(body), 440)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "9618b6beec8ecb55dc3e00510fb11d23951d2c145521c3b418bc445451d6dcb6",
        )
        self.assertEqual(
            tuple(
                address
                for address in range(BASE, BASE + len(blob) - 3, 2)
                if thumb_bl_target(blob, address) == 0x00420002
            ),
            (0x004201CA,),
        )
        self.assertEqual(int.from_bytes(blob[0x10AE4:0x10AE8], "little"), 0x002539C2)
        self.assertEqual(int.from_bytes(blob[0x10AE8:0x10AEC], "little"), 0x20000244)
        self.assertEqual(thumb_bl_target(blob, 0x00420036), 0x004251C0)
        self.assertEqual(thumb_bl_target(blob, 0x0042003C), 0x0042059E)
        self.assertEqual(thumb_bl_target(blob, 0x004200BE), 0x0041FF60)
        self.assertEqual(thumb_bl_target(blob, 0x00420158), 0x0041FF74)

    def test_full_scan_first_longest_selection_result_and_logs(self) -> None:
        self.library.open_cfw_mspi_timing_scan_fixture_reset()
        self.library.open_cfw_mspi_timing_scan_fixture_set_mask(5, 0x000001F0)
        winning_mask = 0x0000FC00
        self.library.open_cfw_mspi_timing_scan_fixture_set_mask(7, winning_mask)
        self.library.open_cfw_mspi_timing_scan_fixture_set_mask(8, 0x003F0000)
        result = (ctypes.c_uint8 * 6)()
        self.assertEqual(self.library.open_cfw_mspi_timing_scan_fixture_run(result), 0)
        self.assertEqual(self.library.open_cfw_mspi_timing_scan_fixture_control_count(), 1152)
        self.assertEqual(self.library.open_cfw_mspi_timing_scan_fixture_read_count(), 1152)
        self.assertEqual(
            list(result),
            [
                self.library.open_cfw_mspi_timing_scan_fixture_table_byte(7, 0),
                self.library.open_cfw_mspi_timing_scan_fixture_table_byte(7, 1),
                self.library.open_cfw_mspi_timing_scan_fixture_table_byte(7, 2),
                self.library.open_cfw_mspi_timing_scan_fixture_table_byte(7, 3),
                expected_center(winning_mask),
                self.library.open_cfw_mspi_timing_scan_fixture_table_byte(7, 5),
            ],
        )
        self.assertEqual(self.library.open_cfw_mspi_timing_scan_fixture_log_count(), 3)
        logs = self.library.open_cfw_mspi_timing_scan_fixture_log
        self.assertEqual([logs(0, i) for i in range(4)], [0x1C6, 0x43160C, 6, 7])
        self.assertEqual([logs(1, i) for i in range(2)], [0x1CD, 0x4313D8])
        self.assertEqual(logs(1, 7), winning_mask)
        self.assertEqual([logs(2, i) for i in range(3)], [0x1D3, 0x4334B4, expected_center(winning_mask)])

    def test_all_failed_reads_select_row_zero_and_zero_center(self) -> None:
        self.library.open_cfw_mspi_timing_scan_fixture_reset()
        result = (ctypes.c_uint8 * 6)(*[0xAA] * 6)
        self.assertEqual(self.library.open_cfw_mspi_timing_scan_fixture_run(result), 0)
        self.assertEqual(result[4], 0)
        self.assertEqual(
            [result[i] for i in (0, 1, 2, 3, 5)],
            [
                self.library.open_cfw_mspi_timing_scan_fixture_table_byte(0, i)
                for i in (0, 1, 2, 3, 5)
            ],
        )

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        output = Path(self.temporary.name) / "timing-scan.o"
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
