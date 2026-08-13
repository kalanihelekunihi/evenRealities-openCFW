from __future__ import annotations

import os

import ctypes
import hashlib
import math
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_decimal_scale.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_decimal_scale_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x0048262C
STOCK_END = 0x00482672


def _bits(value: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", value))[0]


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


def _oracle(
    value: float,
    exponent: int,
) -> tuple[float, list[tuple[int, int, int]]]:
    factor = 10.0
    calls: list[tuple[int, int, int]] = []
    while exponent != 0:
        if exponent & 1:
            result = value * factor
            calls.append((_bits(value), _bits(factor), _bits(result)))
            value = result
        result = factor * factor
        calls.append((_bits(factor), _bits(factor), _bits(result)))
        factor = result
        exponent >>= 1
    return value, calls


class RuntimeDecimalScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_decimal_scale.dylib"
            if sys.platform == "darwin"
            else "runtime_decimal_scale.so"
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
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.scale = cls.loaded.open_cfw_decimal_scale
        cls.scale.argtypes = [ctypes.c_double, ctypes.c_int]
        cls.scale.restype = ctypes.c_double
        cls.reset = cls.loaded.open_cfw_test_decimal_scale_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.call_count = ctypes.c_uint.in_dll(
            cls.loaded,
            "open_cfw_test_decimal_scale_multiply_calls",
        )
        cls.left_bits = (ctypes.c_uint64 * 128).in_dll(
            cls.loaded,
            "open_cfw_test_decimal_scale_left_bits",
        )
        cls.right_bits = (ctypes.c_uint64 * 128).in_dll(
            cls.loaded,
            "open_cfw_test_decimal_scale_right_bits",
        )
        cls.result_bits = (ctypes.c_uint64 * 128).in_dll(
            cls.loaded,
            "open_cfw_test_decimal_scale_result_bits",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def assert_case(self, value: float, exponent: int) -> None:
        expected, calls = _oracle(value, exponent)
        self.reset()
        actual = self.scale(value, exponent)
        self.assertEqual(_bits(actual), _bits(expected))
        self.assertEqual(self.call_count.value, len(calls))
        observed = [
            (
                self.left_bits[index],
                self.right_bits[index],
                self.result_bits[index],
            )
            for index in range(self.call_count.value)
        ]
        self.assertEqual(observed, calls)

    def test_zero_exponent_is_an_exact_no_call_identity(self) -> None:
        for bits in (
            0x0000000000000000,
            0x8000000000000000,
            0x3FF0000000000000,
            0xBFF4000000000000,
            0x0000000000000001,
            0x7FF0000000000000,
            0x7FF8123456789ABC,
        ):
            value = struct.unpack("<d", struct.pack("<Q", bits))[0]
            with self.subTest(bits=f"{bits:016x}"):
                self.assert_case(value, 0)

    def test_reviewed_decimal_adjustment_range_is_bit_exact(self) -> None:
        for value in (
            0.0,
            -0.0,
            1.0,
            -1.0,
            1.25,
            -123.5,
            1.0e-200,
            1.0e200,
        ):
            for exponent in range(1, 9):
                with self.subTest(value=value, exponent=exponent):
                    self.assert_case(value, exponent)

    def test_square_and_multiply_order_and_count_are_exact(self) -> None:
        for exponent in (1, 2, 3, 4, 5, 7, 8, 15, 16, 31):
            with self.subTest(exponent=exponent):
                self.assert_case(1.5, exponent)
                self.assertEqual(
                    self.call_count.value,
                    bin(exponent).count("1") + exponent.bit_length(),
                )

    def test_deterministic_finite_cross_product_matches_oracle(self) -> None:
        generator = random.Random(STOCK_START)
        for index in range(256):
            mantissa = generator.randrange(-(1 << 30), 1 << 30)
            binary_exponent = generator.randrange(-400, 400)
            value = math.ldexp(float(mantissa), binary_exponent - 30)
            exponent = generator.randrange(0, 32)
            with self.subTest(
                index=index,
                value=value,
                exponent=exponent,
            ):
                self.assert_case(value, exponent)

    def test_stock_span_callers_dependency_and_literal_pool_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 70)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "779f44305918c180ef963bd1c49064f2"
            "b2b00b9e1decda3934f8ab0b46c25278",
        )
        caller_context = span(0x00481F7C, 0x00481FAE)
        self.assertEqual(
            hashlib.sha256(caller_context).hexdigest(),
            "437c36dec2c618ea517ea095e33967df"
            "b162960b96e98b4d06ad809fbfea9197",
        )
        self.assertEqual(
            span(0x00481F8C, 0x00481FA2).hex(),
            "2046294600f04cfb0be052420020dff8dc1600f045fb",
        )
        literal_pool = span(STOCK_END, 0x00482684)
        self.assertEqual(
            literal_pool.hex(),
            "0000a08601000000f03f84d7974100002440",
        )
        self.assertEqual(
            hashlib.sha256(literal_pool).hexdigest(),
            "193dc16eaca2246df95bb7dd28baae42"
            "55adaac92a75550c82d285373443fe7a",
        )
        self.assertEqual(
            hashlib.sha256(span(0x00482684, 0x004826B2)).hexdigest(),
            "584f21e8f8b4cc13f7994f623e309f95"
            "22edb33e3b5d9fa5036650fb429532dc",
        )

        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == STOCK_START:
                    observed.append((address, encoded.hex()))
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append((address, target, encoded.hex()))

        self.assertEqual(
            callers,
            [
                (0x00481F90, "00f04cfb"),
                (0x00481F9E, "00f045fb"),
            ],
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x0048264C, 0x004D4354, "51f082fe"),
                (0x0048265C, 0x004D4354, "51f07afe"),
            ],
        )

    def test_no_narrow_entry_interior_or_stored_pointer_exists(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        narrow_entry = []
        narrow_interior = []
        for offset in range(0, len(application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", application, offset)[0]
            candidates = []
            if halfword & 0xF800 == 0xE000:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0x7FF) << 1, 12)
                )
            condition = (halfword >> 8) & 0xF
            if halfword & 0xF000 == 0xD000 and condition < 0xE:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0xFF) << 1, 9)
                )
            if halfword & 0xF500 == 0xB100:
                immediate = (
                    ((halfword >> 9) & 1) << 6
                    | ((halfword >> 3) & 0x1F) << 1
                )
                candidates.append(address + 4 + immediate)
            if STOCK_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    narrow_interior.append((address, target, halfword))
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])

        stored = []
        for offset in range(0, len(application) - 3):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "double open_cfw_decimal_scale(double value, int exponent)",
            "double factor = 10.0;",
            "if ((exponent & 1) != 0)",
            "exponent >>= 1;",
            "0x004D4355U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_decimal_scale.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
