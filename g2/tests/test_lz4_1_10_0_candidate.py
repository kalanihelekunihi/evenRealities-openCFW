from __future__ import annotations

import ctypes
import hashlib
import json
import os
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "third_party" / "lz4"
LZ4_SOURCE = SNAPSHOT / "lz4.c"
LZ4_HEADER = SNAPSHOT / "lz4.h"
LZ4_LICENSE = SNAPSHOT / "LICENSE"
LZ4_PROVENANCE = SNAPSHOT / "PROVENANCE.json"
LZ4_VERIFIER = SNAPSHOT / "verify_snapshot.py"
CANDIDATE_SOURCE = ROOT / "research" / "candidates" / "evenhub_lz4_1_10_0.c"
PRODUCTION_SOURCE = ROOT / "components" / "apollo_main" / "core_overlay" / "evenhub_lz4.c"
RVL_FIXTURE = ROOT / "tests" / "fixtures" / "lz4_length_reader_u32_host.c"

UPSTREAM_COMMIT = "ebb370ca83af193212df4dcbadcc5d87bc0de2f0"
UPSTREAM_TREE = "1ff35e0f086e3b431ea0efd001eb5c6254561953"
UPSTREAM_SOURCE_SHA256 = "9396f7de527bc8435de9c7569fb7998e56545a84b4f3c2d808c0235c01774539"
UPSTREAM_HEADER_SHA256 = "26b82efc53d1570f3b54eef02e9c4764c1ad374ff03cac04e2ced5ea4d4c552f"
UPSTREAM_LICENSE_SHA256 = "8b58c446121a109ccf32edc094bba3010a3d85e4ee3702950db55e4d3e87736c"
V1_9_4_COMMIT = "5ff839680134437dbf4678f3d0c7b371d84f4964"
V1_9_4_SOURCE_SHA256 = "b6a85fd8f9be0fedb568abd1338719b23b999583ccda6f3404d5ae11e4ce7b8e"

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-mcpu=cortex-m55",
    "-O2",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-mllvm",
    "-enable-machine-outliner=never",
]
FREESTANDING_DEFINES = [
    "-DLZ4_FREESTANDING=1",
    "-DLZ4_memcpy=__builtin_memcpy",
    "-DLZ4_memmove=__builtin_memmove",
    "-DLZ4_memset=__builtin_memset",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Lz4V110CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")

        cls.candidate_library = cls.compile_host(
            temporary / cls.library_name("lz4_candidate"),
            CANDIDATE_SOURCE,
            LZ4_SOURCE,
        )
        cls.oracle_library = cls.compile_host(
            temporary / cls.library_name("lz4_oracle"),
            LZ4_SOURCE,
        )
        cls.production_library = cls.compile_host(
            temporary / cls.library_name("lz4_production"),
            PRODUCTION_SOURCE,
        )
        cls.rvl_library = cls.compile_host(
            temporary / cls.library_name("lz4_rvl"),
            RVL_FIXTURE,
        )

        cls.candidate = cls.bind_decoder(
            cls.candidate_library,
            "open_cfw_lz4_decompress_safe",
        )
        cls.oracle = cls.bind_decoder(cls.oracle_library, "LZ4_decompress_safe")
        cls.production = cls.bind_decoder(
            cls.production_library,
            "open_cfw_lz4_decompress_safe_legacy",
        )
        cls.compressor = cls.oracle_library.LZ4_compress_default
        cls.compressor.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_int,
            ctypes.c_int,
        ]
        cls.compressor.restype = ctypes.c_int
        cls.compress_bound = cls.oracle_library.LZ4_compressBound
        cls.compress_bound.argtypes = [ctypes.c_int]
        cls.compress_bound.restype = ctypes.c_int

        cls.rvl_functions = []
        for symbol in (
            "open_cfw_lz4_rvl_v1_10_0_u32",
            "open_cfw_lz4_rvl_v1_9_4_u32",
        ):
            function = getattr(cls.rvl_library, symbol)
            function.argtypes = [
                ctypes.POINTER(ctypes.c_ubyte),
                ctypes.c_size_t,
                ctypes.c_size_t,
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.POINTER(ctypes.c_size_t),
            ]
            function.restype = ctypes.c_int
            cls.rvl_functions.append(function)

        cls.target_objects: dict[str, tuple[Path, Path]] = {}
        for repetition in ("a", "b"):
            upstream = temporary / f"lz4_target_{repetition}.o"
            wrapper = temporary / f"lz4_wrapper_target_{repetition}.o"
            subprocess.run(
                [
                    cls.clang,
                    *TARGET_FLAGS,
                    *FREESTANDING_DEFINES,
                    "-c",
                    str(LZ4_SOURCE),
                    "-o",
                    str(upstream),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    cls.clang,
                    *TARGET_FLAGS,
                    "-c",
                    str(CANDIDATE_SOURCE),
                    "-o",
                    str(wrapper),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.target_objects[repetition] = (upstream, wrapper)

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def library_name(stem: str) -> str:
        return stem + (".dylib" if sys.platform == "darwin" else ".so")

    @classmethod
    def compile_host(cls, output: Path, *sources: Path) -> ctypes.CDLL:
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            *(str(source) for source in sources),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(output)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(output)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        return ctypes.CDLL(str(output))

    @staticmethod
    def bind_decoder(library: ctypes.CDLL, symbol: str) -> Any:
        function = getattr(library, symbol)
        function.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_int,
            ctypes.c_int,
        ]
        function.restype = ctypes.c_int
        return function

    @staticmethod
    def execute(function: Any, encoded: bytes, capacity: int) -> tuple[int, bytes]:
        input_buffer = (ctypes.c_ubyte * max(1, len(encoded)))(*(encoded or b"\0"))
        output_buffer = (ctypes.c_ubyte * max(1, capacity + 32))(
            *([0xCC] * max(1, capacity + 32))
        )
        result = int(function(input_buffer, output_buffer, len(encoded), capacity))
        return result, bytes(output_buffer)

    def parse_target(
        self,
        path: Path,
        selected_symbol: str,
    ) -> tuple[bytes, set[tuple[int, str]], set[str]]:
        data, sections = self.apollo_overlay.parse_elf32(path)
        matches = [
            section
            for section in sections
            if str(section.get("name", "")).startswith(".text")
            and str(section.get("name", "")).endswith("." + selected_symbol)
        ]
        self.assertEqual(len(matches), 1)
        section = matches[0]
        symbol_table = self.apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        symbols: list[tuple[str, tuple[int, ...]]] = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            symbols.append(
                (self.apollo_overlay.elf_string(strings, fields[0], "symbol"), fields)
            )
        relocations = set()
        for relocation_section in sections:
            if (
                int(relocation_section["type"]) != 9
                or int(relocation_section["info"]) != int(section["index"])
            ):
                continue
            for index in range(int(relocation_section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    data,
                    int(relocation_section["offset"]) + index * 8,
                )
                relocations.add((information & 0xFF, symbols[information >> 8][0]))
        undefined = {
            name
            for name, fields in symbols
            if name and fields[5] == 0 and name != "$t.0"
        }
        section_bytes = data[
            int(section["offset"]):
            int(section["offset"]) + int(section["size"])
        ]
        return section_bytes, relocations, undefined

    def test_authenticated_snapshot_and_candidate_isolation(self) -> None:
        subprocess.run(
            [sys.executable, str(LZ4_VERIFIER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        provenance = json.loads(LZ4_PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["upstream"]["selected_commit"], UPSTREAM_COMMIT)
        self.assertEqual(provenance["upstream"]["selected_tree"], UPSTREAM_TREE)
        self.assertFalse(provenance["selection"]["exact_historical_checkout_proven"])
        self.assertEqual(
            provenance["selection"]["comparison_baseline"]["commit"],
            V1_9_4_COMMIT,
        )
        self.assertEqual(
            provenance["selection"]["comparison_baseline"]["lz4_c_sha256"],
            V1_9_4_SOURCE_SHA256,
        )
        self.assertEqual(sha256(LZ4_SOURCE.read_bytes()), UPSTREAM_SOURCE_SHA256)
        self.assertEqual(sha256(LZ4_HEADER.read_bytes()), UPSTREAM_HEADER_SHA256)
        self.assertEqual(sha256(LZ4_LICENSE.read_bytes()), UPSTREAM_LICENSE_SHA256)
        candidate_path = CANDIDATE_SOURCE.relative_to(ROOT).as_posix()
        self.assertNotIn(
            candidate_path,
            (ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json").read_text(),
        )
        for manifest in (ROOT / "manifests").glob("*.json"):
            self.assertNotIn(candidate_path, manifest.read_text(), manifest.name)

    def test_valid_blocks_match_pristine_v1_10_0(self) -> None:
        generator = random.Random(0x1100C0DE)
        sources = [
            b"",
            b"hello world",
            bytes(range(256)),
            b"A" * 4096,
            (b"Even Realities G2 LZ4 candidate\0" * 96),
        ]
        for _ in range(96):
            size = generator.randrange(1, 4097)
            if generator.randrange(2) == 0:
                source = bytes(generator.randrange(8) for _ in range(size))
            else:
                source = bytes(generator.randrange(256) for _ in range(size))
            sources.append(source)

        for source in sources:
            bound = int(self.compress_bound(len(source)))
            source_buffer = (ctypes.c_ubyte * max(1, len(source)))(*(source or b"\0"))
            compressed = (ctypes.c_ubyte * max(1, bound))()
            compressed_size = int(
                self.compressor(source_buffer, compressed, len(source), bound)
            )
            self.assertGreater(compressed_size, 0)
            encoded = bytes(compressed[:compressed_size])
            expected = self.execute(self.oracle, encoded, len(source))
            observed = self.execute(self.candidate, encoded, len(source))
            with self.subTest(source_size=len(source), encoded_size=len(encoded)):
                self.assertEqual(observed, expected)
                self.assertEqual(observed[0], len(source))
                self.assertEqual(observed[1][:len(source)], source)
                self.assertEqual(observed[1][len(source):], b"\xCC" * 32)

    def test_malformed_extensions_and_truncations_match_upstream_exactly(self) -> None:
        cases = {
            "literal_extension_missing": bytes.fromhex("f0"),
            "literal_extension_zero_without_literals": bytes.fromhex("f000"),
            "literal_extension_255_truncated": bytes.fromhex("f0ff"),
            "literal_extension_255_zero_truncated": bytes.fromhex("f0ff00"),
            "literal_extension_short_payload": bytes.fromhex("f00100"),
            "match_offset_truncated": bytes.fromhex("1041ff"),
            "match_length_extension_missing": bytes.fromhex("1f410100"),
            "match_length_extension_255_truncated": bytes.fromhex("1f410100ff"),
            "recovered_error_position_probe": bytes.fromhex(
                "d1ebac5a2b368bca5a00ff799d7a03ee"
            ),
        }
        for name, encoded in cases.items():
            with self.subTest(case=name):
                expected = self.execute(self.oracle, encoded, 512)
                observed = self.execute(self.candidate, encoded, 512)
                self.assertEqual(observed, expected)
                self.assertLess(observed[0], 0)
                self.assertEqual(observed[1][512:], b"\xCC" * 32)

        generator = random.Random(0xBAD1100)
        for index in range(4096):
            size = generator.randrange(1, 96)
            encoded = bytes(generator.randrange(256) for _ in range(size))
            capacity = generator.randrange(0, 256)
            with self.subTest(random_case=index):
                self.assertEqual(
                    self.execute(self.candidate, encoded, capacity),
                    self.execute(self.oracle, encoded, capacity),
                )

    def test_current_production_negative_error_positions_are_not_upstream(self) -> None:
        probes = {
            bytes.fromhex("f000"): (-3, -2),
            bytes.fromhex("f0ff00"): (-4, -2),
            bytes.fromhex("1f410100"): (-3, -2),
            bytes.fromhex("d1ebac5a2b368bca5a00ff799d7a03ee"): (-15, -2),
        }
        for encoded, expected in probes.items():
            production_result = self.execute(self.production, encoded, 512)[0]
            upstream_result = self.execute(self.oracle, encoded, 512)[0]
            candidate_result = self.execute(self.candidate, encoded, 512)[0]
            with self.subTest(encoded=encoded.hex()):
                self.assertEqual((production_result, upstream_result), expected)
                self.assertEqual(candidate_result, upstream_result)

    def test_current_production_misses_upstream_mflimit_and_offset_zero_edges(self) -> None:
        close_match = bytes.fromhex("10410100505a5a5a5a5a")
        production_result, production_output = self.execute(
            self.production,
            close_match,
            10,
        )
        upstream_result, upstream_output = self.execute(self.oracle, close_match, 10)
        candidate_result, candidate_output = self.execute(
            self.candidate,
            close_match,
            10,
        )
        self.assertEqual(production_result, 10)
        self.assertEqual(production_output[:10], b"AAAAAZZZZZ")
        self.assertEqual(upstream_result, -2)
        self.assertEqual(candidate_result, upstream_result)
        self.assertEqual(candidate_output, upstream_output)

        zero_offset = bytes.fromhex("10410000505a5a5a5a5a")
        production_result = self.execute(self.production, zero_offset, 512)[0]
        upstream_result = self.execute(self.oracle, zero_offset, 512)[0]
        candidate_result = self.execute(self.candidate, zero_offset, 512)[0]
        self.assertEqual(production_result, -5)
        self.assertEqual(upstream_result, 10)
        self.assertEqual(candidate_result, upstream_result)

    def test_v1_9_4_and_v1_10_0_u32_length_readers_have_same_edges(self) -> None:
        small_cases = [
            (b"\x00", 1, 1),
            (b"\xfe", 1, 1),
            (b"\xff\x00", 2, 1),
            (b"\xff\xff\x01", 3, 1),
            (b"\xff\xff\xff", 2, 0),
        ]
        for encoded, limit, initial_check in small_cases:
            input_buffer = (ctypes.c_ubyte * len(encoded)).from_buffer_copy(encoded)
            results = []
            for function in self.rvl_functions:
                length = ctypes.c_uint32()
                position = ctypes.c_size_t()
                status = int(
                    function(
                        input_buffer,
                        len(encoded),
                        limit,
                        initial_check,
                        ctypes.byref(length),
                        ctypes.byref(position),
                    )
                )
                results.append((status, length.value, position.value))
            with self.subTest(encoded=encoded.hex(), limit=limit):
                self.assertEqual(results[0], results[1])

        overflow_position = (0x7FFFFFFF // 255) + 1
        encoded = b"\xFF" * (overflow_position + 64)
        input_buffer = (ctypes.c_ubyte * len(encoded)).from_buffer_copy(encoded)
        results = []
        for function in self.rvl_functions:
            length = ctypes.c_uint32()
            position = ctypes.c_size_t()
            status = int(
                function(
                    input_buffer,
                    len(encoded),
                    len(encoded),
                    0,
                    ctypes.byref(length),
                    ctypes.byref(position),
                )
            )
            results.append((status, length.value, position.value))
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0][0], -1)
        self.assertEqual(results[0][2], overflow_position)
        self.assertGreater(results[0][1], 0x7FFFFFFF)

    def test_target_build_is_deterministic_and_selected_closure_is_bounded(self) -> None:
        upstream_a, wrapper_a = self.target_objects["a"]
        upstream_b, wrapper_b = self.target_objects["b"]
        self.assertEqual(upstream_a.read_bytes(), upstream_b.read_bytes())
        self.assertEqual(wrapper_a.read_bytes(), wrapper_b.read_bytes())

        decoder, decoder_relocations, decoder_undefined = self.parse_target(
            upstream_a,
            "LZ4_decompress_safe",
        )
        wrapper, wrapper_relocations, wrapper_undefined = self.parse_target(
            wrapper_a,
            "open_cfw_lz4_decompress_safe",
        )
        self.assertGreater(len(decoder), 1000)
        self.assertLess(len(decoder), 2200)
        self.assertEqual(len(wrapper), 4)
        profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE", "apple-clang")
        if profile == "linux-clang":
            table_relocations = {
                (49, "inc32table"),
                (50, "inc32table"),
                (49, "dec64table"),
                (50, "dec64table"),
            }
        else:
            table_relocations = {
                (3, "inc32table"),
                (3, "dec64table"),
            }
        self.assertEqual(
            decoder_relocations,
            table_relocations
            | {
                (10, "__aeabi_memcpy"),
                (10, "__aeabi_memmove"),
            },
        )
        self.assertEqual(wrapper_relocations, {(30, "LZ4_decompress_safe")})
        self.assertIn("__aeabi_memcpy", decoder_undefined)
        self.assertIn("__aeabi_memmove", decoder_undefined)
        self.assertEqual(wrapper_undefined, {"LZ4_decompress_safe"})
        self.assertNotIn(b"LZ4_compress", decoder)


if __name__ == "__main__":
    unittest.main()
