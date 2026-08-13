from __future__ import annotations

import os

import ctypes
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "shared"
    / "easylogger"
    / "runtime_easylogger_helpers.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT / "tests" / "fixtures" / "runtime_easylogger_helpers_host.c"
)
ORACLE_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_easylogger_helpers_upstream_oracle_host.c"
)
UPSTREAM_ELOG = ROOT / "third_party" / "easylogger" / "src" / "elog.c"
UPSTREAM_UTILS = (
    ROOT / "third_party" / "easylogger" / "src" / "elog_utils.c"
)
UPSTREAM_HEADER = ROOT / "third_party" / "easylogger" / "inc" / "elog.h"
UPSTREAM_CONFIG = (
    ROOT / "third_party" / "easylogger" / "inc" / "elog_cfg.h"
)
PROVENANCE = ROOT / "third_party" / "easylogger" / "PROVENANCE.json"

SOURCE_SHA256 = (
    "8f2850f789fba3b08bdc3e1fa8f3a464"
    "6aaef7e4b16862f3be53478071aa22b5"
)
HEADER_SHA256 = (
    "f3a7e9bce0f136a2ff4a76929c317aef"
    "7bbc7c29dfc60d58311d94e58f6e2393"
)
UPSTREAM_SHA256 = {
    UPSTREAM_ELOG: (
        "d4291ab1314a34cf940c8e0d7246e055"
        "70f8d32ae0704b498cf6fbacab76acb1"
    ),
    UPSTREAM_UTILS: (
        "937eaf98151cb5fa25f102621802637d7"
        "1ccadd56028098e3a45978a0707d9d0"
    ),
    UPSTREAM_HEADER: (
        "2890b272a01820a6336da544c056e773"
        "5b88330cd91a5092fb83a5538de11f48"
    ),
    UPSTREAM_CONFIG: (
        "bccd34ca41c36ce8201d78fd2b844b0"
        "71bad25bfbac452d02764617ca4ed3073"
    ),
}
UPSTREAM_COMMIT = "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"
UPSTREAM_TREE = "dc9ceb7202c5dd2d58e5e5a9b408b1c05a5ec4f3"
UPSTREAM_GIT_BLOBS = {
    "easylogger/src/elog.c": "b3a00e3927edf97013ddfffeb157be5c1462a6b4",
    "easylogger/src/elog_utils.c": (
        "165d855d2c8e8470b3543380ca6064c0799a8a44"
    ),
    "easylogger/inc/elog.h": "adde47c2df84ea40e4a876f02557c7a4801e8c03",
    "easylogger/inc/elog_cfg.h": (
        "0b4481ed49de06e310e72f4ba53bd5871d0e1722"
    ),
}

