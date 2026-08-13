from __future__ import annotations

import os

import ctypes
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_format_out_reverse.c"
PARSE_SOURCE = COMPONENT_ROOT / "runtime_format_parse_helpers.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_format_out_reverse_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
FUNCTION_START = 0x0048306C
FUNCTION_END = 0x004830DA
FLAG_ZEROPAD = 1 << 0
FLAG_LEFT = 1 << 1
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
    index: int,
    reverse: bytes,
    length: int,
    width: int,
    flags: int,
) -> tuple[int, list[int], list[int]]:
    start = index & 0xFFFFFFFF
    current = start
    characters: list[int] = []
    indices: list[int] = []

    if flags & (FLAG_LEFT | FLAG_ZEROPAD) == 0:
        iterator = length
        while iterator < width:
            characters.append(ord(" "))
            indices.append(current)
            current = (current + 1) & 0xFFFFFFFF
            iterator = (iterator + 1) & 0xFFFFFFFF

    remaining = length
    while remaining != 0:
        remaining = (remaining - 1) & 0xFFFFFFFF
        characters.append(reverse[remaining])
        indices.append(current)
        current = (current + 1) & 0xFFFFFFFF

    if flags & FLAG_LEFT:
        while (current - start) & 0xFFFFFFFF < width:
            characters.append(ord(" "))
            indices.append(current)
            current = (current + 1) & 0xFFFFFFFF

    return current, characters, indices


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeFormatOutReverseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.Callback = ctypes.CFUNCTYPE(
            None,
            ctypes.c_char,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        )
        cls.callback_stub = cls.Callback(lambda *_: None)
        cls.callback_address = ctypes.cast(
            cls.callback_stub,
            ctypes.c_void_p,
        ).value
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_format_out_reverse.dylib"
            if sys.platform == "darwin"
            else "runtime_format_out_reverse.so"
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
        cls.output_reverse = (
            cls.loaded.open_cfw_runtime_format_out_reverse
        )
        cls.reset = cls.loaded.open_cfw_test_format_out_reverse_reset
        cls.output_reverse.argtypes = [
            cls.Callback,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.output_reverse.restype = ctypes.c_uint32
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.event_count = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_format_out_reverse_event_count",
        )
        cls.characters = (ctypes.c_uint32 * 256).in_dll(
            cls.loaded,
            "open_cfw_test_format_out_reverse_characters",
        )
        cls.indices = (ctypes.c_uint32 * 256).in_dll(
            cls.loaded,
            "open_cfw_test_format_out_reverse_indices",
        )
        cls.maximum_lengths = (ctypes.c_uint32 * 256).in_dll(
            cls.loaded,
            "open_cfw_test_format_out_reverse_maximum_lengths",
        )
        cls.callback_tokens = (
            (__UINTPTR_CTYPE := ctypes.c_uint64)
            if ctypes.sizeof(ctypes.c_void_p) == 8
            else ctypes.c_uint32
        ) * 256
        cls.callback_tokens = cls.callback_tokens.in_dll(
            cls.loaded,
            "open_cfw_test_format_out_reverse_callback_tokens",
        )
        cls.buffers = (ctypes.c_void_p * 256).in_dll(
            cls.loaded,
            "open_cfw_test_format_out_reverse_buffers",
        )

        target_object = temporary / "runtime_format_out_reverse.o"
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
        from apollo_overlay import extract_linked_overlay

        (
            cls.target_text,
            cls.target_functions,
            cls.target_report,
        ) = extract_linked_overlay(target_object)

        combined_source = temporary / "runtime_format_helpers_combined.c"
        combined_source.write_text(
            f'#include "{PARSE_SOURCE.as_posix()}"\n'
            f'#include "{SOURCE.as_posix()}"\n'
        )
        combined_object = temporary / "runtime_format_helpers_combined.o"
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

    def execute(
        self,
        reverse: bytes,
        *,
        index: int = 0,
        maximum_length: int = 64,
        width: int = 0,
        flags: int = 0,
        callback=None,
    ) -> tuple[int, bytes, int]:
        reverse_storage = (
            (ctypes.c_ubyte * len(reverse))(*reverse)
            if reverse
            else None
        )
        output = (ctypes.c_ubyte * 64)(*[0xA5] * 64)
        result = self.output_reverse(
            callback if callback is not None else self.callback_stub,
            output,
            index,
            maximum_length,
            reverse_storage,
            len(reverse),
            width,
            flags,
        )
        return result, bytes(output), ctypes.addressof(output)

    def test_leading_reverse_and_left_padding_order(self) -> None:
        result, output, _ = self.execute(
            b"dcba",
            width=6,
            flags=0,
        )
        self.assertEqual(result, 6)
        self.assertEqual(output[:6], b"  abcd")
        self.assertEqual(list(self.characters[:6]), list(b"  abcd"))
        self.assertEqual(list(self.indices[:6]), list(range(6)))

        self.reset()
        result, output, _ = self.execute(
            b"dcba",
            width=6,
            flags=FLAG_LEFT,
        )
        self.assertEqual(result, 6)
        self.assertEqual(output[:6], b"abcd  ")
        self.assertEqual(list(self.characters[:6]), list(b"abcd  "))

    def test_zeropad_only_suppresses_space_padding(self) -> None:
        for flags in (
            FLAG_ZEROPAD,
            FLAG_ZEROPAD | 0x80,
        ):
            self.reset()
            result, output, _ = self.execute(
                b"321",
                width=7,
                flags=flags,
            )
            self.assertEqual(result, 3)
            self.assertEqual(output[:3], b"123")
            self.assertEqual(self.event_count.value, 3)

        self.reset()
        result, output, _ = self.execute(
            b"321",
            width=7,
            flags=FLAG_ZEROPAD | FLAG_LEFT,
        )
        self.assertEqual(result, 7)
        self.assertEqual(output[:7], b"123    ")

    def test_small_width_length_flag_grid_matches_oracle(self) -> None:
        reverse_all = b"fedcba"
        for length in range(7):
            reverse = reverse_all[:length]
            for width in range(8):
                for flags in range(8):
                    self.reset()
                    actual, _, _ = self.execute(
                        reverse,
                        index=9,
                        maximum_length=64,
                        width=width,
                        flags=flags,
                    )
                    expected, characters, indices = _oracle(
                        9,
                        reverse,
                        length,
                        width,
                        flags,
                    )
                    with self.subTest(
                        length=length,
                        width=width,
                        flags=flags,
                    ):
                        self.assertEqual(actual, expected)
                        self.assertEqual(
                            self.event_count.value,
                            len(characters),
                        )
                        self.assertEqual(
                            list(self.characters[:len(characters)]),
                            characters,
                        )
                        self.assertEqual(
                            list(self.indices[:len(indices)]),
                            indices,
                        )

    def test_callback_receives_exact_word_abi_arguments(self) -> None:
        callback = self.callback_stub
        maximum_length = 17
        result, _, buffer_address = self.execute(
            b"21",
            index=5,
            maximum_length=maximum_length,
            callback=callback,
        )
        self.assertEqual(result, 7)
        self.assertEqual(self.event_count.value, 2)
        self.assertEqual(list(self.characters[:2]), list(b"12"))
        self.assertEqual(list(self.indices[:2]), [5, 6])
        self.assertEqual(
            list(self.maximum_lengths[:2]),
            [maximum_length, maximum_length],
        )
        self.assertEqual(
            list(self.callback_tokens[:2]),
            [self.callback_address, self.callback_address],
        )
        self.assertEqual(
            list(self.buffers[:2]),
            [buffer_address, buffer_address],
        )

    def test_index_and_left_distance_wrap_as_unsigned_words(self) -> None:
        self.reset()
        result, _, _ = self.execute(
            b"ba",
            index=0xFFFFFFFF,
            width=4,
            flags=FLAG_LEFT,
            maximum_length=0,
        )
        expected, characters, indices = _oracle(
            0xFFFFFFFF,
            b"ba",
            2,
            4,
            FLAG_LEFT,
        )
        self.assertEqual(result, expected)
        self.assertEqual(result, 3)
        self.assertEqual(characters, list(b"ab  "))
        self.assertEqual(
            list(self.indices[:4]),
            [0xFFFFFFFF, 0, 1, 2],
        )
        self.assertEqual(list(self.indices[:4]), indices)

    def test_maximum_length_limits_callback_write_not_callback_count(
        self,
    ) -> None:
        result, output, _ = self.execute(
            b"dcba",
            index=0,
            maximum_length=2,
            width=6,
            flags=0,
        )
        self.assertEqual(result, 6)
        self.assertEqual(self.event_count.value, 6)
        self.assertEqual(output[:2], b"  ")
        self.assertEqual(output[2], 0xA5)

    def test_empty_work_returns_index_without_dereferencing_inputs(
        self,
    ) -> None:
        result = self.output_reverse(
            self.Callback(),
            None,
            0xFFFFFFFF,
            0,
            None,
            0,
            0,
            0,
        )
        self.assertEqual(result, 0xFFFFFFFF)
        self.assertEqual(self.event_count.value, 0)

    def test_stock_body_boundaries_and_adjacent_hashes_are_exact(
        self,
    ) -> None:
        body = self.span(FUNCTION_START, FUNCTION_END)
        self.assertEqual(len(body), 110)
        self.assertEqual(
            body.hex(),
            "2de9f84f05000e00170098460b9cddf83090ddf834a000971a"
            "f0030f0bd1a34607e043463a0031002020a8477f1c1bf1010b"
            "cb45f5d3002c08d0641e43463a0031000a98005da8477f1cf4"
            "e75fea8a7006d409e043463a0031002020a8477f1c0098381a"
            "4845f5d33800bde8f28f",
        )
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "539deb5e8dc993fe5483a052837ce7780"
            "517f23b01ff51e28b4e9976fe4a00c8",
        )
        preceding = self.span(0x00483028, FUNCTION_START)
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "1202ca15ca8a150cea25a8c24c590385"
            "67b45a47be5e42564dfe24147cd5176b",
        )
        following = self.span(FUNCTION_END, 0x00483100)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "0f978373ed65a867576799bff5181294f"
            "eca38c44b54ae2a31b0d5c40b37e9e2",
        )

    def test_callers_dependencies_and_wide_topology_are_exact(self) -> None:
        from apollo_overlay import BuildError, decode_thumb_branch

        callers = []
        jumps = []
        interior = []
        dependencies = []
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
                if target == FUNCTION_START:
                    (callers if link else jumps).append(
                        (address, encoded.hex())
                    )
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    interior.append((address, target, link))
                if link and FUNCTION_START <= address < FUNCTION_END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(
            callers,
            [
                (0x00483200, "fff734ff"),
                (0x0048337C, "fff776fe"),
                (0x004833A0, "fff764fe"),
                (0x004833D8, "fff748fe"),
                (0x00483608, "fff730fd"),
            ],
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in callers
                )
            ).hexdigest(),
            "84e4f91fb913b342309b12af4260ccc54"
            "bfcfb2fff199ae0d5c400b09f766353",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [])
        self.assertEqual(
            [
                self.span(0x00483096, 0x00483098).hex(),
                self.span(0x004830B2, 0x004830B4).hex(),
                self.span(0x004830C8, 0x004830CA).hex(),
            ],
            ["a847", "a847", "a847"],
        )

    def test_narrow_and_stored_interior_candidates_are_false(
        self,
    ) -> None:
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
            if FUNCTION_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    narrow_interior.append((address, target, halfword))

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if value & 1:
                target = value & ~1
                if FUNCTION_START <= target < FUNCTION_END:
                    stored.append((APPLICATION_BASE + offset, target))

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(
            stored,
            [
                (0x00473855, 0x004830D0),
                (0x0049EF01, 0x004830D0),
                (0x00536325, 0x004830B4),
            ],
        )
        contexts = {
            (0x00473850, 0x00473860): (
                "c0b2002808d1304800902e4b4ff49572",
                "5a12962a3a6b3d9c70a4036349b6c7d"
                "604b90d95e24a4d219617419dab3468e3",
            ),
            (0x0049EEFC, 0x0049EF0C): (
                "35fb022809d130480068002803d10021",
                "a7c4d4158121392137fc5c976b1a0ef0"
                "59c14b55d48e210922be230bb1b41940",
            ),
            (0x00536320, 0x00536330): (
                "9847f1bd80b530480021016200214162",
                "c52c3b1e7cc80b4a1976402b72cf0584"
                "ab5bd8826ff65355110f0986f3b93e7b",
            ),
        }
        for (start, end), (body_hex, digest) in contexts.items():
            context = self.span(start, end)
            self.assertEqual(context.hex(), body_hex)
            self.assertEqual(hashlib.sha256(context).hexdigest(), digest)

    @_APPLE_ONLY
    def test_reviewed_target_artifact_is_exact(self) -> None:
        self.assertEqual(
            self.target_functions,
            {
                "open_cfw_runtime_format_out_reverse": {
                    "offset": 0,
                    "size": 130,
                },
            },
        )
        self.assertEqual(self.target_report["text_size"], 130)
        self.assertEqual(self.target_report["rodata_size"], 0)
        self.assertEqual(self.target_report["rodata_sections"], [])
        self.assertEqual(
            self.target_report["resolved_relocation_count"],
            0,
        )
        self.assertEqual(self.target_report["resolved_relocations"], [])
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "0e682a44c949d89cf485c749b216c3bb"
            "7f77d87564f81da1a88ad57e7c20aae3",
        )

    def test_combined_format_translation_unit_is_compatible(self) -> None:
        self.assertEqual(
            set(self.combined_functions),
            {
                "open_cfw_runtime_bounded_byte_store",
                "open_cfw_runtime_noop_output",
                "open_cfw_runtime_ascii_is_digit",
                "open_cfw_runtime_parse_decimal",
                "open_cfw_runtime_format_out_reverse",
            },
        )
        self.assertEqual(self.combined_report["rodata_size"], 0)
        reverse = self.combined_functions[
            "open_cfw_runtime_format_out_reverse"
        ]
        self.assertEqual(reverse["size"], 130)

    def test_source_is_bounded_and_pins_upstream_origin(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "SPDX-License-Identifier: MIT",
            "d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e",
            "open_cfw_runtime_format_out_reverse(",
            "FLAG_ZEROPAD (1U << 0U)",
            "FLAG_LEFT (1U << 1U)",
            "for (iterator = length; iterator < width;",
            "while (length != 0U)",
            "while (index - start_index < width)",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_format_out_reverse.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
