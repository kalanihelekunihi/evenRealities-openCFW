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
    / "components/apollo_main/core_overlay"
    / "runtime_littlefs_file_rewind_private.c"
)
HEADER = SOURCE.with_suffix(".h")
LITTLEFS = ROOT / "third_party/littlefs"
UPSTREAM = LITTLEFS / "lfs.c"
UPSTREAM_HEADER = LITTLEFS / "lfs.h"
UPSTREAM_UTIL = LITTLEFS / "lfs_util.c"
PROVENANCE = LITTLEFS / "PROVENANCE.json"
OFFICIAL = (
    ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
)
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

FUNCTION = "open_cfw_littlefs_file_rewind_private"
SEAM = "open_cfw_littlefs_file_seek_private"
SECTION = ".text." + FUNCTION
BASE = 0x0043_8000
PACKAGE_PREAMBLE = 32
START = 0x004C_E460
END = 0x004C_E472
SEEK_ENTRY = 0x004C_E3BC
SEEK_END = 0x004C_E45C
PUBLIC_START = 0x004C_FC24
PUBLIC_END = 0x004C_FC2E
CALLER = (0x004C_FC28, bytes.fromhex("fef71afc"))
OVERLAY_RUNTIME_BASE = 0x0079_4324

PACKAGE_PIN = (
    3_523_396,
    "36c5b0e499a68ac2493a497bdab9740f"
    "d3e7027730c26a9094eca47268a27863",
)
APPLICATION_PIN = (
    3_523_364,
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701",
)
SOURCE_PIN = (
    1_239,
    "e6afb5b67671b3219971b19c20290c6"
    "01568752d814064147f5ccd4118f5acc8",
)
HEADER_PIN = (
    1_743,
    "7430dcd1ad1ea3973d619f2d67d8d8b1"
    "1a688018d48a3bc26a40e407d1fedb56",
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_PIN = (
    196_753,
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398",
)
UPSTREAM_HEADER_PIN = (
    26_439,
    "ee44e99d6b19119b3e577b969b80c9d"
    "5e6f96410c9593794afddf6d4b314c486",
)
UPSTREAM_UTIL_PIN = (
    988,
    "f2fbde533670560434bd9f5a547174cc"
    "7c5a4670a02c47b4bd85180dced8b2ec",
)
UPSTREAM_DEFINITION = (118_157, 118_349)
UPSTREAM_DEFINITION_PIN = (
    192,
    "74638292061613417c2ce7c6bbed200d"
    "2bee046c35a7a835fb4d9bb183ab755a",
)

STOCK_BYTES = bytes.fromhex(
    "80b500230022fff7a9ff002800d4002002bd"
)
STOCK_PIN = (
    18,
    "be02691b2e7339d7dd1d54b31712c3e8"
    "563e5a86f4406a469888640fad9435cd",
)
PREDECESSOR_PIN = (
    START - 4,
    START,
    4,
    "efdc6e5a708e49cc1158aec6dfbde6a0"
    "115558c29a0f8c6a6ba9c4075df0fb5f",
)
SUCCESSOR_PIN = (
    END,
    END + 24,
    24,
    "98ba58dac7de35e47c75240c0671b11e"
    "6b403a1bffed50a617c6543eb26a83cc",
)
SEEK_PROVIDER_PIN = (
    SEEK_ENTRY,
    SEEK_END,
    160,
    "368a3e58188f71ad37233eaca687cd393"
    "9a9f06406702a176f9731f22bcaf61f",
)
PUBLIC_PROVIDER_PIN = (
    PUBLIC_START,
    PUBLIC_END,
    10,
    "db0377b209a419d889a90e4584af9a0f"
    "351ff7f42b192afd90624def52231b46",
)
CALLER_ADDRESS_SHA256 = (
    "5f13a1403935da397e5110a7461c4fc3"
    "e8fc56d862d58d989ee60074eb10a26e"
)
CALLER_ENCODING_SHA256 = (
    "701af3804b98fe93489475df3f9cd0f5"
    "a0898fac51ef04f9ab715da9dda5783e"
)

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
TARGET_OBJECT_PIN = (
    960,
    "c7398babd0a9adba9ea4a81c8221d882"
    "6f1aac166bebbee4307280778a1443bf",
)
TARGET_TEXT = bytes.fromhex("80b500220023fff7feff00eae07080bd")
TARGET_TEXT_PIN = (
    16,
    "46e8bab056ad39ced45edb5da2612f64"
    "70674ab5a428df7f08822f6c2d9e184b",
)
TARGET_RELOCATIONS = [(6, 10, SEAM)]

PROFILE_PINS = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "offset": 124_480,
        "runtime": 0x007B_2964,
        "relocated": (
            "1c2e2b1fded0de515345b90fe34de51a"
            "9c0f08a02a5ad983c1120481c51c5783"
        ),
        "patch": (
            "e4f280ba" + "00bf" * 7,
            "d6d0947d5f648f4acdab371be5d051e3"
            "c89ad1f2e44b88da2ce0600e7b2f3751",
        ),
        "overlay": (
            147_021,
            "02c48ddcf4fa682ec14c3520ccac159c98a357aff4d18bd7e8ad01817e3bc2cd",
        ),
        "component": (
            3_670_417,
            "eee145e7f687e622447bc33fc9dc45b3ab5eb1f1ad49717029196d589799aa4c",
        ),
        "package": (
            4_448_911,
            "21ba9d6c32c73f390fd68ee9ef2808ad01c7206d746e67eca9c755732b0a6605",
        ),
        "plan": (
            1_046_958,
            "086841ac128a812376e0389b3b6f0fc91d75186b6a48f79d1d8de4297e54e34c",
            (1460, 2, 5),
            1467,
        ),
        "coarse_ownership": (147_634, 103_382, 4_197_895),
        "manifest_ownership": (147_634, 103_382, 4_197_895),
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "offset": 126_300,
        "runtime": 0x007B_3080,
        "relocated": (
            "9731cbf3ff15be31186591ed148d009ae"
            "8985cb18bdfca3ba365aeb0897e3fd1"
        ),
        "patch": (
            "e4f20ebe" + "00bf" * 7,
            "f014878435e10f6bf1feba6c78781bee"
            "5e0a8f15a9b47aa4cfd596cffb7d984b",
        ),
        "overlay": (
            144_266,
            "4c95f20608c70a065b05837415d2d4471fc7eeeb61fa30ce1c1c9f07f717ddb9",
        ),
        "component": (
            3_667_662,
            "686ea217db2837bffd8a190485f0a6f719242e927fba17281c6f54aa066767f6",
        ),
        "package": (
            4_446_156,
            "2cca0fbac8da01ede95a3cecd55dd0706f6dad3a8437605f8a68949cee3c6bc3",
        ),
        "plan": (
            640_188,
            "4480ca9a4a4f237a477ccccdc9cb039f071fb2f6547298595e98a91098302a20",
            (896, 2, 5),
            855,
        ),
        "coarse_ownership": (145_147, 101_698, 4_199_311),
        "manifest_ownership": (145_147, 102_032, 4_198_977),
    },
}

