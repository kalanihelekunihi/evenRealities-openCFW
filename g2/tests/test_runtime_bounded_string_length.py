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
SOURCE = COMPONENT_ROOT / "runtime_bounded_string_length.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_bounded_string_length_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
FUNCTION_START = 0x0048D4E8
FUNCTION_END = 0x0048D53E
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


def _oracle(data: bytes, maximum_length: int) -> int:
    for index in range(min(len(data), maximum_length)):
        if data[index] == 0:
            return index
    return min(len(data), maximum_length)


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeBoundedStringLengthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_bounded_string_length.dylib"
            if sys.platform == "darwin"
            else "runtime_bounded_string_length.so"
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
        cls.execute = cls.loaded.open_cfw_test_bounded_string_length_execute
        cls.execute.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint32,
        ]
        cls.execute.restype = ctypes.c_uint32
        cls.execute_null = (
            cls.loaded.open_cfw_test_bounded_string_length_null
        )
        cls.execute_null.argtypes = [ctypes.c_uint32]
        cls.execute_null.restype = ctypes.c_uint32
        cls.execute_invalid_zero = (
            cls.loaded
            .open_cfw_test_bounded_string_length_zero_maximum_no_load
        )
        cls.execute_invalid_zero.argtypes = []
        cls.execute_invalid_zero.restype = ctypes.c_uint32

        cls.target_object = temporary / "runtime_bounded_string_length.o"
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

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def run_data(
        self,
        data: bytes,
        maximum_length: int,
        offset: int = 0,
    ) -> int:
        storage = (ctypes.c_ubyte * (offset + len(data)))()
        for index, value in enumerate(data):
            storage[offset + index] = value
        pointer = ctypes.cast(
            ctypes.byref(storage, offset),
            ctypes.POINTER(ctypes.c_ubyte),
        )
        return self.execute(pointer, maximum_length)

    def test_null_and_zero_maximum_perform_no_load(self) -> None:
        for maximum_length in (0, 1, 0xFFFFFFFF):
            self.assertEqual(self.execute_null(maximum_length), 0)
        self.assertEqual(self.execute_invalid_zero(), 0)

    def test_alignment_length_and_terminator_grid(self) -> None:
        cases = (
            b"\0",
            b"a\0",
            b"abc\0",
            b"abcdefg\0",
            bytes(range(1, 33)) + b"\0",
            bytes([0xA5]) * 64,
        )
        for offset in range(4):
            for data in cases:
                for maximum_length in range(len(data) + 1):
                    self.assertEqual(
                        self.run_data(data, maximum_length, offset),
                        _oracle(data, maximum_length),
                    )

    def test_bound_precedes_terminator_in_return_value_semantics(
        self,
    ) -> None:
        data = b"abcdefgh\0"
        for maximum_length in range(9):
            self.assertEqual(
                self.run_data(data, maximum_length),
                maximum_length if maximum_length < 8 else 8,
            )

    def test_deterministic_randomized_buffers(self) -> None:
        generator = random.Random(0x48D4E8)
        for _ in range(512):
            length = generator.randrange(1, 193)
            data = bytes(generator.randrange(256) for _ in range(length))
            maximum_length = generator.randrange(length + 1)
            offset = generator.randrange(4)
            self.assertEqual(
                self.run_data(data, maximum_length, offset),
                _oracle(data, maximum_length),
            )

    def test_stock_body_and_adjacent_boundaries_are_exact(self) -> None:
        preceding = self.span(0x0048D4D0, 0x0048D4E6)
        pre_alignment = self.span(0x0048D4E6, FUNCTION_START)
        body = self.span(FUNCTION_START, FUNCTION_END)
        post_alignment = self.span(FUNCTION_END, 0x0048D540)
        following = self.span(0x0048D540, 0x0048D558)

        self.assertEqual(len(preceding), 22)
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "2b65221b1e207b520cc666835bafa78c"
            "16bf4b684c2e9d8b34ca7842ba8f4b1d",
        )
        self.assertEqual(pre_alignment, b"\0\0")
        self.assertEqual(len(body), 86)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "6ae6688c0181b75443a608e2e2de6682"
            "98e9fbe5a81eea0d1db7c3789c7da786",
        )
        self.assertEqual(post_alignment, b"\0\0")
        self.assertEqual(len(following), 24)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "40fc73584b7ab2d723eb1b08d7d80789"
            "e31599de9b6eceb2749666ddf0d1e1d1",
        )
        self.assertEqual(
            self.span(0x0048D558, 0x0048D55A),
            bytes.fromhex("034b"),
        )

    def test_stock_word_scan_and_byte_finish_are_exact(self) -> None:
        body = self.span(FUNCTION_START, FUNCTION_END)
        self.assertEqual(body[:4], bytes.fromhex("030027d0"))
        self.assertIn(bytes.fromhex("a2f1013c"), body)
        self.assertIn(bytes.fromhex("2cea020c1cf0803f"), body)
        self.assertIn(bytes.fromhex("491e26bf10f8012b"), body)
        self.assertIn(bytes.fromhex("491e28bf10f8012b"), body)
        self.assertEqual(body[-6:], bytes.fromhex("491c98417047"))

    def test_wide_caller_dependencies_and_interior_topology_are_exact(
        self,
    ) -> None:
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
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
                if target == FUNCTION_START:
                    destination.append((address, encoded.hex()))
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    interior.append((address, target, link))
                if link and FUNCTION_START <= address < FUNCTION_END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )
        self.assertEqual(callers, [(0x00454772, "38f0b9fe")])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _encoded in callers
                )
            ).hexdigest(),
            "8a68c6110a9cfd6c00adf00e8541d24"
            "b3542dab55c33a7473b4cb44564309d93",
        )
        self.assertEqual(
            hashlib.sha256(b"").hexdigest(),
            "e3b0c44298fc1c149afbf4c8996fb924"
            "27ae41e4649b934ca495991b7852b855",
        )

    def test_narrow_and_stored_pointer_topology_is_classified(self) -> None:
        narrow_entry = []
        narrow_interior = []
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
                candidates.append(
                    address
                    + 4
                    + (((halfword >> 9) & 1) << 6)
                    + (((halfword >> 3) & 0x1F) << 1)
                )
            if FUNCTION_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    narrow_interior.append(
                        (address, target, halfword)
                    )
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])

        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            target = value & ~1
            if (
                value & 1
                and FUNCTION_START <= target < FUNCTION_END
            ):
                context = self.application[offset - 5:offset + 11]
                stored.append(
                    (
                        APPLICATION_BASE + offset,
                        target,
                        value,
                        hashlib.sha256(context).hexdigest(),
                    )
                )
        self.assertEqual(
            stored,
            [
                (
                    0x005944D5,
                    0x0048D4FA,
                    0x0048D4FB,
                    "80ee123869d2286fb755d7b5f1614aaf"
                    "92d4b07915455039040277c131d14b12",
                ),
            ],
        )
        self.assertEqual(
            self.span(0x005944D0, 0x005944E0),
            bytes.fromhex(
                "2022a5f697fbd44800680590d3480068"
            ),
        )

    @_APPLE_ONLY
    def test_target_body_has_no_rodata_or_text_relocations(self) -> None:
        import apollo_overlay

        text = apollo_overlay.section_named(self.target_sections, ".text")
        target = self.target_data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        self.assertEqual(len(target), 26)
        self.assertEqual(
            hashlib.sha256(target).hexdigest(),
            "cf5981636db67e3e3aacef8d9ea91e05"
            "71a0328764f44e78822b006664a4d02b",
        )
        self.assertEqual(
            target,
            bytes.fromhex(
                "30b10022914206d0835c1bb10132f9e7"
                "002100e0114608467047"
            ),
        )
        section_names = {section["name"] for section in self.target_sections}
        self.assertNotIn(".rodata", section_names)
        self.assertNotIn(".rodata.str1.1", section_names)
        relocations = subprocess.run(
            ["/usr/bin/objdump", "-r", str(self.target_object)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertNotIn("RELOCATION RECORDS FOR [.text]", relocations)
        self.assertNotIn("__aeabi", relocations)
        self.assertIn("R_ARM_PREL31", relocations)

    def test_source_explicitly_bounds_semantics_and_uncertainty(self) -> None:
        source = SOURCE.read_text()
        self.assertIn("0x0048D4E8...0x0048D53D", source)
        self.assertIn("open_cfw_runtime_bounded_string_length(", source)
        self.assertIn("length < maximum_length", source)
        self.assertIn("string[length] != '\\0'", source)
        self.assertIn("string == (const char *)0", source)
        self.assertIn("read up to three bytes beyond", source)
        self.assertIn("not fault- or timing-equivalent", source)
        self.assertIn("retain the stock helper", source)
        self.assertIn("minsize", source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_bounded_string_length.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
