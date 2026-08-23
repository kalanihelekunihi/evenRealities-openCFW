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
SOURCE = ROOT / "components/shared/littlefs/runtime_littlefs_tag_size.c"
HEADER = SOURCE.with_suffix(".h")
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
HEADER_PATH = HEADER.relative_to(ROOT).as_posix()
UPSTREAM = ROOT / "third_party/littlefs/lfs.c"
UPSTREAM_HEADER = ROOT / "third_party/littlefs/lfs.h"
PROVENANCE = ROOT / "third_party/littlefs/PROVENANCE.json"
MAIN_PACKAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN_OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BOOT_OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

FUNCTION = "open_cfw_littlefs_tag_size"
SECTION = ".text." + FUNCTION
MAIN_BASE = 0x0043_8000
BOOT_BASE = 0x0041_0000
MAIN_START = 0x004C_AEB8
MAIN_END = 0x004C_AEBE
BOOT_START = 0x0041_0BC0
BOOT_END = 0x0041_0BC6
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
    854,
    "533bbfcbfc2440e02b79692a2a7ccff8"
    "7c3cb62cbb0788c1d5bf806fd3bca849",
)
HEADER_PIN = (
    1_000,
    "0f29febdc25b081de1821a41c9065870"
    "c02154375985bf648d8e1b63f6cc3528",
)
UPSTREAM_PIN = (
    196_753,
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398",
)
UPSTREAM_HEADER_PIN = (
    26_439,
    "ee44e99d6b19119b3e577b969b80c9d5"
    "e6f96410c9593794afddf6d4b314c486",
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_DEFINITION = (10_793, 10_880)
UPSTREAM_DEFINITION_PIN = (
    87,
    "9df85bc43ca9f90ef58c425c5fd9bbbb"
    "f53585093be5fad0cc580fc88814ea5c",
)
UPSTREAM_TAG_TYPEDEF = (9_602, 9_629)
UPSTREAM_TAG_TYPEDEF_PIN = (
    27,
    "cb4dcd6212b1a269371d86dddf98ed7"
    "4853e2eb43753c5d8f8659abbca167ce2",
)
UPSTREAM_SIZE_TYPEDEF = (974, 1_002)
UPSTREAM_SIZE_TYPEDEF_PIN = (
    28,
    "e61a4bdad54f4bb8a78f53764fd104337"
    "6bd4d922f34d2dd554beab89cd0561f",
)

STOCK = bytes.fromhex("8005800d7047")
STOCK_SHA256 = (
    "8596106584e598a657aea7fdd2e1156a"
    "748158d2d63d9c121c92587fabbdf8ca"
)
PREDECESSOR_RETURN = bytes.fromhex("7047")
SUCCESSOR_PREFIX = bytes.fromhex("10b5")
MAIN_CALLERS = [
    (0x004C_AECC, "fff7f4ff"),
    (0x004C_AF10, "fff7d2ff"),
    (0x004C_AF26, "fff7c7ff"),
    (0x004C_AF48, "fff7b6ff"),
    (0x004C_B368, "fff7a6fd"),
    (0x004C_B3D4, "fff770fd"),
    (0x004C_B77E, "fff79bfb"),
    (0x004C_B7DA, "fff76dfb"),
    (0x004C_BFD4, "fef770ff"),
    (0x004C_BFFA, "fef75dff"),
    (0x004C_C026, "fef747ff"),
    (0x004C_C032, "fef741ff"),
    (0x004C_DC5C, "fdf72cf9"),
    (0x004C_F578, "fbf79efc"),
    (0x004C_F59E, "fbf78bfc"),
]
BOOT_CALLERS = [
    (0x0041_0BD4, "fff7f4ff"),
    (0x0041_0C18, "fff7d2ff"),
    (0x0041_0C2E, "fff7c7ff"),
    (0x0041_0C50, "fff7b6ff"),
    (0x0041_1070, "fff7a6fd"),
    (0x0041_10DC, "fff770fd"),
    (0x0041_1486, "fff79bfb"),
    (0x0041_14E2, "fff76dfb"),
    (0x0041_1C5A, "fef7b1ff"),
    (0x0041_1C86, "fef79bff"),
    (0x0041_1C92, "fef795ff"),
    (0x0041_37AC, "fdf708fa"),
    (0x0041_4C48, "fbf7baff"),
    (0x0041_4C6E, "fbf7a7ff"),
]
CALLER_PINS = {
    "main": {
        "addresses": "e23410e3b34d0ccc5f7d7e90b1a02d2544b6cf8421bf0fb96f90468917a92901",
        "encodings": "107e3c7e125825108b2f90ed90762b9ad9010bf1873fb06300087e3379884dcd",
        "records": "320fa8bc85f88a2dc10bd929a751cc9a0f9a82161a3fdb3102ef6e674beb72b9",
    },
    "boot": {
        "addresses": "404e52ad9b8da4197b6fcd0aae1982284e47f1c4a70437df6ea432cc9fafd275",
        "encodings": "5b072bdf79d01c7c43b3c3c6e8fec8d71d2166b1972c5aa397d3089c68b61db2",
        "records": "3cedd904ff7bce58fe38992ad70830407b6389a1cc20c9ca54f28c5802f5e401",
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
            780,
            "a8325647f526cf10d9e5d82df49358fd"
            "c1d4b1f6b2f9ba2a6c15fc085f7f29b7",
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
            780,
            "37511de65a26da5a2d3bf7356f8501355"
            "02a14b3426c7da6c1ea3f84d59cb9bf",
        ),
    },
}
APPLE_CLANG = "/usr/bin/clang"
APPLE_CLANG_VERSION = "Apple clang version 21.0.0 (clang-2100.3.30.1)"
TARGET_TEXT = bytes.fromhex("6ff39f207047")
TARGET_TEXT_PIN = (
    6,
    "35890ebcdee5cb7f51b3e8d874201b7e"
    "0214f6111eebe56c772133f259cf9b54",
)

