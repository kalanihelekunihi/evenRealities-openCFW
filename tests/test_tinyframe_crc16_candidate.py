"""Validate the clean-room TinyFrame CRC-16 candidate against the firmware.

The candidate `research/candidates/tinyframe_crc16.c` is a source re-expression
of the G2 2.2.6.10 TinyFrame `TF_CKSUM_CRC16` checksum recovered by disassembly
(see docs/research/tinyframe-wire-format-recovery-audit.md). This test compiles
it with the resolved host compiler and proves:

1. its generated 256-entry table is byte-identical to the firmware's static
   CRC table at run 0x006C0950 (file offset 0x00288970); and
2. its start/add/end contract computes CRC-16/ARC (poly 0x8005 reflected
   0xA001, seed 0x0000, no final XOR) for arbitrary buffers.

The compile honors OPENCFW_CLANG, so it runs under the Linux (linux-clang)
toolchain. This is a host behavioral/equivalence check; it does not build a
target overlay, sign, flash, or touch hardware.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "research" / "candidates" / "tinyframe_crc16.c"
MAIN_PACKAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"

# Recovered firmware evidence (see the audit doc).
LOAD_BASE = 0x00437FE0
CRC_TABLE_RUN = 0x006C0950
CRC_TABLE_FILE = CRC_TABLE_RUN - LOAD_BASE  # 0x00288970
CRC_TABLE_BYTES = 512  # 256 * uint16
FIRMWARE_TABLE_SHA256 = (
    "961656eaf43bdf70937151a003627324be86c28ca32285f58edd5f5c73c51b79"
)
MAIN_PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
CANDIDATE_SOURCE_SHA256 = (
    "14b9cea3e209a247134b6bb37cfb82f383376d9c7a228b3d473290a6153463ce"
)


def _crc16_arc_reference(data: bytes) -> int:
    """Independent CRC-16/ARC reference (poly 0xA001 reflected, seed 0)."""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return crc & 0xFFFF


class TinyFrameCrc16CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.image = MAIN_PACKAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "tinyframe_crc16.dylib"
            if sys.platform == "darwin"
            else "tinyframe_crc16.so"
        )
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        command = [
            clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(CANDIDATE),
        ]
        command.extend(
            ["-dynamiclib", "-o", str(library)]
            if sys.platform == "darwin"
            else ["-shared", "-fPIC", "-o", str(library)]
        )
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.tf_crc16_build_table.argtypes = [ctypes.POINTER(ctypes.c_uint16)]
        cls.loaded.tf_crc16_build_table.restype = None
        cls.loaded.tf_crc16.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        cls.loaded.tf_crc16.restype = ctypes.c_uint16
        cls.loaded.tf_cksum_start.restype = ctypes.c_uint16

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_firmware_inputs_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.image).hexdigest(), MAIN_PACKAGE_SHA256
        )
        table = self.image[CRC_TABLE_FILE : CRC_TABLE_FILE + CRC_TABLE_BYTES]
        self.assertEqual(hashlib.sha256(table).hexdigest(), FIRMWARE_TABLE_SHA256)
        self.assertEqual(
            hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
            CANDIDATE_SOURCE_SHA256,
        )

    def test_candidate_table_is_byte_identical_to_firmware(self) -> None:
        buffer = (ctypes.c_uint16 * 256)()
        self.loaded.tf_crc16_build_table(buffer)
        candidate_table = struct.pack("<256H", *buffer)
        firmware_table = self.image[
            CRC_TABLE_FILE : CRC_TABLE_FILE + CRC_TABLE_BYTES
        ]
        self.assertEqual(candidate_table, firmware_table)

    def test_candidate_crc_matches_arc_reference(self) -> None:
        self.assertEqual(self.loaded.tf_cksum_start(), 0)
        vectors = [
            b"",
            b"\x01",
            b"123456789",  # canonical CRC check string
            bytes(range(256)),
            b"\x01\x00\x01\x00\x03",  # a plausible SOF|ID|... head prefix
        ]
        for data in vectors:
            with self.subTest(data=data[:16]):
                buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(
                    data or b"\x00"
                )
                observed = self.loaded.tf_crc16(buf, len(data))
                self.assertEqual(observed, _crc16_arc_reference(data))

    def test_arc_check_value(self) -> None:
        # CRC-16/ARC of "123456789" is 0xBB3D (published check value).
        data = b"123456789"
        buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        self.assertEqual(self.loaded.tf_crc16(buf, len(data)), 0xBB3D)


if __name__ == "__main__":
    unittest.main()
