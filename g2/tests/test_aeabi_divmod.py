from __future__ import annotations

import os

import ctypes
import hashlib
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "aeabi_divmod.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "aeabi_divmod_host.c"
MASK64 = (1 << 64) - 1
SIGN64 = 1 << 63


class Result(ctypes.Structure):
    _fields_ = [
        ("quotient_low", ctypes.c_uint),
        ("quotient_high", ctypes.c_uint),
        ("remainder_low", ctypes.c_uint),
        ("remainder_high", ctypes.c_uint),
    ]


def words(value: int) -> tuple[int, int]:
    value &= MASK64
    return value & 0xFFFFFFFF, value >> 32


def joined(low: int, high: int) -> int:
    return low | (high << 32)


def signed(value: int) -> int:
    value &= MASK64
    return value - (1 << 64) if value & SIGN64 else value


def signed_divmod(dividend: int, divisor: int) -> tuple[int, int]:
    dividend = signed(dividend)
    divisor = signed(divisor)
    if divisor == 0:
        return dividend & MASK64, 0
    quotient = abs(dividend) // abs(divisor)
    if (dividend < 0) != (divisor < 0):
        quotient = -quotient
    remainder = dividend - quotient * divisor
    return quotient & MASK64, remainder & MASK64


class AeabiDivmodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "aeabi_divmod.dylib"
            if sys.platform == "darwin"
            else "aeabi_divmod.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.unsigned_core = cls.loaded.open_cfw_aeabi_uldivmod_core
        cls.signed_core = cls.loaded.open_cfw_aeabi_ldivmod_core
        for function in (cls.unsigned_core, cls.signed_core):
            function.argtypes = [
                ctypes.c_uint,
                ctypes.c_uint,
                ctypes.c_uint,
                ctypes.c_uint,
                ctypes.POINTER(Result),
            ]
            function.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def call(
        self,
        function: ctypes._CFuncPtr,
        dividend: int,
        divisor: int,
    ) -> tuple[int, int]:
        dividend_low, dividend_high = words(dividend)
        divisor_low, divisor_high = words(divisor)
        result = Result()
        function(
            dividend_low,
            dividend_high,
            divisor_low,
            divisor_high,
            ctypes.byref(result),
        )
        return (
            joined(result.quotient_low, result.quotient_high),
            joined(result.remainder_low, result.remainder_high),
        )

    def test_unsigned_edges_and_division_by_zero_match_stock_policy(
        self,
    ) -> None:
        values = [
            0,
            1,
            2,
            3,
            0xFFFFFFFF,
            0x100000000,
            0x7FFFFFFFFFFFFFFF,
            0x8000000000000000,
            0xFFFFFFFFFFFFFFFF,
        ]
        for dividend in values:
            for divisor in values:
                expected = (
                    (dividend, 0)
                    if divisor == 0
                    else (dividend // divisor, dividend % divisor)
                )
                self.assertEqual(
                    self.call(self.unsigned_core, dividend, divisor),
                    expected,
                )

    def test_signed_edges_include_overflow_and_division_by_zero(self) -> None:
        values = [
            0,
            1,
            2,
            -1,
            -2,
            0x7FFFFFFF,
            -0x80000000,
            0x7FFFFFFFFFFFFFFF,
            -0x8000000000000000,
        ]
        for dividend in values:
            for divisor in values:
                self.assertEqual(
                    self.call(self.signed_core, dividend, divisor),
                    signed_divmod(dividend, divisor),
                )

    def test_unsigned_randomized_model(self) -> None:
        generator = random.Random(0x0047CC60)
        for _ in range(4000):
            dividend = generator.getrandbits(64)
            divisor = generator.getrandbits(64)
            self.assertEqual(
                self.call(self.unsigned_core, dividend, divisor),
                (dividend // divisor, dividend % divisor),
            )

    def test_signed_randomized_model(self) -> None:
        generator = random.Random(0x0047CC1C)
        for _ in range(4000):
            dividend = generator.getrandbits(64)
            divisor = generator.getrandbits(64)
            self.assertEqual(
                self.call(self.signed_core, dividend, divisor),
                signed_divmod(dividend, divisor),
            )

    def test_sources_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "2222252bb0d1ffdab597d023a0737a77d044b4e1b6addb8fbb545d8386855f7e",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "9e9eec3da396f214345b3193cc55d6d92a2eb7d5de3c9695c74d11dfd8c5134b",
        )


if __name__ == "__main__":
    unittest.main()
