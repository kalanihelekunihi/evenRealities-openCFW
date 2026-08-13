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
SOURCE = COMPONENT_ROOT / "runtime_ftoa.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_ftoa_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
FUNCTION_START = 0x00483350
FUNCTION_END = 0x00483612
FLAG_ZERO_PAD = 1 << 0
FLAG_LEFT = 1 << 1
FLAG_PLUS = 1 << 2
FLAG_SPACE = 1 << 3
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
POW10 = [10.0**exponent for exponent in range(10)]


def _bits(value: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", value))[0]


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


def _oracle(
    value: float,
    precision: int,
    width: int,
    flags: int,
) -> tuple[str, bytes, int, int]:
    if math.isnan(value):
        return "out", b"nan", width, flags
    if value == -math.inf:
        return "out", b"fni-", width, flags
    if value == math.inf:
        reverse = b"fni+" if flags & FLAG_PLUS else b"fni"
        return "out", reverse, width, flags
    if value > 1_000_000_000.0 or value < -1_000_000_000.0:
        return "etoa", b"", width, flags

    negative = value < 0.0
    if negative:
        value = -value
    if not flags & FLAG_PRECISION:
        precision = 6

    reverse = bytearray()
    while len(reverse) < 32 and precision > 9:
        reverse.append(ord("0"))
        precision -= 1

    whole = int(value)
    temporary = (value - float(whole)) * POW10[precision]
    fraction = int(temporary)
    difference = temporary - float(fraction)
    if difference > 0.5:
        fraction += 1
        if fraction >= int(POW10[precision]):
            fraction = 0
            whole += 1
    elif difference == 0.5 and (fraction == 0 or fraction & 1):
        fraction += 1

    if precision == 0:
        difference = value - float(whole)
        if difference == 0.5 and whole & 1:
            whole += 1
    else:
        count = precision
        while len(reverse) < 32:
            count -= 1
            reverse.append(ord("0") + fraction % 10)
            fraction //= 10
            if fraction == 0:
                break
        while len(reverse) < 32 and count > 0:
            count -= 1
            reverse.append(ord("0"))
        if len(reverse) < 32:
            reverse.append(ord("."))

    while len(reverse) < 32:
        reverse.append(ord("0") + whole % 10)
        whole //= 10
        if whole == 0:
            break

    if not flags & FLAG_LEFT and flags & FLAG_ZERO_PAD:
        if width and (
            negative or flags & (FLAG_PLUS | FLAG_SPACE)
        ):
            width = (width - 1) & 0xFFFFFFFF
        while len(reverse) < width and len(reverse) < 32:
            reverse.append(ord("0"))

    if len(reverse) < 32:
        if negative:
            reverse.append(ord("-"))
        elif flags & FLAG_PLUS:
            reverse.append(ord("+"))
        elif flags & FLAG_SPACE:
            reverse.append(ord(" "))
    return "out", bytes(reverse), width, flags


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeFtoaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_ftoa.dylib"
            if sys.platform == "darwin"
            else "runtime_ftoa.so"
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
        cls.Callback = ctypes.CFUNCTYPE(
            None,
            ctypes.c_char,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        )
        cls.callback = cls.Callback(lambda *_: None)
        cls.callback_token = ctypes.cast(
            cls.callback,
            ctypes.c_void_p,
        ).value
        cls.buffer = (ctypes.c_ubyte * 16)(*[0xA5] * 16)
        cls.ftoa = cls.loaded.open_cfw_runtime_ftoa
        cls.ftoa.argtypes = [
            cls.Callback,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_double,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.ftoa.restype = ctypes.c_uint32
        cls.reset = cls.loaded.open_cfw_test_runtime_ftoa_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.reset.restype = None
        cls.reverse = (ctypes.c_ubyte * 32).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_ftoa_reverse",
        )

        for name in (
            "out_calls",
            "etoa_calls",
            "index",
            "maximum_length",
            "length",
            "width",
            "flags",
        ):
            setattr(
                cls,
                name,
                ctypes.c_uint32.in_dll(
                    cls.loaded,
                    f"open_cfw_test_runtime_ftoa_{name}",
                ),
            )
        cls.output_token = cls._uintptr_global("output_token")
        cls.buffer_token = cls._uintptr_global("buffer_token")
        cls.etoa_value_bits = ctypes.c_uint64.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_ftoa_etoa_value_bits",
        )

        cls.target_object = temporary / "runtime_ftoa.o"
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
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        cls.target_data, cls.target_sections = apollo_overlay.parse_elf32(
            cls.target_object
        )

        combined = temporary / "runtime_format_combined.c"
        combined.write_text(
            "\n".join(
                f'#include "{(COMPONENT_ROOT / name).as_posix()}"'
                for name in (
                    "runtime_format_out_reverse.c",
                    "runtime_ntoa_format.c",
                    "runtime_ntoa_integer.c",
                    "runtime_ftoa.c",
                    "runtime_etoa.c",
                )
            )
        )
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(combined),
                "-o",
                str(temporary / "runtime_format_combined.o"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def _uintptr_global(cls, suffix: str):
        carrier = (
            ctypes.c_uint64
            if ctypes.sizeof(ctypes.c_void_p) == 8
            else ctypes.c_uint32
        )
        return carrier.in_dll(
            cls.loaded,
            f"open_cfw_test_runtime_ftoa_{suffix}",
        )

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def execute(
        self,
        value: float,
        precision: int,
        width: int,
        flags: int,
        *,
        index: int = 0x12345678,
        maximum_length: int = 0xABCDEF01,
    ) -> tuple[int, bytes]:
        self.reset(0x13579BDF, 0x2468ACE0)
        result = self.ftoa(
            self.callback,
            self.buffer,
            index,
            maximum_length,
            value,
            precision,
            width,
            flags,
        )
        return result, bytes(self.reverse[: self.length.value])

    def assert_matches(
        self,
        value: float,
        precision: int,
        width: int,
        flags: int,
    ) -> None:
        route, reverse, adjusted_width, expected_flags = _oracle(
            value,
            precision,
            width,
            flags,
        )
        result, observed = self.execute(value, precision, width, flags)
        self.assertEqual(self.output_token.value, self.callback_token)
        self.assertEqual(self.buffer_token.value, ctypes.addressof(self.buffer))
        self.assertEqual(self.index.value, 0x12345678)
        self.assertEqual(self.maximum_length.value, 0xABCDEF01)
        self.assertEqual(self.flags.value, expected_flags)
        if route == "etoa":
            self.assertEqual(result, 0x2468ACE0)
            self.assertEqual(self.etoa_calls.value, 1)
            self.assertEqual(self.out_calls.value, 0)
            self.assertEqual(self.etoa_value_bits.value, _bits(value))
            self.assertEqual(self.length.value, precision)
        else:
            self.assertEqual(result, 0x13579BDF)
            self.assertEqual(self.out_calls.value, 1)
            self.assertEqual(self.etoa_calls.value, 0)
            self.assertEqual(observed, reverse)
            self.assertEqual(self.width.value, adjusted_width)

    def test_special_values_and_large_value_delegation(self) -> None:
        nan_payloads = (
            0x7FF8000000000001,
            0xFFF0000000000001,
        )
        for bits in nan_payloads:
            self.assert_matches(
                struct.unpack("<d", struct.pack("<Q", bits))[0],
                5,
                9,
                FLAG_PLUS,
            )
        for value, flags in (
            (math.inf, 0),
            (math.inf, FLAG_PLUS),
            (-math.inf, FLAG_PLUS),
        ):
            self.assert_matches(value, 3, 11, flags)
        for value in (
            1_000_000_000.0000001,
            -1_000_000_000.0000001,
            1.0e100,
            -1.0e100,
        ):
            self.assert_matches(value, 7, 12, FLAG_PRECISION)

    def test_fixed_boundaries_default_precision_and_negative_zero(self) -> None:
        for value, precision, flags in (
            (1_000_000_000.0, 2, FLAG_PRECISION),
            (-1_000_000_000.0, 2, FLAG_PRECISION),
            (0.0, 9, 0),
            (-0.0, 9, 0),
            (12.375, 1, 0),
            (-12.375, 1, 0),
        ):
            self.assert_matches(value, precision, 0, flags)

    def test_rounding_ties_rollover_and_fractional_zero_fill(self) -> None:
        for value, precision in (
            (1.5, 0),
            (2.5, 0),
            (3.5, 0),
            (0.99, 1),
            (9.95, 1),
            (1.25, 1),
            (1.35, 1),
            (123.0004, 6),
        ):
            self.assert_matches(
                value,
                precision,
                0,
                FLAG_PRECISION,
            )

    def test_sign_and_zero_padding_flag_grid(self) -> None:
        for value in (12.5, -12.5):
            for flags in (
                FLAG_PRECISION,
                FLAG_PRECISION | FLAG_PLUS,
                FLAG_PRECISION | FLAG_SPACE,
                FLAG_PRECISION | FLAG_ZERO_PAD,
                FLAG_PRECISION | FLAG_ZERO_PAD | FLAG_PLUS,
                FLAG_PRECISION | FLAG_ZERO_PAD | FLAG_SPACE,
                FLAG_PRECISION | FLAG_ZERO_PAD | FLAG_LEFT,
            ):
                self.assert_matches(value, 2, 10, flags)

    def test_high_precision_prefix_and_buffer_cap(self) -> None:
        for precision in (10, 17, 32, 41):
            self.assert_matches(
                123.25,
                precision,
                60,
                FLAG_PRECISION | FLAG_PLUS | FLAG_ZERO_PAD,
            )

    def test_deterministic_finite_cross_product(self) -> None:
        generator = random.Random(0x483350)
        for _ in range(256):
            value = generator.uniform(-999_999_999.0, 999_999_999.0)
            precision = generator.randrange(10)
            flags = FLAG_PRECISION | generator.randrange(16)
            width = generator.randrange(20)
            self.assert_matches(value, precision, width, flags)

    def test_stock_body_boundaries_literals_and_hashes_are_exact(self) -> None:
        body = self.span(FUNCTION_START, FUNCTION_END)
        self.assertEqual(len(body), 706)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "184e02e2498722f68a1f12f47502a7d8"
            "ad332e34312c105fd20cc25801e26352",
        )
        alignment = self.span(0x0048334E, FUNCTION_START)
        self.assertEqual(alignment, b"\0\0")
        self.assertEqual(
            hashlib.sha256(alignment).hexdigest(),
            "96a296d224f285c67bee93c30f8a3091"
            "57f0daa35dc5b87e410b78630a09cfc7",
        )
        following = self.span(FUNCTION_END, 0x00483650)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "7bf1982b7e0fcd9899c46f1f481dd651"
            "92ca084cffe789339fc6d8274c200978",
        )
        self.assertEqual(self.span(0x00483614, 0x00483618), b"nan\0")
        self.assertEqual(self.span(0x00483628, 0x0048362C), b"fni\0")
        self.assertEqual(
            self.span(0x006EE378, 0x006EE3C8),
            b"".join(struct.pack("<d", value) for value in POW10),
        )

    def test_callers_dependencies_and_false_overlapping_call_are_exact(
        self,
    ) -> None:
        callers = []
        dependencies = []
        for offset in range(0, len(self.application) - 3, 2):
            first, second = struct.unpack_from(
                "<HH",
                self.application,
                offset,
            )
            if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
                continue
            address = APPLICATION_BASE + offset
            immediate = (
                ((first >> 10) & 1) << 24
                | ((~((second >> 13) & 1) ^ ((first >> 10) & 1)) & 1)
                    << 23
                | ((~((second >> 11) & 1) ^ ((first >> 10) & 1)) & 1)
                    << 22
                | (first & 0x03FF) << 12
                | (second & 0x07FF) << 1
            )
            target = address + 4 + _sign_extend(immediate, 25)
            encoded = struct.pack("<HH", first, second).hex()
            if target == FUNCTION_START:
                callers.append((address, encoded))
            if FUNCTION_START <= address < FUNCTION_END:
                dependencies.append((address, target, encoded))

        self.assertEqual(
            callers,
            [
                (0x00483698, "fff75afe"),
                (0x00483884, "fff764fd"),
                (0x00483E34, "fff78cfa"),
            ],
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(struct.pack("<I", address) for address, _ in callers)
            ).hexdigest(),
            "1c1c0fc72d0e43ba1fa1b5487e0586c"
            "fa33b34fb7b11262630ba4dcfc655cf19",
        )
        self.assertEqual(
            [
                dependency
                for dependency in dependencies
                if dependency[0] != 0x00483566
            ],
            [
                (0x0048337C, 0x0048306C, "fff776fe"),
                (0x004833A0, 0x0048306C, "fff764fe"),
                (0x004833D8, 0x0048306C, "fff748fe"),
                (0x00483404, 0x0048364C, "00f022f9"),
                (0x00483608, 0x0048306C, "fff730fd"),
            ],
        )
        self.assertIn(
            (0x00483566, 0x00477B72, "f4f704fb"),
            dependencies,
        )
        overlapping = self.span(0x00483564, 0x0048356A)
        self.assertEqual(overlapping, bytes.fromhex("95fbf4f704fb"))

    def test_narrow_and_stored_pointer_topology_is_negative(self) -> None:
        entry = []
        interior = []
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
            if FUNCTION_START in candidates:
                entry.append((address, halfword))
            for target in candidates:
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    interior.append((address, target, halfword))
        self.assertEqual(entry, [])
        self.assertEqual(interior, [])

        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            target = value & ~1
            if value & 1 and FUNCTION_START <= target < FUNCTION_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(
            stored,
            [
                (0x004487FB, 0x004835D0),
                (0x00469AB3, 0x004834F8),
                (0x00480635, 0x004833D0),
                (0x004AA579, 0x00483420),
                (0x004D08DD, 0x00483448),
                (0x004D33A3, 0x004834FC),
                (0x004D4AFD, 0x00483520),
            ],
        )
        contexts = {
            0x004487FB:
                "dddb0b7a271e18a671d741b8efd76153"
                "51f0bae068e17c2800cacef1a4137047",
            0x00469AB3:
                "582dcc5226c4f586c245bb9e73816818"
                "b02e41932630397c6fe2f4306e24aa08",
            0x00480635:
                "8b36aae33041b70f0b65a907a90d462"
                "5579fff36021a0e5078f930073f0f80a3",
            0x004AA579:
                "0c6c51d7727713750729c57d2bb50a7"
                "0d795620a00dc9b34a0f4de1604e9231a",
            0x004D08DD:
                "3b49ebf31f2be19f1701e99830ce7538"
                "6940795cc3cc7d77c7d3bc953272b983",
            0x004D33A3:
                "5f2491478b12bbbfc69896bdd49b11a0c"
                "ae8b2b472cee9ca0cf17be15198ae43",
            0x004D4AFD:
                "5221460c99ed4af32ce9eb0c0aebda46"
                "b6a63c73bab18c0a2b769d0bf2f8deae",
        }
        for address, expected_hash in contexts.items():
            context = self.span(address - 5, address + 11)
            self.assertEqual(
                hashlib.sha256(context).hexdigest(),
                expected_hash,
            )

    @_APPLE_ONLY
    def test_target_body_rodata_and_relocations_are_pinned(self) -> None:
        import apollo_overlay

        text = apollo_overlay.section_named(self.target_sections, ".text")
        text_bytes = self.target_data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        strings = apollo_overlay.section_named(
            self.target_sections,
            ".rodata.str1.1",
        )
        string_bytes = self.target_data[
            int(strings["offset"]):
            int(strings["offset"]) + int(strings["size"])
        ]
        rodata = apollo_overlay.section_named(
            self.target_sections,
            ".rodata",
        )
        rodata_bytes = self.target_data[
            int(rodata["offset"]):
            int(rodata["offset"]) + int(rodata["size"])
        ]
        self.assertEqual(len(text_bytes), 732)
        self.assertEqual(
            hashlib.sha256(text_bytes).hexdigest(),
            "8d0271a996fd07a968ba1d0103f0e389"
            "91de1e3e52aa125a8409af92fc8f52ba",
        )
        self.assertEqual(
            hashlib.sha256(string_bytes).hexdigest(),
            "5d29deb34e5ed510f7857735e235fa26"
            "17d88bf6f8398dc100a3c82614b20d1f",
        )
        self.assertEqual(
            hashlib.sha256(rodata_bytes).hexdigest(),
            "1d6d9daf6c036d5d6103c3f06c118aa"
            "2e8862976a7d6ff80fe1bb33b3d0d00a6",
        )
        self.assertEqual(
            string_bytes,
            b"nan\0fni-\0fni+\0fni\0",
        )
        relocations = subprocess.run(
            ["/usr/bin/objdump", "-r", str(self.target_object)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertNotIn("__aeabi", relocations)
        relocation_lines = [
            line.split()
            for line in relocations.splitlines()
            if line.startswith("0000")
        ]
        self.assertEqual(
            relocation_lines,
            [
                [
                    "0000005c",
                    "R_ARM_THM_CALL",
                    "open_cfw_runtime_format_out_reverse",
                ],
                ["000000aa", "R_ARM_THM_JUMP24", "open_cfw_runtime_etoa"],
                ["000002c8", "R_ARM_REL32", ".L.str"],
                ["000002cc", "R_ARM_REL32", ".L.str.1"],
                ["000002d0", "R_ARM_REL32", ".L.str.3"],
                ["000002d4", "R_ARM_REL32", ".L.str.2"],
                [
                    "000002d8",
                    "R_ARM_REL32",
                    "open_cfw_runtime_ftoa_pow10",
                ],
                ["00000000", "R_ARM_PREL31", ".text"],
            ],
        )
        self.assertNotIn("open_cfw_runtime_ntoa_long", relocations)

    def test_source_pins_upstream_abi_and_explicit_vfp_operations(self) -> None:
        source = SOURCE.read_text()
        self.assertIn(
            "d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e",
            source,
        )
        self.assertIn('pcs("aapcs-vfp")', source)
        self.assertIn(".fpu fpv5-d16", source)
        for operation in (
            "vsub.f64",
            "vmul.f64",
            "vcvt.f64.s32",
            "vcvt.f64.u32",
            "vcvt.s32.f64",
            "vcvt.u32.f64",
        ):
            self.assertIn(operation, source)
        self.assertIn("open_cfw_runtime_etoa(", source)
        self.assertIn("open_cfw_runtime_format_out_reverse", source)
        self.assertNotIn("open_cfw_runtime_ntoa_long(", source)


if __name__ == "__main__":
    unittest.main()
