from __future__ import annotations

import os

import ctypes
import hashlib
import itertools
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT / "runtime_vsnprintf.c"
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_vsnprintf_host.c"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BASE = 0x00438000
START, END = 0x00483960, 0x00483FCC
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


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeVsnprintfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_vsnprintf.dylib"
            if sys.platform == "darwin"
            else "runtime_vsnprintf.so"
        )
        host_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            host_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))

        cls.buffer_call = (
            cls.loaded.open_cfw_test_runtime_vsnprintf_buffer
        )
        cls.buffer_call.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint32,
            ctypes.c_char_p,
        ]
        cls.buffer_call.restype = ctypes.c_int32
        cls.observer_call = (
            cls.loaded.open_cfw_test_runtime_vsnprintf_observer
        )
        cls.observer_call.argtypes = [
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.c_char_p,
        ]
        cls.observer_call.restype = ctypes.c_int32
        cls.nested_call = (
            cls.loaded.open_cfw_test_runtime_vsnprintf_nested_buffer
        )
        cls.nested_call.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_int32,
        ]
        cls.nested_call.restype = ctypes.c_int32
        cls.nested_observer = (
            cls.loaded.open_cfw_test_runtime_vsnprintf_nested_observer
        )
        cls.nested_observer.argtypes = [
            ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_int32,
        ]
        cls.nested_observer.restype = ctypes.c_int32
        cls.nested_lowercase = (
            cls.loaded.open_cfw_test_runtime_vsnprintf_nested_lowercase
        )
        cls.nested_lowercase.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_int32,
        ]
        cls.nested_lowercase.restype = ctypes.c_int32
        cls.reset_observer = (
            cls.loaded.open_cfw_test_runtime_vsnprintf_reset
        )
        cls.reset_observer.argtypes = []
        cls.reset_observer.restype = None
        cls.magnitude_s32 = (
            cls.loaded.open_cfw_test_runtime_vsnprintf_magnitude_s32
        )
        cls.magnitude_s32.argtypes = [ctypes.c_int32]
        cls.magnitude_s32.restype = ctypes.c_uint32
        cls.magnitude_s64 = (
            cls.loaded.open_cfw_test_runtime_vsnprintf_magnitude_s64
        )
        cls.magnitude_s64.argtypes = [ctypes.c_int64]
        cls.magnitude_s64.restype = ctypes.c_uint64

        cls.target_object = temporary / "runtime_vsnprintf.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(cls.target_object)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target_text = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields for name, fields in parsed_symbols if name
        }
        cls.relocations = []
        for section in sections:
            if (
                int(section["type"]) == 9
                and int(section["info"]) == int(text["index"])
            ):
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II",
                        data,
                        int(section["offset"]) + index * 8,
                    )
                    cls.relocations.append(
                        (
                            offset,
                            information & 0xFF,
                            parsed_symbols[information >> 8][0],
                        )
                    )
        cls.relocation_dump = subprocess.run(
            ["/usr/bin/objdump", "-r", str(cls.target_object)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def format_pointer(text: bytes) -> tuple[object, ctypes.c_char_p]:
        storage = (ctypes.c_ubyte * (len(text) + 2))()
        storage[:len(text)] = text
        return storage, ctypes.cast(storage, ctypes.c_char_p)

    def render(
        self,
        text: bytes,
        *arguments: object,
        count: int = 512,
        fill: int = 0xCC,
    ) -> tuple[int, bytes]:
        buffer = (ctypes.c_ubyte * 512)(*([fill] * 512))
        format_storage, format_pointer = self.format_pointer(text)
        result = self.buffer_call(
            buffer,
            count,
            format_pointer,
            *arguments,
        )
        self.assertIsNotNone(format_storage)
        return result, bytes(buffer)

    def assert_render(
        self,
        text: bytes,
        expected: bytes,
        *arguments: object,
    ) -> None:
        result, buffer = self.render(text, *arguments)
        self.assertEqual(result, len(expected))
        self.assertEqual(buffer[:len(expected) + 1], expected + b"\0")
        self.assertEqual(buffer[len(expected) + 1], 0xCC)

    def events(
        self,
    ) -> tuple[list[int], list[int], list[int], list[int]]:
        count = ctypes.c_uint32.in_dll(
            self.loaded,
            "open_cfw_test_runtime_vsnprintf_event_count",
        ).value
        characters = (ctypes.c_uint32 * 512).in_dll(
            self.loaded,
            "open_cfw_test_runtime_vsnprintf_characters",
        )
        indices = (ctypes.c_uint32 * 512).in_dll(
            self.loaded,
            "open_cfw_test_runtime_vsnprintf_indices",
        )
        maximum_lengths = (ctypes.c_uint32 * 512).in_dll(
            self.loaded,
            "open_cfw_test_runtime_vsnprintf_maximum_lengths",
        )
        buffers = (ctypes.c_size_t * 512).in_dll(
            self.loaded,
            "open_cfw_test_runtime_vsnprintf_buffers",
        )
        return (
            list(characters[:count]),
            list(indices[:count]),
            list(maximum_lengths[:count]),
            list(buffers[:count]),
        )

    def test_literals_percent_unknown_and_controlled_trailing_formats(
        self,
    ) -> None:
        self.assert_render(b"plain text", b"plain text")
        self.assert_render(b"a%%b", b"a%b")
        self.assert_render(b"%q", b"q")
        self.assert_render(b"A%05qZ", b"AqZ")

        for malformed in (b"%", b"%05", b"%.", b"%ll"):
            result, buffer = self.render(malformed)
            with self.subTest(format=malformed):
                self.assertEqual(result, 1)
                self.assertEqual(buffer[:3], b"\0\0\xCC")

    def test_all_flag_orderings_parse_to_the_same_state(self) -> None:
        flag_characters = "0-+ #"
        for size in range(6):
            for sequence_tuple in itertools.permutations(
                flag_characters,
                size,
            ):
                sequence = "".join(sequence_tuple)
                canonical = "".join(
                    character
                    for character in flag_characters
                    if character in sequence
                )
                observed = self.render(
                    f"%{sequence}9.4d".encode(),
                    ctypes.c_int32(23),
                )
                expected = self.render(
                    f"%{canonical}9.4d".encode(),
                    ctypes.c_int32(23),
                )
                with self.subTest(sequence=sequence):
                    self.assertEqual(observed, expected)

    def test_width_precision_sign_and_integer_base_policy(self) -> None:
        cases = (
            (b"%d", b"-42", ctypes.c_int32(-42)),
            (b"%+06d", b"+00042", ctypes.c_int32(42)),
            (b"% 6d", b"    42", ctypes.c_int32(42)),
            (b"%-6d", b"42    ", ctypes.c_int32(42)),
            (b"%.0d", b"", ctypes.c_int32(0)),
            (b"%08.3d", b"     042", ctypes.c_int32(42)),
            (b"%u", b"4294967295", ctypes.c_uint32(0xFFFFFFFF)),
            (b"%+u", b"42", ctypes.c_uint32(42)),
            (b"%#x", b"0xabc", ctypes.c_uint32(0xABC)),
            (b"%#X", b"0XABC", ctypes.c_uint32(0xABC)),
            (b"%#o", b"0755", ctypes.c_uint32(0o755)),
            (b"%#b", b"0b101", ctypes.c_uint32(5)),
            (b"%#.0x", b"", ctypes.c_uint32(0)),
        )
        for text, expected, argument in cases:
            with self.subTest(format=text):
                self.assert_render(text, expected, argument)

    def test_star_width_precision_and_minimum_magnitudes(self) -> None:
        self.assert_render(
            b"%*.*d",
            b"42      ",
            ctypes.c_int32(-8),
            ctypes.c_int32(3),
            ctypes.c_int32(42),
        )
        self.assert_render(
            b"%0*.*d",
            b"      42",
            ctypes.c_int32(8),
            ctypes.c_int32(-3),
            ctypes.c_int32(42),
        )
        self.assertEqual(
            self.magnitude_s32(ctypes.c_int32(-0x80000000)),
            0x80000000,
        )
        self.assertEqual(
            self.magnitude_s64(ctypes.c_int64(-0x8000000000000000)),
            0x8000000000000000,
        )

    def test_all_firmware_integer_length_modifiers_and_minima(self) -> None:
        cases = (
            (b"%hhd", b"128", ctypes.c_int32(0x80)),
            (b"%hhd", b"255", ctypes.c_int32(-1)),
            (b"%hhu", b"255", ctypes.c_uint32(0x1FF)),
            (b"%hd", b"-32768", ctypes.c_int32(0x8000)),
            (b"%hu", b"65535", ctypes.c_uint32(0x1FFFF)),
            (b"%d", b"-2147483648", ctypes.c_int32(-0x80000000)),
            (b"%ld", b"-2147483648", ctypes.c_int32(-0x80000000)),
            (b"%td", b"-2147483648", ctypes.c_int32(-0x80000000)),
            (b"%zd", b"-2147483648", ctypes.c_int32(-0x80000000)),
            (
                b"%lld",
                b"-9223372036854775808",
                ctypes.c_int64(-0x8000000000000000),
            ),
            (
                b"%jd",
                b"-9223372036854775808",
                ctypes.c_int64(-0x8000000000000000),
            ),
            (
                b"%llu",
                b"18446744073709551615",
                ctypes.c_uint64(0xFFFFFFFFFFFFFFFF),
            ),
            (
                b"%ju",
                b"18446744073709551615",
                ctypes.c_uint64(0xFFFFFFFFFFFFFFFF),
            ),
        )
        for text, expected, argument in cases:
            with self.subTest(format=text):
                self.assert_render(text, expected, argument)

    def test_character_string_width_and_precision(self) -> None:
        text = ctypes.c_char_p(b"alphabet")
        cases = (
            (b"%5c", b"    A", ctypes.c_int32(ord("A"))),
            (b"%-5c", b"A    ", ctypes.c_int32(ord("A"))),
            (b"%5.3s", b"  alp", text),
            (b"%-5.3s", b"alp  ", text),
            (b"%.0s", b"", text),
            (b"%s", b"alphabet", text),
        )
        for format_text, expected, argument in cases:
            with self.subTest(format=format_text):
                self.assert_render(format_text, expected, argument)

    def test_pointer_policy_is_hash_long_not_fixed_width(self) -> None:
        cases = (
            (b"%p", b"0x12"),
            (b"%P", b"0X12"),
            (b"%08p", b"0x000012"),
            (b"%.8p", b"0x00000012"),
            (b"%12P", b"        0X12"),
        )
        for text, expected in cases:
            with self.subTest(format=text):
                self.assert_render(
                    text,
                    expected,
                    ctypes.c_void_p(0x12),
                )

    def test_fixed_and_exponential_float_feature_set(self) -> None:
        cases = (
            (b"%f", b"1.250000", 1.25),
            (b"%+08.2f", b"+0001.25", 1.25),
            (b"%.2e", b"1.25e+01", 12.5),
            (b"%.2E", b"1.25E+01", 12.5),
            (b"%.3g", b"12.5", 12.5),
            (b"%.3G", b"1.25E-05", 0.0000125),
            (b"%f", b"nan", float("nan")),
            (b"%F", b"inf", float("inf")),
        )
        for text, expected, value in cases:
            with self.subTest(format=text):
                self.assert_render(
                    text,
                    expected,
                    ctypes.c_double(value),
                )

    def test_count_and_termination_semantics_for_every_boundary(self) -> None:
        expected_prefixes = {
            0: b"\xCC\xCC\xCC\xCC\xCC\xCC\xCC",
            1: b"\0\xCC\xCC\xCC\xCC\xCC\xCC",
            2: b"a\0\xCC\xCC\xCC\xCC\xCC",
            6: b"abcde\0\xCC",
            7: b"abcdef\0",
        }
        for count, expected in expected_prefixes.items():
            result, buffer = self.render(b"abcdef", count=count)
            with self.subTest(count=count):
                self.assertEqual(result, 6)
                self.assertEqual(buffer[:7], expected)

        self.reset_observer()
        format_storage, format_pointer = self.format_pointer(b"ab")
        result = self.observer_call(0x1000, 0, format_pointer)
        self.assertEqual(result, 2)
        characters, indices, maximums, buffers = self.events()
        self.assertEqual(characters, [ord("a"), ord("b"), 0])
        self.assertEqual(indices, [0, 1, 0xFFFFFFFF])
        self.assertEqual(maximums, [0, 0, 0])
        self.assertEqual(buffers, [0x1000, 0x1000, 0x1000])
        self.assertIsNotNone(format_storage)

    def test_null_buffer_selects_noop_and_preserves_count(self) -> None:
        format_storage, format_pointer = self.format_pointer(b"%08x")
        result = self.buffer_call(
            None,
            0,
            format_pointer,
            ctypes.c_uint32(0x1234),
        )
        self.assertEqual(result, 8)
        self.assertIsNotNone(format_storage)

    def test_recursive_PV_descriptor_and_following_outer_format(self) -> None:
        buffer = (ctypes.c_ubyte * 128)(*([0xCC] * 128))
        nested_storage, nested_format = self.format_pointer(b"<%d:%s>")
        result = self.nested_call(
            buffer,
            128,
            nested_format,
            ctypes.c_int32(9),
            ctypes.c_int32(-7),
            ctypes.c_char_p(b"xy"),
        )
        self.assertEqual(result, 10)
        self.assertEqual(bytes(buffer[:12]), b"A<-7:xy>Z9\0\xCC")
        self.assertIsNotNone(nested_storage)

        lower_buffer = (ctypes.c_ubyte * 128)(*([0xCC] * 128))
        lower_storage, lower_format = self.format_pointer(b"%d")
        lower_result = self.nested_lowercase(
            lower_buffer,
            128,
            lower_format,
            ctypes.c_int32(4),
            ctypes.c_int32(3),
        )
        self.assertEqual(lower_result, 4)
        self.assertEqual(bytes(lower_buffer[:6]), b"A3Z4\0\xCC")
        self.assertIsNotNone(lower_storage)

    def test_recursive_unsigned_arithmetic_and_both_terminations(self) -> None:
        self.reset_observer()
        nested_storage, nested_format = self.format_pointer(b"BC")
        result = self.nested_observer(
            0x1000,
            0,
            nested_format,
            ctypes.c_int32(9),
        )
        self.assertEqual(result, 5)
        characters, indices, maximums, buffers = self.events()
        self.assertEqual(
            characters,
            [ord("A"), ord("B"), ord("C"), 0, ord("Z"), ord("9"), 0],
        )
        self.assertEqual(
            indices,
            [0, 0, 1, 2, 3, 4, 0xFFFFFFFF],
        )
        self.assertEqual(
            maximums,
            [
                0,
                0xFFFFFFFF,
                0xFFFFFFFF,
                0xFFFFFFFF,
                0,
                0,
                0,
            ],
        )
        self.assertEqual(
            buffers,
            [0x1000, 0x1001, 0x1001, 0x1001, 0x1000, 0x1000, 0x1000],
        )
        self.assertIsNotNone(nested_storage)

    def test_stock_body_hash_feature_set_and_dependencies_are_exact(
        self,
    ) -> None:
        body = self.application[START - BASE:END - BASE]
        self.assertEqual(len(body), 1644)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "69f04620a01aaca4a11601ea426644fa"
            "3e2bd47c972700c6ddc1676607e1435b",
        )
        self.assertEqual(
            struct.unpack_from(
                "<I",
                self.application,
                0x0048400C - BASE,
            )[0],
            0x00483031,
        )
        source = SOURCE.read_text()
        for token in (
            "case 'b':",
            "case 'P':",
            "case 't':",
            "case 'j':",
            "case 'z':",
            "case 'f':",
            "case 'e':",
            "case 'g':",
            "format[1] == (unsigned char)'V'",
            "maximum_length - index",
            "recursive->format",
            "*recursive->arguments",
        ):
            self.assertIn(token, source)

    def test_wide_callers_dependencies_and_interior_topology_are_exact(
        self,
    ) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
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
                if target == START:
                    destination.append((address, encoded.hex()))
                if (
                    START < target < END
                    and not START <= address < END
                ):
                    interior.append((address, target, link))
                if link and START <= address < END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )
        self.assertEqual(
            callers,
            [
                (0x00483D3E, "fff70ffe"),
                (0x00483FE0, "fff7befc"),
                (0x00483FF6, "fff7b3fc"),
            ],
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in callers
                )
            ).hexdigest(),
            "784822765d93f8db698757a1912c2bf8"
            "f12939f5a98083c6154de3d481b01ccd",
        )
        self.assertEqual(
            dependencies,
            [
                (0x00483A14, 0x00483032, "fff70dfb"),
                (0x00483A1E, 0x00483044, "fff711fb"),
                (0x00483A60, 0x00483032, "fff7e7fa"),
                (0x00483A6A, 0x00483044, "fff7ebfa"),
                (0x00483C74, 0x0048329C, "fff712fb"),
                (0x00483CB4, 0x0048320A, "fff7a9fa"),
                (0x00483D12, 0x0048320A, "fff77afa"),
                (0x00483D3E, 0x00483960, "fff70ffe"),
                (0x00483D7C, 0x0048329C, "fff78efa"),
                (0x00483DAC, 0x0048320A, "fff72dfa"),
                (0x00483DFA, 0x0048320A, "fff706fa"),
                (0x00483E34, 0x00483350, "fff78cfa"),
                (0x00483E8A, 0x0048364C, "fff7dffb"),
                (0x00483F04, 0x00454770, "d0f734fc"),
            ],
        )

    def test_narrow_and_stored_pointer_topology_is_exact(self) -> None:
        narrow_entry = []
        narrow_interior = []

        def signed(value: int, bits: int) -> int:
            sign = 1 << (bits - 1)
            return value - (1 << bits) if value & sign else value

        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            candidates = []
            if halfword & 0xF800 == 0xE000:
                candidates.append(
                    address
                    + 4
                    + signed((halfword & 0x7FF) << 1, 12)
                )
            condition = (halfword >> 8) & 15
            if halfword & 0xF000 == 0xD000 and condition < 14:
                candidates.append(
                    address
                    + 4
                    + signed((halfword & 255) << 1, 9)
                )
            if halfword & 0xF500 == 0xB100:
                candidates.append(
                    address
                    + 4
                    + (((halfword >> 9) & 1) << 6)
                    + (((halfword >> 3) & 31) << 1)
                )
            if START in candidates:
                narrow_entry.append((address, halfword))
            narrow_interior.extend(
                (address, target, halfword)
                for target in candidates
                if (
                    START < target < END
                    and not START <= address < END
                )
            )
        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from(
                "<I",
                self.application,
                offset,
            )[0]
            target = value & ~1
            if value & 1 and START <= target < END:
                stored.append((BASE + offset, target, value))
        self.assertEqual(narrow_entry, [])
        self.assertEqual(
            narrow_interior,
            [
                (0x00483942, 0x004839B2, 0xBBB5),
                (0x00483FFC, 0x00483F08, 0xDC84),
            ],
        )
        self.assertEqual(
            stored,
            [
                (0x00454537, 0x00483E20, 0x00483E21),
                (0x00470FBF, 0x00483A20, 0x00483A21),
                (0x00473827, 0x004839D0, 0x004839D1),
                (0x00480611, 0x00483CD0, 0x00483CD1),
                (0x004A6537, 0x00483DBC, 0x00483DBD),
                (0x004A653D, 0x00483D46, 0x00483D47),
                (0x004A6543, 0x00483C46, 0x00483C47),
                (0x004A6549, 0x00483C46, 0x00483C47),
                (0x004B59CD, 0x00483BD4, 0x00483BD5),
                (0x004CFC01, 0x00483B48, 0x00483B49),
                (0x004E306F, 0x00483EB4, 0x00483EB5),
                (0x004F194F, 0x00483E2A, 0x00483E2B),
                (0x00539CD9, 0x00483A46, 0x00483A47),
                (0x0059477B, 0x00483D62, 0x00483D63),
                (0x00594787, 0x00483C62, 0x00483C63),
                (0x0059478F, 0x00483B62, 0x00483B63),
            ],
        )

    @_APPLE_ONLY
    def test_reviewed_target_body_dependencies_and_relocations_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.target_text), 1554)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "4399b83ddb04b106d12367db01b0238d1"
            "c76273690f91c4d2edb0a492faab2e1",
        )
        function = self.symbols["open_cfw_runtime_vsnprintf"]
        self.assertEqual((function[1] & ~1, function[2]), (0, 1554))
        self.assertEqual(
            self.relocations,
            [
                (16, 49, "open_cfw_runtime_noop_output"),
                (20, 50, "open_cfw_runtime_noop_output"),
                (66, 10, "open_cfw_runtime_vsnprintf"),
                (340, 10, "open_cfw_runtime_ascii_is_digit"),
                (348, 10, "open_cfw_runtime_parse_decimal"),
                (414, 10, "open_cfw_runtime_ascii_is_digit"),
                (422, 10, "open_cfw_runtime_parse_decimal"),
                (746, 10, "open_cfw_runtime_strnlen_s"),
                (882, 10, "open_cfw_runtime_etoa"),
                (944, 10, "open_cfw_runtime_ftoa"),
                (1206, 10, "open_cfw_runtime_ntoa_long_long"),
                (1520, 10, "open_cfw_runtime_ntoa_long"),
            ],
        )
        undefined = sorted(
            name
            for name, fields in self.symbols.items()
            if fields[5] == 0
        )
        self.assertEqual(
            undefined,
            [
                "open_cfw_runtime_ascii_is_digit",
                "open_cfw_runtime_etoa",
                "open_cfw_runtime_ftoa",
                "open_cfw_runtime_noop_output",
                "open_cfw_runtime_ntoa_long",
                "open_cfw_runtime_ntoa_long_long",
                "open_cfw_runtime_parse_decimal",
                "open_cfw_runtime_strnlen_s",
            ],
        )
        self.assertNotIn("__aeabi", self.relocation_dump)
        self.assertNotIn("__aeabi", " ".join(self.symbols))

    def test_source_scope_and_fixture_composition_are_bounded(self) -> None:
        source = SOURCE.read_text()
        self.assertNotIn("#include <", source)
        self.assertIn(
            "d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e",
            source,
        )
        self.assertIn("Linux-style %PV", source)
        self.assertIn(
            "open_cfw_runtime_vsnprintf_magnitude_s32(",
            source,
        )
        self.assertIn(
            "open_cfw_runtime_vsnprintf_magnitude_s64(",
            source,
        )
        fixture = FIXTURE.read_text()
        for dependency in (
            "runtime_format_parse_helpers.c",
            "runtime_format_out_reverse.c",
            "runtime_ntoa_format.c",
            "runtime_ntoa_integer.c",
            "runtime_bounded_string_length.c",
            "runtime_strnlen_s.c",
            "runtime_etoa.c",
            "runtime_ftoa.c",
            "runtime_vsnprintf.c",
        ):
            self.assertIn(dependency, fixture)


if __name__ == "__main__":
    unittest.main()
