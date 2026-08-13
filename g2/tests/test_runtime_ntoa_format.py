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
SOURCE = COMPONENT_ROOT / "runtime_ntoa_format.c"
INTEGER_SOURCE = COMPONENT_ROOT / "runtime_ntoa_integer.c"
OUT_REVERSE_SOURCE = COMPONENT_ROOT / "runtime_format_out_reverse.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_ntoa_format_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x004830DA
STOCK_END = 0x0048320A

FLAG_ZERO_PAD = 1 << 0
FLAG_LEFT = 1 << 1
FLAG_PLUS = 1 << 2
FLAG_SPACE = 1 << 3
FLAG_HASH = 1 << 4
FLAG_UPPERCASE = 1 << 5
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
    *,
    scratch: bytes,
    index: int,
    maximum_length: int,
    length: int,
    negative: int,
    base: int,
    precision: int,
    width: int,
    flags: int,
) -> tuple[bytes, bytes, int, int, int, int]:
    work = bytearray(scratch)
    flags &= 0xFFFFFFFF
    width &= 0xFFFFFFFF
    length &= 0xFFFFFFFF
    negative = 1 if negative else 0

    if not flags & FLAG_LEFT:
        if (
            width
            and flags & FLAG_ZERO_PAD
            and (negative or flags & (FLAG_PLUS | FLAG_SPACE))
        ):
            width = (width - 1) & 0xFFFFFFFF
        while length < precision and length < 32:
            work[length] = ord("0")
            length += 1
        while flags & FLAG_ZERO_PAD and length < width and length < 32:
            work[length] = ord("0")
            length += 1

    if flags & FLAG_HASH:
        if (
            not flags & FLAG_PRECISION
            and length
            and (length == precision or length == width)
        ):
            length -= 1
            if length and base == 16:
                length -= 1
        if base == 16 and not flags & FLAG_UPPERCASE and length < 32:
            work[length] = ord("x")
            length += 1
        elif base == 16 and flags & FLAG_UPPERCASE and length < 32:
            work[length] = ord("X")
            length += 1
        elif base == 2 and length < 32:
            work[length] = ord("b")
            length += 1
        if length < 32:
            work[length] = ord("0")
            length += 1

    if length < 32:
        if negative:
            work[length] = ord("-")
            length += 1
        elif flags & FLAG_PLUS:
            work[length] = ord("+")
            length += 1
        elif flags & FLAG_SPACE:
            work[length] = ord(" ")
            length += 1

    emitted = bytearray()
    if not flags & FLAG_LEFT and not flags & FLAG_ZERO_PAD:
        emitted.extend(b" " * max(0, width - length))
    emitted.extend(reversed(work[:length]))
    if flags & FLAG_LEFT:
        emitted.extend(b" " * max(0, width - len(emitted)))

    output = bytearray([0xCC] * 128)
    for offset, character in enumerate(emitted):
        destination = index + offset
        if destination < maximum_length:
            output[destination] = character
    return (
        bytes(work),
        bytes(output),
        index + len(emitted),
        length,
        width,
        len(emitted),
    )


class RuntimeNtoaFormatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_ntoa_format.dylib"
            if sys.platform == "darwin"
            else "runtime_ntoa_format.so"
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
        cls.reset = cls.loaded.open_cfw_test_ntoa_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.execute = cls.loaded.open_cfw_test_ntoa_execute
        cls.execute.argtypes = [ctypes.c_uint32] * 8
        cls.execute.restype = ctypes.c_uint32
        scratch = cls.loaded.open_cfw_test_ntoa_scratch
        scratch.argtypes = []
        scratch.restype = ctypes.POINTER(ctypes.c_ubyte)
        cls.scratch = scratch
        storage = cls.loaded.open_cfw_test_ntoa_scratch_storage
        storage.argtypes = []
        storage.restype = ctypes.POINTER(ctypes.c_ubyte)
        cls.storage = storage
        output = cls.loaded.open_cfw_test_ntoa_output_bytes
        output.argtypes = []
        output.restype = ctypes.POINTER(ctypes.c_ubyte)
        cls.output = output

        cls.target_object = Path(cls.temporary.name) / "ntoa_format.o"
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

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def run_case(
        self,
        *,
        scratch: bytes,
        index: int,
        maximum_length: int,
        length: int,
        negative: int,
        base: int,
        precision: int,
        width: int,
        flags: int,
    ) -> tuple[bytes, bytes, int]:
        self.assertEqual(len(scratch), 32)
        self.reset()
        target = self.scratch()
        for offset, value in enumerate(scratch):
            target[offset] = value
        result = self.execute(
            index,
            maximum_length,
            length,
            negative,
            base,
            precision,
            width,
            flags,
        )
        return bytes(self.storage()[:40]), bytes(self.output()[:128]), result

    def assert_case(self, **case: object) -> None:
        expected = _oracle(**case)
        storage, output, result = self.run_case(**case)
        expected_scratch, expected_output, expected_result = expected[:3]
        expected_length, expected_width, callback_calls = expected[3:]
        self.assertEqual(storage[:4], b"\xA5" * 4)
        self.assertEqual(storage[4:36], expected_scratch)
        self.assertEqual(storage[36:], b"\xA5" * 4)
        self.assertEqual(output, expected_output)
        self.assertEqual(result, expected_result)
        self.assertEqual(self.uint("open_cfw_test_ntoa_reverse_calls"), 1)
        self.assertEqual(
            self.uint("open_cfw_test_ntoa_callback_calls"),
            callback_calls,
        )
        self.assertEqual(
            self.uint("open_cfw_test_ntoa_reverse_index"),
            case["index"],
        )
        self.assertEqual(
            self.uint("open_cfw_test_ntoa_reverse_maximum_length"),
            case["maximum_length"],
        )
        self.assertEqual(
            self.uint("open_cfw_test_ntoa_reverse_length"),
            expected_length,
        )
        self.assertEqual(
            self.uint("open_cfw_test_ntoa_reverse_width"),
            expected_width,
        )
        self.assertEqual(
            self.uint("open_cfw_test_ntoa_reverse_flags"),
            case["flags"],
        )

    def test_precision_width_zero_padding_and_sign_precedence(self) -> None:
        initial = b"21" + b"\xA5" * 30
        cases = [
            {
                "scratch": initial,
                "index": 0,
                "maximum_length": 128,
                "length": 2,
                "negative": 1,
                "base": 10,
                "precision": 5,
                "width": 8,
                "flags": FLAG_ZERO_PAD | FLAG_PLUS | FLAG_SPACE,
            },
            {
                "scratch": initial,
                "index": 3,
                "maximum_length": 7,
                "length": 2,
                "negative": 0,
                "base": 10,
                "precision": 7,
                "width": 9,
                "flags": FLAG_PLUS | FLAG_SPACE,
            },
            {
                "scratch": initial,
                "index": 2,
                "maximum_length": 128,
                "length": 2,
                "negative": 0,
                "base": 10,
                "precision": 20,
                "width": 7,
                "flags": FLAG_LEFT | FLAG_ZERO_PAD | FLAG_SPACE,
            },
        ]
        for case in cases:
            with self.subTest(case=case):
                self.assert_case(**case)

    def test_hash_prefixes_case_adjustment_and_precision_flag(self) -> None:
        initial = b"ff000001" + b"\xA5" * 24
        for base in (2, 8, 10, 16):
            for uppercase in (0, FLAG_UPPERCASE):
                for precision_flag in (0, FLAG_PRECISION):
                    for matching in ("none", "precision", "width"):
                        precision = 11 if matching == "none" else 8
                        width = 13 if matching != "width" else 8
                        flags = FLAG_HASH | uppercase | precision_flag
                        case = {
                            "scratch": initial,
                            "index": 1,
                            "maximum_length": 96,
                            "length": 8,
                            "negative": 0,
                            "base": base,
                            "precision": precision,
                            "width": width,
                            "flags": flags,
                        }
                        with self.subTest(
                            base=base,
                            uppercase=uppercase,
                            precision_flag=precision_flag,
                            matching=matching,
                        ):
                            self.assert_case(**case)

    def test_complete_flag_combinations_and_randomized_inputs(self) -> None:
        generator = random.Random(0x4830DA)
        flag_bits = [
            FLAG_ZERO_PAD,
            FLAG_LEFT,
            FLAG_PLUS,
            FLAG_SPACE,
            FLAG_HASH,
            FLAG_UPPERCASE,
            FLAG_PRECISION,
        ]
        cases: list[dict[str, object]] = []
        for mask in range(1 << len(flag_bits)):
            flags = 0
            for bit_index, bit in enumerate(flag_bits):
                if mask & (1 << bit_index):
                    flags |= bit
            length = generator.randrange(0, 33)
            cases.append(
                {
                    "scratch": generator.randbytes(32),
                    "index": generator.randrange(0, 12),
                    "maximum_length": generator.randrange(0, 60),
                    "length": length,
                    "negative": generator.choice((0, 1)),
                    "base": generator.choice((2, 8, 10, 16, 36)),
                    "precision": generator.randrange(0, 48),
                    "width": generator.randrange(0, 48),
                    "flags": flags,
                }
            )
        for _ in range(256):
            cases.append(
                {
                    "scratch": generator.randbytes(32),
                    "index": generator.randrange(0, 32),
                    "maximum_length": generator.randrange(0, 128),
                    "length": generator.randrange(0, 33),
                    "negative": generator.choice((0, 1)),
                    "base": generator.choice((2, 8, 10, 16, 36)),
                    "precision": generator.randrange(0, 96),
                    "width": generator.randrange(0, 96),
                    "flags": generator.getrandbits(12),
                }
            )
        for index, case in enumerate(cases):
            with self.subTest(index=index):
                self.assert_case(**case)

    def test_thirty_two_byte_bound_blocks_prefix_and_sign_writes(self) -> None:
        initial = bytes(range(32))
        for flags in (
            FLAG_HASH,
            FLAG_HASH | FLAG_UPPERCASE,
            FLAG_PLUS | FLAG_SPACE,
            FLAG_HASH | FLAG_PLUS | FLAG_SPACE | FLAG_ZERO_PAD,
        ):
            with self.subTest(flags=flags):
                self.assert_case(
                    scratch=initial,
                    index=0,
                    maximum_length=128,
                    length=32,
                    negative=1,
                    base=16,
                    precision=96,
                    width=96,
                    flags=flags,
                )

    def test_stock_span_and_adjacent_hashes_are_exact(self) -> None:
        def span(start: int, end: int) -> bytes:
            return self.application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        body = span(STOCK_START, STOCK_END)
        self.assertEqual(len(body), 304)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "b5694553bfa306e4696cdf5b6cd02bee"
            "3fb27f8db9e1eab5a27ca90319901a32",
        )
        self.assertEqual(
            hashlib.sha256(span(0x0048306C, STOCK_START)).hexdigest(),
            "539deb5e8dc993fe5483a052837ce778"
            "0517f23b01ff51e28b4e9976fe4a00c8",
        )
        self.assertEqual(
            hashlib.sha256(span(STOCK_END, 0x0048329A)).hexdigest(),
            "c017fd87db991a624fa92f5c97a4cd33"
            "f1a165aa9d436d45b815059da99bb041",
        )

    def test_callers_dependency_and_wide_topology_are_exact(self) -> None:
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        from apollo_overlay import BuildError, decode_thumb_branch

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except BuildError:
                    continue
                if target == STOCK_START:
                    observed.append((address, encoded.hex()))
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(
            callers,
            [
                (0x00483292, "fff722ff"),
                (0x00483344, "fff7c9fe"),
            ],
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _encoded in callers
                )
            ).hexdigest(),
            "716c2bff7f46da5eaa99bfb64ad0675c"
            "d2ef88f4b8a36b9733890b02c86ee620",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [(0x00483200, 0x0048306C, "fff734ff")],
        )

    def test_no_narrow_entries_and_stored_candidates_are_false(self) -> None:
        narrow_entry = []
        narrow_interior = []
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
            if STOCK_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    narrow_interior.append(
                        (address, target, halfword)
                    )
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])

        stored = []
        for target in range(STOCK_START, STOCK_END, 2):
            needle = struct.pack("<I", target | 1)
            position = self.application.find(needle)
            while position >= 0:
                stored.append((APPLICATION_BASE + position, target))
                position = self.application.find(needle, position + 1)
        self.assertEqual(
            sorted(stored),
            [
                (0x0047E1ED, 0x004831B4),
                (0x004ED681, 0x004831D4),
                (0x00539D01, 0x004830E6),
            ],
        )
        for storage_address, target in stored:
            self.assertEqual(storage_address & 1, 1)
            self.assertEqual(target & 1, 0)

    def test_reviewed_target_artifact_and_relocation_are_exact(self) -> None:
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(self.target_object)
        text_section = next(
            section for section in sections
            if section["name"] == ".text"
        )
        text = data[
            text_section["offset"]:
            text_section["offset"] + text_section["size"]
        ]
        self.assertEqual(len(text), 432)
        self.assertEqual(
            hashlib.sha256(text).hexdigest(),
            "7d46b5071d8503fcdad681ae9a39b39"
            "a2e61cdc76a971f028fb256432ac2c1f6",
        )
        self.assertEqual(
            [
                section["name"]
                for section in sections
                if apollo_overlay.is_rodata(section)
            ],
            [],
        )

        symbol_section = next(
            section for section in sections
            if section["type"] == apollo_overlay.SHT_SYMTAB
        )
        strings = sections[symbol_section["link"]]
        string_data = data[
            strings["offset"]:strings["offset"] + strings["size"]
        ]
        symbols = []
        for index in range(symbol_section["size"] // 16):
            offset = symbol_section["offset"] + index * 16
            name_offset, value, size, info, _other, section_index = (
                struct.unpack_from("<IIIBBH", data, offset)
            )
            symbols.append(
                {
                    "name": apollo_overlay.elf_string(
                        string_data,
                        name_offset,
                        "symbol name",
                    ),
                    "value": value,
                    "size": size,
                    "type": info & 0x0F,
                    "section_index": section_index,
                }
            )
        owned = next(
            symbol for symbol in symbols
            if symbol["name"] == "open_cfw_runtime_ntoa_format"
        )
        self.assertEqual(
            (owned["value"] & ~1, owned["size"], owned["section_index"]),
            (0, 432, text_section["index"]),
        )
        unresolved = [
            symbol["name"]
            for symbol in symbols
            if symbol["section_index"] == 0 and symbol["name"]
        ]
        self.assertEqual(
            unresolved,
            ["open_cfw_runtime_format_out_reverse"],
        )

        relocations = []
        for section in sections:
            if (
                section["type"] != apollo_overlay.SHT_REL
                or section["info"] != text_section["index"]
            ):
                continue
            for index in range(section["size"] // 8):
                offset = section["offset"] + index * 8
                site, info = struct.unpack_from("<II", data, offset)
                relocations.append(
                    (
                        section["name"],
                        site,
                        info & 0xFF,
                        symbols[info >> 8]["name"],
                    )
                )
        self.assertEqual(
            relocations,
            [
                (
                    ".rel.text",
                    0x1AC,
                    apollo_overlay.R_ARM_THM_JUMP24,
                    "open_cfw_runtime_format_out_reverse",
                )
            ],
        )

    def test_integer_source_translation_unit_compatibility(self) -> None:
        translation_unit = Path(self.temporary.name) / "combined.c"
        translation_unit.write_text(
            (
                f'#include "{INTEGER_SOURCE}"\n'
                f'#include "{OUT_REVERSE_SOURCE}"\n'
                f'#include "{SOURCE}"\n'
            ),
            encoding="utf-8",
        )
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(translation_unit),
                "-o",
                str(Path(self.temporary.name) / "combined.o"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_source_and_fixture_hashes_are_review_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "4ce36ff24dba43783c1cd75d5a029ecf"
            "352a8cad15c2019ef3c932a9b277d990",
        )
        self.assertEqual(
            hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
            "0131eecd8fcedafd9bf282c1c0725e3e"
            "0699be1ae000d651999be0961cc53826",
        )


if __name__ == "__main__":
    unittest.main()
