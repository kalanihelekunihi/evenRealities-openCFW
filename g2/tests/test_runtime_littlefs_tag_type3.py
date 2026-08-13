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
SOURCE = ROOT / "components/shared/littlefs/runtime_littlefs_tag_type3.c"
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

FUNCTION = "open_cfw_littlefs_tag_type3"
SECTION = ".text." + FUNCTION
MAIN_BASE = 0x0043_8000
BOOT_BASE = 0x0041_0000
MAIN_START = 0x004C_AE98
MAIN_END = 0x004C_AEA0
BOOT_START = 0x0041_0BA0
BOOT_END = 0x0041_0BA8
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
    857,
    "6940b4ac0622dc1f2b84a0c663dc1522"
    "dfc7b198f59d6f452828adfd299e37c8",
)
HEADER_PIN = (
    893,
    "4e3b70d5ad8e8fce0e5dc2bd43fc8459"
    "c62c742d84a93f949bf0dd4fb44fe869",
)
UPSTREAM_PIN = (
    196_753,
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398",
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_DEFINITION = (10_420, 10_514)
UPSTREAM_DEFINITION_PIN = (
    94,
    "3cc2c9ec46ebb7fc3d3d71c6b39b235a"
    "5da0cde23adf2c182cafd24d6410b53e",
)
UPSTREAM_TAG_TYPEDEF = (9_602, 9_629)
UPSTREAM_TAG_TYPEDEF_PIN = (
    27,
    "cb4dcd6212b1a269371d86dddf98ed7"
    "4853e2eb43753c5d8f8659abbca167ce2",
)

STOCK = bytes.fromhex("000d4005400d7047")
STOCK_SHA256 = (
    "818012c47ba81ee18e2996d51a8a29a9"
    "6a78ced50854b6fefcebf92e7b9ed9d6"
)
PREDECESSOR_RETURN = bytes.fromhex("7047")
SUCCESSOR_PREFIX = bytes.fromhex("000d")
MAIN_CALLERS = [
    (0x004C_B70A, "fff7c5fb"),
    (0x004C_B716, "fff7bffb"),
    (0x004C_B7C0, "fff76afb"),
    (0x004C_BD5E, "fff79bf8"),
    (0x004C_BF82, "fef789ff"),
    (0x004C_BFB2, "fef771ff"),
    (0x004C_BFC6, "fef767ff"),
    (0x004C_C07E, "fef70bff"),
    (0x004C_C12E, "fef7b3fe"),
    (0x004C_CBDC, "fef75cf9"),
    (0x004C_CC18, "fef73ef9"),
    (0x004C_CE72, "fef711f8"),
    (0x004C_CEB2, "fdf7f1ff"),
    (0x004C_CEF8, "fdf7ceff"),
    (0x004C_D57A, "fdf78dfc"),
    (0x004C_DB46, "fdf7a7f9"),
    (0x004C_DC4C, "fdf724f9"),
    (0x004C_E4B6, "fcf7effc"),
    (0x004C_E520, "fcf7bafc"),
    (0x004C_E5C8, "fcf766fc"),
    (0x004C_E6C6, "fcf7e7fb"),
    (0x004C_E702, "fcf7c9fb"),
    (0x004C_E70A, "fcf7c5fb"),
    (0x004C_E718, "fcf7befb"),
    (0x004C_E746, "fcf7a7fb"),
    (0x004C_E802, "fcf749fb"),
    (0x004C_E8CA, "fcf7e5fa"),
    (0x004C_F346, "fbf7a7fd"),
    (0x004C_F376, "fbf78ffd"),
    (0x004C_F726, "fbf7b7fb"),
]
BOOT_CALLERS = [
    (0x0041_1412, "fff7c5fb"),
    (0x0041_141E, "fff7bffb"),
    (0x0041_14C8, "fff76afb"),
    (0x0041_1A66, "fff79bf8"),
    (0x0041_1CDE, "fef75fff"),
    (0x0041_1D8E, "fef707ff"),
    (0x0041_27E0, "fef7def9"),
    (0x0041_281C, "fef7c0f9"),
    (0x0041_2A76, "fef793f8"),
    (0x0041_2AB6, "fef773f8"),
    (0x0041_2AFC, "fef750f8"),
    (0x0041_317E, "fdf70ffd"),
    (0x0041_3696, "fdf783fa"),
    (0x0041_379C, "fdf700fa"),
    (0x0041_4A16, "fcf7c3f8"),
    (0x0041_4A46, "fcf7abf8"),
    (0x0041_4DF6, "fbf7d3fe"),
]
CALLER_PINS = {
    "main": {
        "addresses": "0118197b8b33207bd4188384b00ebe8f400a19780ae2cb6fc0e71fe739a31d66",
        "encodings": "039114068b0da49cd7ca9239b368c44b0ab5d349eae96288450f15cc9cfa16b4",
        "records": "0017668c7690b4edba82415b7023fcbae82ea720454a214375425b088298d88a",
    },
    "boot": {
        "addresses": "24880dfe7ab1b30670330e5eaffda21683118091f906c7ef36403b102989029f",
        "encodings": "67aea6e13012127639aa8163680a3f4fc7a319a81f0b11cd643268f520b7fbe0",
        "records": "6ca71e2e3014534a257564169eef0afdb50e554b2fc2be6bc6401270b55a5616",
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
            784,
            "e314943356d7da90680a50e249b082c8"
            "3a4ca105f2a6e4bc2173495f9be52a31",
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
            784,
            "745001dad9d930eb56e1ac3799ddf71c"
            "29506e4662703ccbc7daa2a7a14f55f9",
        ),
    },
}
APPLE_CLANG = "/usr/bin/clang"
APPLE_CLANG_VERSION = "Apple clang version 21.0.0 (clang-2100.3.30.1)"
TARGET_TEXT = bytes.fromhex("c0f30a507047")
TARGET_TEXT_PIN = (
    6,
    "a6781f0a92086cca25476ca00824d8f0"
    "fd736ac7d800aa9e3f6e4d6544490921",
)