# Aggregate hashes are filled from independently verified Apple and exact-root
# Linux builds during the atomic overlay/manifest promotion. Leaf placements
# and complete redirects are deterministic before those aggregate builds.
PRODUCTION_PROFILES = {
    "apple-clang": {
        "main_leaf": (124_604, 0x007B_29E0),
        "boot_leaf": (656, 0x0043_4708),
        "main_patch": "e7f292bd00bf",
        "boot_patch": "23f0a2bd00bf",
        "main_overlay_size": 165_412,
        "main_overlay_sha256": (
            "91449e27a73806e1537548657bed4486d77b275e4ee8a58b2bb1ef527c252ada"
        ),
        "main_component_size": 3_688_808,
        "main_component_sha256": (
            "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c"
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
        "package_size": 4_467_302,
        "package_sha256": (
            "88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f"
        ),
    },
    "linux-clang": {
        "main_leaf": (126_424, 0x007B_30FC),
        "boot_leaf": (656, 0x0043_4708),
        "main_patch": "e8f220b900bf",
        "boot_patch": "23f0a2bd00bf",
        "main_overlay_size": 145_180,
        "main_overlay_sha256": (
            "afbcb57a8414e65a18c6c95396a0f32fe454cb2087e6a03d51717196a4854b57"
        ),
        "main_component_size": 3_668_576,
        "main_component_sha256": (
            "292f55478951dc8d41a8bc5e4cc01f80ae88f9c44350d8fec89958c939a4fac5"
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
        "package_size": 4_447_070,
        "package_sha256": (
            "be5c62a97b9d31f4df257615c28ce81d79ab186feadb68262f96ac5bc35a1c25"
        ),
    },
}

ORACLE_PREFIX = b"""\
#include <stdint.h>

typedef uint32_t lfs_tag_t;
typedef uint32_t lfs_size_t;
"""
ORACLE_SUFFIX = b"""

uint32_t open_cfw_test_littlefs_tag_size_pristine(uint32_t tag)
{
    return lfs_tag_size(tag);
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


class RuntimeLittlefsTagSizeProductionTests(unittest.TestCase):
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
            prefix="open-cfw-littlefs-tag-size-production-",
        )
        temporary = Path(cls.temporary.name)
        definition = UPSTREAM.read_bytes()[slice(*UPSTREAM_DEFINITION)]
        oracle = temporary / "oracle.c"
        oracle.write_bytes(ORACLE_PREFIX + definition + ORACLE_SUFFIX)
        library = temporary / (
            "tag-size.dylib" if sys.platform == "darwin" else "tag-size.so"
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
        cls.production = cls.library.open_cfw_littlefs_tag_size
        cls.pristine = cls.library.open_cfw_test_littlefs_tag_size_pristine
        for function in (cls.production, cls.pristine):
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32

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
        self.assertEqual(
            (UPSTREAM_HEADER.stat().st_size, sha256(UPSTREAM_HEADER)),
            UPSTREAM_HEADER_PIN,
        )

        upstream = UPSTREAM.read_bytes()
        definition = upstream[slice(*UPSTREAM_DEFINITION)]
        self.assertEqual(
            (len(definition), sha256(definition)),
            UPSTREAM_DEFINITION_PIN,
        )
        self.assertEqual(
            definition,
            b"static inline lfs_size_t lfs_tag_size(lfs_tag_t tag) {\n"
            b"    return tag & 0x000003ff;\n}\n\n",
        )
        typedef = upstream[slice(*UPSTREAM_TAG_TYPEDEF)]
        self.assertEqual((len(typedef), sha256(typedef)), UPSTREAM_TAG_TYPEDEF_PIN)
        self.assertEqual(typedef, b"typedef uint32_t lfs_tag_t;")
        upstream_header = UPSTREAM_HEADER.read_bytes()
        size_typedef = upstream_header[slice(*UPSTREAM_SIZE_TYPEDEF)]
        self.assertEqual(
            (len(size_typedef), sha256(size_typedef)),
            UPSTREAM_SIZE_TYPEDEF_PIN,
        )
        self.assertEqual(size_typedef, b"typedef uint32_t lfs_size_t;")

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["upstream"]["selected_tag"], "v2.10.1")
        self.assertEqual(provenance["upstream"]["selected_commit"], UPSTREAM_COMMIT)
        self.assertEqual(provenance["license"], "BSD-3-Clause")
        self.assertFalse(provenance["selection"]["exact_historical_checkout_proven"])

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn("Production adaptation", source)
        self.assertIn("redirected atomically", source)
        self.assertIn("tag & UINT32_C(0x000003ff)", source)
        self.assertIn("typedef uint32_t open_cfw_littlefs_size_tag_t", header)
        self.assertIn("typedef uint32_t open_cfw_littlefs_size_t", header)
        self.assertIn("sizeof(open_cfw_littlefs_size_t) == 4U", header)

        integration = provenance["production_integration"]
        self.assertIn(SOURCE_PATH, integration["allowed_production_source_paths"])
        self.assertIn(HEADER_PATH, integration["allowed_production_source_paths"])
        self.assertIn(FUNCTION, integration["allowed_production_symbols"])
        leaf_provenance = integration["tag_size_leaf"]
        self.assertEqual(leaf_provenance["upstream_function"], "lfs_tag_size")
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
                    "name": "replace_littlefs_tag_size",
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
                self.assertEqual(replacement[4:], bytes.fromhex("00bf"))
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
            "littlefs_tag_size_source_replacement": (
                main_regions,
                601_816,
                6,
                MAIN_START,
                "generated_source_entry_replacement",
            ),
            "opaque_between_littlefs_tag_size_and_littlefs_mlist_isopen": (
                main_regions,
                601_822,
                452,
                0x004C_AEBE,
                "official_blob",
            ),
            "apollo_littlefs_tag_size_source_alignment": (
                main_regions,
                3_647_998,
                2,
                0x007B_29DE,
                "generated_alignment",
            ),
            "apollo_littlefs_tag_size_source_leaf": (
                main_regions,
                3_648_000,
                6,
                0x007B_29E0,
                "source_compiled",
            ),
            "bootloader_littlefs_tag_size_source_replacement": (
                boot_regions,
                3_008,
                6,
                BOOT_START,
                "generated_source_entry_replacement",
            ),
            "bootloader_opaque_between_littlefs_tag_size_and_mlist_isopen": (
                boot_regions,
                3_014,
                452,
                0x0041_0BC6,
                "official_blob",
            ),
            "bootloader_littlefs_tag_size_source_leaf": (
                boot_regions,
                149_256,
                6,
                0x0043_4708,
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
                self.span(image, base, start - 2, start),
                PREDECESSOR_RETURN,
                name,
            )
            self.assertEqual(
                self.span(image, base, end - 2, end),
                PREDECESSOR_RETURN,
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
            0x0000_03FF,
            0x0000_0400,
            0x8000_0000,
            0x0000_0001,
            0x1234_5678,
            0xA5A5_5A5A,
            0xFFFF_FC00,
        )
        for tag in directed:
            expected = tag & 0x0000_03FF
            self.assertEqual(self.production(tag), expected, hex(tag))
            self.assertEqual(self.production(tag), self.pristine(tag), hex(tag))

        for lower in range(1 << 16):
            upper = (lower * 0x9E37 + 0x5A5A) & 0xFFFF
            tag = (upper << 16) | lower
            self.assertEqual(self.production(tag), self.pristine(tag), hex(tag))

        rng = random.Random(0x4C_AEB8)
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
