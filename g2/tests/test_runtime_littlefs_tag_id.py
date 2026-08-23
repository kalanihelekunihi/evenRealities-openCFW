from __future__ import annotations

import ctypes
import hashlib
import json
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/littlefs/runtime_littlefs_tag_id.c"
HEADER = SOURCE.with_suffix(".h")
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
HEADER_PATH = HEADER.relative_to(ROOT).as_posix()
UPSTREAM = ROOT / "third_party/littlefs/lfs.c"
PROVENANCE = ROOT / "third_party/littlefs/PROVENANCE.json"
MAIN_PACKAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN_OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BOOT_OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

FUNCTION = "open_cfw_littlefs_tag_id"
SECTION = ".text." + FUNCTION
MAIN_BASE = 0x0043_8000
BOOT_BASE = 0x0041_0000
MAIN_START = 0x004C_AEB0
MAIN_END = 0x004C_AEB8
BOOT_START = 0x0041_0BB8
BOOT_END = 0x0041_0BC0
PACKAGE_PREAMBLE = 32

MAIN_PACKAGE_PIN = (
    3_523_396,
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863",
)
MAIN_PAYLOAD_PIN = (
    3_523_364,
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701",
)
BOOT_PIN = (
    148_599,
    "f89a4c4657537cec6bfc572bdb831886"
    "6309b90a5d180c4307680d39824167b5",
)
SOURCE_PIN = (
    845,
    "5b6c3ce0f4236d6c6bc0a12891e41929"
    "e9034a7ddc2f68bd4f6a1d5d4fa07638",
)
HEADER_PIN = (
    872,
    "5d6d1c5df9a0fb31f80ad0f6a876795"
    "cb154b039fa72df17c615b38cd5e2099e",
)
UPSTREAM_PIN = (
    196_753,
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398",
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_DEFINITION = (10_702, 10_793)
UPSTREAM_DEFINITION_PIN = (
    91,
    "50140c563689852013dfad180ec3b646"
    "4c6b6c5b22854f5492d63cf5de57fbe2",
)
UPSTREAM_TAG_TYPEDEF = (9_602, 9_629)
UPSTREAM_TAG_TYPEDEF_PIN = (
    27,
    "cb4dcd6212b1a269371d86dddf98ed7"
    "4853e2eb43753c5d8f8659abbca167ce2",
)

STOCK = bytes.fromhex("800a8005800d7047")
STOCK_SHA256 = (
    "0843abb3e9ef39afac8e69ae1e181efa"
    "0b5b5c8ebf53e20844b53fdf245b1036"
)
PREDECESSOR_WINDOW = bytes.fromhex("40b202bd")
PREDECESSOR_RETURN = bytes.fromhex("02bd")
SUCCESSOR_PREFIX = bytes.fromhex("8005")
MAIN_CALLERS = [
    (0x004C_B262, "fff725fe"),
    (0x004C_B26C, "fff720fe"),
    (0x004C_B274, "fff71cfe"),
    (0x004C_B286, "fff713fe"),
    (0x004C_B28E, "fff70ffe"),
    (0x004C_B2E6, "fff7e3fd"),
    (0x004C_B2FE, "fff7d7fd"),
    (0x004C_B306, "fff7d3fd"),
    (0x004C_B56C, "fff7a0fc"),
    (0x004C_B574, "fff79cfc"),
    (0x004C_B64A, "fff731fc"),
    (0x004C_B786, "fff793fb"),
    (0x004C_B7EA, "fff761fb"),
    (0x004C_B92A, "fff7c1fa"),
    (0x004C_B936, "fff7bbfa"),
    (0x004C_B944, "fff7b4fa"),
    (0x004C_BC9E, "fff707f9"),
    (0x004C_BCAC, "fff700f9"),
    (0x004C_BCEE, "fff7dff8"),
    (0x004C_BCF8, "fff7daf8"),
    (0x004C_BDF8, "fff75af8"),
    (0x004C_BE02, "fff755f8"),
    (0x004C_BE3A, "fff739f8"),
    (0x004C_BE42, "fff735f8"),
    (0x004C_BE60, "fff726f8"),
    (0x004C_BE68, "fff722f8"),
    (0x004C_BE82, "fff715f8"),
    (0x004C_BEA0, "fff706f8"),
    (0x004C_C138, "fef7bafe"),
    (0x004C_C146, "fef7b3fe"),
    (0x004C_CE82, "fef715f8"),
    (0x004C_CEBE, "fdf7f7ff"),
    (0x004C_CF04, "fdf7d4ff"),
    (0x004C_D184, "fdf794fe"),
    (0x004C_D1B6, "fdf77bfe"),
    (0x004C_D2A8, "fdf702fe"),
    (0x004C_D58A, "fdf791fc"),
    (0x004C_D5A2, "fdf785fc"),
    (0x004C_E4C6, "fcf7f3fc"),
    (0x004C_E502, "fcf7d5fc"),
    (0x004C_E52A, "fcf7c1fc"),
    (0x004C_E59E, "fcf787fc"),
    (0x004C_E63C, "fcf738fc"),
    (0x004C_E66A, "fcf721fc"),
    (0x004C_E6A8, "fcf702fc"),
    (0x004C_E82C, "fcf740fb"),
    (0x004C_E89C, "fcf708fb"),
    (0x004C_F700, "fbf7d6fb"),
    (0x004C_F756, "fbf7abfb"),
    (0x004C_F894, "fbf70cfb"),
]
BOOT_CALLERS = [
    (0x0041_0F6A, "fff725fe"),
    (0x0041_0F74, "fff720fe"),
    (0x0041_0F7C, "fff71cfe"),
    (0x0041_0F8E, "fff713fe"),
    (0x0041_0F96, "fff70ffe"),
    (0x0041_0FEE, "fff7e3fd"),
    (0x0041_1006, "fff7d7fd"),
    (0x0041_100E, "fff7d3fd"),
    (0x0041_1274, "fff7a0fc"),
    (0x0041_127C, "fff79cfc"),
    (0x0041_1352, "fff731fc"),
    (0x0041_148E, "fff793fb"),
    (0x0041_14F2, "fff761fb"),
    (0x0041_1632, "fff7c1fa"),
    (0x0041_163E, "fff7bbfa"),
    (0x0041_164C, "fff7b4fa"),
    (0x0041_19A6, "fff707f9"),
    (0x0041_19B4, "fff700f9"),
    (0x0041_19F6, "fff7dff8"),
    (0x0041_1A00, "fff7daf8"),
    (0x0041_1B00, "fff75af8"),
    (0x0041_1B0A, "fff755f8"),
    (0x0041_1B42, "fff739f8"),
    (0x0041_1B4A, "fff735f8"),
    (0x0041_1B68, "fff726f8"),
    (0x0041_1B70, "fff722f8"),
    (0x0041_1B8A, "fff715f8"),
    (0x0041_1BA8, "fff706f8"),
    (0x0041_1D98, "fef70eff"),
    (0x0041_1DA6, "fef707ff"),
    (0x0041_2A86, "fef797f8"),
    (0x0041_2AC2, "fef779f8"),
    (0x0041_2B08, "fef756f8"),
    (0x0041_2D88, "fdf716ff"),
    (0x0041_2DBA, "fdf7fdfe"),
    (0x0041_2EAC, "fdf784fe"),
    (0x0041_318E, "fdf713fd"),
    (0x0041_31A6, "fdf707fd"),
    (0x0041_4DD0, "fbf7f2fe"),
    (0x0041_4E26, "fbf7c7fe"),
    (0x0041_4F64, "fbf728fe"),
]
CALLER_PINS = {
    "main": {
        "addresses": "8b299c57f8287b2897c79cabf888f16064f4cdb4ea60a91c2b81bb4a47a67f8a",
        "encodings": "6e0f0ed7af5c0c98793ac6dbef408721984f75c7c1b97de11082ca911a1c032c",
        "records": "6873a8429b442e11eb62f6f8b2af3332390b31b468a429609092eab5442536ce",
    },
    "boot": {
        "addresses": "274d04664805db5bbaa04be1e525f2ba476ee71e4e965499cfd3bff37ddb76bd",
        "encodings": "77b629db9b027cdd46c9a59eb2a5d00eb93ddfae3710909bc81a1a06ade7d548",
        "records": "f8d8594ec11e50553a9c7c050a88c3efa76ed134cb2399ec05a6bbee396b3e0b",
    },
}

COMMON_TARGET_FLAGS = (
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
)
TARGET_PROFILES = {
    "main": {
        "flags": ("--target=thumbv7em-none-eabi", "-mthumb", "-O2"),
        "alignment": 4,
        "object": (
            776,
            "4ae5a9c3581c22b232e9e8b46ed66df8"
            "bbd5a94d1790087615781664ac63be2a",
        ),
    },
    "boot": {
        "flags": (
            "--target=arm-none-eabi",
            "-mcpu=cortex-m55",
            "-mthumb",
            "-Oz",
        ),
        "alignment": 2,
        "object": (
            776,
            "12a1f7437db7132bf25a8d8011e0f69a"
            "40f083d6cc259f3bbcf195b244f8f15a",
        ),
    },
}
APPLE_CLANG = "/usr/bin/clang"
APPLE_CLANG_VERSION = "Apple clang version 21.0.0 (clang-2100.3.30.1)"
TARGET_TEXT = bytes.fromhex("c0f389207047")
TARGET_TEXT_PIN = (
    6,
    "6194594e24288e708887a0e938b2a544"
    "01c8c732210d91af7a5927d03bd3604c",
)

# Aggregate hashes are filled from independently verified Apple and exact-root
# Linux builds during the atomic overlay/manifest promotion. Leaf placements
# and complete redirects are deterministic before those aggregate builds.
PRODUCTION_PROFILES = {
    "apple-clang": {
        "main_leaf": (124_596, 0x007B_29D8),
        "boot_leaf": (650, 0x0043_4702),
        "main_patch": "e7f292bd00bf00bf",
        "boot_patch": "23f0a3bd00bf00bf",
        "main_overlay_size": 167_426,
        "main_overlay_sha256": (
            "b732d58cda6cf0a05c15e3eeb5beaa6bcf472a2822065ae6ca614a3417f7f6bf"
        ),
        "main_component_size": 3_690_822,
        "main_component_sha256": (
            "125cfeb1bda76cbb2cc7d7d1e6fab92e00c63c4f00f5fa8a893c6f33912a55f3"
        ),
        "boot_overlay_size": 662,
        "boot_overlay_sha256": (
            "7cb3c17a03dda3b8576d8288ffa61df1"
            "332d89f1f24d6c5877bf0143e233902b"
        ),
        "boot_component_size": 149_262,
        "boot_component_sha256": (
            "695688b7cc4d9583e9e5c854db44980a"
            "cab9a58d367bc7e02fa5e51eb00e3267"
        ),
        "package_size": 4_469_316,
        "package_sha256": (
            "26bf3d84c06987461340f6af8773e0ae59bd3ae75c630c00a2158fe3a4945058"
        ),
    },
    "linux-clang": {
        "main_leaf": (126_416, 0x007B_30F4),
        "boot_leaf": (650, 0x0043_4702),
        "main_patch": "e8f220b900bf00bf",
        "boot_patch": "23f0a3bd00bf00bf",
        "main_overlay_size": 145_208,
        "main_overlay_sha256": (
            "fac5b48b6ae2eac985a0a65ddb8d1595dd10e2abcbdd0c6a3bb562f72e43a826"
        ),
        "main_component_size": 3_668_604,
        "main_component_sha256": (
            "378c868e151060a59ab91b0de1a722e8678b8e1da8eede248c5702ccf8902798"
        ),
        "boot_overlay_size": 662,
        "boot_overlay_sha256": (
            "e4c743531f56c190b7e3129768d41048"
            "0a2f3433a5b680c7bf432ef0b05a7021"
        ),
        "boot_component_size": 149_262,
        "boot_component_sha256": (
            "fc3d07c8a59e1c33f26965cdb188811"
            "4412c3ca671d6137f7c3166acc81c8d74"
        ),
        "package_size": 4_447_098,
        "package_sha256": (
            "deb4cdb9d869abcb3aee5e122661ee45b541680cf277df5d1a7c6eed67bb7b6e"
        ),
    },
}

ORACLE_PREFIX = b"""\
#include <stdint.h>

typedef uint32_t lfs_tag_t;
"""
ORACLE_SUFFIX = b"""

uint16_t open_cfw_test_littlefs_tag_id_pristine(uint32_t tag)
{
    return lfs_tag_id(tag);
}
"""


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
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((first & 0x03FF) << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def wide_conditional_target(address: int, first: int, second: int) -> int | None:
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


class RuntimeLittlefsTagIdProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[PACKAGE_PREAMBLE:]
        cls.boot = BOOT_IMAGE.read_bytes()
        version = subprocess.run(
            [APPLE_CLANG, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        if version != APPLE_CLANG_VERSION:
            raise AssertionError(f"unreviewed compiler: {version!r}")

        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-littlefs-tag-id-production-",
        )
        temporary = Path(cls.temporary.name)
        definition = UPSTREAM.read_bytes()[slice(*UPSTREAM_DEFINITION)]
        oracle = temporary / "oracle.c"
        oracle.write_bytes(ORACLE_PREFIX + definition + ORACLE_SUFFIX)
        library = temporary / (
            "tag-id.dylib" if sys.platform == "darwin" else "tag-id.so"
        )
        command = [
            APPLE_CLANG,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(SOURCE.parent),
            str(SOURCE),
            str(oracle),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        cls.production = cls.library.open_cfw_littlefs_tag_id
        cls.pristine = cls.library.open_cfw_test_littlefs_tag_id_pristine
        for function in (cls.production, cls.pristine):
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint16

        cls.objects: dict[str, list[Path]] = {}
        for name, profile in TARGET_PROFILES.items():
            cls.objects[name] = []
            for index in range(2):
                output = temporary / f"production-{name}-{index}.o"
                subprocess.run(
                    [
                        APPLE_CLANG,
                        *profile["flags"],
                        *COMMON_TARGET_FLAGS,
                        "-c",
                        SOURCE_PATH,
                        "-o",
                        str(output),
                    ],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                cls.objects[name].append(output)

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def span(image: bytes, base: int, start: int, end: int) -> bytes:
        return image[start - base:end - base]

    def test_authenticated_upstream_source_and_dual_registration_are_exact(self) -> None:
        self.assertEqual(
            (len(self.main_package), sha256(self.main_package)),
            MAIN_PACKAGE_PIN,
        )
        self.assertEqual((len(self.main), sha256(self.main)), MAIN_PAYLOAD_PIN)
        self.assertEqual((len(self.boot), sha256(self.boot)), BOOT_PIN)
        self.assertEqual((SOURCE.stat().st_size, sha256(SOURCE)), SOURCE_PIN)
        self.assertEqual((HEADER.stat().st_size, sha256(HEADER)), HEADER_PIN)
        self.assertEqual((UPSTREAM.stat().st_size, sha256(UPSTREAM)), UPSTREAM_PIN)

        upstream = UPSTREAM.read_bytes()
        definition = upstream[slice(*UPSTREAM_DEFINITION)]
        self.assertEqual(
            (len(definition), sha256(definition)),
            UPSTREAM_DEFINITION_PIN,
        )
        self.assertEqual(
            definition,
            b"static inline uint16_t lfs_tag_id(lfs_tag_t tag) {\n"
            b"    return (tag & 0x000ffc00) >> 10;\n}\n\n",
        )
        typedef = upstream[slice(*UPSTREAM_TAG_TYPEDEF)]
        self.assertEqual((len(typedef), sha256(typedef)), UPSTREAM_TAG_TYPEDEF_PIN)
        self.assertEqual(typedef, b"typedef uint32_t lfs_tag_t;")

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["upstream"]["selected_tag"], "v2.10.1")
        self.assertEqual(provenance["upstream"]["selected_commit"], UPSTREAM_COMMIT)
        self.assertEqual(provenance["license"], "BSD-3-Clause")
        self.assertFalse(provenance["selection"]["exact_historical_checkout_proven"])

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn("Production adaptation", source)
        self.assertIn("redirected atomically", source)
        self.assertIn("(tag & UINT32_C(0x000ffc00)) >> 10U", source)
        self.assertIn("typedef uint32_t open_cfw_littlefs_id_tag_t", header)
        self.assertIn("sizeof(uint16_t) == 2U", header)

        integration = provenance["production_integration"]
        self.assertIn(SOURCE_PATH, integration["allowed_production_source_paths"])
        self.assertIn(HEADER_PATH, integration["allowed_production_source_paths"])
        self.assertIn(FUNCTION, integration["allowed_production_symbols"])
        leaf_provenance = integration["tag_id_leaf"]
        self.assertEqual(leaf_provenance["upstream_function"], "lfs_tag_id")
        self.assertEqual(
            (
                leaf_provenance["upstream_definition_offset"],
                leaf_provenance["upstream_definition_size"],
                leaf_provenance["upstream_definition_sha256"],
            ),
            (
                UPSTREAM_DEFINITION[0],
                UPSTREAM_DEFINITION_PIN[0],
                UPSTREAM_DEFINITION_PIN[1],
            ),
        )
        self.assertEqual(
            (
                leaf_provenance["local_source_size"],
                leaf_provenance["local_source_sha256"],
            ),
            SOURCE_PIN,
        )
        self.assertEqual(
            (
                leaf_provenance["local_header_size"],
                leaf_provenance["local_header_sha256"],
            ),
            HEADER_PIN,
        )
        self.assertEqual(
            (leaf_provenance["stock_size"], leaf_provenance["stock_sha256"]),
            (len(STOCK), STOCK_SHA256),
        )
        self.assertEqual(leaf_provenance["relocations"], [])

        configs = {
            "main": json.loads(MAIN_OVERLAY.read_text(encoding="utf-8")),
            "boot": json.loads(BOOT_OVERLAY.read_text(encoding="utf-8")),
        }
        for image_name, config in configs.items():
            self.assertIn(FUNCTION, config["functions"])
            leaves = [
                leaf
                for leaf in config["relocated_leaves"]
                if leaf["function"] == FUNCTION
            ]
            self.assertEqual(len(leaves), 1, image_name)
            leaf = leaves[0]
            self.assertEqual(
                {
                    key: leaf["source"][key]
                    for key in (
                        "path",
                        "size",
                        "sha256",
                        "license",
                        "upstream_commit",
                    )
                },
                {
                    "path": SOURCE_PATH,
                    "size": SOURCE_PIN[0],
                    "sha256": SOURCE_PIN[1],
                    "license": "BSD-3-Clause",
                    "upstream_commit": UPSTREAM_COMMIT,
                },
            )
            self.assertTrue(leaf["strict_relocation_contract"])
            self.assertEqual(leaf["relocations"], [])
            apple_offset = PRODUCTION_PROFILES["apple-clang"][
                f"{image_name}_leaf"
            ][0]
            alignment = 4 if image_name == "main" else 2
            self.assertEqual(
                leaf["expected"],
                {
                    "size": TARGET_TEXT_PIN[0],
                    "sha256": TARGET_TEXT_PIN[1],
                    "alignment": alignment,
                    "offset": apple_offset,
                    "unrelocated_sha256": TARGET_TEXT_PIN[1],
                },
            )
            linux = leaf["toolchain_profiles"]["linux-clang"]
            self.assertEqual(
                linux["reviewed_version_prefix"],
                "Homebrew clang version 22.1.8",
            )
            if image_name == "main":
                self.assertEqual(
                    linux["expected"],
                    {
                        "size": TARGET_TEXT_PIN[0],
                        "sha256": TARGET_TEXT_PIN[1],
                        "alignment": 4,
                        "offset": PRODUCTION_PROFILES["linux-clang"][
                            "main_leaf"
                        ][0],
                        "unrelocated_sha256": TARGET_TEXT_PIN[1],
                    },
                )
                self.assertEqual(linux["relocations"], [])
            else:
                self.assertNotIn("expected", linux)
                self.assertEqual(
                    config["function_profiles"]["linux-clang"][FUNCTION],
                    {
                        "expected_offset": apple_offset,
                        "expected_size": TARGET_TEXT_PIN[0],
                    },
                )
            patch = [
                item
                for item in config["patch_sites"]
                if item["target_function"] == FUNCTION
            ]
            self.assertEqual(
                patch,
                [{
                    "name": "replace_littlefs_tag_id",
                    "runtime_address": (
                        MAIN_START if image_name == "main" else BOOT_START
                    ),
                    "expected_size": len(STOCK),
                    "expected_sha256": STOCK_SHA256,
                    "branch": "b_w",
                    "target_function": FUNCTION,
                }],
            )

        for profile_name, pins in PRODUCTION_PROFILES.items():
            for image_name, config in configs.items():
                aggregate = (
                    config["expected"]
                    if profile_name == "apple-clang"
                    else config["toolchain_profiles"][profile_name]["expected"]
                )
                self.assertEqual(
                    aggregate["overlay_size"],
                    pins[f"{image_name}_overlay_size"],
                )
                self.assertEqual(
                    aggregate["overlay_sha256"],
                    pins[f"{image_name}_overlay_sha256"],
                )
                self.assertEqual(
                    aggregate["component_size"],
                    pins[f"{image_name}_component_size"],
                )
                self.assertEqual(
                    aggregate["component_sha256"],
                    pins[f"{image_name}_component_sha256"],
                )
                replacement = bytes.fromhex(pins[f"{image_name}_patch"])
                self.assertEqual(replacement[4:], bytes.fromhex("00bf") * 2)
                start = MAIN_START if image_name == "main" else BOOT_START
                self.assertEqual(
                    wide_branch_target(
                        start,
                        *struct.unpack("<HH", replacement[:4]),
                        link=False,
                    ),
                    pins[f"{image_name}_leaf"][1],
                )

            production_profile = leaf_provenance["production_profiles"][
                profile_name
            ]
            for image_name, component_name in (
                ("main", "apollo_main"),
                ("boot", "apollo_bootloader"),
            ):
                self.assertEqual(
                    production_profile[component_name],
                    {
                        "leaf_size": TARGET_TEXT_PIN[0],
                        "overlay_offset": pins[f"{image_name}_leaf"][0],
                        "runtime_address": (
                            f"0x{pins[f'{image_name}_leaf'][1]:08X}"
                        ),
                        "relocated_sha256": TARGET_TEXT_PIN[1],
                        "unrelocated_sha256": TARGET_TEXT_PIN[1],
                    },
                )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        boot = manifest["component_overrides"]["apollo_bootloader"]
        for profile_name, pins in PRODUCTION_PROFILES.items():
            package = (
                manifest["package"]
                if profile_name == "apple-clang"
                else manifest["package"]["profiles"][profile_name]
            )
            main_provider = (
                main["provider"]
                if profile_name == "apple-clang"
                else main["provider"]["profiles"][profile_name]
            )
            boot_provider = (
                boot["provider"]
                if profile_name == "apple-clang"
                else boot["provider"]["profiles"][profile_name]
            )
            self.assertEqual(package["expected_size"], pins["package_size"])
            self.assertEqual(
                package["expected_sha256"], pins["package_sha256"]
            )
            self.assertEqual(
                main_provider["size"], pins["main_component_size"]
            )
            self.assertEqual(
                main_provider["sha256"], pins["main_component_sha256"]
            )
            self.assertEqual(
                boot_provider["size"], pins["boot_component_size"]
            )
            self.assertEqual(
                boot_provider["sha256"], pins["boot_component_sha256"]
            )
            main_aggregate = (
                configs["main"]["expected"]
                if profile_name == "apple-clang"
                else configs["main"]["toolchain_profiles"][profile_name][
                    "expected"
                ]
            )
            boot_aggregate = (
                configs["boot"]["expected"]
                if profile_name == "apple-clang"
                else configs["boot"]["toolchain_profiles"][profile_name][
                    "expected"
                ]
            )
            self.assertEqual(
                main_provider["sha256"], main_aggregate["component_sha256"]
            )
            self.assertEqual(
                boot_provider["sha256"], boot_aggregate["component_sha256"]
            )

        main_regions = {region["name"]: region for region in main["regions"]}
        boot_regions = {region["name"]: region for region in boot["regions"]}
        expected_regions = {
            "opaque_between_littlefs_tag_chunk_and_littlefs_tag_id": (
                main_regions,
                601_798,
                10,
                0x004C_AEA6,
                "official_blob",
            ),
            "littlefs_tag_id_source_replacement": (
                main_regions,
                601_808,
                8,
                MAIN_START,
                "generated_source_entry_replacement",
            ),
            "littlefs_tag_size_source_replacement": (
                main_regions,
                601_816,
                6,
                0x004C_AEB8,
                "generated_source_entry_replacement",
            ),
            "apollo_littlefs_tag_id_source_alignment": (
                main_regions,
                3_647_990,
                2,
                0x007B_29D6,
                "generated_alignment",
            ),
            "apollo_littlefs_tag_id_source_leaf": (
                main_regions,
                3_647_992,
                6,
                0x007B_29D8,
                "source_compiled",
            ),
            "bootloader_littlefs_tag_id_source_replacement": (
                boot_regions,
                3_000,
                8,
                BOOT_START,
                "generated_source_entry_replacement",
            ),
            "bootloader_opaque_between_littlefs_tag_chunk_and_tag_id": (
                boot_regions,
                2_990,
                10,
                0x0041_0BAE,
                "official_blob",
            ),
            "bootloader_littlefs_tag_size_source_replacement": (
                boot_regions,
                3_008,
                6,
                0x0041_0BC0,
                "generated_source_entry_replacement",
            ),
            "bootloader_littlefs_tag_id_source_leaf": (
                boot_regions,
                149_250,
                6,
                0x0043_4702,
                "source_compiled",
            ),
        }
        for region_name, (
            regions,
            offset,
            size,
            address,
            status,
        ) in expected_regions.items():
            region = regions[region_name]
            self.assertEqual(
                (
                    region["file_offset"],
                    region["size"],
                    region["target_address"],
                    region["address_status"],
                ),
                (offset, size, address, status),
            )
        for component in (main, boot):
            regions = component["regions"]
            for previous, current in zip(regions, regions[1:]):
                self.assertEqual(
                    previous["file_offset"] + previous["size"],
                    current["file_offset"],
                    (previous["name"], current["name"]),
                )
            self.assertEqual(
                regions[-1]["file_offset"] + regions[-1]["size"],
                component["provider"]["size"],
            )

    def test_dual_image_stock_callers_and_outgoing_closure_are_exact(self) -> None:
        for name, image, base, start, end, callers in (
            ("main", self.main, MAIN_BASE, MAIN_START, MAIN_END, MAIN_CALLERS),
            ("boot", self.boot, BOOT_BASE, BOOT_START, BOOT_END, BOOT_CALLERS),
        ):
            stock = self.span(image, base, start, end)
            self.assertEqual(stock, STOCK, name)
            self.assertEqual(sha256(stock), STOCK_SHA256, name)
            records = []
            for address, expected_encoding in callers:
                encoding = self.span(image, base, address, address + 4)
                self.assertEqual(encoding.hex(), expected_encoding, (name, hex(address)))
                self.assertEqual(
                    wide_branch_target(
                        address,
                        *struct.unpack("<HH", encoding),
                        link=True,
                    ),
                    start,
                )
                records.append(struct.pack("<I", address) + encoding)
            pins = CALLER_PINS[name]
            self.assertEqual(
                sha256(b"".join(struct.pack("<I", address) for address, _ in callers)),
                pins["addresses"],
            )
            self.assertEqual(
                sha256(b"".join(bytes.fromhex(value) for _, value in callers)),
                pins["encodings"],
            )
            self.assertEqual(sha256(b"".join(records)), pins["records"])

            outgoing = []
            for offset in range(0, len(stock) - 1, 2):
                address = start + offset
                halfword = struct.unpack_from("<H", stock, offset)[0]
                for target in narrow_targets(address, halfword):
                    outgoing.append((address, "narrow", target))
                if offset + 4 <= len(stock):
                    first, second = struct.unpack_from("<HH", stock, offset)
                    for link in (True, False):
                        target = wide_branch_target(address, first, second, link=link)
                        if target is not None:
                            outgoing.append((address, "bl" if link else "bw", target))
                    target = wide_conditional_target(address, first, second)
                    if target is not None:
                        outgoing.append((address, "wide-conditional", target))
            self.assertEqual(outgoing, [], name)

    def test_complete_dual_image_ingress_pointer_and_fallthrough_closure(self) -> None:
        for name, image, base, start, end, callers in (
            ("main", self.main, MAIN_BASE, MAIN_START, MAIN_END, MAIN_CALLERS),
            ("boot", self.boot, BOOT_BASE, BOOT_START, BOOT_END, BOOT_CALLERS),
        ):
            incoming_bl = []
            incoming_bw = []
            interior = []
            conditional = []
            for offset in range(0, len(image) - 3, 2):
                address = base + offset
                first, second = struct.unpack_from("<HH", image, offset)
                for link, owner in ((True, incoming_bl), (False, incoming_bw)):
                    target = wide_branch_target(address, first, second, link=link)
                    if target is None or not start <= target < end:
                        continue
                    if target == start:
                        owner.append((address, image[offset:offset + 4].hex()))
                    elif not start <= address < end:
                        interior.append((address, target, link))
                target = wide_conditional_target(address, first, second)
                if (
                    target is not None
                    and start <= target < end
                    and not start <= address < end
                ):
                    conditional.append((address, target))

            narrow = []
            final_halfword = None
            for offset in range(0, len(image) - 1, 2):
                address = base + offset
                final_halfword = address
                if start <= address < end:
                    continue
                halfword = struct.unpack_from("<H", image, offset)[0]
                for target in narrow_targets(address, halfword):
                    if start <= target < end:
                        narrow.append((address, target))
            self.assertEqual(
                final_halfword,
                base + 2 * ((len(image) - 2) // 2),
                name,
            )

            stored = []
            for canonical in range(start, end):
                for value in {canonical, canonical | 1}:
                    needle = struct.pack("<I", value)
                    cursor = 0
                    while True:
                        position = image.find(needle, cursor)
                        if position < 0:
                            break
                        stored.append((base + position, value, canonical))
                        cursor = position + 1

            self.assertEqual(incoming_bl, callers, name)
            self.assertEqual(incoming_bw, [], name)
            self.assertEqual(interior, [], name)
            self.assertEqual(conditional, [], name)
            self.assertEqual(narrow, [], name)
            self.assertEqual(stored, [], name)
            self.assertEqual(
                self.span(image, base, start - 4, start),
                PREDECESSOR_WINDOW,
                name,
            )
            self.assertEqual(
                self.span(image, base, start - 2, start),
                PREDECESSOR_RETURN,
                name,
            )
            self.assertEqual(
                self.span(image, base, end - 2, end),
                bytes.fromhex("7047"),
                name,
            )
            self.assertEqual(
                self.span(image, base, end, end + 2),
                SUCCESSOR_PREFIX,
                name,
            )

    def test_production_adapter_matches_pristine_definition_broadly(self) -> None:
        directed = (
            0x0000_0000,
            0xFFFF_FFFF,
            0x000F_FC00,
            0x8000_0000,
            0x0000_0400,
            0x1234_5678,
            0xA5A5_5A5A,
            0xFFE0_03FF,
        )
        for tag in directed:
            expected = (tag & 0x000F_FC00) >> 10
            self.assertEqual(self.production(tag), expected, hex(tag))
            self.assertEqual(self.production(tag), self.pristine(tag), hex(tag))

        for window in range(1 << 16):
            low = (window * 0x9E37 + 0x5A) & 0xFF
            high = ((window * 0x45D9 + 0xA5) & 0xFF) << 24
            tag = high | (window << 8) | low
            self.assertEqual(self.production(tag), self.pristine(tag), hex(tag))

        rng = random.Random(0x4C_AEB0)
        for _ in range(20_000):
            tag = rng.getrandbits(32)
            self.assertEqual(self.production(tag), self.pristine(tag), hex(tag))

    def test_apple_main_and_boot_objects_are_deterministic_and_closed(self) -> None:
        for name, profile in TARGET_PROFILES.items():
            first = self.objects[name][0].read_bytes()
            second = self.objects[name][1].read_bytes()
            self.assertEqual(first, second, name)
            self.assertEqual((len(first), sha256(first)), profile["object"], name)

            leaf, extraction = self.apollo_overlay.extract_isolated_function_section(
                self.objects[name][0],
                FUNCTION,
            )
            self.assertEqual(leaf, TARGET_TEXT, name)
            self.assertEqual((len(leaf), sha256(leaf)), TARGET_TEXT_PIN, name)
            self.assertEqual(
                extraction,
                {
                    "function": FUNCTION,
                    "section": SECTION,
                    "size": TARGET_TEXT_PIN[0],
                    "sha256": TARGET_TEXT_PIN[1],
                    "alignment": profile["alignment"],
                    "relocation_count": 0,
                    "discarded_alloc_section_count": 1,
                    "discarded_alloc_section_bytes": 8,
                    "discarded_alloc_sections": [
                        {
                            "name": ".ARM.exidx" + SECTION,
                            "size": 8,
                            "flags": 130,
                        }
                    ],
                },
                name,
            )

            data, sections = self.apollo_overlay.parse_elf32(self.objects[name][0])
            symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
            undefined = sorted(
                symbol["name"]
                for symbol in symbols
                if symbol["name"] and symbol["section_index"] == 0
            )
            self.assertEqual(undefined, [], name)


if __name__ == "__main__":
    unittest.main()
