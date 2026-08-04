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


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_format_parse_helpers.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_format_parse_helpers_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
FUNCTIONS = {
    "store": (0x00483028, 0x00483030),
    "noop": (0x00483030, 0x00483032),
    "digit": (0x00483032, 0x00483044),
    "parse": (0x00483044, 0x0048306C),
}
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


def _decimal_oracle(data: bytes) -> tuple[int, int]:
    result = 0
    consumed = 0
    for value in data:
        if value < ord("0") or value > ord("9"):
            break
        consumed += 1
        result = (result * 10 + value - ord("0")) & 0xFFFFFFFF
    return result, consumed


class RuntimeFormatParseHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_format_parse_helpers.dylib"
            if sys.platform == "darwin"
            else "runtime_format_parse_helpers.so"
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
        cls.store = cls.loaded.open_cfw_runtime_bounded_byte_store
        cls.noop = cls.loaded.open_cfw_runtime_noop_output
        cls.is_digit = cls.loaded.open_cfw_runtime_ascii_is_digit
        cls.parse = cls.loaded.open_cfw_test_runtime_parse_decimal_execute
        cls.reset = cls.loaded.open_cfw_test_runtime_parse_reset
        output_arguments = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.store.argtypes = output_arguments
        cls.noop.argtypes = output_arguments
        cls.store.restype = None
        cls.noop.restype = None
        cls.is_digit.argtypes = [ctypes.c_uint32]
        cls.is_digit.restype = ctypes.c_uint32
        cls.parse.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        cls.parse.restype = ctypes.c_uint32
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.query_count = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_parse_digit_query_count",
        )
        cls.queries = (ctypes.c_uint32 * 128).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_parse_digit_queries",
        )

        target_object = temporary / "runtime_format_parse_helpers.o"
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
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        from apollo_overlay import extract_linked_overlay

        (
            cls.target_text,
            cls.target_functions,
            cls.target_report,
        ) = extract_linked_overlay(target_object)

        combined_source = temporary / "runtime_helpers_combined.c"
        combined_source.write_text(
            "\n".join(
                f'#include "{path.as_posix()}"'
                for path in (
                    COMPONENT_ROOT / "runtime_color_math.c",
                    COMPONENT_ROOT / "runtime_color_over32.c",
                    SOURCE,
                )
            )
            + "\n"
        )
        combined_object = temporary / "runtime_helpers_combined.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(combined_source),
                "-o",
                str(combined_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        (
            cls.combined_text,
            cls.combined_functions,
            cls.combined_report,
        ) = extract_linked_overlay(combined_object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def setUp(self) -> None:
        self.reset()

    def execute_parse(self, data: bytes) -> tuple[int, int]:
        values = data + b"\x00"
        storage = (ctypes.c_ubyte * len(values))(*values)
        consumed = ctypes.c_uint32()
        result = self.parse(storage, ctypes.byref(consumed))
        return result, consumed.value

    def test_bounded_store_exhausts_byte_values_and_unsigned_bounds(
        self,
    ) -> None:
        for value in range(256):
            storage = (ctypes.c_ubyte * 12)(*[0xA5] * 12)
            self.store(value | 0xA5A50000, storage, 5, 6)
            expected = bytearray([0xA5] * 12)
            expected[5] = value
            self.assertEqual(bytes(storage), bytes(expected))

            storage = (ctypes.c_ubyte * 12)(*[0xA5] * 12)
            self.store(value, storage, 5, 5)
            self.assertEqual(bytes(storage), bytes([0xA5] * 12))

        storage = (ctypes.c_ubyte * 12)(*[0xA5] * 12)
        for index, capacity in (
            (0, 0),
            (1, 0),
            (0xFFFFFFFF, 0),
            (0xFFFFFFFF, 0xFFFFFFFF),
            (7, 7),
            (8, 7),
        ):
            self.store(0x42, storage, index, capacity)
        self.assertEqual(bytes(storage), bytes([0xA5] * 12))
        self.store(0x42, storage, 0, 1)
        self.assertEqual(storage[0], 0x42)

        self.store(0xFF, None, 0xFFFFFFFF, 0xFFFFFFFF)

    def test_noop_output_preserves_all_memory_for_callback_arguments(
        self,
    ) -> None:
        storage = (ctypes.c_ubyte * 32)(*range(32))
        before = bytes(storage)
        for value, index, capacity in (
            (0, 0, 0),
            (0xFFFFFFFF, 0, 32),
            (0x12345678, 31, 32),
            (0xA5A5A5A5, 0xFFFFFFFF, 0xFFFFFFFF),
        ):
            self.noop(value, storage, index, capacity)
            self.assertEqual(bytes(storage), before)
        self.noop(0, None, 0, 1)

    def test_digit_predicate_exhausts_low_byte_and_ignores_upper_bits(
        self,
    ) -> None:
        for value in range(256):
            expected = int(ord("0") <= value <= ord("9"))
            for upper in (0, 0x01000000, 0xA5A5A500, 0xFFFFFF00):
                with self.subTest(value=value, upper=hex(upper)):
                    self.assertEqual(
                        self.is_digit(upper | value),
                        expected,
                    )

    def test_parser_exhausts_every_two_byte_prefix(self) -> None:
        storage = (ctypes.c_ubyte * 3)()
        consumed = ctypes.c_uint32()
        for first in range(256):
            storage[0] = first
            for second in range(256):
                storage[1] = second
                storage[2] = 0
                consumed.value = 0xFFFFFFFF
                actual = self.parse(storage, ctypes.byref(consumed))
                expected, expected_consumed = _decimal_oracle(
                    bytes((first, second, 0))
                )
                if (
                    actual != expected
                    or consumed.value != expected_consumed
                ):
                    self.fail(
                        f"parser mismatch for {first:#04x}, {second:#04x}: "
                        f"{actual:#x}/{consumed.value} != "
                        f"{expected:#x}/{expected_consumed}"
                    )

    def test_parser_exhausts_all_four_digit_values(self) -> None:
        for digits in itertools.product(b"0123456789", repeat=4):
            data = bytes(digits) + b"x"
            self.assertEqual(self.execute_parse(data), _decimal_oracle(data))

    def test_parser_wraps_u32_and_stops_without_consuming_suffix(self) -> None:
        cases = (
            b"",
            b"x",
            b"-1",
            b"+1",
            b" 1",
            b"0x10",
            b"00000123!",
            b"4294967295;",
            b"4294967296;",
            b"4294967297;",
            b"99999999999999999999;",
            b"18446744073709551615;",
            b"123\x00456",
        )
        for data in cases:
            with self.subTest(data=data):
                self.assertEqual(
                    self.execute_parse(data),
                    _decimal_oracle(data),
                )

    def test_parser_queries_each_digit_and_first_terminator_in_order(
        self,
    ) -> None:
        self.assertEqual(self.execute_parse(b"123x"), (123, 3))
        self.assertEqual(self.query_count.value, 4)
        self.assertEqual(list(self.queries[:4]), list(b"123x"))

        self.reset()
        self.assertEqual(self.execute_parse(b"x123"), (0, 0))
        self.assertEqual(self.query_count.value, 1)
        self.assertEqual(self.queries[0], ord("x"))

    def test_stock_spans_boundaries_padding_and_hashes_are_exact(
        self,
    ) -> None:
        expected = {
            "store": (
                "9a4200d288547047",
                "2032c8f8ef50daff503549cb03c03abc"
                "fbd6319a9d25b72948d4c4dc0954b6a5",
            ),
            "noop": (
                "7047",
                "c7dfbb7d02759eacb64dbc916c1bb6f21"
                "eabaff1c1032ea5c9176abf7fd28df8",
            ),
            "digit": (
                "c0b230380a2801d2012000e00020c0b27047",
                "f397c48340ecfea3718d8251334de9ec"
                "9df2ecbadbe00475a49f46641342b5b8",
            ),
            "parse": (
                "38b50400002507e02068411c21600a210078303801fb0505"
                "20680078fff7e7ff0028f1d1280032bd",
                "436082fd720dad573c13a2e2407e2a38"
                "86faa198346ddee929e18ba3819f5055",
            ),
        }
        for name, (start, end) in FUNCTIONS.items():
            body = self.span(start, end)
            body_hex, digest = expected[name]
            with self.subTest(name=name):
                self.assertEqual(body.hex(), body_hex)
                self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

        cluster = self.span(0x00483028, 0x0048306C)
        self.assertEqual(len(cluster), 68)
        self.assertEqual(
            hashlib.sha256(cluster).hexdigest(),
            "1202ca15ca8a150cea25a8c24c590385"
            "67b45a47be5e42564dfe24147cd5176b",
        )
        preceding = self.span(0x00483000, 0x00483028)
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "7cb5ddd8e1b1af44741917b66cf2038b"
            "9559d614b8b1370a4153be63a75d2008",
        )
        self.assertEqual(
            self.span(0x0048306C, 0x00483070).hex(),
            "2de9f84f",
        )

    def test_callers_dependencies_and_wide_topology_are_exact(self) -> None:
        from apollo_overlay import BuildError, decode_thumb_branch

        callers = {name: [] for name in FUNCTIONS}
        jumps = {name: [] for name in FUNCTIONS}
        interior = {name: [] for name in FUNCTIONS}
        dependencies = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link in (True, False):
                try:
                    target = decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except BuildError:
                    continue
                for name, (start, end) in FUNCTIONS.items():
                    if target == start:
                        (callers if link else jumps)[name].append(
                            (address, encoded.hex())
                        )
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interior[name].append((address, target, link))
                    if link and start <= address < end:
                        dependencies[name].append(
                            (address, target, encoded.hex())
                        )

        expected_callers = {
            "store": [],
            "noop": [],
            "digit": [
                (0x00483060, "fff7e7ff"),
                (0x00483A14, "fff70dfb"),
                (0x00483A60, "fff7e7fa"),
            ],
            "parse": [
                (0x00483A1E, "fff711fb"),
                (0x00483A6A, "fff7ebfa"),
            ],
        }
        expected_digests = {
            "store": (
                "e3b0c44298fc1c149afbf4c8996fb924"
                "27ae41e4649b934ca495991b7852b855"
            ),
            "noop": (
                "e3b0c44298fc1c149afbf4c8996fb924"
                "27ae41e4649b934ca495991b7852b855"
            ),
            "digit": (
                "d05911a4c298614373b6b6cc31befb0b"
                "301957967ea31a93060f8726058b78c9"
            ),
            "parse": (
                "d892bc433717618ec3f64b4d804cea0d"
                "e1add80f028702536c4045c05a1a4416"
            ),
        }
        for name in FUNCTIONS:
            digest = hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in callers[name]
                )
            ).hexdigest()
            with self.subTest(name=name):
                self.assertEqual(callers[name], expected_callers[name])
                self.assertEqual(digest, expected_digests[name])
                self.assertEqual(jumps[name], [])
                self.assertEqual(interior[name], [])

        self.assertEqual(dependencies["store"], [])
        self.assertEqual(dependencies["noop"], [])
        self.assertEqual(dependencies["digit"], [])
        self.assertEqual(
            dependencies["parse"],
            [(0x00483060, 0x00483032, "fff7e7ff")],
        )

    def test_narrow_and_stored_pointer_topology_is_exact(self) -> None:
        narrow_entry = {name: [] for name in FUNCTIONS}
        narrow_interior = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
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
            for name, (start, end) in FUNCTIONS.items():
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

        stored = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if not value & 1:
                continue
            target = value & ~1
            for name, (start, end) in FUNCTIONS.items():
                if start <= target < end:
                    stored[name].append(
                        (APPLICATION_BASE + offset, target)
                    )

        for name in FUNCTIONS:
            self.assertEqual(narrow_entry[name], [])
            self.assertEqual(narrow_interior[name], [])
        self.assertEqual(stored["store"], [(0x00484010, 0x00483028)])
        self.assertEqual(stored["noop"], [(0x0048400C, 0x00483030)])
        self.assertEqual(stored["digit"], [])
        self.assertEqual(stored["parse"], [])

        table = self.span(0x00484008, 0x00484014)
        self.assertEqual(table.hex(), "0000f03f3130480029304800")
        self.assertEqual(
            hashlib.sha256(table).hexdigest(),
            "395ce4c0715f77543a4633ea29610999"
            "e487f0ce21e26ddeb826c74eb93ab29b",
        )
        self.assertEqual(
            [
                self.span(0x00483FDE, 0x00483FE0).hex(),
                self.span(0x00483FF4, 0x00483FF6).hex(),
            ],
            ["0c48", "0648"],
        )

    def test_reviewed_target_artifact_is_exact(self) -> None:
        expected = {
            "open_cfw_runtime_bounded_byte_store": {
                "offset": 0,
                "size": 8,
            },
            "open_cfw_runtime_noop_output": {
                "offset": 8,
                "size": 2,
            },
            "open_cfw_runtime_ascii_is_digit": {
                "offset": 12,
                "size": 18,
            },
            "open_cfw_runtime_parse_decimal": {
                "offset": 32,
                "size": 60,
            },
        }
        self.assertEqual(self.target_functions, expected)
        self.assertEqual(self.target_report["text_size"], 92)
        self.assertEqual(self.target_report["rodata_size"], 0)
        self.assertEqual(self.target_report["rodata_sections"], [])
        self.assertEqual(
            self.target_report["resolved_relocations"],
            [
                {
                    "section": ".rel.text",
                    "site": 40,
                    "type": 10,
                    "symbol": "open_cfw_runtime_ascii_is_digit",
                },
                {
                    "section": ".rel.text",
                    "site": 74,
                    "type": 10,
                    "symbol": "open_cfw_runtime_ascii_is_digit",
                },
            ],
        )
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "84bc5bdb95ba0da36ed89aa6496fdbe0"
            "99d62c23c16dc71ad77fa90db30afbd1",
        )
        body_hashes = {
            "open_cfw_runtime_bounded_byte_store":
                "f6231897ea30fec22eaf14c6f9383603"
                "e2b4c73de57df80a24252452a9d3643e",
            "open_cfw_runtime_noop_output":
                "c7dfbb7d02759eacb64dbc916c1bb6f21"
                "eabaff1c1032ea5c9176abf7fd28df8",
            "open_cfw_runtime_ascii_is_digit":
                "5780b185bd44e15e835c4b6faf1e364c"
                "634e790b40c4810cbe549663f5272e9b",
            "open_cfw_runtime_parse_decimal":
                "c85d25b085a773405882898145436083"
                "535369af28b012abdbb18ed7283d4cd3",
        }
        for name, digest in body_hashes.items():
            info = self.target_functions[name]
            body = self.target_text[
                info["offset"]:info["offset"] + info["size"]
            ]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

    def test_combined_translation_unit_is_compatible(self) -> None:
        self.assertEqual(
            set(self.combined_functions),
            {
                "open_cfw_runtime_color_mix_alpha",
                "open_cfw_runtime_color_brightness",
                "open_cfw_runtime_color_over32",
                "open_cfw_runtime_bounded_byte_store",
                "open_cfw_runtime_noop_output",
                "open_cfw_runtime_ascii_is_digit",
                "open_cfw_runtime_parse_decimal",
            },
        )
        self.assertEqual(self.combined_report["rodata_size"], 0)
        parse_info = self.combined_functions[
            "open_cfw_runtime_parse_decimal"
        ]
        self.assertEqual(parse_info["size"], 60)

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_bounded_byte_store(",
            "open_cfw_runtime_noop_output(",
            "open_cfw_runtime_ascii_is_digit(",
            "open_cfw_runtime_parse_decimal(",
            "if (index < capacity)",
            "*cursor = current + 1;",
            "result = 10U * result",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_format_parse_helpers.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
