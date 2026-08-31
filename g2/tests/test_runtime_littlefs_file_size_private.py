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
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_littlefs_file_size_private.c"
)
HEADER = SOURCE.with_suffix(".h")
LITTLEFS_SOURCE = ROOT / "third_party" / "littlefs" / "lfs.c"
LITTLEFS_HEADER = ROOT / "third_party" / "littlefs" / "lfs.h"
LITTLEFS_UTIL_SOURCE = ROOT / "third_party" / "littlefs" / "lfs_util.c"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY = SOURCE.parent / "overlay.json"
MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"

BASE = 0x0043_8000
START = 0x004C_E472
END = 0x004C_E48A
MAX_ADDRESS = 0x004C_A6F8
PACKAGE_PREAMBLE = 32
LFS_F_WRITING = 0x0002_0000
FUNCTION = "open_cfw_littlefs_file_size_private"
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
OVERLAY_RUNTIME_BASE = 0x0079_4324

PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740f"
    "d3e7027730c26a9094eca47268a27863"
)
PAYLOAD_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
STOCK_BYTES = bytes.fromhex(
    "80b50800016b890304d5c16a406bfcf73af900e0c06a02bd"
)
STOCK_SHA256 = (
    "98ba58dac7de35e47c75240c0671b11e"
    "6b403a1bffed50a617c6543eb26a83cc"
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_SOURCE_SHA256 = (
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398"
)
UPSTREAM_HEADER_SHA256 = (
    "ee44e99d6b19119b3e577b969b80c9d"
    "5e6f96410c9593794afddf6d4b314c486"
)
UPSTREAM_UTIL_SHA256 = (
    "f2fbde533670560434bd9f5a547174cc"
    "7c5a4670a02c47b4bd85180dced8b2ec"
)

SOURCE_SHA256 = (
    "149094dca037bf50fd389b146446cc55"
    "babac0bfa011cf2429688838f94626fb"
)
HEADER_SHA256 = (
    "3afdf02b583c7b81b5d31d599043f3a8"
    "b606d0dbcc3251abb5384a1be9a414c1"
)
TARGET_TEXT_SIZE = 20
TARGET_TEXT_SHA256 = (
    "1edf2a8aae0009f5fca77cb8ba1430c2"
    "bfa7e52181c4620841450cbc2cbb3683"
)
TARGET_TEXT_HEX = "91f8320080075cbfc86a7047486bc96afff7febf"
TARGET_RELOCATIONS = [(16, 30, "open_cfw_littlefs_util_max")]

PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.33.1)",
        "placement": 124_336,
        "relocated_sha256": (
            "d4cc044bcd8d14e246fe1626c70814ea"
            "2d37f47f32290852aa47efc460241a43"
        ),
        "overlay": (
            360_578,
            "6f1f38ff89e350a1e104f09fd9278056ac6b8884d0bc21c8357c845ba82035a7",
        ),
        "component": (
            3_883_974,
            "a3d36ad784519c7193976e1bbfe1b5dc7c6a07fd3bba185166e12fce2a0f19d9",
        ),
        "stage_overlay": (
            360_578,
            "6f1f38ff89e350a1e104f09fd9278056ac6b8884d0bc21c8357c845ba82035a7",
        ),
        "stage_component": (
            3_883_974,
            "71d4e2b8011cc1e7503bdbe9e7251963f04b0092a80934d00e5a5ad181c651eb",
        ),
        "component_accounting": {
            "generated_patch_site_bytes": 397_446,
            "generated_wrapper_bytes": 32,
            "opaque_base_bytes": 3_123_534,
            "replaced_stock_function_bytes": 397_626,
            "source_owned_bytes": 362_962,
            "source_owned_in_place_bytes": 184,
        },
        "package": (
            4_677_046,
            "46733920d307a3830513b7f492de5345f552e27de65679eb4fde2b54dfca4ab4",
        ),
        "patch": (
            "e4f22fba00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf",
            "f9766969393fd2ad67f0182de711d93054fb8eecb153e6d4a2618750c2bd2adb",
        ),
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "placement": 126_156,
        "relocated_sha256": (
            "74544bcbc851e0164d33575a42b8fe3d"
            "9270ff4fc25b056fd7dc743a7410fc72"
        ),
        "overlay": (
            152_912,
            "e045351065be7c01ff3bc4666940e0b536c2b114df0681169bd37031139d7c20",
        ),
        "component": (
            3_676_308,
            "dc726a1c6187357c6c9a6b39152957bf3772fa06bc30d8bdd6db662af7c3dee7",
        ),
        "stage_overlay": (
            145_314,
            "2bea2be98b0154fa117e9a6e6cedc61a41c7b980279398657af3722cb96c8c19",
        ),
        "stage_component": (
            3_668_710,
            "dc7f8a490c731da02850abec1d214f59c79c55062379f5100199e9999e5b28e8",
        ),
        "component_accounting": {
            "generated_patch_site_bytes": 99_340,
            "generated_wrapper_bytes": 32,
            "opaque_base_bytes": 3_423_840,
            "replaced_stock_function_bytes": 99_520,
            "source_owned_bytes": 145_498,
            "source_owned_in_place_bytes": 184,
        },
        "package": (
            4_469_364,
            "79e0ecab05996ac4d1bd71483b1045544a9bdc767abb6bff51a2cc700f89333e",
        ),
        "patch": (
            "e4f2bdbd00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf",
            "faa50b6a896129aef410f74f4f4c333bc32f2e0d5604ed939d3cc6bd7519ae3a",
        ),
    },
}

