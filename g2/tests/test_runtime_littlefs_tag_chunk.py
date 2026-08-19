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


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/littlefs/runtime_littlefs_tag_chunk.c"
HEADER = SOURCE.with_suffix(".h")
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
HEADER_PATH = HEADER.relative_to(ROOT).as_posix()
LITTLEFS = ROOT / "third_party/littlefs"
UPSTREAM = LITTLEFS / "lfs.c"
PROVENANCE = LITTLEFS / "PROVENANCE.json"
MAIN_PACKAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN_OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BOOT_OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

FUNCTION = "open_cfw_littlefs_tag_chunk"
SECTION = ".text." + FUNCTION
MAIN_BASE = 0x0043_8000
BOOT_BASE = 0x0041_0000
MAIN_START = 0x004C_AEA0
MAIN_END = 0x004C_AEA6
BOOT_START = 0x0041_0BA8
BOOT_END = 0x0041_0BAE
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
    773,
    "71851bd05e26e703b8697b9994b556db"
    "46511c37e9500da98e3406b37a92c8da",
)
HEADER_PIN = (
    879,
    "1061f5d68ff6f81a6f1853bfefe37b7"
    "7f5f3b8b09e627b1bfa0d191842d1f6f5",
)
UPSTREAM_PIN = (
    196_753,
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398",
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_DEFINITION = (10_514, 10_607)
UPSTREAM_DEFINITION_PIN = (
    93,
    "406b74c2d10482c959cf1048d9589d00"
    "d8b416ee4661203bd339144baa74cd09",
)
UPSTREAM_TAG_TYPEDEF = (9_602, 9_629)
UPSTREAM_TAG_TYPEDEF_PIN = (
    27,
    "cb4dcd6212b1a269371d86dddf98ed7"
    "4853e2eb43753c5d8f8659abbca167ce2",
)

STOCK = bytes.fromhex("000dc0b27047")
STOCK_SHA256 = (
    "63fc572597119c756fa5d4ee0904c8c3"
    "4dfa545495b77bba02e2ff3298ce23ae"
)
MAIN_CALLERS = [
    (0x004C_AEA8, "fff7faff"),
    (0x004C_BB68, "fff79af9"),
    (0x004C_BD1E, "fff7bff8"),
    (0x004C_CBC4, "fef76cf9"),
]
BOOT_CALLERS = [
    (0x0041_0BB0, "fff7faff"),
    (0x0041_1870, "fff79af9"),
    (0x0041_1A26, "fff7bff8"),
    (0x0041_27C8, "fef7eef9"),
]
CALLER_PINS = {
    "main": {
        "addresses": "53fe680d2304be812e2d3d7b4c194642f0250aacddfa2a2d319dcb9c04a77a20",
        "encodings": "089750335e98afdca16b29120336a01172cdc3c7584094cd5c2952ef885cc742",
        "records": "4d34c3705c5ada46756ea6ffcf00722a1d960716627d0f293ea6bf03b9b655b0",
    },
    "boot": {
        "addresses": "0d397f7452143ad98aff7e29880f28885c35d8ab24b1481e057dabff3a1e478f",
        "encodings": "077793ca6848ed5f3c7fabf50d9698fb2ef23ef3010e99fa3fa854aee5d28ff3",
        "records": "b74dadb016ec167ffc6aadae7ff6bdbb6120671cfcbaa239682f13ad6a45b97a",
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
APPLE_CLANG_VERSION = "Apple clang version 21.0.0 (clang-2100.3.30.1)"
TARGET_OBJECT_PIN = (
    784,
    "517b3e244b391c21f714f21c54544b9c"
    "e93a6008781e2daa536e3f954ddf2f9d",
)
TARGET_TEXT = bytes.fromhex("c0f307507047")
TARGET_TEXT_PIN = (
    6,
    "db1dfda72afb267e96cd4e11eaf5d446"
    "59195b0afecbdcd8ed8572c34049df74",
)

ORACLE_PREFIX = b"""\
#include <stdint.h>

typedef uint32_t lfs_tag_t;
"""
ORACLE_SUFFIX = b"""

uint8_t open_cfw_test_littlefs_tag_chunk_pristine(uint32_t tag)
{
    return lfs_tag_chunk(tag);
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


class RuntimeLittlefsTagChunkProductionTests(unittest.TestCase):
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

        parent = ROOT / "build"
        parent.mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-littlefs-tag-chunk-production-",
            dir=parent,
        )
        temporary = Path(cls.temporary.name)
        definition = UPSTREAM.read_bytes()[slice(*UPSTREAM_DEFINITION)]
        oracle = temporary / "oracle.c"
        oracle.write_bytes(ORACLE_PREFIX + definition + ORACLE_SUFFIX)
        library = temporary / (
            "tag-chunk.dylib" if sys.platform == "darwin" else "tag-chunk.so"
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
        cls.production_adapter = cls.library.open_cfw_littlefs_tag_chunk
        cls.pristine = cls.library.open_cfw_test_littlefs_tag_chunk_pristine
        for function in (cls.production_adapter, cls.pristine):
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint8

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
            b"static inline uint8_t lfs_tag_chunk(lfs_tag_t tag) {\n"
            b"    return (tag & 0x0ff00000) >> 20;\n}\n\n",
        )
        typedef = upstream[slice(*UPSTREAM_TAG_TYPEDEF)]
        self.assertEqual((len(typedef), sha256(typedef)), UPSTREAM_TAG_TYPEDEF_PIN)
        self.assertEqual(typedef, b"typedef uint32_t lfs_tag_t;")

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["upstream"]["selected_tag"], "v2.10.1")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertEqual(provenance["license"], "BSD-3-Clause")
        self.assertFalse(provenance["selection"]["exact_historical_checkout_proven"])

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn("Altered production adaptation", source)
        self.assertIn("(tag & UINT32_C(0x0ff00000)) >> 20U", source)
        self.assertIn("typedef uint32_t open_cfw_littlefs_tag_t", header)
        self.assertIn("sizeof(uint8_t) == 1U", header)
        integration = provenance["production_integration"]
        self.assertIn(SOURCE_PATH, integration["allowed_production_source_paths"])
        self.assertIn(HEADER_PATH, integration["allowed_production_source_paths"])
        self.assertIn(FUNCTION, integration["allowed_production_symbols"])
        tag_chunk = integration["tag_chunk_leaf"]
        self.assertEqual(tag_chunk["upstream_function"], "lfs_tag_chunk")
        self.assertEqual(tag_chunk["upstream_definition_offset"], 10_514)
        self.assertEqual(tag_chunk["upstream_definition_size"], 93)
        self.assertEqual(tag_chunk["upstream_definition_sha256"], UPSTREAM_DEFINITION_PIN[1])
        self.assertEqual(tag_chunk["upstream_tag_typedef_offset"], 9_602)
        self.assertEqual(tag_chunk["upstream_tag_typedef_size"], 27)
        self.assertEqual(
            tag_chunk["upstream_tag_typedef_sha256"],
            UPSTREAM_TAG_TYPEDEF_PIN[1],
        )
        self.assertEqual(tag_chunk["local_source_sha256"], SOURCE_PIN[1])
        self.assertEqual(tag_chunk["local_header_sha256"], HEADER_PIN[1])
        self.assertEqual(tag_chunk["stock_size"], len(STOCK))
        self.assertEqual(tag_chunk["stock_sha256"], STOCK_SHA256)
        self.assertEqual(tag_chunk["relocations"], [])

        registrations = (
            (MAIN_OVERLAY, MAIN_START, 124_560, 4, "relocated_leaves"),
            (BOOT_OVERLAY, BOOT_START, 622, 2, "relocated_leaves"),
        )
        for path, stock_start, offset, alignment, collection in registrations:
            config = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn(FUNCTION, config["functions"])
            if path == MAIN_OVERLAY:
                self.assertEqual(
                    config["toolchain_profiles"]["linux-clang"]["expected"],
                    {
                        "overlay_size": 144_266,
                        "overlay_sha256": (
                            "4c95f20608c70a065b05837415d2d4471fc7eeeb61fa30ce1c1c9f07f717ddb9"
                        ),
                        "component_size": 3_667_662,
                        "component_sha256": (
                            "686ea217db2837bffd8a190485f0a6f719242e927fba17281c6f54aa066767f6"
                        ),
                    },
                )
            else:
                self.assertEqual(
                    config["toolchain_profiles"]["linux-clang"]["expected"],
                    {
                        "overlay_size": 662,
                        "overlay_sha256": (
                            "e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021"
                        ),
                        "component_size": 149_262,
                        "component_sha256": (
                            "fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74"
                        ),
                    },
                )
            leaves = []
            categories = []
            for category in ("isolated_leaves", "relocated_leaves"):
                for leaf_record in config.get(category, []):
                    if leaf_record["function"] == FUNCTION:
                        leaves.append(leaf_record)
                        categories.append(category)
            self.assertEqual(len(leaves), 1, path)
            self.assertEqual(categories, [collection], path)
            leaf = leaves[0]
            self.assertEqual(leaf["source"]["path"], SOURCE_PATH)
            self.assertEqual(leaf["source"]["size"], SOURCE_PIN[0])
            self.assertEqual(leaf["source"]["sha256"], SOURCE_PIN[1])
            self.assertTrue(leaf["strict_relocation_contract"])
            self.assertEqual(
                leaf["expected"],
                {
                    "size": TARGET_TEXT_PIN[0],
                    "sha256": TARGET_TEXT_PIN[1],
                    "alignment": alignment,
                    "offset": offset,
                    "unrelocated_sha256": TARGET_TEXT_PIN[1],
                },
            )
            self.assertEqual(leaf["relocations"], [])
            linux = leaf["toolchain_profiles"]["linux-clang"]
            self.assertEqual(
                linux["reviewed_version_prefix"],
                "Homebrew clang version 22.1.8",
            )
            if path == MAIN_OVERLAY:
                self.assertEqual(
                    linux,
                    {
                        "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                        "expected": {
                            "size": 6,
                            "sha256": TARGET_TEXT_PIN[1],
                            "alignment": 4,
                            "offset": 126_380,
                            "unrelocated_sha256": TARGET_TEXT_PIN[1],
                        },
                        "relocations": [],
                    },
                )
            else:
                self.assertNotIn("expected", linux)
                self.assertEqual(
                    config["function_profiles"]["linux-clang"][FUNCTION],
                    {"expected_offset": 622, "expected_size": 6},
                )
            patches = [
                patch
                for patch in config["patch_sites"]
                if patch["target_function"] == FUNCTION
            ]
            self.assertEqual(
                patches,
                [{
                    "name": "replace_littlefs_tag_chunk",
                    "runtime_address": stock_start,
                    "expected_size": len(STOCK),
                    "expected_sha256": STOCK_SHA256,
                    "branch": "b_w",
                    "target_function": FUNCTION,
                }],
            )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        boot = manifest["component_overrides"]["apollo_bootloader"]
        self.assertEqual(
            (main["provider"]["size"], main["provider"]["sha256"]),
            (3_670_417, "eee145e7f687e622447bc33fc9dc45b3ab5eb1f1ad49717029196d589799aa4c"),
        )
        self.assertEqual(
            (boot["provider"]["size"], boot["provider"]["sha256"]),
            (149_262, "695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267"),
        )
        self.assertEqual(
            (manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]),
            (4_448_911, "21ba9d6c32c73f390fd68ee9ef2808ad01c7206d746e67eca9c755732b0a6605"),
        )
        self.assertEqual(
            main["provider"]["profiles"]["linux-clang"],
            {
                "size": 3_667_662,
                "sha256": (
                    "686ea217db2837bffd8a190485f0a6f719242e927fba17281c6f54aa066767f6"
                ),
            },
        )
        self.assertEqual(
            boot["provider"]["profiles"]["linux-clang"],
            {
                "size": 149_262,
                "sha256": (
                    "fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74"
                ),
            },
        )
        self.assertEqual(
            manifest["package"]["profiles"]["linux-clang"],
            {
                "expected_size": 4_446_156,
                "expected_sha256": (
                    "2cca0fbac8da01ede95a3cecd55dd0706f6dad3a8437605f8a68949cee3c6bc3"
                ),
            },
        )
        main_regions = {region["name"]: region for region in main["regions"]}
        boot_regions = {region["name"]: region for region in boot["regions"]}
        expected_regions = {
            "littlefs_tag_chunk_source_replacement": (
                601_792, 6, 0x004C_AEA0, "generated_source_entry_replacement"
            ),
            "apollo_littlefs_tag_chunk_source_alignment": (
                3_647_954, 2, 0x007B_29B2, "generated_alignment"
            ),
            "apollo_littlefs_tag_chunk_source_leaf": (
                3_647_956, 6, 0x007B_29B4, "source_compiled"
            ),
            "bootloader_littlefs_tag_chunk_source_replacement": (
                2_984, 6, 0x0041_0BA8, "generated_source_entry_replacement"
            ),
            "bootloader_littlefs_tag_chunk_source_leaf": (
                149_222, 6, 0x0043_46E6, "source_compiled"
            ),
        }
        for name, (file_offset, size, address, status) in expected_regions.items():
            region = (main_regions | boot_regions)[name]
            self.assertEqual(
                (
                    region["file_offset"],
                    region["size"],
                    region["target_address"],
                    region["address_status"],
                ),
                (file_offset, size, address, status),
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

    def test_dual_image_stock_callers_and_dependency_closure_are_exact(self) -> None:
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
            final_complete_halfword = base + 2 * ((len(image) - 2) // 2)
            self.assertEqual(final_halfword, final_complete_halfword, name)

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

    def test_production_adapter_matches_pristine_definition_exhaustively_and_randomly(self) -> None:
        directed = (
            0x0000_0000,
            0xFFFF_FFFF,
            0x0FF0_0000,
            0xF000_0000,
            0x8000_0000,
            0x00F0_0000,
            0x1234_5678,
            0xA5A5_5A5A,
        )
        for tag in directed:
            expected = (tag & 0x0FF0_0000) >> 20
            self.assertEqual(self.production_adapter(tag), expected, hex(tag))
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

        # Exhaust every possible combination of the twelve source-relevant
        # bits 20..31, with deterministic lower-bit noise.
        for upper in range(1 << 12):
            lower = (upper * 0x9E377 + 0x5A5A5) & 0x000F_FFFF
            tag = (upper << 20) | lower
            self.assertEqual(self.production_adapter(tag), self.pristine(tag), hex(tag))

        rng = random.Random(0x4C_AEA0)
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
