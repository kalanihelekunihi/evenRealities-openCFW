#!/usr/bin/env python3
"""Host semantics checks for the LC3-owned freestanding target runtime."""

from __future__ import annotations

import ctypes
import math
import random
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/liblc3/runtime_liblc3_target_runtime.c"
INCLUDE = SOURCE.parent
RENAMES = {
    "__aeabi_memclr": "open_cfw_test_aeabi_memclr",
    "__aeabi_memclr4": "open_cfw_test_aeabi_memclr4",
    "fabsf": "open_cfw_test_fabsf",
    "floorf": "open_cfw_test_floorf",
    "fmaxf": "open_cfw_test_fmaxf",
    "fminf": "open_cfw_test_fminf",
    "memcpy": "open_cfw_test_memcpy",
    "memmove": "open_cfw_test_memmove",
    "memset": "open_cfw_test_memset",
    "truncf": "open_cfw_test_truncf",
}


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def from_bits(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", value))[0]


class Lc3TargetRuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library_path = Path(cls.temporary.name) / "liblc3-runtime.dylib"
        command = [
            "/usr/bin/clang", "-shared", "-fPIC", "-std=c11", "-O2",
            "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
            "-I", str(INCLUDE),
            *(f"-D{name}={replacement}" for name, replacement in RENAMES.items()),
            str(SOURCE), "-o", str(cls.library_path),
        ]
        subprocess.run(command, check=True, cwd=ROOT, capture_output=True)
        cls.library = ctypes.CDLL(str(cls.library_path))
        cls.memcpy = cls.library.open_cfw_test_memcpy
        cls.memmove = cls.library.open_cfw_test_memmove
        cls.memset = cls.library.open_cfw_test_memset
        for function in (cls.memcpy, cls.memmove):
            function.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
            function.restype = ctypes.c_void_p
        cls.memset.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t]
        cls.memset.restype = ctypes.c_void_p
        cls.memclr = cls.library.open_cfw_test_aeabi_memclr
        cls.memclr4 = cls.library.open_cfw_test_aeabi_memclr4
        for function in (cls.memclr, cls.memclr4):
            function.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
            function.restype = None
        for name in ("fabsf", "floorf", "truncf"):
            function = getattr(cls.library, f"open_cfw_test_{name}")
            function.argtypes = [ctypes.c_float]
            function.restype = ctypes.c_float
            setattr(cls, name, function)
        for name in ("fmaxf", "fminf"):
            function = getattr(cls.library, f"open_cfw_test_{name}")
            function.argtypes = [ctypes.c_float, ctypes.c_float]
            function.restype = ctypes.c_float
            setattr(cls, name, function)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_copy_set_and_clear_preserve_guards_and_return_destination(self) -> None:
        source = (ctypes.c_ubyte * 40)(*range(40))
        destination = (ctypes.c_ubyte * 40)(*[0xA5] * 40)
        source_address = ctypes.addressof(source)
        destination_address = ctypes.addressof(destination)
        result = self.memcpy(destination_address + 7, source_address + 5, 23)
        self.assertEqual(result, destination_address + 7)
        self.assertEqual(bytes(destination[:7]), b"\xA5" * 7)
        self.assertEqual(bytes(destination[7:30]), bytes(source[5:28]))
        self.assertEqual(bytes(destination[30:]), b"\xA5" * 10)
        self.assertEqual(self.memcpy(destination_address + 3,
                                     source_address + 3, 0),
                         destination_address + 3)

        result = self.memset(destination_address + 9, 0x1234, 17)
        self.assertEqual(result, destination_address + 9)
        self.assertEqual(bytes(destination[9:26]), b"\x34" * 17)
        self.assertEqual(destination[8], source[6])
        self.assertEqual(destination[26], source[24])
        self.memclr(destination_address + 10, 5)
        self.memclr4(destination_address + 20, 4)
        self.assertEqual(bytes(destination[10:15]), b"\0" * 5)
        self.assertEqual(bytes(destination[20:24]), b"\0" * 4)
        self.assertEqual(destination[9], 0x34)
        self.assertEqual(destination[15], 0x34)

    def test_memmove_handles_both_overlap_directions_and_exact_alias(self) -> None:
        for destination, source, length in ((9, 3, 21), (3, 9, 21),
                                             (8, 8, 20), (2, 31, 0)):
            original = bytearray(range(48))
            expected = bytearray(original)
            expected[destination:destination + length] = \
                original[source:source + length]
            storage = (ctypes.c_ubyte * len(original))(*original)
            address = ctypes.addressof(storage)
            result = self.memmove(address + destination, address + source,
                                  length)
            self.assertEqual(result, address + destination)
            self.assertEqual(bytes(storage), bytes(expected))

    def test_fabs_and_trunc_preserve_float32_bit_contract(self) -> None:
        values = [
            0x00000000, 0x80000000, 0x00000001, 0x80000001,
            0x3F7FFFFF, 0xBF7FFFFF, 0x3FC00000, 0xBFC00000,
            0x4AFFFFFF, 0xCAFFFFFF, 0x7F800000, 0xFF800000,
            0x7FC12345, 0xFFC12345,
        ]
        random_values = random.Random(0x1C3).getrandbits
        values.extend(random_values(32) for _ in range(512))
        for encoded in values:
            value = from_bits(encoded)
            exponent = (encoded >> 23) & 0xFF
            if exponent == 0xFF and encoded & 0x7FFFFF:
                # The host ABI may quiet a signaling NaN before the call.
                self.assertTrue(math.isnan(self.fabsf(value)))
                self.assertEqual(bits(self.fabsf(value)) >> 31, 0)
            else:
                self.assertEqual(bits(self.fabsf(value)),
                                 encoded & 0x7FFFFFFF)
            expected = encoded
            if exponent < 127:
                expected &= 0x80000000
            elif exponent < 150:
                expected &= ~((1 << (150 - exponent)) - 1)
            result = bits(self.truncf(value))
            if exponent == 0xFF and encoded & 0x7FFFFF:
                self.assertTrue(math.isnan(from_bits(result)))
            else:
                self.assertEqual(result, expected & 0xFFFFFFFF)

    def test_floor_matches_float32_semantics_including_special_values(self) -> None:
        cases = [0.0, -0.0, 0.25, -0.25, 1.0, -1.0, 1.999,
                 -1.001, 8388607.5, -8388607.5, math.inf, -math.inf]
        generator = random.Random(0xF100)
        cases.extend(f32(generator.uniform(-1.0e6, 1.0e6))
                     for _ in range(512))
        for value in cases:
            result = self.floorf(value)
            if math.isinf(value):
                self.assertEqual(result, value)
            elif value == 0.0:
                self.assertEqual(bits(result), bits(f32(value)))
            else:
                self.assertEqual(result, f32(float(math.floor(value))))
        self.assertTrue(math.isnan(self.floorf(from_bits(0x7FC12345))))

    def test_minmax_nan_and_signed_zero_selection(self) -> None:
        nan = from_bits(0x7FC12345)
        self.assertEqual(self.fmaxf(nan, 3.0), 3.0)
        self.assertEqual(self.fmaxf(3.0, nan), 3.0)
        self.assertEqual(self.fminf(nan, -3.0), -3.0)
        self.assertEqual(self.fminf(-3.0, nan), -3.0)
        self.assertTrue(math.isnan(self.fmaxf(nan, nan)))
        self.assertTrue(math.isnan(self.fminf(nan, nan)))
        self.assertEqual(bits(self.fmaxf(-0.0, 0.0)), 0x00000000)
        self.assertEqual(bits(self.fmaxf(0.0, -0.0)), 0x00000000)
        self.assertEqual(bits(self.fminf(-0.0, 0.0)), 0x80000000)
        self.assertEqual(bits(self.fminf(0.0, -0.0)), 0x80000000)
        for first, second in ((-8.0, 5.0), (4.0, 9.0), (-2.0, -7.0)):
            self.assertEqual(self.fmaxf(first, second), max(first, second))
            self.assertEqual(self.fminf(first, second), min(first, second))


if __name__ == "__main__":
    unittest.main()