MANIFEST_STATUS = {
    "container_only": (1, 32),
    "generated_alignment": (133, 265),
    "generated_source_entry_replacement": (726, 101_138),
    "generated_source_exact_load_image": (1, 6),
    "generated_source_exact_replacement": (7, 134),
    "official_blob": (225, 3_421_868),
    "source_compiled": (307, 146_974),
}
CANONICAL_CONTAINER_REFINEMENT = (17, 135, 84)
CANONICAL_OWNERSHIP = (147_080, 102_418, 4_198_825)

CANDIDATE_HARNESS = r"""
#include <stddef.h>
#include <stdint.h>

#include "runtime_littlefs_file_rewind_private.h"

struct rewind_result {
    uint64_t lfs_address;
    uint64_t file_address;
    int32_t return_value;
    int32_t offset;
    int32_t whence;
    uint32_t calls;
};

static int32_t configured_result;
static uintptr_t observed_lfs;
static uintptr_t observed_file;
static int32_t observed_offset;
static int32_t observed_whence;
static uint32_t observed_calls;

open_cfw_littlefs_file_rewind_private_soff
open_cfw_littlefs_file_seek_private(
    struct open_cfw_littlefs_file_rewind_private_lfs *lfs,
    struct open_cfw_littlefs_file_rewind_private_file *file,
    open_cfw_littlefs_file_rewind_private_soff offset,
    int whence
)
{
    observed_calls++;
    observed_lfs = (uintptr_t)lfs;
    observed_file = (uintptr_t)file;
    observed_offset = offset;
    observed_whence = whence;
    return configured_result;
}

void candidate_run(
    int32_t seek_result,
    uintptr_t lfs_address,
    uintptr_t file_address,
    struct rewind_result *result
)
{
    configured_result = seek_result;
    observed_lfs = 0U;
    observed_file = 0U;
    observed_offset = INT32_MAX;
    observed_whence = INT32_MAX;
    observed_calls = 0U;
    result->return_value = open_cfw_littlefs_file_rewind_private(
        (struct open_cfw_littlefs_file_rewind_private_lfs *)lfs_address,
        (struct open_cfw_littlefs_file_rewind_private_file *)file_address
    );
    result->lfs_address = observed_lfs;
    result->file_address = observed_file;
    result->offset = observed_offset;
    result->whence = observed_whence;
    result->calls = observed_calls;
}

size_t candidate_int_size(void) { return sizeof(int); }
size_t candidate_pointer_size(void) { return sizeof(void *); }
size_t candidate_soff_size(void)
{
    return sizeof(open_cfw_littlefs_file_rewind_private_soff);
}
int candidate_seek_set(void)
{
    return OPEN_CFW_LITTLEFS_FILE_REWIND_PRIVATE_SEEK_SET;
}
"""