# Exact byte ownership within the five retained non-main container wrappers.
# Their 268 bytes refine into 17 authenticated source bytes, 167 generated
# metadata/checksum bytes, and 84 opaque vendor bytes.
CANONICAL_CONTAINER_REFINEMENT = (17, 167, 84)

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
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-fno-ident",
]

CANDIDATE_HARNESS = r"""
#include <stddef.h>
#include <stdint.h>

#include "runtime_littlefs_file_size_private.h"

static struct open_cfw_littlefs_file_size_private_file candidate_file;
static uint32_t candidate_max_calls;
static uint32_t candidate_max_a;
static uint32_t candidate_max_b;

open_cfw_littlefs_file_size_private_u32 open_cfw_littlefs_util_max(
    open_cfw_littlefs_file_size_private_u32 a,
    open_cfw_littlefs_file_size_private_u32 b
)
{
    candidate_max_calls += 1U;
    candidate_max_a = a;
    candidate_max_b = b;
    return (a > b) ? a : b;
}

void candidate_reset(
    uint8_t pattern,
    uint32_t flags,
    uint32_t position,
    uint32_t size
)
{
    uint8_t *bytes = (uint8_t *)(void *)&candidate_file;
    size_t index;

    for (index = 0U; index < sizeof(candidate_file); ++index) {
        bytes[index] = pattern;
    }
    candidate_file.flags = flags;
    candidate_file.position = position;
    candidate_file.ctz.size = size;
    candidate_max_calls = 0U;
    candidate_max_a = 0U;
    candidate_max_b = 0U;
}

int32_t candidate_call(uintptr_t lfs_address)
{
    return open_cfw_littlefs_file_size_private(
        (struct open_cfw_littlefs_file_size_private_lfs *)lfs_address,
        &candidate_file
    );
}

uint32_t candidate_checksum(void)
{
    const uint8_t *bytes = (const uint8_t *)(const void *)&candidate_file;
    uint32_t checksum = 2166136261U;
    size_t index;

    for (index = 0U; index < sizeof(candidate_file); ++index) {
        checksum ^= bytes[index];
        checksum *= 16777619U;
    }
    return checksum;
}

size_t candidate_file_size(void) { return sizeof(candidate_file); }
size_t candidate_cache_size(void)
{
    return sizeof(struct open_cfw_littlefs_file_size_private_cache);
}
size_t candidate_mdir_size(void)
{
    return sizeof(struct open_cfw_littlefs_file_size_private_mdir);
}
size_t candidate_ctz_size_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_file_size_private_file,
        ctz.size
    );
}
size_t candidate_flags_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_file_size_private_file,
        flags
    );
}
size_t candidate_position_offset(void)
{
    return offsetof(
        struct open_cfw_littlefs_file_size_private_file,
        position
    );
}
uint32_t candidate_max_call_count(void) { return candidate_max_calls; }
uint32_t candidate_max_left(void) { return candidate_max_a; }
uint32_t candidate_max_right(void) { return candidate_max_b; }
"""

ORACLE_HARNESS = r"""
#include <stddef.h>
#include <stdint.h>

#include "lfs.c"
#include "lfs_util.c"

static lfs_file_t oracle_file;

void oracle_reset(
    uint8_t pattern,
    uint32_t flags,
    uint32_t position,
    uint32_t size
)
{
    uint8_t *bytes = (uint8_t *)(void *)&oracle_file;
    size_t index;

    for (index = 0U; index < sizeof(oracle_file); ++index) {
        bytes[index] = pattern;
    }
    oracle_file.flags = flags;
    oracle_file.pos = position;
    oracle_file.ctz.size = size;
}

int32_t oracle_call(uintptr_t lfs_address)
{
    return lfs_file_size_((lfs_t *)lfs_address, &oracle_file);
}

uint32_t oracle_checksum(void)
{
    const uint8_t *bytes = (const uint8_t *)(const void *)&oracle_file;
    uint32_t checksum = 2166136261U;
    size_t index;

    for (index = 0U; index < sizeof(oracle_file); ++index) {
        checksum ^= bytes[index];
        checksum *= 16777619U;
    }
    return checksum;
}

size_t oracle_file_size(void) { return sizeof(oracle_file); }
size_t oracle_cache_size(void) { return sizeof(lfs_cache_t); }
size_t oracle_mdir_size(void) { return sizeof(lfs_mdir_t); }
size_t oracle_ctz_size_offset(void) { return offsetof(lfs_file_t, ctz.size); }
size_t oracle_flags_offset(void) { return offsetof(lfs_file_t, flags); }
size_t oracle_position_offset(void) { return offsetof(lfs_file_t, pos); }
"""


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


class RuntimeLittlefsFileSizePrivateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-littlefs-file-size-private-",
            dir=temporary_parent,
        )
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        matches = [
            profile
            for profile, pins in PROFILE_PINS.items()
            if (cls.clang, version) == (pins["compiler"], pins["version"])
        ]
        if len(matches) != 1:
            raise AssertionError(
                f"unreviewed compiler: {(cls.clang, version)!r}"
            )
        cls.profile = matches[0]
        cls.pins = PROFILE_PINS[cls.profile]

        candidate_harness = temporary / "candidate_harness.c"
        candidate_harness.write_text(
            textwrap.dedent(CANDIDATE_HARNESS),
            encoding="utf-8",
        )
        oracle_harness = temporary / "oracle_harness.c"
        oracle_harness.write_text(
            textwrap.dedent(ORACLE_HARNESS),
            encoding="utf-8",
        )

        cls.candidate = cls.compile_library(
            temporary / "candidate",
            [SOURCE, candidate_harness],
            ["-I", str(SOURCE.parent)],
        )
        cls.oracle = cls.compile_library(
            temporary / "oracle",
            [oracle_harness],
            ["-I", str(LITTLEFS_SOURCE.parent)],
        )
        cls.bind_common(cls.candidate, "candidate")
        cls.bind_common(cls.oracle, "oracle")
        for name in (
            "candidate_max_call_count",
            "candidate_max_left",
            "candidate_max_right",
        ):
            function = getattr(cls.candidate, name)
            function.argtypes = []
            function.restype = ctypes.c_uint32

        cls.target_object = temporary / "file_size_private.o"
        subprocess.run(
            [
                cls.clang,
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
        cls.read_target_object()

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        import open_cfw

        cls.apollo_overlay = apollo_overlay
        cls.open_cfw = open_cfw
        cls.overlay_output = temporary / "production-overlay"
        stage_config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        stage_config["expected"] = stage_config["core_stage_expected"]
        for profile in stage_config.get("toolchain_profiles", {}).values():
            if "core_stage_expected" in profile:
                profile["expected"] = profile["core_stage_expected"]
        stage_config_path = temporary / "main-stage-overlay.json"
        stage_config_path.write_text(
            json.dumps(stage_config, indent=2) + "\n",
            encoding="utf-8",
        )
        cls.component_report = apollo_overlay.build(
            root=ROOT,
            config_path=stage_config_path,
            output_dir=cls.overlay_output,
            clang=cls.clang,
            toolchain_profile=cls.profile,
        )

    @classmethod
    def compile_library(
        cls,
        stem: Path,
        sources: list[Path],
        extra_flags: list[str],
    ) -> ctypes.CDLL:
        library = stem.with_suffix(".dylib" if sys.platform == "darwin" else ".so")
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            *extra_flags,
            *(str(source) for source in sources),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        return ctypes.CDLL(str(library))

    @staticmethod
    def bind_common(library: ctypes.CDLL, prefix: str) -> None:
        reset = getattr(library, prefix + "_reset")
        reset.argtypes = [
            ctypes.c_uint8,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        reset.restype = None
        call = getattr(library, prefix + "_call")
        call.argtypes = [ctypes.c_size_t]
        call.restype = ctypes.c_int32
        checksum = getattr(library, prefix + "_checksum")
        checksum.argtypes = []
        checksum.restype = ctypes.c_uint32
        for suffix in (
            "file_size",
            "cache_size",
            "mdir_size",
            "ctz_size_offset",
            "flags_offset",
            "position_offset",
        ):
            function = getattr(library, prefix + "_" + suffix)
            function.argtypes = []
            function.restype = ctypes.c_size_t

    @classmethod
    def read_target_object(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(cls.target_object)
        text = apollo_overlay.section_named(
            sections,
            ".text.open_cfw_littlefs_file_size_private",
        )
        cls.target_text = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        cls.parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(strings, fields[0], "symbol")
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields
            for name, fields in cls.parsed_symbols
            if name
        }
        cls.text_relocations = []
        for section in sections:
            if int(section["type"]) != 9 or int(section["info"]) != int(text["index"]):
                continue
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    data,
                    int(section["offset"]) + index * 8,
                )
                cls.text_relocations.append(
                    (
                        offset,
                        information & 0xFF,
                        cls.parsed_symbols[information >> 8][0],
                    )
                )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    def reset_both(
        self,
        pattern: int,
        flags: int,
        position: int,
        size: int,
    ) -> None:
        self.candidate.candidate_reset(pattern, flags, position, size)
        self.oracle.oracle_reset(pattern, flags, position, size)

    def coarse_ownership(
        self,
        merged_manifest: dict[str, object],
        profile: str,
    ) -> tuple[int, int, int]:
        status_bytes: dict[str, int] = {}
        provider_bytes = 0
        for component in merged_manifest["components"]:
            provider = component["provider"]
            selected_provider = (
                self.open_cfw.profile_pins(provider, profile) or provider
            )
            component_size = int(selected_provider["size"])
            provider_bytes += component_size
            regions = self.open_cfw.effective_component_regions(
                component,
                component_size,
                profile,
            )
            for region in regions:
                status = region["address_status"]
                status_bytes[status] = (
                    status_bytes.get(status, 0) + region["size"]
                )

        package_size = PROFILE_PINS[profile]["package"][0]
        package_envelope_bytes = package_size - provider_bytes
        main = next(
            component
            for component in merged_manifest["components"]
            if component["name"] == "apollo_main"
        )
        main_preamble_bytes = next(
            region["size"]
            for region in main["regions"]
            if region["name"] == "ota_preamble"
        )
        source_bytes = status_bytes["source_compiled"]
        generated_bytes = (
            sum(
                size
                for status, size in status_bytes.items()
                if status.startswith("generated_")
            )
            + package_envelope_bytes
            + main_preamble_bytes
        )
        return (
            source_bytes,
            generated_bytes,
            package_size - source_bytes - generated_bytes,
        )

    def test_recovered_abi_matches_pristine_upstream(self) -> None:
        for suffix in (
            "file_size",
            "cache_size",
            "mdir_size",
            "ctz_size_offset",
            "flags_offset",
            "position_offset",
        ):
            self.assertEqual(
                getattr(self.candidate, "candidate_" + suffix)(),
                getattr(self.oracle, "oracle_" + suffix)(),
                suffix,
            )
        self.assertEqual(self.candidate.candidate_mdir_size(), 0x20)

    def test_writing_and_nonwriting_states_match_upstream_oracle(self) -> None:
        edge_values = (
            0x0000_0000,
            0x0000_0001,
            0x7FFF_FFFF,
            0x8000_0000,
            0xFFFF_FFFF,
        )
        cases = [
            (pattern, flags, position, size)
            for pattern in (0x00, 0x5A, 0xFF)
            for flags in (
                0,
                1,
                0x0001_0000,
                LFS_F_WRITING,
                LFS_F_WRITING | 0x0010_0000,
                0xFFFF_FFFF,
            )
            for position in edge_values
            for size in edge_values
        ]
        randomizer = random.Random(0x4C_E472)
        cases.extend(
            (
                randomizer.randrange(256),
                randomizer.getrandbits(32),
                randomizer.getrandbits(32),
                randomizer.getrandbits(32),
            )
            for _ in range(512)
        )

        for pattern, flags, position, size in cases:
            with self.subTest(
                pattern=pattern,
                flags=flags,
                position=position,
                size=size,
            ):
                self.reset_both(pattern, flags, position, size)
                candidate_before = self.candidate.candidate_checksum()
                oracle_before = self.oracle.oracle_checksum()
                self.assertEqual(candidate_before, oracle_before)

                candidate_result = self.candidate.candidate_call(0x1234_5678)
                oracle_result = self.oracle.oracle_call(0x1234_5678)
                self.assertEqual(candidate_result, oracle_result)
                expected_u32 = (
                    max(position, size)
                    if flags & LFS_F_WRITING
                    else size
                )
                self.assertEqual(
                    candidate_result,
                    ctypes.c_int32(expected_u32).value,
                )
                self.assertEqual(
                    self.candidate.candidate_max_call_count(),
                    1 if flags & LFS_F_WRITING else 0,
                )
                if flags & LFS_F_WRITING:
                    self.assertEqual(
                        (
                            self.candidate.candidate_max_left(),
                            self.candidate.candidate_max_right(),
                        ),
                        (position, size),
                    )
                self.assertEqual(
                    self.candidate.candidate_checksum(),
                    candidate_before,
                )
                self.assertEqual(self.oracle.oracle_checksum(), oracle_before)

    def test_target_object_is_single_reviewed_helper_closure(self) -> None:
        function = self.symbols["open_cfw_littlefs_file_size_private"]
        self.assertEqual((function[1], function[2]), (1, TARGET_TEXT_SIZE))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertNotEqual(function[5], 0)
        self.assertEqual(len(self.target_text), TARGET_TEXT_SIZE)
        self.assertEqual(self.target_text.hex(), TARGET_TEXT_HEX)
        self.assertEqual(sha256(self.target_text), TARGET_TEXT_SHA256)
        self.assertEqual(self.text_relocations, TARGET_RELOCATIONS)
        helper = self.symbols["open_cfw_littlefs_util_max"]
        self.assertEqual(helper[3] & 0x0F, 0)
        self.assertEqual(helper[5], 0)
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            ["open_cfw_littlefs_util_max"],
        )
        self.assertEqual(
            {
                name
                for name, fields in self.symbols.items()
                if fields[3] & 0x0F == 2 and fields[5] != 0
            },
            {"open_cfw_littlefs_file_size_private"},
        )

    def test_source_and_authenticated_upstream_are_pinned(self) -> None:
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(sha256(HEADER), HEADER_SHA256)
        self.assertEqual(sha256(LITTLEFS_SOURCE), UPSTREAM_SOURCE_SHA256)
        self.assertEqual(sha256(LITTLEFS_HEADER), UPSTREAM_HEADER_SHA256)
        self.assertEqual(sha256(LITTLEFS_UTIL_SOURCE), UPSTREAM_UTIL_SHA256)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "lfs_file_size_()",
            "littlefs v2.10.1",
            UPSTREAM_COMMIT,
            "[0x004CE472, 0x004CE48A)",
            "LFS_READONLY is",
            "open_cfw_littlefs_util_max",
            "file->position",
            "file->ctz.size",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_LITTLEFS_FILE_SIZE_PRIVATE_WRITING = 0x00020000U",
            "OPEN_CFW_LITTLEFS_FILE_SIZE_PRIVATE_MAX_ADDRESS = 0x004CA6F8U",
            "ctz.size\n    ) == 0x2CU",
            "flags\n    ) == 0x30U",
            "position\n    ) == 0x34U",
        ):
            self.assertIn(token, header)

    def test_production_registration_patch_and_aggregate_pins_are_exact(
        self,
    ) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = [
            item
            for item in config["relocated_leaves"]
            if item["function"] == FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        self.assertEqual(config["functions"].count(FUNCTION), 1)
        leaf = leaves[0]
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual(
            leaf["source"],
            {
                "path": SOURCE_PATH,
                "size": SOURCE.stat().st_size,
                "sha256": SOURCE_SHA256,
                "license": "BSD-3-Clause",
                "origin": (
                    "bounded freestanding adaptation of authenticated "
                    "littlefs v2.10.1 lfs_file_size_ using the recovered "
                    "32-bit lfs_file_t ABI and source-owned lfs_max"
                ),
                "upstream": (
                    "https://github.com/littlefs-project/littlefs/blob/"
                    f"{UPSTREAM_COMMIT}/lfs.c"
                ),
                "upstream_commit": UPSTREAM_COMMIT,
                "evidence": (
                    "docs/research/littlefs-file-size-source-audit.md"
                ),
            },
        )
        self.assertEqual(leaf["toolchain"]["target"], TARGET_FLAGS[0][9:])
        self.assertEqual(leaf["toolchain"]["flags"], TARGET_FLAGS[1:])
        self.assertNotIn("closure", leaf)

        relocation_pin = [{
            "offset": 16,
            "type": "R_ARM_THM_JUMP24",
            "symbol": "open_cfw_littlefs_util_max",
            "symbol_type": "STT_NOTYPE",
            "target_function": "open_cfw_littlefs_util_max",
        }]
        for profile, pins in PROFILE_PINS.items():
            expected = (
                leaf["expected"]
                if profile == "apple-clang"
                else leaf["toolchain_profiles"][profile]["expected"]
            )
            relocations = (
                leaf["relocations"]
                if profile == "apple-clang"
                else leaf["toolchain_profiles"][profile]["relocations"]
            )
            self.assertEqual(
                expected,
                {
                    "size": TARGET_TEXT_SIZE,
                    "sha256": pins["relocated_sha256"],
                    "alignment": 4,
                    "offset": pins["placement"],
                    "unrelocated_sha256": TARGET_TEXT_SHA256,
                },
            )
            self.assertEqual(relocations, relocation_pin)
            aggregate = (
                config["expected"]
                if profile == "apple-clang"
                else config["toolchain_profiles"][profile]["expected"]
            )
            self.assertEqual(
                (aggregate["overlay_size"], aggregate["overlay_sha256"]),
                pins["overlay"],
            )
            self.assertEqual(
                (
                    aggregate["component_size"],
                    aggregate["component_sha256"],
                ),
                pins["component"],
            )
            replacement = bytes.fromhex(pins["patch"][0])
            self.assertEqual(len(replacement), END - START)
            self.assertEqual(sha256(replacement), pins["patch"][1])
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    START,
                    replacement[:4],
                    link=False,
                ),
                OVERLAY_RUNTIME_BASE + pins["placement"],
            )
            self.assertEqual(replacement[4:], b"\x00\xbf" * 10)

        patches = [
            item
            for item in config["patch_sites"]
            if item.get("target_function") == FUNCTION
        ]
        self.assertEqual(
            patches,
            [{
                "name": "replace_littlefs_file_size_private",
                "runtime_address": START,
                "expected_size": END - START,
                "expected_sha256": STOCK_SHA256,
                "branch": "b_w",
                "target_function": FUNCTION,
            }],
        )
        registration_text = (
            OVERLAY.read_text(encoding="utf-8")
            + MANIFEST.read_text(encoding="utf-8")
        )
        self.assertNotIn("littlefs_file_size_private_candidate", registration_text)

        report = self.component_report
        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            self.pins["stage_overlay"],
        )
        component = report["component"]
        self.assertEqual(
            (component["size"], component["sha256"]),
            self.pins["stage_component"],
        )
        for key, value in self.pins["component_accounting"].items():
            self.assertEqual(component[key], value, key)

        extracted = next(
            item
            for item in report["relocated_leaves"]
            if item["extraction"]["function"] == FUNCTION
        )
        runtime = OVERLAY_RUNTIME_BASE + self.pins["placement"]
        self.assertEqual(
            extracted["placement"],
            {
                "offset": self.pins["placement"],
                "runtime_address": runtime,
                "runtime_address_hex": f"0x{runtime:08X}",
                "size": TARGET_TEXT_SIZE,
                "alignment": 4,
                "padding_before": 0,
            },
        )
        extraction = extracted["extraction"]
        self.assertEqual(extraction["sha256"], self.pins["relocated_sha256"])
        self.assertEqual(extraction["unrelocated_sha256"], TARGET_TEXT_SHA256)
        self.assertEqual(extraction["relocation_count"], 1)
        relocation = extraction["relocations"][0]
        self.assertEqual(
            {
                key: relocation[key]
                for key in (
                    "offset",
                    "type",
                    "type_id",
                    "symbol",
                    "symbol_type",
                    "target_function",
                )
            },
            {
                "offset": 16,
                "type": "R_ARM_THM_JUMP24",
                "type_id": 30,
                "symbol": "open_cfw_littlefs_util_max",
                "symbol_type": "STT_NOTYPE",
                "target_function": "open_cfw_littlefs_util_max",
            },
        )
        max_offset = report["overlay"]["functions"][
            "open_cfw_littlefs_util_max"
        ]["offset"]
        self.assertEqual(
            relocation["target_address"],
            OVERLAY_RUNTIME_BASE + max_offset,
        )

        patch = next(
            item
            for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_littlefs_file_size_private"
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(
            (replacement.hex(), sha256(replacement)),
            self.pins["patch"],
        )
        self.assertEqual(patch["target_address"], runtime)
        component_bytes = (
            self.overlay_output / "ota_s200_firmware_ota.bin"
        ).read_bytes()
        patch_offset = PACKAGE_PREAMBLE + START - BASE
        self.assertEqual(
            component_bytes[patch_offset:patch_offset + len(replacement)],
            replacement,
        )
        self.assertEqual(
            component_bytes[patch_offset - 8:patch_offset],
            b"\x00\xbf" * 4,
        )
        self.assertNotEqual(
            component_bytes[patch_offset - 8:patch_offset],
            self.package[patch_offset - 8:patch_offset],
        )
        self.assertEqual(
            component_bytes[
                patch_offset + len(replacement):
                patch_offset + len(replacement) + 8
            ],
            self.package[
                patch_offset + len(replacement):
                patch_offset + len(replacement) + 8
            ],
        )

    def test_production_manifest_tiling_tail_and_coarse_ownership_are_exact(
        self,
    ) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        regions = main["regions"]
        self.assertGreater(len(regions), 0)
        self.assertEqual(regions[0]["file_offset"], 0)
        for left, right in zip(regions, regions[1:]):
            self.assertEqual(
                left["file_offset"] + left["size"],
                right["file_offset"],
            )
        provider = main["provider"]
        self.assertEqual(
            regions[-1]["file_offset"] + regions[-1]["size"],
            provider["size"],
        )
        accounting: dict[str, tuple[int, int]] = {}
        for status in {region["address_status"] for region in regions}:
            selected = [
                region
                for region in regions
                if region["address_status"] == status
            ]
            accounting[status] = (
                len(selected),
                sum(region["size"] for region in selected),
            )
        self.assertEqual(sum(count for count, _ in accounting.values()), len(regions))
        self.assertEqual(sum(size for _, size in accounting.values()), provider["size"])
        self.assertIn("official_blob", accounting)
        self.assertIn("source_compiled", accounting)

        by_name = {region["name"]: region for region in regions}
        self.assertEqual(
            by_name["littlefs_file_rewind_private_source_replacement"],
            {
                "name": "littlefs_file_rewind_private_source_replacement",
                "function": (
                    "Generated entry redirect and NOP fill replacing "
                    "littlefs v2.10.1 lfs_file_rewind_"
                ),
                "file_offset": 615_552,
                "size": 18,
                "target": "apollo510b_internal_mram",
                "target_address": 0x004C_E460,
                "address_status": "generated_source_entry_replacement",
                "output": (
                    "apollo510b/"
                    "source-entry-littlefs-file-rewind-private-0x004ce460.bin"
                ),
            },
        )
        self.assertEqual(
            by_name["littlefs_file_size_private_source_replacement"],
            {
                "name": "littlefs_file_size_private_source_replacement",
                "function": (
                    "Generated entry redirect and NOP fill replacing "
                    "littlefs v2.10.1 lfs_file_size_"
                ),
                "file_offset": 615_570,
                "size": END - START,
                "target": "apollo510b_internal_mram",
                "target_address": START,
                "address_status": "generated_source_entry_replacement",
                "output": (
                    "apollo510b/source-entry-littlefs-file-size-private-"
                    "0x004ce472.bin"
                ),
            },
        )
        self.assertEqual(
            by_name[
                "opaque_between_littlefs_file_size_private_and_tlsf"
            ]["file_offset"],
            615_594,
        )
        source_tail = by_name["apollo_littlefs_file_size_private_source_leaf"]
        self.assertIs(source_tail, regions[-2_686])
        self.assertEqual(
            source_tail["file_offset"] + source_tail["size"],
            regions[-2_685]["file_offset"],
        )
        self.assertEqual(
            source_tail,
            {
                "name": "apollo_littlefs_file_size_private_source_leaf",
                "function": (
                    "BSD-3-Clause littlefs v2.10.1 private file-size "
                    "source compatibility leaf"
                ),
                "file_offset": 3_647_732,
                "size": TARGET_TEXT_SIZE,
                "target": "apollo510b_internal_mram",
                "target_address": (
                    OVERLAY_RUNTIME_BASE
                    + PROFILE_PINS["apple-clang"]["placement"]
                ),
                "address_status": "source_compiled",
                "output": (
                    "apollo510b/main-source-littlefs-file-size-private-"
                    "0x007c129c.bin"
                ),
            },
        )
        for region in regions:
            if region["address_status"] != "official_blob":
                continue
            region_start = region.get("target_address")
            if not isinstance(region_start, int):
                continue
            self.assertFalse(
                region_start < END
                and START < region_start + region["size"],
                region,
            )

        package = manifest["package"]
        for profile, pins in PROFILE_PINS.items():
            selected_provider = (
                provider
                if profile == "apple-clang"
                else provider["profiles"][profile]
            )
            selected_package = (
                package
                if profile == "apple-clang"
                else package["profiles"][profile]
            )
            self.assertEqual(
                (selected_provider["size"], selected_provider["sha256"]),
                pins["component"],
            )
            self.assertEqual(
                (
                    selected_package["expected_size"],
                    selected_package["expected_sha256"],
                ),
                pins["package"],
            )

        merged_manifest = self.open_cfw.load_manifest(MANIFEST)
        for profile, pins in PROFILE_PINS.items():
            ownership = self.coarse_ownership(merged_manifest, profile)
            self.assertTrue(all(value >= 0 for value in ownership))
            self.assertEqual(sum(ownership), pins["package"][0])

    def test_active_profile_package_plan_and_ownership_are_exact(
        self,
    ) -> None:
        output = Path(self.temporary.name) / "package-plan"
        report = self.open_cfw.build(
            MANIFEST,
            output,
            toolchain_profile=self.profile,
        )
        plan = json.loads(
            (output / "flash-plan.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            (
                len(plan["flash_regions"]),
                len(plan["unresolved_flash_regions"]),
                len(plan["container_only_regions"]),
            ),
            (
                report["placed_region_count"],
                report["unresolved_region_count"],
                report["container_region_count"],
            ),
        )
        self.assertEqual(report["unresolved_region_count"], 0)
        self.assertEqual(plan["package_sha256"], self.pins["package"][1])
        self.assertEqual(
            (report["package"]["size"], report["package"]["sha256"]),
            self.pins["package"],
        )

        merged_manifest = self.open_cfw.load_manifest(MANIFEST)
        provider_bytes = 0
        for component in merged_manifest["components"]:
            provider = component["provider"]
            selected_provider = (
                self.open_cfw.profile_pins(provider, self.profile) or provider
            )
            provider_bytes += selected_provider["size"]
        package_envelope_bytes = self.pins["package"][0] - provider_bytes
        main = next(
            component
            for component in merged_manifest["components"]
            if component["name"] == "apollo_main"
        )
        main_preamble_bytes = next(
            region["size"]
            for region in main["regions"]
            if region["name"] == "ota_preamble"
        )
        source_owned_bytes = sum(
            region["size"]
            for region in plan["flash_regions"]
            if region["address_status"] == "source_compiled"
        )
        generated_bytes = (
            sum(
                region["size"]
                for region in plan["flash_regions"]
                if region["address_status"].startswith("generated_")
            )
            + package_envelope_bytes
            + main_preamble_bytes
        )
        opaque_bytes = (
            self.pins["package"][0]
            - source_owned_bytes
            - generated_bytes
        )
        coarse_ownership = (
            source_owned_bytes,
            generated_bytes,
            opaque_bytes,
        )
        merged_manifest = self.open_cfw.load_manifest(MANIFEST)
        self.assertEqual(
            coarse_ownership,
            self.coarse_ownership(merged_manifest, self.profile),
        )
        if self.profile == "apple-clang":
            non_main_container_bytes = sum(
                region["size"]
                for region in plan["container_only_regions"]
                if region["component"] != "apollo_main"
            )
            self.assertEqual(
                sum(CANONICAL_CONTAINER_REFINEMENT),
                non_main_container_bytes,
            )
            canonical_source, canonical_generated, canonical_opaque = (
                CANONICAL_CONTAINER_REFINEMENT
            )
            canonical_ownership = (
                source_owned_bytes + canonical_source,
                generated_bytes + canonical_generated,
                opaque_bytes
                - canonical_source
                - canonical_generated,
            )
            self.assertEqual(
                canonical_opaque,
                non_main_container_bytes
                - canonical_source
                - canonical_generated,
            )
            self.assertEqual(sum(canonical_ownership), self.pins["package"][0])

        by_name = {
            region["region"]: region for region in plan["flash_regions"]
        }
        replacement = by_name[
            "littlefs_file_size_private_source_replacement"
        ]
        self.assertEqual(
            (
                replacement["address_status"],
                replacement["target_address"],
                replacement["size"],
                replacement["sha256"],
            ),
            (
                "generated_source_entry_replacement",
                START,
                END - START,
                self.pins["patch"][1],
            ),
        )
        if self.profile == "apple-clang":
            source_leaf = by_name[
                "apollo_littlefs_file_size_private_source_leaf"
            ]
            self.assertEqual(
                (
                    source_leaf["address_status"],
                    source_leaf["target_address"],
                    source_leaf["size"],
                    source_leaf["sha256"],
                ),
                (
                    "source_compiled",
                    OVERLAY_RUNTIME_BASE + self.pins["placement"],
                    TARGET_TEXT_SIZE,
                    self.pins["relocated_sha256"],
                ),
            )

    def test_official_leaf_boundaries_and_callers_are_exact(self) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(len(self.application), 3_523_364)
        self.assertEqual(sha256(self.application), PAYLOAD_SHA256)
        self.assertEqual(self.span(START, END), STOCK_BYTES)
        self.assertEqual(sha256(self.span(START, END)), STOCK_SHA256)
        self.assertEqual(
            sha256(self.span(0x004C_E460, START)),
            "be02691b2e7339d7dd1d54b31712c3e8"
            "563e5a86f4406a469888640fad9435cd",
        )
        self.assertEqual(
            sha256(self.span(END, 0x004C_E4A0)),
            "643792648a30cb35b2a3bf79199a4fb4"
            "5680d1c717e7e9ac6ea05b5932d17366",
        )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        self.assertEqual(
            apollo_overlay.decode_thumb_branch(
                START + 14,
                STOCK_BYTES[14:18],
                link=True,
            ),
            MAX_ADDRESS,
        )
        callers = []
        jumps = []
        interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == START:
                    observed.append((address, encoded.hex()))
                if (
                    START < target < END
                    and not START <= address < END
                ):
                    interior.append((address, target, link, encoded.hex()))
        self.assertEqual(
            callers,
            [
                (0x004C_E3E2, "00f046f8"),
                (0x004C_FC56, "fef70cfc"),
            ],
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])


if __name__ == "__main__":
    unittest.main()
