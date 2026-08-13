"""Behaviourally validate the clean-room TinyFrame receive parser.

`research/candidates/tinyframe_parser.c` re-expresses the G2 2.2.6.10 TinyFrame
receive state machine (TF_AcceptChar) recovered by disassembly
(docs/research/tinyframe-wire-format-recovery-audit.md). This test compiles it
with the resolved host compiler (honours OPENCFW_CLANG, so it runs under
linux-clang), composes frames per the recovered wire format, and checks that
the parser accepts valid frames, extracts id/len/type/payload correctly,
rejects head- and data-checksum mismatches, resynchronises on the SOF byte, and
enforces the recovered 24576-byte payload cap.

Host behavioural check only; no target overlay, signing, flashing, or hardware.
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
CANDIDATE = ROOT / "research" / "candidates" / "tinyframe_parser.c"
MAX_PAYLOAD = 0x6000
SOF = 0x01
CANDIDATE_SOURCE_SHA256 = "5f9fac64bdf11fb6fdc3e7bead5386537dc2ff60304beecd39305cc4beced7ac"


def crc16_arc(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
    return crc & 0xFFFF


def compose(frame_id: int, frame_type: int, payload: bytes) -> bytes:
    sof = bytes([SOF])
    head = struct.pack(">HHH", frame_id, len(payload), frame_type)
    frame = sof + head + struct.pack(">H", crc16_arc(sof + head)) + payload
    if payload:
        frame += struct.pack(">H", crc16_arc(payload))
    return frame


class TfRx(ctypes.Structure):
    _fields_ = [
        ("state", ctypes.c_uint8),
        ("id", ctypes.c_uint16),
        ("len", ctypes.c_uint16),
        ("type", ctypes.c_uint16),
        ("rxi", ctypes.c_uint16),
        ("cksum", ctypes.c_uint16),
        ("ref_cksum", ctypes.c_uint16),
        ("data", ctypes.c_uint8 * MAX_PAYLOAD),
    ]


class TfFrame(ctypes.Structure):
    _fields_ = [
        ("accepted", ctypes.c_int),
        ("id", ctypes.c_uint16),
        ("len", ctypes.c_uint16),
        ("type", ctypes.c_uint16),
        ("data", ctypes.c_uint8 * MAX_PAYLOAD),
    ]


class TinyFrameParserCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "tinyframe_parser.dylib"
            if sys.platform == "darwin"
            else "tinyframe_parser.so"
        )
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(CANDIDATE)]
        command.extend(
            ["-dynamiclib", "-o", str(library)]
            if sys.platform == "darwin"
            else ["-shared", "-fPIC", "-o", str(library)]
        )
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.tf_rx_init.argtypes = [ctypes.POINTER(TfRx)]
        cls.lib.tf_accept_char.argtypes = [
            ctypes.POINTER(TfRx),
            ctypes.c_uint8,
            ctypes.POINTER(TfFrame),
        ]
        cls.lib.tf_accept_char.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def _feed(self, stream: bytes):
        rx = TfRx()
        self.lib.tf_rx_init(ctypes.byref(rx))
        out = TfFrame()
        accepted = []
        for byte in stream:
            if self.lib.tf_accept_char(ctypes.byref(rx), byte, ctypes.byref(out)):
                accepted.append(
                    (out.id, out.type, bytes(out.data[: out.len]))
                )
                out.accepted = 0
        return accepted

    def test_candidate_source_is_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
            CANDIDATE_SOURCE_SHA256,
        )

    def test_valid_frame_is_accepted_and_decoded(self) -> None:
        payload = b"hello G2 openCFW"
        got = self._feed(compose(0x1234, 0x0009, payload))
        self.assertEqual(got, [(0x1234, 0x0009, payload)])

    def test_zero_length_payload(self) -> None:
        frame = compose(0x0001, 0x00E0, b"")
        self.assertEqual(len(frame), 9)
        got = self._feed(frame)
        self.assertEqual(got, [(0x0001, 0x00E0, b"")])

    def test_legacy_head_crc_without_sof_is_rejected(self) -> None:
        payload = b"legacy"
        head = struct.pack(">HHH", 0x0102, len(payload), 0x0304)
        legacy = (
            bytes([SOF])
            + head
            + struct.pack(">H", crc16_arc(head))
            + payload
            + struct.pack(">H", crc16_arc(payload))
        )
        self.assertEqual(self._feed(legacy), [])

    def test_zero_length_frame_does_not_consume_data_checksum(self) -> None:
        zero = compose(0x0001, 0x0002, b"")
        following = compose(0x0003, 0x0004, b"next")
        self.assertEqual(
            self._feed(zero + following),
            [(0x0001, 0x0002, b""), (0x0003, 0x0004, b"next")],
        )

    def test_resync_on_leading_garbage(self) -> None:
        # Garbage must not contain the SOF byte (0x01): as in real TinyFrame,
        # a spurious SOF legitimately starts a doomed frame. Non-SOF noise is
        # skipped until the real SOF.
        payload = b"\xde\xad\xbe\xef"
        stream = b"\x00\xff\x02\xaa" + compose(0x0042, 0x0003, payload)
        self.assertEqual(self._feed(stream), [(0x0042, 0x0003, payload)])

    def test_head_checksum_mismatch_is_rejected(self) -> None:
        frame = bytearray(compose(0x1111, 0x2222, b"abc"))
        frame[7] ^= 0xFF  # corrupt a head-checksum byte
        self.assertEqual(self._feed(bytes(frame)), [])

    def test_data_checksum_mismatch_is_rejected(self) -> None:
        frame = bytearray(compose(0x1111, 0x2222, b"abcd"))
        frame[-1] ^= 0x01  # corrupt a data-checksum byte
        self.assertEqual(self._feed(bytes(frame)), [])

    def test_two_back_to_back_frames(self) -> None:
        a = compose(0x0001, 0x0001, b"one")
        b = compose(0x0002, 0x0002, b"twotwo")
        self.assertEqual(
            self._feed(a + b),
            [(0x0001, 0x0001, b"one"), (0x0002, 0x0002, b"twotwo")],
        )

    def test_max_payload_boundary(self) -> None:
        payload = bytes((i * 7) & 0xFF for i in range(MAX_PAYLOAD))
        got = self._feed(compose(0x0abc, 0x0005, payload))
        self.assertEqual(got, [(0x0abc, 0x0005, payload)])


if __name__ == "__main__":
    unittest.main()
