"""Validate the clean-room IAR DLIB scanset-matcher candidate against stock.

The candidate `research/candidates/iar_dlib_scanset_matcher.c` is a clean-room
behavioral recreation of the 70-byte %[...] scanset membership matcher at
stock [0x004D2112,0x004D2158), bounded by the formatted-I/O audit (see
docs/research/g2-iar-dlib-format-io-recovery.md).  This test compiles it with
the resolved host compiler and proves:

1. the pinned stock body (SHA-256 cross-checked against the bounded audit's
   per-unit pin) and the candidate source are byte-identical to the reviewed
   evidence; and
2. the candidate reproduces the stock body's verdicts on a deterministic
   4,022-vector stream (22 directed scanset edge cases plus 4,000 seeded
   random tables), pinned to the digest recorded by emulating the
   authenticated stock bytes under Unicorn 2.1.4 on the Lorelei host
   (Cortex-M Thumb mode, stop-at-LR harness, disposable transport directory
   `/var/tmp/opencfw-scanset-qualify`).

The compile honors OPENCFW_CLANG.  This is a host behavioral/equivalence
check; it does not build a target overlay, sign, flash, or touch hardware.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "research" / "candidates" / "iar_dlib_scanset_matcher.c"
MAIN_PACKAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"

LOAD_BASE = 0x00437FE0
STOCK_START = 0x004D2112
STOCK_END = 0x004D2158
# Cross-checked against the scanset_matcher pin in
# tools/analyze_g2_iar_dlib_format_io.py EXPECTED_UNITS.
STOCK_BODY_SHA256 = "154d24d2cf8f15fed12b16d091a734a70d216ceda6fabb0978cadb522139a2c2"
MAIN_PACKAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
CANDIDATE_SOURCE_SHA256 = "162af5e2a81165cdbb52f748e8a062eca3c3933b1df7b7f851285eee8f1eb43c"

SEED = 0x004D2112
ITERATIONS = 4_000
# Recorded by emulating the authenticated stock body under Unicorn 2.1.4 on
# Lorelei over the exact vector stream below.
STOCK_STREAM_SHA256 = "a6b61024db97f4f2cde71c88d8b7276a4f19dd0fff1c5bc0a3aa1865b5d51929"
STOCK_RESULTS_SHA256 = "9a6be0ba5dc0e399717bce0ef4d79a2792bcb084830bab3ec5f76a397d41dde9"
STOCK_MATCHES = 204


def _vectors():
    """Deterministic (table, ch) stream shared with the stock emulation."""

    rng = random.Random(SEED)
    directed = [
        (b"", 0x41),
        (b"A", 0x41),
        (b"A", 0x42),
        (b"-", 0x2D),
        (b"ab", 0x62),
        (b"abc", 0x62),
        (b"a-c", 0x62),   # range hit
        (b"a-c", 0x61),   # range low edge
        (b"a-c", 0x63),   # range high edge
        (b"a-c", 0x60),   # below range
        (b"a-c", 0x64),   # above range
        (b"--", 0x2D),    # '-' first byte, tail length
        (b"---", 0x2D),   # range over '-'
        (b"a-", 0x2D),    # trailing '-' is literal in the tail
        (b"xa-c", 0x62),  # literal then range
        (b"xa-c", 0x79),  # literal miss, range miss
        (b"a-cx", 0x78),  # range then trailing literal
        (b"\x00-\xff", 0x80),  # full-span range
        (b"A", 0x141),    # ch > 0xFF: stock UXTB masks to 0x41
        (b"A", 0x241),
        (b"z-a", 0x62),   # reversed range never matches mid
        (b"z-a", 0x7A),
    ]
    yield from directed
    for _ in range(ITERATIONS):
        length = rng.randrange(0, 25)
        table = bytes(rng.randrange(0, 256) for _ in range(length))
        yield table, rng.randrange(0, 0x200)


def _reference_match(table: bytes, ch: int) -> int:
    """Independent Python model of the recovered table walk."""

    value = ch & 0xFF
    cursor = 0
    remaining = len(table)
    while remaining >= 3:
        if table[cursor + 1] == 0x2D:
            if table[cursor] <= value <= table[cursor + 2]:
                return 1
            cursor += 3
            remaining -= 3
        else:
            if table[cursor] == value:
                return 1
            cursor += 1
            remaining -= 1
    while remaining:
        if table[cursor] == value:
            return 1
        cursor += 1
        remaining -= 1
    return 0


class IarDlibScansetMatcherCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.image = MAIN_PACKAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "iar_dlib_scanset_matcher.dylib"
            if sys.platform == "darwin"
            else "iar_dlib_scanset_matcher.so"
        )
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        command = [clang, "-O2", "-Wall", "-Wextra", "-Werror", str(CANDIDATE)]
        command.extend(
            ["-dynamiclib", "-o", str(library)]
            if sys.platform == "darwin"
            else ["-shared", "-fPIC", "-o", str(library)]
        )
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        function = cls.loaded.open_cfw_iar_scanset_match
        function.argtypes = [ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint]
        function.restype = ctypes.c_int
        cls.match = function

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_firmware_and_candidate_inputs_are_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(self.image).hexdigest(), MAIN_PACKAGE_SHA256
        )
        body = self.image[STOCK_START - LOAD_BASE : STOCK_END - LOAD_BASE]
        self.assertEqual(len(body), 70)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_BODY_SHA256)
        self.assertEqual(
            hashlib.sha256(CANDIDATE.read_bytes()).hexdigest(),
            CANDIDATE_SOURCE_SHA256,
        )

    def test_candidate_reproduces_stock_vector_stream(self) -> None:
        stream = bytearray()
        results = bytearray()
        for table, ch in _vectors():
            result = self.match(table, len(table), ch) & 1
            stream += bytes([len(table)]) + table + ch.to_bytes(4, "little")
            results.append(result)
        self.assertEqual(len(results), 4_022)
        self.assertEqual(hashlib.sha256(stream).hexdigest(), STOCK_STREAM_SHA256)
        self.assertEqual(sum(results), STOCK_MATCHES)
        self.assertEqual(
            hashlib.sha256(results).hexdigest(), STOCK_RESULTS_SHA256
        )

    def test_candidate_matches_independent_reference_model(self) -> None:
        for table, ch in _vectors():
            with self.subTest(table=table, ch=ch):
                self.assertEqual(
                    self.match(table, len(table), ch) & 1,
                    _reference_match(table, ch),
                )


if __name__ == "__main__":
    unittest.main()
