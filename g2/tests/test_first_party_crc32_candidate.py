"""Validate the first-party CRC-32 candidate against the firmware.

`research/candidates/first_party_crc32.c` re-expresses the standard reflected
CRC-32 (poly 0xEDB88320) used by the G2 2.2.6.10 first-party protocol layer.
This test compiles it with the resolved host compiler (honours OPENCFW_CLANG,
so it runs under linux-clang) and proves its generated table is byte-identical
to the firmware's CRC-32 table at run 0x006987A8 (file 0x00260BC8), and that it
computes the published CRC-32 check value. Host equivalence check only; no
target overlay, signing, flashing, or hardware.
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
CANDIDATE = ROOT / "research" / "candidates" / "first_party_crc32.c"
MAIN_PACKAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"

LOAD_BASE = 0x00437FE0
CRC_TABLE_RUN = 0x006987A8
CRC_TABLE_FILE = CRC_TABLE_RUN - LOAD_BASE  # 0x00260BC8
CRC_TABLE_BYTES = 1024  # 256 * uint32
FIRMWARE_TABLE_SHA256 = (
    "12f3e0576d447eb37b36d82ba0c1c5481b8f0d12fdc70347ce4a076b229d4c86"
)
MAIN_PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
CANDIDATE_SOURCE_SHA256 = "5d8de79499214e551c3afdd548547b03fbe3ff5802d304a56e9899c376c10e9a"


def crc32_reference(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xEDB88320 if (crc & 1) else (crc >> 1)
    return crc ^ 0xFFFFFFFF


class FirstPartyCrc32CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.image = MAIN_PACKAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory()
        lib = Path(cls.temporary.name) / (
            "crc32.dylib" if sys.platform == "darwin" else "crc32.so"
        )
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(CANDIDATE)]
        command.extend(
            ["-dynamiclib", "-o", str(lib)]
            if sys.platform == "darwin"
            else ["-shared", "-fPIC", "-o", str(lib)]
        )
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(lib))
        cls.lib.even_crc32_build_table.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.even_crc32_build_table.restype = None
        cls.lib.even_crc32.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        cls.lib.even_crc32.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_firmware_inputs_are_pinned(self) -> None:
        self.assertEqual(hashlib.sha256(self.image).hexdigest(), MAIN_PACKAGE_SHA256)
        table = self.image[CRC_TABLE_FILE : CRC_TABLE_FILE + CRC_TABLE_BYTES]
        self.assertEqual(hashlib.sha256(table).hexdigest(), FIRMWARE_TABLE_SHA256)
        self.assertEqual(
            hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
            CANDIDATE_SOURCE_SHA256,
        )

    def test_candidate_table_is_byte_identical_to_firmware(self) -> None:
        buffer = (ctypes.c_uint32 * 256)()
        self.lib.even_crc32_build_table(buffer)
        candidate_table = struct.pack("<256I", *buffer)
        firmware_table = self.image[
            CRC_TABLE_FILE : CRC_TABLE_FILE + CRC_TABLE_BYTES
        ]
        self.assertEqual(candidate_table, firmware_table)

    def test_check_value_and_reference(self) -> None:
        data = b"123456789"
        buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        self.assertEqual(self.lib.even_crc32(buf, len(data)), 0xCBF43926)
        for vector in (b"", b"\x00", bytes(range(256)), b"openCFW"):
            with self.subTest(vector=vector[:16]):
                buf = (ctypes.c_uint8 * len(vector)).from_buffer_copy(
                    vector or b"\x00"
                )
                self.assertEqual(
                    self.lib.even_crc32(buf, len(vector)),
                    crc32_reference(vector),
                )


if __name__ == "__main__":
    unittest.main()