ORACLE_PREAMBLE = r"""
#include <stddef.h>
#include <stdint.h>

#include "lfs.h"

struct rewind_result {
    uint64_t lfs_address;
    uint64_t file_address;
    int32_t return_value;
    int32_t offset;
    int32_t whence;
    uint32_t calls;
};

static int32_t configured_result;
static uintptr_t observed_lfs;
static uintptr_t observed_file;
static int32_t observed_offset;
static int32_t observed_whence;
static uint32_t observed_calls;

static lfs_soff_t lfs_file_seek_(
    lfs_t *lfs,
    lfs_file_t *file,
    lfs_soff_t offset,
    int whence
)
{
    observed_calls++;
    observed_lfs = (uintptr_t)lfs;
    observed_file = (uintptr_t)file;
    observed_offset = offset;
    observed_whence = whence;
    return configured_result;
}
"""

ORACLE_POSTAMBLE = r"""
void oracle_run(
    int32_t seek_result,
    uintptr_t lfs_address,
    uintptr_t file_address,
    struct rewind_result *result
)
{
    configured_result = seek_result;
    observed_lfs = 0U;
    observed_file = 0U;
    observed_offset = INT32_MAX;
    observed_whence = INT32_MAX;
    observed_calls = 0U;
    result->return_value = lfs_file_rewind_(
        (lfs_t *)lfs_address,
        (lfs_file_t *)file_address
    );
    result->lfs_address = observed_lfs;
    result->file_address = observed_file;
    result->offset = observed_offset;
    result->whence = observed_whence;
    result->calls = observed_calls;
}

size_t oracle_int_size(void) { return sizeof(int); }
size_t oracle_pointer_size(void) { return sizeof(void *); }
size_t oracle_soff_size(void) { return sizeof(lfs_soff_t); }
int oracle_seek_set(void) { return LFS_SEEK_SET; }
"""


class RewindResult(ctypes.Structure):
    _fields_ = [
        ("lfs_address", ctypes.c_uint64),
        ("file_address", ctypes.c_uint64),
        ("return_value", ctypes.c_int32),
        ("offset", ctypes.c_int32),
        ("whence", ctypes.c_int32),
        ("calls", ctypes.c_uint32),
    ]

    def values(self) -> tuple[int, ...]:
        return (
            self.return_value,
            self.lfs_address,
            self.file_address,
            self.offset,
            self.whence,
            self.calls,
        )


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def wide_conditional_target(
    address: int,
    first: int,
    second: int,
) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    if (first >> 6) & 0x0F >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        (sign << 20)
        | (((second >> 11) & 1) << 19)
        | (((second >> 13) & 1) << 18)
        | ((first & 0x003F) << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 21
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + 2 * immediate,)
    if halfword & 0xF000 == 0xD000 and (halfword >> 8) & 0x0F < 0x0E:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + 2 * immediate,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return (address + 4 + 2 * immediate,)
    return ()


class RuntimeLittlefsFileRewindPrivateProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for path, expected in (
            (SOURCE, SOURCE_PIN),
            (HEADER, HEADER_PIN),
            (UPSTREAM, UPSTREAM_PIN),
            (UPSTREAM_HEADER, UPSTREAM_HEADER_PIN),
            (UPSTREAM_UTIL, UPSTREAM_UTIL_PIN),
        ):
            actual = (path.stat().st_size, sha256(path))
            if actual != expected:
                raise AssertionError(
                    f"unauthenticated production input: "
                    f"{path.relative_to(ROOT)} {actual!r}"
                )
        upstream = UPSTREAM.read_bytes()
        cls.upstream_definition = upstream[slice(*UPSTREAM_DEFINITION)]
        if (
            len(cls.upstream_definition),
            sha256(cls.upstream_definition),
        ) != UPSTREAM_DEFINITION_PIN:
            raise AssertionError("unauthenticated upstream rewind definition")

        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        profiles = [
            name
            for name, pins in PROFILE_PINS.items()
            if (cls.clang, version) == (pins["compiler"], pins["version"])
        ]
        if len(profiles) != 1:
            raise AssertionError(f"unreviewed compiler: {(cls.clang, version)!r}")
        cls.profile = profiles[0]
        cls.pins = PROFILE_PINS[cls.profile]

        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-littlefs-file-rewind-private-",
            dir=temporary_parent,
        )
        temporary = Path(cls.temporary.name)
        candidate_harness = temporary / "candidate_harness.c"
        candidate_harness.write_text(
            textwrap.dedent(CANDIDATE_HARNESS),
            encoding="utf-8",
        )
        oracle_harness = temporary / "oracle_harness.c"
        oracle_harness.write_bytes(
            textwrap.dedent(ORACLE_PREAMBLE).encode("utf-8")
            + cls.upstream_definition
            + textwrap.dedent(ORACLE_POSTAMBLE).encode("utf-8")
        )
        cls.candidate = cls.compile_library(
            temporary / "candidate",
            [SOURCE, candidate_harness],
            ["-I", str(SOURCE.parent)],
        )
        cls.oracle = cls.compile_library(
            temporary / "oracle",
            [oracle_harness],
            ["-I", str(LITTLEFS)],
        )
        cls.candidate_run = cls.bind_runner(cls.candidate, "candidate")
        cls.oracle_run = cls.bind_runner(cls.oracle, "oracle")

        cls.objects = []
        for index in range(2):
            target = temporary / f"rewind-{index}.o"
            subprocess.run(
                [
                    cls.clang,
                    *TARGET_FLAGS,
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(target),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.objects.append(target)

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        import open_cfw

        cls.apollo_overlay = apollo_overlay
        cls.open_cfw = open_cfw
        cls.overlay_output = temporary / "production-overlay"
        cls.component_report = apollo_overlay.build(
            root=ROOT,
            config_path=OVERLAY,
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
        library = stem.with_suffix(
            ".dylib" if sys.platform == "darwin" else ".so"
        )
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            *extra_flags,
            *(str(source) for source in sources),
        ]
        command.extend(
            ["-dynamiclib", "-o", str(library)]
            if sys.platform == "darwin"
            else ["-shared", "-fPIC", "-o", str(library)]
        )
        subprocess.run(command, check=True, capture_output=True, text=True)
        return ctypes.CDLL(str(library))

    @staticmethod
    def bind_runner(
        library: ctypes.CDLL,
        prefix: str,
    ) -> ctypes._CFuncPtr:
        runner = getattr(library, prefix + "_run")
        runner.argtypes = [
            ctypes.c_int32,
            ctypes.c_size_t,
            ctypes.c_size_t,
            ctypes.POINTER(RewindResult),
        ]
        runner.restype = None
        for suffix in ("int_size", "pointer_size", "soff_size"):
            function = getattr(library, prefix + "_" + suffix)
            function.argtypes = []
            function.restype = ctypes.c_size_t
        seek_set = getattr(library, prefix + "_seek_set")
        seek_set.argtypes = []
        seek_set.restype = ctypes.c_int
        return runner

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

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

    @staticmethod
    def run_case(
        runner: ctypes._CFuncPtr,
        seek_result: int,
        lfs_address: int,
        file_address: int,
    ) -> tuple[int, ...]:
        result = RewindResult()
        runner(
            seek_result,
            lfs_address,
            file_address,
            ctypes.byref(result),
        )
        return result.values()

    def test_authenticated_source_header_and_upstream_definition_are_exact(
        self,
    ) -> None:
        self.assertEqual((SOURCE.stat().st_size, sha256(SOURCE)), SOURCE_PIN)
        self.assertEqual((HEADER.stat().st_size, sha256(HEADER)), HEADER_PIN)
        self.assertEqual((UPSTREAM.stat().st_size, sha256(UPSTREAM)), UPSTREAM_PIN)
        self.assertEqual(
            (UPSTREAM_HEADER.stat().st_size, sha256(UPSTREAM_HEADER)),
            UPSTREAM_HEADER_PIN,
        )
        self.assertEqual(
            (UPSTREAM_UTIL.stat().st_size, sha256(UPSTREAM_UTIL)),
            UPSTREAM_UTIL_PIN,
        )
        self.assertEqual(
            (len(self.upstream_definition), sha256(self.upstream_definition)),
            UPSTREAM_DEFINITION_PIN,
        )
        self.assertTrue(self.upstream_definition.startswith(
            b"static int lfs_file_rewind_(lfs_t *lfs, lfs_file_t *file) {"
        ))
        for token in (
            b"lfs_file_seek_(lfs, file, 0, LFS_SEEK_SET)",
            b"if (res < 0)",
            b"return (int)res;",
            b"return 0;",
        ):
            self.assertIn(token, self.upstream_definition)

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["license"], "BSD-3-Clause")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertEqual(
            provenance["selection"]["classification"],
            "source-equivalent release baseline",
        )

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "SPDX-License-Identifier: BSD-3-Clause",
            "Altered, freestanding adaptation",
            "littlefs v2.10.1 source-equivalent baseline",
            UPSTREAM_COMMIT,
            "[0x004CE460, 0x004CE472)",
            "lfs_file_seek_ at 0x004CE3BC",
            "if (result < 0)",
        ):
            self.assertIn(token, source)
        for token in (
            "sizeof(int) == 4U",
            "sizeof(void *) == 4U",
            "sizeof(open_cfw_littlefs_file_rewind_private_soff) == 4U",
            "OPEN_CFW_LITTLEFS_FILE_REWIND_PRIVATE_SEEK_SET = 0",
            "OPEN_CFW_LITTLEFS_FILE_REWIND_PRIVATE_SEEK_ADDRESS = 0x004CE3BCU",
            SEAM,
        ):
            self.assertIn(token, header)

    def test_pristine_upstream_differential_preserves_only_negative_results(
        self,
    ) -> None:
        for prefix, library in (
            ("candidate", self.candidate),
            ("oracle", self.oracle),
        ):
            self.assertEqual(getattr(library, prefix + "_int_size")(), 4)
            self.assertEqual(
                getattr(library, prefix + "_pointer_size")(),
                ctypes.sizeof(ctypes.c_void_p),
            )
            self.assertEqual(getattr(library, prefix + "_soff_size")(), 4)
            self.assertEqual(getattr(library, prefix + "_seek_set")(), 0)

        edge_results = (
            -0x8000_0000,
            -0x7FFF_FFFF,
            -65_535,
            -2,
            -1,
            0,
            1,
            2,
            65_535,
            0x7FFF_FFFF,
        )
        cases = [
            (value, 0x1234_5678, 0x7654_3210)
            for value in edge_results
        ]
        rng = random.Random(0x4C_E460)
        cases.extend(
            (
                ctypes.c_int32(rng.getrandbits(32)).value,
                rng.getrandbits(ctypes.sizeof(ctypes.c_void_p) * 8),
                rng.getrandbits(ctypes.sizeof(ctypes.c_void_p) * 8),
            )
            for _ in range(1_000)
        )
        pointer_mask = (1 << (ctypes.sizeof(ctypes.c_void_p) * 8)) - 1
        for seek_result, lfs_address, file_address in cases:
            with self.subTest(seek_result=seek_result):
                expected = (
                    seek_result if seek_result < 0 else 0,
                    lfs_address & pointer_mask,
                    file_address & pointer_mask,
                    0,
                    0,
                    1,
                )
                candidate = self.run_case(
                    self.candidate_run,
                    seek_result,
                    lfs_address,
                    file_address,
                )
                pristine = self.run_case(
                    self.oracle_run,
                    seek_result,
                    lfs_address,
                    file_address,
                )
                self.assertEqual(candidate, expected)
                self.assertEqual(pristine, expected)
                self.assertEqual(candidate, pristine)

    def test_target_object_text_and_strict_call_closure_are_exact(self) -> None:
        first = self.objects[0].read_bytes()
        second = self.objects[1].read_bytes()
        self.assertEqual(first, second)
        self.assertEqual((len(first), sha256(first)), TARGET_OBJECT_PIN)
        data, sections = self.apollo_overlay.parse_elf32(self.objects[0])
        text = self.apollo_overlay.section_named(sections, SECTION)
        payload = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        self.assertEqual(payload, TARGET_TEXT)
        self.assertEqual((len(payload), sha256(payload)), TARGET_TEXT_PIN)
        self.assertEqual(text["alignment"], 4)

        symtab = self.apollo_overlay.section_named(sections, ".symtab")
        strtab = sections[int(symtab["link"])]
        strings = data[
            int(strtab["offset"]):
            int(strtab["offset"]) + int(strtab["size"])
        ]
        symbols = []
        for index in range(int(symtab["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symtab["offset"]) + 16 * index,
            )
            name = self.apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            symbols.append((name, fields))
        by_name = {name: fields for name, fields in symbols if name}
        function = by_name[FUNCTION]
        self.assertEqual((function[1], function[2]), (1, TARGET_TEXT_PIN[0]))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertNotEqual(function[5], 0)
        seam = by_name[SEAM]
        self.assertEqual(seam[3] & 0x0F, 0)
        self.assertEqual(seam[5], 0)

        relocations = []
        for section in sections:
            if int(section["type"]) != 9:
                continue
            target = sections[int(section["info"])]
            if target["name"] != SECTION:
                continue
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    data,
                    int(section["offset"]) + 8 * index,
                )
                relocations.append((
                    offset,
                    information & 0xFF,
                    symbols[information >> 8][0],
                ))
        self.assertEqual(relocations, TARGET_RELOCATIONS)
        self.assertEqual(relocations[0][1], 10)
        undefined = sorted(
            name for name, fields in by_name.items() if fields[5] == 0
        )
        self.assertEqual(undefined, [SEAM])
        allocated = {
            section["name"]: section["size"]
            for section in sections
            if section["size"] and int(section["flags"]) & 2
        }
        self.assertEqual(allocated, {
            SECTION: TARGET_TEXT_PIN[0],
            ".ARM.exidx" + SECTION: 8,
        })

    def test_stock_neighbors_caller_and_seek_provider_are_exact(self) -> None:
        self.assertEqual(
            (len(self.package), sha256(self.package)),
            PACKAGE_PIN,
        )
        self.assertEqual(
            (len(self.application), sha256(self.application)),
            APPLICATION_PIN,
        )
        self.assertEqual(self.span(START, END), STOCK_BYTES)
        self.assertEqual((len(STOCK_BYTES), sha256(STOCK_BYTES)), STOCK_PIN)
        for start, end, size, digest in (
            PREDECESSOR_PIN,
            SUCCESSOR_PIN,
            SEEK_PROVIDER_PIN,
            PUBLIC_PROVIDER_PIN,
        ):
            payload = self.span(start, end)
            self.assertEqual((len(payload), sha256(payload)), (size, digest))
        caller_address, caller_encoding = CALLER
        self.assertEqual(
            self.span(caller_address, caller_address + 4),
            caller_encoding,
        )
        self.assertEqual(
            sha256(struct.pack("<I", caller_address)),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(sha256(caller_encoding), CALLER_ENCODING_SHA256)
        first, second = struct.unpack("<HH", STOCK_BYTES[6:10])
        self.assertEqual(
            wide_branch_target(START + 6, first, second, link=True),
            SEEK_ENTRY,
        )

    def test_whole_image_branch_and_stored_address_ingress_is_exact(self) -> None:
        self.assertEqual(
            wide_conditional_target(0x1000, 0xF000, 0x8000),
            0x1004,
        )
        self.assertIsNone(wide_conditional_target(0x1000, 0xF380, 0x8000))
        self.assertIsNone(wide_conditional_target(0x1000, 0xF000, 0x9000))

        incoming_bl = []
        incoming_bw = []
        direct_interior = []
        wide_conditional_entry = []
        wide_conditional_interior = []
        narrow_entry = []
        narrow_interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            for link, entry_owner in (
                (True, incoming_bl),
                (False, incoming_bw),
            ):
                target = wide_branch_target(
                    address,
                    first,
                    second,
                    link=link,
                )
                if target == START:
                    entry_owner.append((address, self.application[offset:offset + 4]))
                elif (
                    target is not None
                    and START < target < END
                    and not (START <= address < END)
                ):
                    direct_interior.append((address, target, link))

            conditional = wide_conditional_target(address, first, second)
            if (
                conditional is not None
                and START <= conditional < END
                and not (START <= address < END)
            ):
                owner = (
                    wide_conditional_entry
                    if conditional == START
                    else wide_conditional_interior
                )
                owner.append((address, conditional))
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            first = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_targets(address, first):
                if START <= target < END and not (START <= address < END):
                    owner = narrow_entry if target == START else narrow_interior
                    owner.append((address, target))

        self.assertEqual(incoming_bl, [CALLER])
        self.assertEqual(incoming_bw, [])
        self.assertEqual(direct_interior, [])
        self.assertEqual(wide_conditional_entry, [])
        self.assertEqual(wide_conditional_interior, [])
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])

        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            canonical = value & ~1
            if START <= canonical < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

    def test_production_registration_active_build_and_patch_are_exact(
        self,
    ) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertEqual(
            (
                len(config["functions"]),
                len(config["patch_sites"]),
                len(config["relocated_leaves"]),
            ),
            (825, 766, 256),
        )
        self.assertEqual(config["functions"].count(FUNCTION), 1)
        leaves = [
            leaf
            for leaf in config["relocated_leaves"]
            if leaf["function"] == FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        leaf = leaves[0]
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual(leaf["source"], {
            "path": SOURCE.relative_to(ROOT).as_posix(),
            "size": SOURCE_PIN[0],
            "sha256": SOURCE_PIN[1],
            "license": "BSD-3-Clause",
            "origin": (
                "bounded freestanding adaptation of authenticated littlefs "
                "v2.10.1 lfs_file_rewind_ with a retained private "
                "lfs_file_seek_ provider seam"
            ),
            "upstream": (
                "https://github.com/littlefs-project/littlefs/blob/"
                f"{UPSTREAM_COMMIT}/lfs.c"
            ),
            "upstream_commit": UPSTREAM_COMMIT,
            "evidence": (
                "docs/research/littlefs-file-rewind-source-audit.md"
            ),
        })
        self.assertEqual(leaf["toolchain"]["target"], TARGET_FLAGS[0][9:])
        self.assertEqual(leaf["toolchain"]["flags"], TARGET_FLAGS[1:])

        relocation_pin = [{
            "offset": 6,
            "type": "R_ARM_THM_CALL",
            "symbol": SEAM,
            "symbol_type": "STT_NOTYPE",
            "target_address": SEEK_ENTRY,
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
            self.assertEqual(expected, {
                "size": TARGET_TEXT_PIN[0],
                "sha256": pins["relocated"],
                "alignment": 4,
                "offset": pins["offset"],
                "unrelocated_sha256": TARGET_TEXT_PIN[1],
            })
            self.assertEqual(relocations, relocation_pin)
            self.assertEqual(
                pins["runtime"],
                OVERLAY_RUNTIME_BASE + pins["offset"],
            )
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

        patches = [
            patch
            for patch in config["patch_sites"]
            if patch.get("target_function") == FUNCTION
        ]
        self.assertEqual(patches, [{
            "name": "replace_littlefs_file_rewind_private",
            "runtime_address": START,
            "expected_size": END - START,
            "expected_sha256": STOCK_PIN[1],
            "branch": "b_w",
            "target_function": FUNCTION,
        }])

        report = self.component_report
        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            self.pins["overlay"],
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]),
            self.pins["component"],
        )
        extracted = next(
            item
            for item in report["relocated_leaves"]
            if item["extraction"]["function"] == FUNCTION
        )
        self.assertEqual(extracted["placement"], {
            "offset": self.pins["offset"],
            "runtime_address": self.pins["runtime"],
            "runtime_address_hex": f"0x{self.pins['runtime']:08X}",
            "size": TARGET_TEXT_PIN[0],
            "alignment": 4,
            "padding_before": 0,
        })
        extraction = extracted["extraction"]
        self.assertEqual(extraction["sha256"], self.pins["relocated"])
        self.assertEqual(
            extraction["unrelocated_sha256"],
            TARGET_TEXT_PIN[1],
        )
        self.assertEqual(extraction["relocation_count"], 1)
        self.assertEqual(
            {
                key: extraction["relocations"][0][key]
                for key in (
                    "offset",
                    "type",
                    "type_id",
                    "symbol",
                    "symbol_type",
                    "target_address",
                )
            },
            {
                "offset": 6,
                "type": "R_ARM_THM_CALL",
                "type_id": 10,
                "symbol": SEAM,
                "symbol_type": "STT_NOTYPE",
                "target_address": SEEK_ENTRY,
            },
        )
        patch = next(
            item
            for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_littlefs_file_rewind_private"
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(
            (replacement.hex(), sha256(replacement)),
            self.pins["patch"],
        )
        self.assertEqual(len(replacement), END - START)
        self.assertEqual(replacement[4:], b"\x00\xbf" * 7)
        self.assertEqual(patch["target_address"], self.pins["runtime"])
        component = (
            self.overlay_output / "ota_s200_firmware_ota.bin"
        ).read_bytes()
        patch_offset = PACKAGE_PREAMBLE + START - BASE
        self.assertEqual(
            component[patch_offset:patch_offset + END - START],
            replacement,
        )

    def test_manifest_replacement_tail_tiling_and_profile_pins_are_exact(
        self,
    ) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        regions = main["regions"]
        self.assertEqual(len(regions), 1400)
        self.assertEqual(main["source_appended_boundary"], PACKAGE_PIN[0])
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
        status = {}
        for region in regions:
            count, size = status.get(region["address_status"], (0, 0))
            status[region["address_status"]] = (
                count + 1,
                size + region["size"],
            )
        self.assertEqual(status, MANIFEST_STATUS)

        by_name = {region["name"]: region for region in regions}
        replacement = by_name["littlefs_file_rewind_private_source_replacement"]
        self.assertEqual(replacement, {
            "name": "littlefs_file_rewind_private_source_replacement",
            "function": (
                "Generated entry redirect and NOP fill replacing "
                "littlefs v2.10.1 lfs_file_rewind_"
            ),
            "file_offset": 615_552,
            "size": END - START,
            "target": "apollo510b_internal_mram",
            "target_address": START,
            "address_status": "generated_source_entry_replacement",
            "output": (
                "apollo510b/source-entry-littlefs-file-rewind-private-"
                "0x004ce460.bin"
            ),
        })
        tail = by_name["apollo_littlefs_file_rewind_private_source_leaf"]
        self.assertIs(tail, regions[-296])
        self.assertEqual(tail, {
            "name": "apollo_littlefs_file_rewind_private_source_leaf",
            "function": (
                "BSD-3-Clause littlefs v2.10.1 private file-rewind "
                "source compatibility leaf"
            ),
            "file_offset": 3_647_876,
            "size": TARGET_TEXT_PIN[0],
            "target": "apollo510b_internal_mram",
            "target_address": PROFILE_PINS["apple-clang"]["runtime"],
            "address_status": "source_compiled",
            "output": (
                "apollo510b/main-source-littlefs-file-rewind-private-"
                "0x007b2964.bin"
            ),
        })
        overlapping = []
        for region in regions:
            address = region.get("target_address")
            if not isinstance(address, int):
                continue
            if address < END and START < address + region["size"]:
                overlapping.append(region)
        self.assertEqual(overlapping, [replacement])

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

        merged = self.open_cfw.load_manifest(MANIFEST)
        for profile, pins in PROFILE_PINS.items():
            self.assertEqual(
                self.coarse_ownership(merged, profile),
                pins["manifest_ownership"],
            )

    def test_active_profile_package_plan_and_ownership_are_exact(self) -> None:
        output = Path(self.temporary.name) / "production-package"
        report = self.open_cfw.build(
            MANIFEST,
            output,
            toolchain_profile=self.profile,
        )
        plan_bytes = (output / "flash-plan.json").read_bytes()
        plan_size, plan_hash, plan_counts, total_count = self.pins["plan"]
        self.assertEqual(
            (len(plan_bytes), sha256(plan_bytes)),
            (plan_size, plan_hash),
        )
        plan = json.loads(plan_bytes)
        observed_counts = (
            len(plan["flash_regions"]),
            len(plan["unresolved_flash_regions"]),
            len(plan["container_only_regions"]),
        )
        self.assertEqual(total_count, sum(plan_counts))
        self.assertEqual(observed_counts, plan_counts)
        self.assertEqual(sum(observed_counts), total_count)
        self.assertEqual(
            (
                report["placed_region_count"],
                report["unresolved_region_count"],
                len(plan["container_only_regions"]),
            ),
            plan_counts,
        )
        self.assertEqual(
            (report["package"]["size"], report["package"]["sha256"]),
            self.pins["package"],
        )

        merged = self.open_cfw.load_manifest(MANIFEST)
        provider_bytes = 0
        for component in merged["components"]:
            provider = component["provider"]
            selected = (
                self.open_cfw.profile_pins(provider, self.profile) or provider
            )
            provider_bytes += selected["size"]
        package_envelope_bytes = self.pins["package"][0] - provider_bytes
        main = next(
            component
            for component in merged["components"]
            if component["name"] == "apollo_main"
        )
        main_preamble_bytes = next(
            region["size"]
            for region in main["regions"]
            if region["name"] == "ota_preamble"
        )
        source_bytes = sum(
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
        ownership = (
            source_bytes,
            generated_bytes,
            self.pins["package"][0] - source_bytes - generated_bytes,
        )
        self.assertEqual(ownership, self.pins["coarse_ownership"])
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
            source_refinement, generated_refinement, opaque_refinement = (
                CANONICAL_CONTAINER_REFINEMENT
            )
            canonical = (
                source_bytes + source_refinement,
                generated_bytes + generated_refinement,
                ownership[2] - source_refinement - generated_refinement,
            )
            self.assertEqual(
                opaque_refinement,
                non_main_container_bytes
                - source_refinement
                - generated_refinement,
            )
            self.assertEqual(canonical, CANONICAL_OWNERSHIP)

        by_name = {
            region["region"]: region for region in plan["flash_regions"]
        }
        replacement = by_name[
            "littlefs_file_rewind_private_source_replacement"
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
                "apollo_littlefs_file_rewind_private_source_leaf"
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
                    self.pins["runtime"],
                    TARGET_TEXT_PIN[0],
                    self.pins["relocated"],
                ),
            )
        else:
            appended = by_name["apollo_main_source_appended"]
            self.assertEqual(
                (
                    appended["address_status"],
                    appended["target_address"],
                    appended["size"],
                    appended["sha256"],
                ),
                (
                    "source_compiled",
                    OVERLAY_RUNTIME_BASE,
                    self.pins["overlay"][0],
                    self.pins["overlay"][1],
                ),
            )


if __name__ == "__main__":
    unittest.main()
