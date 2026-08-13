from __future__ import annotations

import os

import ctypes
import hashlib
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_integer_format.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_integer_format_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482518
STOCK_END = 0x0048262C
SCRATCH_ADDRESS = 0x20000020


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class FormatContext(ctypes.Structure):
    _fields_ = [
        ("value", ctypes.c_uint64),
        ("reserved_08", ctypes.c_uint32),
        ("digits", ctypes.c_uint32),
        ("scratch", ctypes.c_uint32),
        ("prefix_length", ctypes.c_uint32),
        ("digit_length", ctypes.c_uint32),
        ("reserved_1c", ctypes.c_uint32),
        ("zero_padding", ctypes.c_uint32),
        ("reserved_24", ctypes.c_uint32),
        ("reserved_28", ctypes.c_uint32),
        ("reserved_2c", ctypes.c_uint32),
        ("precision", ctypes.c_int32),
        ("field_width", ctypes.c_int32),
        ("flags", ctypes.c_uint16),
    ]


def _oracle(
    *,
    value: int,
    specifier: int,
    digit_limit_offset: int = 0,
    prefix_length: int = 0,
    zero_padding: int = 0,
    precision: int = -1,
    field_width: int = 0,
    flags: int = 0,
) -> tuple[bytes, int, int, int, int, int, int]:
    mask64 = (1 << 64) - 1
    specifier &= 0xFFFFFFFF
    flags &= 0xFFFF
    if specifier == ord("o"):
        base = 8
    elif (specifier | 0x20) & 0xFFFFFFFF == ord("x"):
        base = 16
    else:
        base = 10

    value &= mask64
    if (
        specifier in (ord("d"), ord("i"))
        and value & (1 << 63)
    ):
        value = (-value) & mask64

    scratch = bytearray([0xA5] * 60)
    cursor = 60
    divmod_calls = 0
    if value == 0 and precision == 0:
        if base == 8 and flags & 0x08:
            cursor = 59
            scratch[cursor] = ord("0")
    else:
        while True:
            value, remainder = divmod(value, base)
            divmod_calls += 1
            character = remainder + ord("0")
            cursor -= 1
            if character & 0xFF >= ord(":"):
                character += (specifier & 0xFF) - 0x51
            scratch[cursor] = character & 0xFF
            if not (
                value != 0
                and SCRATCH_ADDRESS + digit_limit_offset
                < SCRATCH_ADDRESS + cursor
            ):
                break

        if base == 8 and flags & 0x08 and scratch[cursor] != ord("0"):
            cursor -= 1
            scratch[cursor] = ord("0")

    digit_length = 60 - cursor
    if precision > digit_length:
        zero_padding = precision - digit_length
        flags &= 0xFFEF
    elif precision < 0 and (flags & 0xFF) & 0x14 == 0x10:
        available = (
            field_width
            - prefix_length
            - zero_padding
            - digit_length
        ) & 0xFFFFFFFF
        if ctypes.c_int32(available).value > 0:
            zero_padding = available

    return (
        bytes(scratch),
        cursor,
        digit_length,
        zero_padding & 0xFFFFFFFF,
        flags,
        base,
        divmod_calls,
    )


class RuntimeIntegerFormatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_integer_format.dylib"
            if sys.platform == "darwin"
            else "runtime_integer_format.so"
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
        cls.reset = cls.loaded.open_cfw_test_integer_format_reset
        cls.reset.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_int32,
            ctypes.c_int32,
            ctypes.c_uint32,
        ]
        cls.reset.restype = None
        cls.execute = cls.loaded.open_cfw_test_integer_format_execute
        cls.execute.argtypes = [ctypes.c_uint32]
        cls.execute.restype = None
        context = cls.loaded.open_cfw_test_integer_format_context
        context.argtypes = []
        context.restype = ctypes.POINTER(FormatContext)
        cls.context = context
        scratch = cls.loaded.open_cfw_test_integer_format_scratch
        scratch.argtypes = []
        scratch.restype = ctypes.POINTER(ctypes.c_ubyte)
        cls.scratch = scratch

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def run_case(
        self,
        *,
        value: int,
        specifier: int,
        digit_limit_offset: int = 0,
        prefix_length: int = 0,
        zero_padding: int = 0,
        precision: int = -1,
        field_width: int = 0,
        flags: int = 0,
    ) -> tuple[FormatContext, bytes]:
        self.reset(
            value & 0xFFFFFFFF,
            value >> 32,
            digit_limit_offset,
            prefix_length,
            zero_padding,
            precision,
            field_width,
            flags,
        )
        self.execute(specifier)
        return self.context().contents, bytes(self.scratch()[:60])

    def assert_case(self, **case: int) -> None:
        expected = _oracle(**case)
        context, scratch = self.run_case(**case)
        (
            expected_scratch,
            cursor,
            length,
            zero_padding,
            flags,
            base,
            divmod_calls,
        ) = expected

        self.assertEqual(scratch, expected_scratch)
        self.assertEqual(context.digits, SCRATCH_ADDRESS + cursor)
        self.assertEqual(context.scratch, SCRATCH_ADDRESS)
        self.assertEqual(context.digit_length, length)
        self.assertEqual(context.zero_padding, zero_padding)
        self.assertEqual(context.flags, flags)
        self.assertEqual(context.reserved_08, 0x08080808)
        self.assertEqual(context.reserved_1c, 0x1C1C1C1C)
        self.assertEqual(context.reserved_24, 0x24242424)
        self.assertEqual(context.reserved_28, 0x28282828)
        self.assertEqual(context.reserved_2c, 0x2C2C2C2C)
        self.assertEqual(
            self.uint("open_cfw_test_integer_format_divmod_calls").value,
            divmod_calls,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_integer_format_last_divisor_low"
            ).value,
            base if divmod_calls != 0 else 0,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_integer_format_last_divisor_high"
            ).value,
            0,
        )
        expected_ascii_calls = 0 if case["specifier"] == ord("o") else 1
        self.assertEqual(
            self.uint("open_cfw_test_integer_format_ascii_calls").value,
            expected_ascii_calls,
        )
        if expected_ascii_calls:
            self.assertEqual(
                self.uint("open_cfw_test_integer_format_ascii_input").value,
                case["specifier"] & 0xFFFFFFFF,
            )

    def test_decimal_signed_and_unsigned_extremes(self) -> None:
        for specifier, value in (
            (ord("d"), 0),
            (ord("d"), 1),
            (ord("i"), 0xFFFFFFFFFFFFFFFF),
            (ord("d"), 0x8000000000000000),
            (ord("u"), 0x8000000000000000),
            (ord("u"), 0xFFFFFFFFFFFFFFFF),
        ):
            with self.subTest(specifier=specifier, value=value):
                self.assert_case(value=value, specifier=specifier)

    def test_octal_hex_case_and_full_width_specifier_semantics(self) -> None:
        for specifier, value, flags in (
            (ord("o"), 0o1234567012345670, 0),
            (ord("o"), 0o123, 0x08),
            (ord("x"), 0x1234ABCDEF, 0),
            (ord("X"), 0x1234ABCDEF, 0),
            (0x100006F, 15, 0),
            (0x1000058, 15, 0),
        ):
            with self.subTest(
                specifier=f"0x{specifier:08X}",
                value=value,
                flags=flags,
            ):
                self.assert_case(
                    value=value,
                    specifier=specifier,
                    flags=flags,
                )

    def test_zero_precision_and_alternate_octal_exception(self) -> None:
        for specifier, flags in (
            (ord("d"), 0),
            (ord("x"), 0x08),
            (ord("o"), 0),
            (ord("o"), 0x08),
        ):
            with self.subTest(specifier=specifier, flags=flags):
                self.assert_case(
                    value=0,
                    specifier=specifier,
                    precision=0,
                    flags=flags,
                )

    def test_precision_and_width_zero_padding_policy(self) -> None:
        cases = (
            {
                "value": 123,
                "specifier": ord("d"),
                "precision": 7,
                "zero_padding": 2,
                "flags": 0xAB10,
            },
            {
                "value": 123,
                "specifier": ord("d"),
                "precision": 3,
                "zero_padding": 2,
                "flags": 0xAB10,
            },
            {
                "value": 123,
                "specifier": ord("d"),
                "precision": -1,
                "prefix_length": 1,
                "zero_padding": 2,
                "field_width": 12,
                "flags": 0xAB10,
            },
            {
                "value": 123,
                "specifier": ord("d"),
                "precision": -1,
                "prefix_length": 1,
                "zero_padding": 2,
                "field_width": 12,
                "flags": 0xAB14,
            },
        )
        for case in cases:
            with self.subTest(case=case):
                self.assert_case(**case)

    def test_digit_pointer_bound_stops_after_current_digit(self) -> None:
        for digit_limit_offset in (0, 58, 59, 60):
            with self.subTest(digit_limit_offset=digit_limit_offset):
                self.assert_case(
                    value=0xFFFFFFFFFFFFFFFF,
                    specifier=ord("X"),
                    digit_limit_offset=digit_limit_offset,
                )

    def test_deterministic_cross_product_matches_independent_oracle(
        self,
    ) -> None:
        generator = random.Random(STOCK_START)
        specifiers = (
            ord("d"),
            ord("i"),
            ord("u"),
            ord("o"),
            ord("x"),
            ord("X"),
            ord("q"),
            0x100006F,
            0x1000058,
        )
        flag_values = (0, 0x08, 0x10, 0x14, 0x18, 0xAB10, 0xAB18)
        precisions = (-1, 0, 1, 2, 7, 20, 60)

        for index in range(256):
            case = {
                "value": generator.getrandbits(64),
                "specifier": generator.choice(specifiers),
                "digit_limit_offset": generator.choice((0, 1, 32, 58, 59, 60)),
                "prefix_length": generator.randrange(0, 4),
                "zero_padding": generator.randrange(0, 8),
                "precision": generator.choice(precisions),
                "field_width": generator.randrange(-4, 80),
                "flags": generator.choice(flag_values),
            }
            with self.subTest(index=index, case=case):
                self.assert_case(**case)

    def test_stock_span_callsite_dependencies_and_adjacent_bytes(self) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 276)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "be063cc5e8c7478419a02b8f09e24e93"
            "209ee2ec042cdcf325729564f91d4897",
        )
        self.assertEqual(
            span(0x004824EE, STOCK_START).hex(),
            "0000cbcccc0c686a6c747a4c00007072696e74665f733a20"
            "62616420257320617267756d656e74000000",
        )
        self.assertEqual(
            hashlib.sha256(span(0x004824EE, STOCK_START)).hexdigest(),
            "adc812e90c0f52b8d206815c60e08db9"
            "eaeae99c4c0357c3e5a06078be03415d",
        )
        self.assertEqual(span(0x0048246C, 0x0048247E).hex(),
                         "12a8079901440591594602a800f04ef816e0")
        self.assertEqual(
            hashlib.sha256(span(STOCK_END, 0x00482672)).hexdigest(),
            "779f44305918c180ef963bd1c49064f2"
            "b2b00b9e1decda3934f8ab0b46c25278",
        )
        self.assertEqual(
            hashlib.sha256(span(0x00482672, 0x00482684)).hexdigest(),
            "193dc16eaca2246df95bb7dd28baae42"
            "55adaac92a75550c82d285373443fe7a",
        )

        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
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

        self.assertEqual(callers, [(0x00482478, "00f04ef8")])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x0048252C, 0x00481830, "fff780f9"),
                (0x0048258C, 0x0047CC60, "faf768fb"),
                (0x004825A6, 0x0047CC60, "faf75bfb"),
            ],
        )

    def test_false_positive_branch_and_stored_pointer_topology_is_pinned(
        self,
    ) -> None:
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
        self.assertEqual(
            narrow_interior,
            [(0x0048267C, 0x00482588, 0xD784)],
        )

        stored = []
        for offset in range(0, len(application) - 3):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(
            stored,
            [
                (0x00448F6D, 0x00482620),
                (0x0046F32D, 0x004825B4),
                (0x004AAADB, 0x00482620),
            ],
        )

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "struct open_cfw_integer_format_context",
            "void open_cfw_integer_format(",
            "cursor = 60U;",
            "context->flags &= (unsigned short)0xffefU;",
            "OPEN_CFW_INTEGER_FORMAT_DIVMOD(",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_integer_format.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