PRODUCTION_PROFILES = {
    "apple-clang": {
        "main_leaf": (124_588, 0x007B_29D0),
        "boot_leaf": (644, 0x0043_46FC),
        "main_patch": "e7f29abd00bf00bf",
        "boot_patch": "23f0acbd00bf00bf",
        "main_overlay": (
            125_258,
            "1f71240bd75af28798d93eba217b99464156ee40ae353333c2fd0f449b9a8c76",
        ),
        "main_component": (
            3_648_654,
            "36b7f32f9f5f1a4c2fbf800b8cda0f48aa521bfc87638d671932b80b49f7e991",
        ),
        "boot_overlay": (
            662,
            "7cb3c17a03dda3b8576d8288ffa61df1332d89f1f24d6c5877bf0143e233902b",
        ),
        "boot_component": (
            149_262,
            "695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267",
        ),
        "package": (
            4_427_148,
            "532743c6a1b96f198f0991c320bf3318eac88bc538a90a9e0b0267aaacef07b3",
        ),
    },
    "linux-clang": {
        "main_leaf": (126_408, 0x007B_30EC),
        "boot_leaf": (644, 0x0043_46FC),
        "main_patch": "e8f228b900bf00bf",
        "boot_patch": "23f0acbd00bf00bf",
        "main_overlay": (
            132_888,
            "7036c0e07a36376e5d98700c922ffeec7a6826388b75060a2b98b4228a411c61",
        ),
        "main_component": (
            3_656_284,
            "d5daf89121f44a61b303fa953da78550edd31e9159cf9b0b397aeb1b5cfef54d",
        ),
        "boot_overlay": (
            662,
            "e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021",
        ),
        "boot_component": (
            149_262,
            "fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74",
        ),
        "package": (
            4_434_778,
            "63d5cd1d1cbab2c3ece4a48f96b58a0cb14a7487917831f4c6d370b40ed41d90",
        ),
    },
}

