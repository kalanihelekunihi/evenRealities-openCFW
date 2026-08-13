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
SOURCE = COMPONENT_ROOT / "runtime_ntoa_integer.c"
DIVISION_SOURCE = COMPONENT_ROOT / "aeabi_divmod.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_ntoa_integer_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
LONG_START = 0x0048320A
LONG_END = 0x0048329C
LONG_LONG_START = LONG_END
LONG_LONG_END = 0x0048334E
BUFFER_SIZE = 32
FLAG_HASH = 1 << 4
FLAG_UPPER = 1 << 5
FLAG_PRECISION = 1 << 10

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-Wall",
    "-Wextra",
    "-Werror",
]


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


def _oracle(
    value: int,
    base: int,
    flags: int,
) -> tuple[bytes, int, list[tuple[int, int, int, int]]]:
    if value == 0:
        flags &= ~FLAG_HASH

    digits = bytearray()
    divisions = []
    if not flags & FLAG_PRECISION or value:
        while True:
            quotient, remainder = divmod(value, base)
            divisions.append((value, base, quotient, remainder))
            if remainder < 10:
                character = ord("0") + remainder
            else:
                character = (
                    ord("A") if flags & FLAG_UPPER else ord("a")
                ) + remainder - 10
            digits.append(character)
            value = quotient
            if not value or len(digits) >= BUFFER_SIZE:
                break
    return bytes(digits), flags, divisions


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeNtoaIntegerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_ntoa_integer.dylib"
            if sys.platform == "darwin"
            else "runtime_ntoa_integer.so"
        )
        native_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            native_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            native_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            native_command,
            check=True,
            capture_output=True,
            text=True,
        )

        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_runtime_ntoa_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.reset.restype = None
        cls.execute_long = (
            cls.loaded.open_cfw_test_runtime_ntoa_execute_long
        )
        cls.execute_long.argtypes = [ctypes.c_uint32] * 8
        cls.execute_long.restype = ctypes.c_uint32
        cls.execute_long_long = (
            cls.loaded.open_cfw_test_runtime_ntoa_execute_long_long
        )
        cls.execute_long_long.argtypes = [ctypes.c_uint32] * 10
        cls.execute_long_long.restype = ctypes.c_uint32
        cls.observed_digits = (ctypes.c_ubyte * BUFFER_SIZE).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_ntoa_observed_digits",
        )
        cls.output_buffer = (ctypes.c_ubyte * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_ntoa_output_buffer",
        )
        cls.division_value = (ctypes.c_uint64 * BUFFER_SIZE).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_ntoa_division_value",
        )
        cls.division_base = (ctypes.c_uint64 * BUFFER_SIZE).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_ntoa_division_base",
        )
        cls.division_quotient = (
            ctypes.c_uint64 * BUFFER_SIZE
        ).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_ntoa_division_quotient",
        )
        cls.division_remainder = (
            ctypes.c_uint64 * BUFFER_SIZE
        ).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_ntoa_division_remainder",
        )

        target_object = temporary / "runtime_ntoa_integer.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(target_object)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target_text = data[
            int(text["offset"]):
            int(text["offset"]) + int(text["size"])
        ]
        cls.target_functions, symbols = cls._read_symbols(
            data,
            sections,
            int(text["index"]),
        )
        cls.target_relocations = cls._read_relocations(
            data,
            sections,
            symbols,
            int(text["index"]),
        )

        combined = temporary / "runtime_ntoa_with_division.c"
        combined.write_text(
            f'#include "{DIVISION_SOURCE.as_posix()}"\n'
            f'#include "{SOURCE.as_posix()}"\n'
        )
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(combined),
                "-o",
                str(temporary / "runtime_ntoa_with_division.o"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    @staticmethod
    def _read_symbols(
        data: bytes,
        sections: list[dict[str, int | str]],
        text_index: int,
    ) -> tuple[
        dict[str, dict[str, int]],
        list[dict[str, int | str]],
    ]:
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        symbols_section = apollo_overlay.section_named(
            sections,
            ".symtab",
        )
        strings = sections[int(symbols_section["link"])]
        string_data = data[
            int(strings["offset"]):
            int(strings["offset"]) + int(strings["size"])
        ]
        symbols = []
        functions = {}
        for index in range(int(symbols_section["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbols_section["offset"]) + index * 16,
            )
            symbol = {
                "name": apollo_overlay.elf_string(
                    string_data,
                    fields[0],
                    "symbol",
                ),
                "value": fields[1],
                "size": fields[2],
                "type": fields[3] & 0x0F,
                "section": fields[5],
            }
            symbols.append(symbol)
            if symbol["type"] == 2 and symbol["section"] == text_index:
                functions[str(symbol["name"])] = {
                    "offset": int(symbol["value"]) & ~1,
                    "size": int(symbol["size"]),
                }
        return functions, symbols

    @staticmethod
    def _read_relocations(
        data: bytes,
        sections: list[dict[str, int | str]],
        symbols: list[dict[str, int | str]],
        text_index: int,
    ) -> list[dict[str, int | str]]:
        relocations = []
        for section in sections:
            if int(section["type"]) != 9:
                continue
            if int(section["info"]) != text_index:
                continue
            for index in range(int(section["size"]) // 8):
                offset, info = struct.unpack_from(
                    "<II",
                    data,
                    int(section["offset"]) + index * 8,
                )
                relocations.append(
                    {
                        "section": str(section["name"]),
                        "site": offset,
                        "type": info & 0xFF,
                        "symbol": str(symbols[info >> 8]["name"]),
                    }
                )
        return relocations

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def uintptr(self, name: str) -> int:
        return ctypes.c_size_t.in_dll(self.loaded, name).value

    def assert_format_call(
        self,
        *,
        digits: bytes,
        negative: int,
        base: int,
        precision: int,
        width: int,
        flags: int,
        index: int,
        maximum_length: int,
    ) -> None:
        self.assertEqual(
            self.uint("open_cfw_test_runtime_ntoa_format_calls").value,
            1,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_ntoa_observed_digit_count"
            ).value,
            len(digits),
        )
        self.assertEqual(bytes(self.observed_digits[:len(digits)]), digits)
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_ntoa_observed_negative"
            ).value,
            bool(negative),
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_ntoa_observed_base").value,
            base & 0xFFFFFFFF,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_ntoa_observed_precision"
            ).value,
            precision,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_ntoa_observed_width").value,
            width,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_ntoa_observed_flags").value,
            flags,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_ntoa_observed_index").value,
            index,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_ntoa_observed_maximum_length"
            ).value,
            maximum_length,
        )
        self.assertEqual(
            self.uintptr(
                "open_cfw_test_runtime_ntoa_observed_buffer"
            ),
            ctypes.addressof(self.output_buffer),
        )
        self.assertNotEqual(
            self.uintptr(
                "open_cfw_test_runtime_ntoa_observed_output"
            ),
            0,
        )

    def test_long_exhausts_bases_values_case_and_forwarded_arguments(
        self,
    ) -> None:
        values = (
            0,
            1,
            9,
            10,
            31,
            0xFFFF,
            0x80000000,
            0xFFFFFFFF,
        )
        for base in range(2, 37):
            for value in values:
                for upper in (0, FLAG_UPPER):
                    flags = upper | FLAG_HASH | 0x80000000
                    digits, expected_flags, _divisions = _oracle(
                        value,
                        base,
                        flags,
                    )
                    return_value = value ^ (base << 24) ^ 0xA5A55A5A
                    self.reset(return_value)
                    observed = self.execute_long(
                        value,
                        value & 1,
                        base,
                        7,
                        41,
                        flags,
                        0x10203040,
                        0x50607080,
                    )
                    with self.subTest(
                        base=base,
                        value=value,
                        upper=bool(upper),
                    ):
                        self.assertEqual(observed, return_value & 0xFFFFFFFF)
                        self.assert_format_call(
                            digits=digits,
                            negative=value & 1,
                            base=base,
                            precision=7,
                            width=41,
                            flags=expected_flags,
                            index=0x10203040,
                            maximum_length=0x50607080,
                        )
                        self.assertEqual(
                            self.uint(
                                "open_cfw_test_runtime_ntoa_division_calls"
                            ).value,
                            0,
                        )

    def test_zero_precision_suppresses_the_only_zero_digit(self) -> None:
        for flags, expected in (
            (0, b"0"),
            (FLAG_HASH, b"0"),
            (FLAG_PRECISION, b""),
            (FLAG_PRECISION | FLAG_HASH | FLAG_UPPER, b""),
        ):
            self.reset(0xC001D00D)
            self.assertEqual(
                self.execute_long(0, 0, 16, 0, 0, flags, 0, 0),
                0xC001D00D,
            )
            self.assert_format_call(
                digits=expected,
                negative=0,
                base=16,
                precision=0,
                width=0,
                flags=flags & ~FLAG_HASH,
                index=0,
                maximum_length=0,
            )

    def test_long_long_randomized_digits_and_divmod_trace_are_exact(
        self,
    ) -> None:
        generator = random.Random(LONG_LONG_START)
        cases = [
            (0, 2),
            (1, 10),
            ((1 << 64) - 1, 2),
            ((1 << 64) - 1, 10),
            ((1 << 64) - 1, 36),
            (0x8000000000000000, 16),
        ]
        cases.extend(
            (generator.getrandbits(64), generator.randrange(2, 37))
            for _ in range(512)
        )
        for case_index, (value, base) in enumerate(cases):
            flags = (
                (FLAG_UPPER if case_index & 1 else 0)
                | (FLAG_HASH if case_index % 3 else 0)
                | (FLAG_PRECISION if case_index % 5 == 0 else 0)
                | 0x40000000
            )
            digits, expected_flags, divisions = _oracle(
                value,
                base,
                flags,
            )
            self.reset(case_index ^ 0xDEADBEEF)
            observed = self.execute_long_long(
                value & 0xFFFFFFFF,
                value >> 32,
                case_index & 1,
                base,
                0,
                case_index,
                case_index * 3,
                flags,
                0x01020304,
                0xF0E0D0C0,
            )
            with self.subTest(case_index=case_index):
                self.assertEqual(
                    observed,
                    (case_index ^ 0xDEADBEEF) & 0xFFFFFFFF,
                )
                self.assert_format_call(
                    digits=digits,
                    negative=case_index & 1,
                    base=base,
                    precision=case_index,
                    width=case_index * 3,
                    flags=expected_flags,
                    index=0x01020304,
                    maximum_length=0xF0E0D0C0,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_ntoa_division_calls"
                    ).value,
                    len(divisions),
                )
                self.assertEqual(
                    [
                        (
                            self.division_value[index],
                            self.division_base[index],
                            self.division_quotient[index],
                            self.division_remainder[index],
                        )
                        for index in range(len(divisions))
                    ],
                    divisions,
                )

    def test_both_converters_stop_at_the_32_byte_digit_boundary(
        self,
    ) -> None:
        self.reset(1)
        self.execute_long(0xFFFFFFFF, 0, 2, 0, 0, 0, 0, 0)
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_ntoa_observed_digit_count"
            ).value,
            32,
        )
        self.assertEqual(bytes(self.observed_digits), b"1" * 32)

        self.reset(2)
        self.execute_long_long(
            0xFFFFFFFF,
            0xFFFFFFFF,
            0,
            2,
            0,
            0,
            0,
            0,
            0,
            0,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_ntoa_observed_digit_count"
            ).value,
            32,
        )
        self.assertEqual(bytes(self.observed_digits), b"1" * 32)
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_ntoa_division_calls"
            ).value,
            32,
        )

    def test_stock_spans_combined_context_and_alignment_are_pinned(
        self,
    ) -> None:
        long_body = self.span(LONG_START, LONG_END)
        self.assertEqual(len(long_body), 146)
        self.assertEqual(
            hashlib.sha256(long_body).hexdigest(),
            "ff618cbd02cd895efb5160e764d501fd"
            "6f18994b42cff1fe7db7d288b3eccf15",
        )

        long_long_body = self.span(LONG_LONG_START, LONG_LONG_END)
        self.assertEqual(len(long_long_body), 178)
        self.assertEqual(
            hashlib.sha256(long_long_body).hexdigest(),
            "51b5a24f5952ae265e5677f4e754dd7"
            "76571836b367943ef28f8b941adeeda8f",
        )

        combined = self.span(0x0048306C, LONG_LONG_END)
        self.assertEqual(len(combined), 738)
        self.assertEqual(
            hashlib.sha256(combined).hexdigest(),
            "2a8c547155464ac3a3b9f668af76ac84"
            "c10c89d755ae500467beb8d337d07ca9",
        )
        alignment = self.span(LONG_LONG_END, 0x00483350)
        self.assertEqual(alignment, b"\0\0")
        self.assertEqual(
            hashlib.sha256(alignment).hexdigest(),
            "96a296d224f285c67bee93c30f8a3091"
            "57f0daa35dc5b87e410b78630a09cfc7",
        )

    def test_wide_callers_dependencies_and_interior_topology_are_exact(
        self,
    ) -> None:
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        functions = {
            "long": (LONG_START, LONG_END),
            "long_long": (LONG_LONG_START, LONG_LONG_END),
        }
        callers = {name: [] for name in functions}
        jumps = {name: [] for name in functions}
        interior = {name: [] for name in functions}
        dependencies = {name: [] for name in functions}
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, destination in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                for name, (start, end) in functions.items():
                    if target == start:
                        destination[name].append(
                            (address, encoded.hex())
                        )
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interior[name].append(
                            (address, target, link)
                        )
                    if link and start <= address < end:
                        dependencies[name].append(
                            (address, target, encoded.hex())
                        )

        self.assertEqual(
            callers,
            {
                "long": [
                    (0x004838DC, "fff795fc"),
                    (0x00483CB4, "fff7a9fa"),
                    (0x00483D12, "fff77afa"),
                    (0x00483DAC, "fff72dfa"),
                    (0x00483DFA, "fff706fa"),
                ],
                "long_long": [
                    (0x00483C74, "fff712fb"),
                    (0x00483D7C, "fff78efa"),
                ],
            },
        )
        self.assertEqual(
            {
                name: hashlib.sha256(
                    b"".join(
                        struct.pack("<I", address)
                        for address, _encoded in entries
                    )
                ).hexdigest()
                for name, entries in callers.items()
            },
            {
                "long":
                    "aef5f99dc66357962d2f71ed6cd7e1f3"
                    "b35749e56614274904ded710a65af996",
                "long_long":
                    "481a76f759fa5c4d077a5c17b0ec730a"
                    "545bd05b1939624eae0b722a995533a0",
            },
        )
        self.assertEqual(jumps, {"long": [], "long_long": []})
        self.assertEqual(interior, {"long": [], "long_long": []})
        self.assertEqual(
            dependencies,
            {
                "long": [
                    (0x00483292, 0x004830DA, "fff722ff"),
                ],
                "long_long": [
                    (0x004832D8, 0x0047CC60, "f9f7c2fc"),
                    (0x0048330A, 0x0047CC60, "f9f7a9fc"),
                    (0x00483344, 0x004830DA, "fff7c9fe"),
                ],
            },
        )

    def test_narrow_and_stored_pointer_topology_is_reviewed(self) -> None:
        functions = {
            "long": (LONG_START, LONG_END),
            "long_long": (LONG_LONG_START, LONG_LONG_END),
        }
        narrow_entry = {name: [] for name in functions}
        narrow_interior = {name: [] for name in functions}
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
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
            for name, (start, end) in functions.items():
                if start in candidates:
                    narrow_entry[name].append((address, halfword))
                for target in candidates:
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        narrow_interior[name].append(
                            (address, target, halfword)
                        )

        stored = {name: [] for name in functions}
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if not value & 1:
                continue
            target = value & ~1
            for name, (start, end) in functions.items():
                if start <= target < end:
                    stored[name].append(
                        (APPLICATION_BASE + offset, target, value)
                    )

        self.assertEqual(narrow_entry, {"long": [], "long_long": []})
        self.assertEqual(
            narrow_interior,
            {
                "long": [
                    (0x004831F6, 0x00483212, 0xE00C),
                ],
                "long_long": [],
            },
        )
        self.assertEqual(
            stored,
            {
                "long": [
                    (0x00484929, 0x00483210, 0x00483211),
                    (0x0048830F, 0x00483290, 0x00483291),
                    (0x004AA085, 0x00483220, 0x00483221),
                    (0x004AA099, 0x00483220, 0x00483221),
                    (0x004B5A09, 0x00483294, 0x00483295),
                ],
                "long_long": [],
            },
        )

    @_APPLE_ONLY
    def test_raw_target_clang_artifact_and_external_relocations_are_exact(
        self,
    ) -> None:
        self.assertEqual(
            self.target_functions,
            {
                "open_cfw_runtime_ntoa_long": {
                    "offset": 0,
                    "size": 132,
                },
                "open_cfw_runtime_ntoa_long_long": {
                    "offset": 132,
                    "size": 154,
                },
            },
        )
        self.assertEqual(len(self.target_text), 286)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "7ad979d28bda2347c5385490bcab9797"
            "fabad0907e00731d0c571f8a41d5bf03",
        )
        self.assertEqual(
            self.target_relocations,
            [
                {
                    "section": ".rel.text",
                    "site": 122,
                    "type": 10,
                    "symbol": "open_cfw_runtime_ntoa_format",
                },
                {
                    "section": ".rel.text",
                    "site": 208,
                    "type": 10,
                    "symbol": "open_cfw_aeabi_uldivmod_core",
                },
                {
                    "section": ".rel.text",
                    "site": 276,
                    "type": 10,
                    "symbol": "open_cfw_runtime_ntoa_format",
                },
            ],
        )
        expected_bodies = {
            "open_cfw_runtime_ntoa_long":
                "eb905d87c072e3ee024cbd6ea0ab81e7"
                "0f995ecff1f528cb0b9ac4f3703992f5",
            "open_cfw_runtime_ntoa_long_long":
                "c3a833489789c88b321b6291f8ac32f2"
                "8b2c73c71b1b4a35126f33ef384c7a6f",
        }
        for name, expected in expected_bodies.items():
            info = self.target_functions[name]
            body = self.target_text[
                info["offset"]:info["offset"] + info["size"]
            ]
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected)

    def test_source_fixture_and_upstream_provenance_are_bounded(
        self,
    ) -> None:
        source = SOURCE.read_text()
        for token in (
            "d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e",
            "OPEN_CFW_RUNTIME_NTOA_BUFFER_SIZE = 32U",
            "OPEN_CFW_RUNTIME_NTOA_FLAG_HASH = 1U << 4U",
            "OPEN_CFW_RUNTIME_NTOA_FLAG_UPPER = 1U << 5U",
            "OPEN_CFW_RUNTIME_NTOA_FLAG_PRECISION = 1U << 10U",
            "open_cfw_runtime_ntoa_long(",
            "open_cfw_runtime_ntoa_long_long(",
            "OPEN_CFW_RUNTIME_NTOA_DIVMOD_U64(",
            "OPEN_CFW_RUNTIME_NTOA_FORMAT(",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_ntoa_integer.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