PROFILE_MAIN = 1
PROFILE_BOOT = 2
PROFILE_CONSTANTS = {
    PROFILE_MAIN: (0x20070BE8, 0x2007456C, 0x0043D574, 0x0044B0AE),
    PROFILE_BOOT: (0x20026700, 0x200270E4, 0x004176CE, 0x0041AC8A),
}
TARGET_PROFILES = {
    "main": {
        "profile": PROFILE_MAIN,
        "flags": [
            "--target=thumbv7em-none-eabi",
            "-mthumb",
            "-O2",
        ],
    },
    "boot": {
        "profile": PROFILE_BOOT,
        "flags": [
            "--target=arm-none-eabi",
            "-mcpu=cortex-m55",
            "-mthumb",
            "-Oz",
        ],
    },
}
TARGET_COMMON_FLAGS = [
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
]
LEAVES = {
    "STRCPY": (
        "open_cfw_easylogger_strcpy",
        {"open_cfw_easylogger_helpers_assert_failed"},
    ),
    "GET_FMT_ENABLED": (
        "open_cfw_easylogger_get_fmt_enabled",
        {
            "open_cfw_easylogger_helpers_assert_failed",
            "open_cfw_easylogger_helpers_get_logger",
        },
    ),
    "GET_FMT_USED_AND_ENABLED_U32": (
        "open_cfw_easylogger_get_fmt_used_and_enabled_u32",
        {"open_cfw_easylogger_get_fmt_enabled"},
    ),
    "GET_FMT_USED_AND_ENABLED_PTR": (
        "open_cfw_easylogger_get_fmt_used_and_enabled_ptr",
        {"open_cfw_easylogger_get_fmt_enabled"},
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


def finish_library_command(command: list[str], output: Path) -> list[str]:
    if sys.platform == "darwin":
        return [*command, "-dynamiclib", "-o", str(output)]
    return [*command, "-shared", "-fPIC", "-o", str(output)]


def bind_noarg_u32(library: ctypes.CDLL, name: str):
    function = getattr(library, name)
    function.argtypes = []
    function.restype = ctypes.c_uint32
    return function


class EasyLoggerLibrary:
    def __init__(self, loaded: ctypes.CDLL):
        self.loaded = loaded
        self.reset = loaded.open_cfw_test_easylogger_helpers_reset
        self.reset.argtypes = []
        self.reset.restype = None

        self.set_format = (
            loaded.open_cfw_test_easylogger_helpers_set_format
        )
        self.set_format.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        self.set_format.restype = None

        self.strcpy = loaded.open_cfw_easylogger_strcpy
        self.strcpy.argtypes = [
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_char_p,
        ]
        self.strcpy.restype = ctypes.c_uint32

        self.get_fmt = loaded.open_cfw_easylogger_get_fmt_enabled
        self.get_fmt.argtypes = [ctypes.c_uint8, ctypes.c_uint32]
        self.get_fmt.restype = ctypes.c_uint8

        self.get_fmt_u32 = (
            loaded.open_cfw_easylogger_get_fmt_used_and_enabled_u32
        )
        self.get_fmt_u32.argtypes = [
            ctypes.c_uint8,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        self.get_fmt_u32.restype = ctypes.c_uint8

        self.get_fmt_ptr = (
            loaded.open_cfw_easylogger_get_fmt_used_and_enabled_ptr
        )
        self.get_fmt_ptr.argtypes = [
            ctypes.c_uint8,
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        self.get_fmt_ptr.restype = ctypes.c_uint8

        self.trapped_strcpy = (
            loaded.open_cfw_test_easylogger_helpers_call_strcpy_trapped
        )
        self.trapped_strcpy.argtypes = [
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        self.trapped_strcpy.restype = ctypes.c_uint32

        self.trapped_get_fmt = (
            loaded.open_cfw_test_easylogger_helpers_call_get_fmt_trapped
        )
        self.trapped_get_fmt.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        self.trapped_get_fmt.restype = ctypes.c_uint32

        self.assert_count = bind_noarg_u32(
            loaded,
            "open_cfw_test_easylogger_helpers_get_assert_count",
        )
        self.assert_line = bind_noarg_u32(
            loaded,
            "open_cfw_test_easylogger_helpers_get_assert_line",
        )


class OracleLibrary:
    def __init__(self, loaded: ctypes.CDLL):
        self.loaded = loaded
        self.reset = loaded.open_cfw_oracle_easylogger_helpers_reset
        self.reset.argtypes = []
        self.reset.restype = None

        self.set_format = (
            loaded.open_cfw_oracle_easylogger_helpers_set_format
        )
        self.set_format.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        self.set_format.restype = None

        self.strcpy = (
            loaded.open_cfw_oracle_easylogger_helpers_strcpy
        )
        self.strcpy.argtypes = [
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_char_p,
        ]
        self.strcpy.restype = ctypes.c_uint32

        self.get_fmt = (
            loaded.open_cfw_oracle_easylogger_helpers_get_fmt_enabled
        )
        self.get_fmt.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        self.get_fmt.restype = ctypes.c_uint32

        self.get_fmt_u32 = getattr(
            loaded,
            "open_cfw_oracle_easylogger_helpers_"
            "get_fmt_used_and_enabled_u32",
        )
        self.get_fmt_u32.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        self.get_fmt_u32.restype = ctypes.c_uint32

        self.get_fmt_ptr = getattr(
            loaded,
            "open_cfw_oracle_easylogger_helpers_"
            "get_fmt_used_and_enabled_ptr",
        )
        self.get_fmt_ptr.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        self.get_fmt_ptr.restype = ctypes.c_uint32

        self.trapped_strcpy = getattr(
            loaded,
            "open_cfw_oracle_easylogger_helpers_call_strcpy_trapped",
        )
        self.trapped_strcpy.argtypes = [
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        self.trapped_strcpy.restype = ctypes.c_uint32

        self.trapped_get_fmt = getattr(
            loaded,
            "open_cfw_oracle_easylogger_helpers_call_get_fmt_trapped",
        )
        self.trapped_get_fmt.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        self.trapped_get_fmt.restype = ctypes.c_uint32

        self.assert_count = bind_noarg_u32(
            loaded,
            "open_cfw_oracle_easylogger_helpers_get_assert_count",
        )
        self.assert_line = bind_noarg_u32(
            loaded,
            "open_cfw_oracle_easylogger_helpers_get_assert_line",
        )


class RuntimeEasyLoggerHelpersSharedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        cls.profile_libraries: dict[int, EasyLoggerLibrary] = {}

        for profile in (PROFILE_MAIN, PROFILE_BOOT):
            output = temporary / library_name(f"easylogger_helpers_{profile}")
            command = [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                f"-DOPEN_CFW_EASYLOGGER_HELPERS_PROFILE={profile}",
                str(HOST_FIXTURE),
            ]
            subprocess.run(
                finish_library_command(command, output),
                check=True,
                capture_output=True,
                text=True,
            )
            cls.profile_libraries[profile] = EasyLoggerLibrary(
                ctypes.CDLL(str(output))
            )

        oracle_output = temporary / library_name("easylogger_helpers_oracle")
        oracle_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(UPSTREAM_HEADER.parent),
            str(ORACLE_FIXTURE),
        ]
        subprocess.run(
            finish_library_command(oracle_command, oracle_output),
            check=True,
            capture_output=True,
            text=True,
        )
        cls.oracle = OracleLibrary(ctypes.CDLL(str(oracle_output)))

        cls.target_objects: dict[tuple[str, str], Path] = {}
        for profile_name, profile in TARGET_PROFILES.items():
            for leaf_name in LEAVES:
                output = temporary / f"{profile_name}-{leaf_name}.o"
                command = [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *profile["flags"],
                    *TARGET_COMMON_FLAGS,
                    (
                        "-DOPEN_CFW_EASYLOGGER_HELPERS_PROFILE="
                        f"{profile['profile']}"
                    ),
                    "-DOPEN_CFW_EASYLOGGER_HELPERS_BUILD_LEAF",
                    f"-DOPEN_CFW_EASYLOGGER_HELPERS_LEAF_{leaf_name}",
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(output),
                ]
                subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                cls.target_objects[(profile_name, leaf_name)] = output

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        for library in self.profile_libraries.values():
            library.reset()
        self.oracle.reset()

    def compare_copy(
        self,
        library: EasyLoggerLibrary,
        current_length: int,
        source_length: int,
    ) -> None:
        payload = bytes((index % 251) + 1 for index in range(source_length))
        source = ctypes.create_string_buffer(payload + b"\0")
        destination_type = ctypes.c_ubyte * 1100
        actual_destination = destination_type(*([0xA5] * 1100))
        oracle_destination = destination_type(*([0xA5] * 1100))

        actual = library.strcpy(
            current_length,
            actual_destination,
            source,
        )
        expected = self.oracle.strcpy(
            current_length,
            oracle_destination,
            source,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(
            bytes(actual_destination),
            bytes(oracle_destination),
        )

    def test_authenticated_upstream_and_adaptation_are_hash_pinned(
        self,
    ) -> None:
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(sha256(HEADER), HEADER_SHA256)
        for path, expected in UPSTREAM_SHA256.items():
            with self.subTest(path=path.name):
                self.assertEqual(sha256(path), expected)

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertEqual(
            provenance["upstream"]["selected_tree"],
            UPSTREAM_TREE,
        )
        self.assertEqual(
            provenance["selection"]["source_equivalent_core_blobs"],
            UPSTREAM_GIT_BLOBS,
        )
        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn(UPSTREAM_COMMIT, source)
        self.assertIn(UPSTREAM_COMMIT, header)
        self.assertIn(UPSTREAM_GIT_BLOBS["easylogger/src/elog.c"], header)
        self.assertIn(
            UPSTREAM_GIT_BLOBS["easylogger/src/elog_utils.c"],
            header,
        )

    def test_both_profiles_pin_g2_addresses_and_common_object_abi(
        self,
    ) -> None:
        for profile, expected_addresses in PROFILE_CONSTANTS.items():
            loaded = self.profile_libraries[profile].loaded
            observed = tuple(
                bind_noarg_u32(loaded, name)()
                for name in (
                    "open_cfw_test_easylogger_helpers_get_state_address",
                    "open_cfw_test_easylogger_helpers_get_assert_hook_address",
                    "open_cfw_test_easylogger_helpers_get_output_address",
                    "open_cfw_test_easylogger_helpers_get_assert_wait_address",
                )
            )
            self.assertEqual(observed, expected_addresses)
            self.assertEqual(
                bind_noarg_u32(
                    loaded,
                    "open_cfw_test_easylogger_helpers_get_profile",
                )(),
                profile,
            )
            self.assertEqual(
                tuple(
                    bind_noarg_u32(loaded, name)()
                    for name in (
                        "open_cfw_test_easylogger_helpers_"
                        "get_line_buffer_size",
                        "open_cfw_test_easylogger_helpers_get_level_count",
                        "open_cfw_test_easylogger_helpers_"
                        "get_tag_level_size",
                        "open_cfw_test_easylogger_helpers_get_tag_offset",
                        "open_cfw_test_easylogger_helpers_"
                        "get_tag_use_flag_offset",
                        "open_cfw_test_easylogger_helpers_get_logger_size",
                        "open_cfw_test_easylogger_helpers_"
                        "get_enabled_format_offset",
                    )
                ),
                (1024, 6, 0x21, 0x01, 0x20, 0xF8, 0xD8),
            )

    def test_strcpy_matches_upstream_across_every_buffer_position(
        self,
    ) -> None:
        for profile, library in self.profile_libraries.items():
            for current_length in range(1027):
                for source_length in (0, 1, 3, 17):
                    with self.subTest(
                        profile=profile,
                        current_length=current_length,
                        source_length=source_length,
                    ):
                        self.compare_copy(
                            library,
                            current_length,
                            source_length,
                        )

    def test_strcpy_matches_upstream_for_bounded_lengths_and_wrap_edge(
        self,
    ) -> None:
        for profile, library in self.profile_libraries.items():
            for current_length in (0, 1, 1022, 1023, 1024, 1025, 0xFFFFFFFF):
                for source_length in range(65):
                    with self.subTest(
                        profile=profile,
                        current_length=current_length,
                        source_length=source_length,
                    ):
                        self.compare_copy(
                            library,
                            current_length,
                            source_length,
                        )

    def test_get_fmt_matches_upstream_exhaustively_for_low_byte_domain(
        self,
    ) -> None:
        for profile, library in self.profile_libraries.items():
            library.reset()
            self.oracle.reset()
            for level in range(6):
                for enabled in range(256):
                    library.set_format(level, enabled)
                    self.oracle.set_format(level, enabled)
                    for requested in range(256):
                        actual = library.get_fmt(level, requested)
                        expected = self.oracle.get_fmt(level, requested)
                        self.assertEqual(
                            actual,
                            expected,
                            (
                                profile,
                                level,
                                enabled,
                                requested,
                            ),
                        )

    def test_get_fmt_matches_upstream_for_32_bit_edges(self) -> None:
        values = (
            0,
            1,
            2,
            0x80,
            0x100,
            0x80000000,
            0xFFFFFFFF,
            0x55555555,
            0xAAAAAAAA,
        )
        for profile, library in self.profile_libraries.items():
            for level in range(6):
                for enabled in values:
                    library.set_format(level, enabled)
                    self.oracle.set_format(level, enabled)
                    for requested in values:
                        with self.subTest(
                            profile=profile,
                            level=level,
                            enabled=enabled,
                            requested=requested,
                        ):
                            self.assertEqual(
                                library.get_fmt(level, requested),
                                self.oracle.get_fmt(level, requested),
                            )

    def test_argument_predicates_match_upstream_and_short_circuit(
        self,
    ) -> None:
        pointer = ctypes.create_string_buffer(b"x")
        sets = (0, 1, 0x80, 0x100, 0x80000000, 0xFFFFFFFF)
        for profile, library in self.profile_libraries.items():
            for level in range(6):
                for enabled in sets:
                    library.set_format(level, enabled)
                    self.oracle.set_format(level, enabled)
                    for requested in sets:
                        for argument in (0, 1, 0xFFFFFFFF):
                            self.assertEqual(
                                library.get_fmt_u32(
                                    level,
                                    requested,
                                    argument,
                                ),
                                self.oracle.get_fmt_u32(
                                    level,
                                    requested,
                                    argument,
                                ),
                            )
                        for argument in (None, pointer):
                            self.assertEqual(
                                library.get_fmt_ptr(
                                    level,
                                    requested,
                                    argument,
                                ),
                                self.oracle.get_fmt_ptr(
                                    level,
                                    requested,
                                    argument,
                                ),
                            )

            library.reset()
            self.oracle.reset()
            self.assertEqual(library.get_fmt_u32(0xFF, 1, 0), 0)
            self.assertEqual(self.oracle.get_fmt_u32(0xFF, 1, 0), 0)
            self.assertEqual(library.get_fmt_ptr(0xFF, 1, None), 0)
            self.assertEqual(self.oracle.get_fmt_ptr(0xFF, 1, None), 0)
            self.assertEqual(library.assert_count(), 0)
            self.assertEqual(self.oracle.assert_count(), 0)

    def test_recovered_assertion_lines_and_order_are_explicit(self) -> None:
        for profile, library in self.profile_libraries.items():
            for destination, source, line in (
                (None, b"x", 44),
                (ctypes.create_string_buffer(8), None, 45),
                (None, None, 44),
            ):
                library.reset()
                self.oracle.reset()
                copied = ctypes.c_uint32(0xFFFFFFFF)
                oracle_copied = ctypes.c_uint32(0xFFFFFFFF)
                self.assertEqual(
                    library.trapped_strcpy(
                        0,
                        destination,
                        source,
                        ctypes.byref(copied),
                    ),
                    1,
                )
                self.assertEqual(
                    self.oracle.trapped_strcpy(
                        0,
                        destination,
                        source,
                        ctypes.byref(oracle_copied),
                    ),
                    1,
                )
                self.assertEqual(library.assert_count(), 1)
                self.assertEqual(self.oracle.assert_count(), 1)
                self.assertEqual(library.assert_line(), line)
                self.assertEqual(self.oracle.assert_line(), line)

            for level in (6, 0xFF):
                library.reset()
                self.oracle.reset()
                enabled = ctypes.c_uint32(0xFFFFFFFF)
                oracle_enabled = ctypes.c_uint32(0xFFFFFFFF)
                self.assertEqual(
                    library.trapped_get_fmt(
                        level,
                        1,
                        ctypes.byref(enabled),
                    ),
                    1,
                )
                self.assertEqual(
                    self.oracle.trapped_get_fmt(
                        level,
                        1,
                        ctypes.byref(oracle_enabled),
                    ),
                    1,
                )
                self.assertEqual(library.assert_count(), 1)
                self.assertEqual(self.oracle.assert_count(), 1)
                self.assertEqual(library.assert_line(), 743)
                self.assertEqual(
                    self.oracle.assert_line(),
                    735,
                    "pristine snapshot line differs from recovered G2 line",
                )

    def test_each_target_leaf_has_only_reviewed_call_seams(self) -> None:
        for (profile, leaf_name), object_path in self.target_objects.items():
            data, sections = self.apollo_overlay.parse_elf32(object_path)
            symbol_table = self.apollo_overlay.section_named(
                sections,
                ".symtab",
            )
            string_table = sections[int(symbol_table["link"])]
            strings = data[
                int(string_table["offset"]):
                int(string_table["offset"]) + int(string_table["size"])
            ]
            symbols = []
            for index in range(int(symbol_table["size"]) // 16):
                fields = struct.unpack_from(
                    "<IIIBBH",
                    data,
                    int(symbol_table["offset"]) + index * 16,
                )
                name = self.apollo_overlay.elf_string(
                    strings,
                    fields[0],
                    "symbol",
                )
                symbols.append((name, fields))

            function_name, expected_undefined = LEAVES[leaf_name]
            function = next(
                fields for name, fields in symbols if name == function_name
            )
            function_section = sections[int(function[5])]
            self.assertEqual(
                function_section["name"],
                f".text.{function_name}",
            )

            defined_functions = {
                name
                for name, fields in symbols
                if name and fields[3] & 0x0F == 2 and fields[5] != 0
            }
            undefined = {
                name
                for name, fields in symbols
                if name and fields[5] == 0
            }
            self.assertEqual(defined_functions, {function_name})
            self.assertEqual(undefined, expected_undefined)

            relocations = []
            for section in sections:
                if (
                    int(section["type"]) == 9
                    and int(section["info"]) == int(function_section["index"])
                ):
                    for index in range(int(section["size"]) // 8):
                        offset, information = struct.unpack_from(
                            "<II",
                            data,
                            int(section["offset"]) + index * 8,
                        )
                        relocations.append(
                            (
                                offset,
                                information & 0xFF,
                                symbols[information >> 8][0],
                            )
                        )
            self.assertEqual(
                {relocation_type for _, relocation_type, _ in relocations},
                {10},
                (profile, leaf_name, relocations),
            )
            self.assertEqual(
                {symbol for _, _, symbol in relocations},
                expected_undefined,
            )
            self.assertFalse(
                any(
                    section["name"].startswith(".rodata")
                    and int(section["size"]) != 0
                    for section in sections
                )
            )

    def test_profile_and_leaf_selection_fail_closed(self) -> None:
        base_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            *TARGET_PROFILES["main"]["flags"],
            *TARGET_COMMON_FLAGS,
            "-fsyntax-only",
            str(SOURCE),
        ]
        missing_profile = subprocess.run(
            base_command,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(missing_profile.returncode, 0)
        self.assertIn(
            "select an explicit G2 EasyLogger image profile",
            missing_profile.stderr,
        )

        no_leaf = subprocess.run(
            [
                *base_command[:-1],
                "-DOPEN_CFW_EASYLOGGER_HELPERS_PROFILE=1",
                "-DOPEN_CFW_EASYLOGGER_HELPERS_BUILD_LEAF",
                str(SOURCE),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(no_leaf.returncode, 0)
        self.assertIn(
            "select exactly one EasyLogger helper leaf",
            no_leaf.stderr,
        )

        two_leaves = subprocess.run(
            [
                *base_command[:-1],
                "-DOPEN_CFW_EASYLOGGER_HELPERS_PROFILE=1",
                "-DOPEN_CFW_EASYLOGGER_HELPERS_BUILD_LEAF",
                "-DOPEN_CFW_EASYLOGGER_HELPERS_LEAF_STRCPY",
                "-DOPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_ENABLED",
                str(SOURCE),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(two_leaves.returncode, 0)
        self.assertIn(
            "select exactly one EasyLogger helper leaf",
            two_leaves.stderr,
        )


if __name__ == "__main__":
    unittest.main()