ORACLE_PREFIX = b"""\
#include <stdint.h>

typedef uint32_t lfs_tag_t;
"""
ORACLE_SUFFIX = b"""

uint16_t open_cfw_test_littlefs_tag_type3_pristine(uint32_t tag)
{
    return lfs_tag_type3(tag);
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


class RuntimeLittlefsTagType3ProductionTests(unittest.TestCase):
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
            prefix="open-cfw-littlefs-tag-type3-production-",
            dir=ROOT / "build",
        )
        temporary = Path(cls.temporary.name)
        definition = UPSTREAM.read_bytes()[slice(*UPSTREAM_DEFINITION)]
        oracle = temporary / "oracle.c"
        oracle.write_bytes(ORACLE_PREFIX + definition + ORACLE_SUFFIX)
        library = temporary / (
            "tag-type3.dylib" if sys.platform == "darwin" else "tag-type3.so"
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
        cls.production_adapter = cls.library.open_cfw_littlefs_tag_type3
        cls.pristine = cls.library.open_cfw_test_littlefs_tag_type3_pristine
        for function in (cls.production_adapter, cls.pristine):
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

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
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
            b"static inline uint16_t lfs_tag_type3(lfs_tag_t tag) {\n"
            b"    return (tag & 0x7ff00000) >> 20;\n}\n\n",
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
        self.assertIn("(tag & UINT32_C(0x7ff00000)) >> 20U", source)
        self.assertIn("typedef uint32_t open_cfw_littlefs_type3_tag_t", header)
        self.assertIn("sizeof(uint16_t) == 2U", header)
        integration = provenance["production_integration"]
        self.assertIn(SOURCE_PATH, integration["allowed_production_source_paths"])
        self.assertIn(HEADER_PATH, integration["allowed_production_source_paths"])
        self.assertIn(FUNCTION, integration["allowed_production_symbols"])
        leaf_provenance = integration["tag_type3_leaf"]
        self.assertEqual(leaf_provenance["upstream_function"], "lfs_tag_type3")
        self.assertEqual(
            (
                leaf_provenance["upstream_definition_offset"],
                leaf_provenance["upstream_definition_size"],
                leaf_provenance["upstream_definition_sha256"],
            ),
            (UPSTREAM_DEFINITION[0], UPSTREAM_DEFINITION_PIN[0], UPSTREAM_DEFINITION_PIN[1]),
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
                    for key in ("path", "size", "sha256", "license", "upstream_commit")
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
            apple_offset = PRODUCTION_PROFILES["apple-clang"][f"{image_name}_leaf"][0]
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
                        "offset": PRODUCTION_PROFILES["linux-clang"]["main_leaf"][0],
                        "unrelocated_sha256": TARGET_TEXT_PIN[1],
                    },
                )
                self.assertEqual(linux["relocations"], [])
            else:
                self.assertNotIn("expected", linux)
                self.assertEqual(
                    config["function_profiles"]["linux-clang"][FUNCTION],
                    {"expected_offset": apple_offset, "expected_size": TARGET_TEXT_PIN[0]},
                )
            patch = [
                item for item in config["patch_sites"]
                if item["target_function"] == FUNCTION
            ]
            self.assertEqual(
                patch,
                [{
                    "name": "replace_littlefs_tag_type3",
                    "runtime_address": MAIN_START if image_name == "main" else BOOT_START,
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
                    (aggregate["overlay_size"], aggregate["overlay_sha256"]),
                    pins[f"{image_name}_overlay"],
                )
                self.assertEqual(
                    (aggregate["component_size"], aggregate["component_sha256"]),
                    pins[f"{image_name}_component"],
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
            production_profile = leaf_provenance["production_profiles"][profile_name]
            for image_name, component_name in (
                ("main", "apollo_main"),
                ("boot", "apollo_bootloader"),
            ):
                self.assertEqual(
                    production_profile[component_name],
                    {
                        "leaf_size": TARGET_TEXT_PIN[0],
                        "overlay_offset": pins[f"{image_name}_leaf"][0],
                        "runtime_address": f"0x{pins[f'{image_name}_leaf'][1]:08X}",
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
            self.assertEqual(
                (package["expected_size"], package["expected_sha256"]),
                pins["package"],
            )
            self.assertEqual(
                (main_provider["size"], main_provider["sha256"]),
                pins["main_component"],
            )
            self.assertEqual(
                (boot_provider["size"], boot_provider["sha256"]),
                pins["boot_component"],
            )

        main_regions = {region["name"]: region for region in main["regions"]}
        boot_regions = {region["name"]: region for region in boot["regions"]}
        expected_regions = {
            "littlefs_tag_type3_source_replacement": (
                main_regions, 601_784, 8, MAIN_START,
                "generated_source_entry_replacement",
            ),
            "apollo_littlefs_tag_type3_source_alignment": (
                main_regions, 3_647_982, 2, 0x007B_29CE, "generated_alignment",
            ),
            "apollo_littlefs_tag_type3_source_leaf": (
                main_regions, 3_647_984, 6, 0x007B_29D0, "source_compiled",
            ),
            "bootloader_littlefs_tag_type3_source_replacement": (
                boot_regions, 2_976, 8, BOOT_START,
                "generated_source_entry_replacement",
            ),
            "bootloader_littlefs_tag_type3_source_leaf": (
                boot_regions, 149_244, 6, 0x0043_46FC, "source_compiled",
            ),
        }
        for region_name, (regions, offset, size, address, status) in expected_regions.items():
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
            0x7FF0_0000,
            0x8000_0000,
            0x0010_0000,
            0x1234_5678,
            0xA5A5_5A5A,
            0xFFE0_03FF,
        )
        for tag in directed:
            expected = (tag & 0x7FF0_0000) >> 20
            self.assertEqual(self.production_adapter(tag), expected, hex(tag))
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

        for upper in range(1 << 16):
            lower = (upper * 0x9E37 + 0x5A5A) & 0xFFFF
            tag = (upper << 16) | lower
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

        rng = random.Random(0x4C_AE98)
        for _ in range(20_000):
            tag = rng.getrandbits(32)
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

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
