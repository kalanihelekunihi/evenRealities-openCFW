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
SOURCE = ROOT / "components/shared/littlefs/runtime_littlefs_tag_isvalid.c"
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
MAIN_BUILD = ROOT / "components/apollo_main/core_overlay/build"
BOOT_BUILD = ROOT / "components/bootloader/core_overlay/build"
PACKAGE_BUILD = ROOT / "build/source"

FUNCTION = "open_cfw_littlefs_tag_isvalid"
SECTION = ".text." + FUNCTION
MAIN_BASE = 0x0043_8000
BOOT_BASE = 0x0041_0000
MAIN_START = 0x004C_AE6A
MAIN_END = 0x004C_AE74
BOOT_START = 0x0041_0B72
BOOT_END = 0x0041_0B7C
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
    848,
    "a91417d6193cdfb9589cd9e62f9b6eeb"
    "e65e1e11a75ca36d0f42d85c36d907a2",
)
HEADER_PIN = (
    928,
    "6efcd1b229fb0477285f8fbdfbc6f1c9"
    "2701a787fb17995a6115bfa5a944c6cd",
)
UPSTREAM_PIN = (
    196_753,
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398",
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_DEFINITION = (10_042, 10_129)
UPSTREAM_DEFINITION_PIN = (
    87,
    "bb8e571d6dbddd1fe446ec7b4838979a"
    "4ab9bd6d6184e2f8d9b6c00cc0835b13",
)
UPSTREAM_TAG_TYPEDEF = (9_602, 9_629)
UPSTREAM_TAG_TYPEDEF_PIN = (
    27,
    "cb4dcd6212b1a269371d86dddf98ed7"
    "4853e2eb43753c5d8f8659abbca167ce2",
)

STOCK = bytes.fromhex("c00f90f00100c0b27047")
STOCK_SHA256 = (
    "0249b2c9c987097c7c0e628917a7dd6b"
    "67d4d1ee24f64339a7e0dd11977e4c9e"
)
PREDECESSOR_RETURN = bytes.fromhex("10bd")
MAIN_CALLERS = [
    (0x004C_BB06, "fff7b0f9"),
    (0x004C_BE92, "fef7eaff"),
    (0x004C_F230, "fbf71bfe"),
]
BOOT_CALLERS = [
    (0x0041_180E, "fff7b0f9"),
    (0x0041_1B9A, "fef7eaff"),
    (0x0041_4908, "fcf733f9"),
]
CALLER_PINS = {
    "main": {
        "addresses": "a8d1a349dc8381e29584323692b0c96df2c9b94bfbb477407aa6d22beb3e82ee",
        "encodings": "a11852b39f3aecf105c16a86767437920cb2d41a5d8685249d6b22d3f882a0ee",
        "records": "3218754d3f33ad2be3ddaf81bfc38ed4326a30b30a25ea62f3415fb1113a4491",
    },
    "boot": {
        "addresses": "0305b3c824b1748953137975ca3f81b345fbe15f66a7fd5883e85c937a71331c",
        "encodings": "e45c22e5d0653aeaaf0eccb8f9ddd5ac04aa3e547a34695e9402ed2beed09918",
        "records": "59ab470669e02502e855df6f10be748e2fbad41af14ccb9745506437938a3751",
    },
}

TARGET_FLAGS = (
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
)
APPLE_CLANG = "/usr/bin/clang"
APPLE_CLANG_VERSION = "Apple clang version 21.0.0 (clang-2100.3.33.1)"
TARGET_OBJECT_PIN = (
    788,
    "e3871538017e418dada7c63f5d4395c7"
    "911e691256971de34883fdb43952400a",
)
TARGET_TEXT = bytes.fromhex("c043c00f7047")
TARGET_TEXT_PIN = (
    6,
    "65e477818b1c6002b2ceb88812da2585"
    "24e438ded36dfa059e034c3bce19624e",
)

PROFILE_PINS = {
    "apple-clang": {
        "main_leaf": (124_568, 0x007B_29BC),
        "boot_leaf": (628, 0x0043_46EC),
        "main_patch": (
            "e7f2a7bd00bf00bf00bf",
            "7d4e4d18c00d6e4e39be78f8bc1e9a"
            "5ab7609ae6efc331d0151c85abfd06a587",
        ),
        "boot_patch": (
            "23f0bbbd00bf00bf00bf",
            "f85bc273e2b89e8cc3cebe1bc7ee0604"
            "6b4c718d2b1415ae1d3b20f67924af30",
        ),
        "main_overlay": (
            362_272,
            "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae",
        ),
        "main_component": (
            3_956_468,
            "aa3dbf59ad8912a92fcd9ea6e1ce33834da51989f5fb19257e7064871fb6a3b2",
        ),
        "boot_overlay": (
            15_240,
            "d68bca1fc09b1b734a65a706e9d5a4d5aa4201e53441f6ad1354be44f428b314",
        ),
        "boot_component": (
            163_840,
            "94afbc3d7e1aa8d0d21095de081523c2ed9e422287355128eb20d36bf27c88e2",
        ),
        "package": (
            4_750_576,
            "56f3c555b58099e0a744905856cc803c9aa681bdffc2b2ad8b4f61141ff8c1e6",
        ),
    },
    "linux-clang": {
        "main_leaf": (126_388, 0x007B_30D8),
        "boot_leaf": (628, 0x0043_46EC),
        "main_patch": (
            "e8f235b900bf00bf00bf",
            "9f019085d722f2670a85c782b1070378"
            "9c4aadf49e6e8a13cd32f80bd1b8a20a",
        ),
        "boot_patch": (
            "23f0bbbd00bf00bf00bf",
            "f85bc273e2b89e8cc3cebe1bc7ee0604"
            "6b4c718d2b1415ae1d3b20f67924af30",
        ),
        "main_overlay": (
            154_604,
            "4caa6c35e2c8f559d7668511d8c36fd19ba95a94a8762215f9bed4ba91e006c6",
        ),
        "main_component": (
            3_956_468,
            "3255f998ea3c115803bf957e63b50e0b4a969cf478e64939610592c6fd4758f7",
        ),
        "boot_overlay": (
            15_224,
            "2dad91f7403219c30fee3130d62833c98561c8fb56387960f0654723ceed67ca",
        ),
        "boot_component": (
            163_824,
            "426d77749f96307ae9a45173d20684570d5994d902cf1f1f5cb01f935c6ba7c6",
        ),
        "package": (
            4_750_560,
            "e888fd7de4ed3b6a3a2b071f001f4769cf783ad2fc785a01ae0e08c0e5d808c2",
        ),
    },
}

ORACLE_PREFIX = b"""\
#include <stdbool.h>
#include <stdint.h>

typedef uint32_t lfs_tag_t;
"""
ORACLE_SUFFIX = b"""

bool open_cfw_test_littlefs_tag_isvalid_pristine(uint32_t tag)
{
    return lfs_tag_isvalid(tag);
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


class RuntimeLittlefsTagIsvalidProductionTests(unittest.TestCase):
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
            prefix="open-cfw-littlefs-tag-isvalid-production-",
            dir=ROOT / "build",
        )
        temporary = Path(cls.temporary.name)
        definition = UPSTREAM.read_bytes()[slice(*UPSTREAM_DEFINITION)]
        oracle = temporary / "oracle.c"
        oracle.write_bytes(ORACLE_PREFIX + definition + ORACLE_SUFFIX)
        library = temporary / (
            "tag-isvalid.dylib" if sys.platform == "darwin" else "tag-isvalid.so"
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
        cls.production_adapter = cls.library.open_cfw_littlefs_tag_isvalid
        cls.pristine = cls.library.open_cfw_test_littlefs_tag_isvalid_pristine
        for function in (cls.production_adapter, cls.pristine):
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_bool

        cls.objects = []
        for index in range(2):
            output = temporary / f"production-adapter-{index}.o"
            subprocess.run(
                [APPLE_CLANG, *TARGET_FLAGS, "-c", SOURCE_PATH, "-o", str(output)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            cls.objects.append(output)

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
            b"static inline bool lfs_tag_isvalid(lfs_tag_t tag) {\n"
            b"    return !(tag & 0x80000000);\n}\n\n",
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
        self.assertIn("(tag & UINT32_C(0x80000000)) == 0U", source)
        self.assertIn("typedef uint32_t open_cfw_littlefs_isvalid_tag_t", header)
        self.assertIn("sizeof(bool) == 1U", header)

        integration = provenance["production_integration"]
        self.assertIn(SOURCE_PATH, integration["allowed_production_source_paths"])
        self.assertIn(HEADER_PATH, integration["allowed_production_source_paths"])
        self.assertIn(FUNCTION, integration["allowed_production_symbols"])
        leaf_provenance = integration["tag_isvalid_leaf"]
        self.assertEqual(leaf_provenance["upstream_function"], "lfs_tag_isvalid")
        self.assertEqual(leaf_provenance["upstream_definition_offset"], 10_042)
        self.assertEqual(leaf_provenance["upstream_definition_size"], 87)
        self.assertEqual(
            leaf_provenance["upstream_definition_sha256"],
            UPSTREAM_DEFINITION_PIN[1],
        )
        self.assertEqual(leaf_provenance["upstream_tag_typedef_offset"], 9_602)
        self.assertEqual(leaf_provenance["upstream_tag_typedef_size"], 27)
        self.assertEqual(
            leaf_provenance["upstream_tag_typedef_sha256"],
            UPSTREAM_TAG_TYPEDEF_PIN[1],
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
        self.assertEqual(leaf_provenance["stock_size"], len(STOCK))
        self.assertEqual(leaf_provenance["stock_sha256"], STOCK_SHA256)
        self.assertEqual(leaf_provenance["relocations"], [])
        self.assertEqual(
            leaf_provenance["stock_images"]["apollo_main"]["stock_callers"],
            [
                {"address": f"0x{address:08X}", "encoding": encoding}
                for address, encoding in MAIN_CALLERS
            ],
        )
        self.assertEqual(
            leaf_provenance["stock_images"]["apollo_bootloader"]["stock_callers"],
            [
                {"address": f"0x{address:08X}", "encoding": encoding}
                for address, encoding in BOOT_CALLERS
            ],
        )

        configs = {
            "main": json.loads(MAIN_OVERLAY.read_text(encoding="utf-8")),
            "boot": json.loads(BOOT_OVERLAY.read_text(encoding="utf-8")),
        }
        for name, config in configs.items():
            self.assertIn(FUNCTION, config["functions"])
            leaves = [
                item
                for category in ("isolated_leaves", "relocated_leaves")
                for item in config.get(category, [])
                if item["function"] == FUNCTION
            ]
            self.assertEqual(len(leaves), 1, name)
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
            expected_offset = PROFILE_PINS["apple-clang"][f"{name}_leaf"][0]
            expected_alignment = 4 if name == "main" else 2
            self.assertEqual(
                leaf["expected"],
                {
                    "size": TARGET_TEXT_PIN[0],
                    "sha256": TARGET_TEXT_PIN[1],
                    "alignment": expected_alignment,
                    "offset": expected_offset,
                    "unrelocated_sha256": TARGET_TEXT_PIN[1],
                },
            )
            linux = leaf["toolchain_profiles"]["linux-clang"]
            self.assertEqual(
                linux["reviewed_version_prefix"],
                "Homebrew clang version 22.1.8",
            )
            if name == "main":
                self.assertEqual(
                    linux["expected"],
                    {
                        "size": TARGET_TEXT_PIN[0],
                        "sha256": TARGET_TEXT_PIN[1],
                        "alignment": 4,
                        "offset": PROFILE_PINS["linux-clang"]["main_leaf"][0],
                        "unrelocated_sha256": TARGET_TEXT_PIN[1],
                    },
                )
                self.assertEqual(linux["relocations"], [])
            else:
                self.assertNotIn("expected", linux)
                self.assertEqual(
                    config["function_profiles"]["linux-clang"][FUNCTION],
                    {"expected_offset": expected_offset, "expected_size": 6},
                )

            patch = [
                item
                for item in config["patch_sites"]
                if item["target_function"] == FUNCTION
            ]
            self.assertEqual(
                patch,
                [{
                    "name": "replace_littlefs_tag_isvalid",
                    "runtime_address": MAIN_START if name == "main" else BOOT_START,
                    "expected_size": len(STOCK),
                    "expected_sha256": STOCK_SHA256,
                    "branch": "b_w",
                    "target_function": FUNCTION,
                }],
            )

        for profile, pins in PROFILE_PINS.items():
            for name, config in configs.items():
                aggregate = (
                    config["expected"]
                    if profile == "apple-clang"
                    else config["toolchain_profiles"][profile]["expected"]
                )
                self.assertEqual(
                    (aggregate["overlay_size"], aggregate["overlay_sha256"]),
                    pins[f"{name}_overlay"],
                )
                self.assertEqual(
                    (aggregate["component_size"], aggregate["component_sha256"]),
                    pins[f"{name}_component"],
                )
                replacement = bytes.fromhex(pins[f"{name}_patch"][0])
                self.assertEqual(sha256(replacement), pins[f"{name}_patch"][1])
                self.assertEqual(replacement[4:], bytes.fromhex("00bf") * 3)
                start = MAIN_START if name == "main" else BOOT_START
                self.assertEqual(
                    wide_branch_target(
                        start,
                        *struct.unpack("<HH", replacement[:4]),
                        link=False,
                    ),
                    pins[f"{name}_leaf"][1],
                )
            production_profile = leaf_provenance["production_profiles"][profile]
            self.assertEqual(
                production_profile["apollo_main"],
                {
                    "leaf_size": 6,
                    "overlay_offset": pins["main_leaf"][0],
                    "runtime_address": f"0x{pins['main_leaf'][1]:08X}",
                    "relocated_sha256": TARGET_TEXT_PIN[1],
                    "unrelocated_sha256": TARGET_TEXT_PIN[1],
                },
            )
            self.assertEqual(
                production_profile["apollo_bootloader"],
                {
                    "leaf_size": 6,
                    "overlay_offset": pins["boot_leaf"][0],
                    "runtime_address": f"0x{pins['boot_leaf'][1]:08X}",
                    "relocated_sha256": TARGET_TEXT_PIN[1],
                    "unrelocated_sha256": TARGET_TEXT_PIN[1],
                },
            )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        boot = manifest["component_overrides"]["apollo_bootloader"]
        for profile, pins in PROFILE_PINS.items():
            package = (
                manifest["package"]
                if profile == "apple-clang"
                else manifest["package"]["profiles"][profile]
            )
            main_provider = (
                main["provider"]
                if profile == "apple-clang"
                else main["provider"]["profiles"][profile]
            )
            boot_provider = (
                boot["provider"]
                if profile == "apple-clang"
                else boot["provider"]["profiles"][profile]
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

        main_regions = {item["name"]: item for item in main["regions"]}
        boot_regions = {item["name"]: item for item in boot["regions"]}
        expected_regions = {
            "littlefs_tag_isvalid_source_replacement": (
                main_regions, 601_738, 10, MAIN_START,
                "generated_source_entry_replacement",
            ),
            "apollo_littlefs_tag_isvalid_source_alignment": (
                main_regions, 3_647_962, 2, 0x007B_29BA, "generated_alignment",
            ),
            "apollo_littlefs_tag_isvalid_source_leaf": (
                main_regions, 3_647_964, 6, 0x007B_29BC, "source_compiled",
            ),
            "bootloader_littlefs_tag_isvalid_source_replacement": (
                boot_regions, 2_930, 10, BOOT_START,
                "generated_source_entry_replacement",
            ),
            "bootloader_littlefs_tag_isvalid_source_leaf": (
                boot_regions, 149_228, 6, 0x0043_46EC, "source_compiled",
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
            self.assertEqual(regions[0]["file_offset"], 0)
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

        apple = PROFILE_PINS["apple-clang"]
        artifacts = {
            "main_overlay": MAIN_BUILD / "apollo_core_overlay.bin",
            "main_component": MAIN_BUILD / "ota_s200_firmware_ota.bin",
            "main_report": MAIN_BUILD / "build-report.json",
            "boot_overlay": BOOT_BUILD / "bootloader_core_overlay.bin",
            "boot_component": BOOT_BUILD / "ota_s200_bootloader.bin",
            "boot_report": BOOT_BUILD / "build-report.json",
            "boot_contract": BOOT_BUILD / "provider-contract.json",
            "package": PACKAGE_BUILD / "package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin",
            "flash_plan": PACKAGE_BUILD / "flash-plan.json",
            "package_report": PACKAGE_BUILD / "build-report.json",
        }
        exact_artifacts = {
            "main_overlay", "main_component", "boot_overlay",
            "boot_component", "package",
        }
        for name in exact_artifacts:
            path = artifacts[name]
            self.assertEqual((path.stat().st_size, sha256(path)), apple[name], name)

        main_report = json.loads(artifacts["main_report"].read_text(encoding="utf-8"))
        boot_report = json.loads(artifacts["boot_report"].read_text(encoding="utf-8"))
        for name, report, start in (
            ("main", main_report, MAIN_START),
            ("boot", boot_report, BOOT_START),
        ):
            reported_leaf = next(
                item
                for item in report["relocated_leaves"]
                if item["extraction"]["function"] == FUNCTION
            )
            self.assertEqual(
                reported_leaf["placement"],
                {
                    "offset": apple[f"{name}_leaf"][0],
                    "runtime_address": apple[f"{name}_leaf"][1],
                    "runtime_address_hex": f"0x{apple[f'{name}_leaf'][1]:08X}",
                    "size": 6,
                    "alignment": 4 if name == "main" else 2,
                    "padding_before": 2 if name == "main" else 0,
                },
            )
            reported_patch = next(
                item
                for item in report["overlay"]["patched_sites"]
                if item["target_function"] == FUNCTION
            )
            self.assertEqual(
                reported_patch["replacement_hex"],
                apple[f"{name}_patch"][0],
            )
            self.assertEqual(reported_patch["runtime_address"], start)
            self.assertEqual(
                reported_patch["target_address"],
                apple[f"{name}_leaf"][1],
            )
        package_report = json.loads(
            artifacts["package_report"].read_text(encoding="utf-8")
        )
        flash_plan = json.loads(
            artifacts["flash_plan"].read_text(encoding="utf-8")
        )
        self.assertEqual(
            (
                package_report["placed_region_count"],
                package_report["unresolved_region_count"],
                package_report["container_region_count"],
            ),
            (
                len(flash_plan["flash_regions"]),
                len(flash_plan["unresolved_flash_regions"]),
                len(flash_plan["container_only_regions"]),
            ),
        )
        self.assertEqual(package_report["unresolved_region_count"], 0)
        self.assertEqual(flash_plan["package_sha256"], apple["package"][1])
        self.assertEqual(
            (
                len(flash_plan["flash_regions"]),
                len(flash_plan["unresolved_flash_regions"]),
                len(flash_plan["container_only_regions"]),
            ),
            (
                package_report["placed_region_count"],
                package_report["unresolved_region_count"],
                package_report["container_region_count"],
            ),
        )

    def test_dual_image_stock_callers_and_dependency_closure_are_exact(self) -> None:
        for name, image, base, start, end, callers in (
            ("main", self.main, MAIN_BASE, MAIN_START, MAIN_END, MAIN_CALLERS),
            ("boot", self.boot, BOOT_BASE, BOOT_START, BOOT_END, BOOT_CALLERS),
        ):
            stock = self.span(image, base, start, end)
            self.assertEqual(stock, STOCK, name)
            self.assertEqual(sha256(stock), STOCK_SHA256, name)
            self.assertEqual(
                self.span(image, base, start - 2, start),
                PREDECESSOR_RETURN,
                name,
            )
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
            for offset in range(0, len(stock) - 3, 2):
                address = start + offset
                first, second = struct.unpack_from("<HH", stock, offset)
                for link in (True, False):
                    target = wide_branch_target(address, first, second, link=link)
                    if target is not None:
                        outgoing.append((address, link, target))
            self.assertEqual(outgoing, [], name)

    def test_complete_dual_image_ingress_and_pointer_closure_is_exact(self) -> None:
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

    def test_production_adapter_matches_pristine_definition_exhaustively_and_randomly(
        self,
    ) -> None:
        directed = (
            0x0000_0000,
            0xFFFF_FFFF,
            0x7FFF_FFFF,
            0x8000_0000,
            0x0000_0001,
            0x4000_0000,
            0x1234_5678,
            0xA5A5_5A5A,
        )
        for tag in directed:
            expected = (tag & 0x8000_0000) == 0
            self.assertEqual(self.production_adapter(tag), expected, hex(tag))
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

        # Exhaust the upper 16-bit word, covering both validity-bit classes
        # and every combination of the ignored upper tag bits.
        for upper in range(1 << 16):
            lower = (upper * 0x9E37 + 0x5A5A) & 0xFFFF
            tag = (upper << 16) | lower
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

        rng = random.Random(0x4C_AE6A)
        for _ in range(20_000):
            tag = rng.getrandbits(32)
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

    def test_apple_thumb_object_text_and_no_relocation_closure_are_exact(self) -> None:
        first = self.objects[0].read_bytes()
        second = self.objects[1].read_bytes()
        self.assertEqual(first, second)
        self.assertEqual((len(first), sha256(first)), TARGET_OBJECT_PIN)

        leaf, extraction = self.apollo_overlay.extract_isolated_function_section(
            self.objects[0],
            FUNCTION,
        )
        self.assertEqual(leaf, TARGET_TEXT)
        self.assertEqual((len(leaf), sha256(leaf)), TARGET_TEXT_PIN)
        self.assertEqual(
            extraction,
            {
                "function": FUNCTION,
                "section": SECTION,
                "size": TARGET_TEXT_PIN[0],
                "sha256": TARGET_TEXT_PIN[1],
                "alignment": 4,
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
        )

        data, sections = self.apollo_overlay.parse_elf32(self.objects[0])
        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        undefined = sorted(
            symbol["name"]
            for symbol in symbols
            if symbol["name"] and symbol["section_index"] == 0
        )
        self.assertEqual(undefined, [])


if __name__ == "__main__":
    unittest.main()
