from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/littlefs/runtime_littlefs_tag_type2.c"
HEADER = SOURCE.with_suffix(".h")
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
LITTLEFS = ROOT / "third_party/littlefs"
UPSTREAM = LITTLEFS / "lfs.c"
PROVENANCE = LITTLEFS / "PROVENANCE.json"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

FUNCTION = "open_cfw_littlefs_tag_type2"
SECTION = ".text." + FUNCTION
PACKAGE_PREAMBLE = 32
APPLICATION_BASE = 0x0043_8000
START = 0x004C_AE90
END = 0x004C_AE98

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
    789,
    "c2ea0965e62aa126fb4b8e752526b8a9"
    "26a9088739811cba09dcf7d1ed6f3940",
)
HEADER_PIN = (
    883,
    "17915b900db79e3e611379645a878072"
    "3410e5c826f6bfa7619d86bac28f0b13",
)
UPSTREAM_PIN = (
    196_753,
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398",
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_DEFINITION = (10_326, 10_418)
UPSTREAM_DEFINITION_PIN = (
    92,
    "65f614cf5ed7152f7ad2176547453c32"
    "9b1f15442e550ef6632b0f7773970f78",
)
UPSTREAM_TAG_TYPEDEF = (9_602, 9_629)
UPSTREAM_TAG_TYPEDEF_PIN = (
    27,
    "cb4dcd6212b1a269371d86dddf98ed7"
    "4853e2eb43753c5d8f8659abbca167ce2",
)

STOCK = bytes.fromhex("000d10f4f0607047")
STOCK_SHA256 = (
    "a017094f8fc58d202d8c5a588f66dd31"
    "9248578fa39e0f392ba3c7857d3500ef"
)
CALLERS = [
    (0x004C_BB26, "fff7b3f9"),
    (0x004C_BC38, "fff72af9"),
]
CALLER_ADDRESS_SHA256 = (
    "358e54fd96099fb219db8ec7d846edde"
    "f29381ccc56fe839af29ff787c844732"
)
CALLER_ENCODING_SHA256 = (
    "b88d9d1d5f3c95897a8c5bc1975e441"
    "efe3bb41764d6d4d55e24b24b6ec549a7"
)
CALLER_RECORD_SHA256 = (
    "85f2f7613d51ea12e6fd297ec5c1f2f"
    "7d1a903e8d58a7a9de4893f0d0d90414a"
)

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
    788,
    "8114a6a47e5e5f65517bc62afdfca88"
    "bae1c38961643a12940d62554a077887e",
)
TARGET_TEXT = bytes.fromhex("4ff4f06101ea10507047")
TARGET_TEXT_PIN = (
    10,
    "88be40d05d37142bf0bae8306026d8c4"
    "05a4f8f441aabd87ee6731557d4149fd",
)

APPLE_OVERLAY_PIN = (
    165_412,
    "91449e27a73806e1537548657bed4486d77b275e4ee8a58b2bb1ef527c252ada",
)
APPLE_COMPONENT_PIN = (
    3_688_808,
    "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c",
)
LINUX_OVERLAY_PIN = (
    145_180,
    "afbcb57a8414e65a18c6c95396a0f32fe454cb2087e6a03d51717196a4854b57",
)
LINUX_COMPONENT_PIN = (
    3_668_576,
    "292f55478951dc8d41a8bc5e4cc01f80ae88f9c44350d8fec89958c939a4fac5",
)
APPLE_PACKAGE_PIN = (
    4_467_302,
    "88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f",
)
LINUX_PACKAGE_PIN = (
    4_447_070,
    "be5c62a97b9d31f4df257615c28ce81d79ab186feadb68262f96ac5bc35a1c25",
)
APPLE_LEAF = (124_548, 0x007B_29A8)
LINUX_LEAF = (126_368, 0x007B_30C4)
APPLE_PATCH = bytes.fromhex("e7f28abd00bf00bf")
APPLE_PATCH_SHA256 = (
    "659991e787790e45f3c2b41575292709"
    "cf44eb4b6342c9f6ff4b735426d188df"
)

ORACLE_PREFIX = b"""\
#include <stdint.h>

typedef uint32_t lfs_tag_t;
"""
ORACLE_SUFFIX = b"""

uint16_t open_cfw_test_littlefs_tag_type2_pristine(uint32_t tag)
{
    return lfs_tag_type2(tag);
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


class RuntimeLittlefsTagType2ProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]
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
            prefix="open-cfw-littlefs-tag-type2-production-",
            dir=parent,
        )
        temporary = Path(cls.temporary.name)
        definition = UPSTREAM.read_bytes()[slice(*UPSTREAM_DEFINITION)]
        oracle = temporary / "oracle.c"
        oracle.write_bytes(ORACLE_PREFIX + definition + ORACLE_SUFFIX)
        library = temporary / (
            "tag-type2.dylib" if sys.platform == "darwin" else "tag-type2.so"
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
        cls.candidate = cls.library.open_cfw_littlefs_tag_type2
        cls.pristine = cls.library.open_cfw_test_littlefs_tag_type2_pristine
        for function in (cls.candidate, cls.pristine):
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint16

        cls.objects = []
        for index in range(2):
            output = temporary / f"candidate-{index}.o"
            subprocess.run(
                [
                    APPLE_CLANG,
                    *TARGET_FLAGS,
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
            cls.objects.append(output)

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.production = apollo_overlay.build(
            root=ROOT,
            config_path=OVERLAY,
            output_dir=temporary / "production",
            clang=APPLE_CLANG,
            toolchain_profile="apple-clang",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def test_authenticated_upstream_local_source_and_registration_are_exact(
        self,
    ) -> None:
        self.assertEqual((len(self.package), sha256(self.package)), PACKAGE_PIN)
        self.assertEqual(
            (len(self.application), sha256(self.application)),
            APPLICATION_PIN,
        )
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
            b"static inline uint16_t lfs_tag_type2(lfs_tag_t tag) {\n"
            b"    return (tag & 0x78000000) >> 20;\n}",
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
        self.assertFalse(
            provenance["selection"]["exact_historical_checkout_proven"]
        )

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn("Altered production adaptation", source)
        self.assertIn("(tag & UINT32_C(0x78000000)) >> 20U", source)
        self.assertIn("typedef uint32_t open_cfw_littlefs_tag_t", header)
        self.assertIn("sizeof(uint16_t) == 2U", header)

        for path in (OVERLAY, PROVENANCE):
            text = path.read_text(encoding="utf-8")
            self.assertIn(SOURCE_PATH, text, path)
            self.assertIn(FUNCTION, text, path)
        integration = provenance["production_integration"]
        self.assertIn(
            SOURCE_PATH,
            integration["allowed_production_source_paths"],
        )
        self.assertIn(
            HEADER.relative_to(ROOT).as_posix(),
            integration["allowed_production_source_paths"],
        )
        self.assertIn(FUNCTION, integration["allowed_production_symbols"])
        tag_leaf = integration["tag_type2_leaf"]
        self.assertEqual(tag_leaf["upstream_function"], "lfs_tag_type2")
        self.assertEqual(tag_leaf["stock_span"], "[0x004CAE90,0x004CAE98)")
        self.assertEqual(tag_leaf["stock_size"], 8)
        self.assertEqual(tag_leaf["stock_sha256"], STOCK_SHA256)
        self.assertEqual(
            tag_leaf["stock_callers"],
            [
                {"address": "0x004CBB26", "encoding": "fff7b3f9"},
                {"address": "0x004CBC38", "encoding": "fff72af9"},
            ],
        )
        self.assertEqual(tag_leaf["relocations"], [])

        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        function_index = config["functions"].index(FUNCTION)
        self.assertEqual(
            config["functions"][function_index:function_index + 2],
            [FUNCTION, "open_cfw_littlefs_tag_chunk"],
        )
        leaf = next(
            item for item in config["relocated_leaves"]
            if item["function"] == FUNCTION
        )
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
        self.assertEqual(
            leaf["expected"],
            {
                "size": TARGET_TEXT_PIN[0],
                "sha256": TARGET_TEXT_PIN[1],
                "alignment": 4,
                "offset": APPLE_LEAF[0],
                "unrelocated_sha256": TARGET_TEXT_PIN[1],
            },
        )
        self.assertEqual(leaf["relocations"], [])
        linux = leaf["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            linux["expected"],
            {
                "size": TARGET_TEXT_PIN[0],
                "sha256": TARGET_TEXT_PIN[1],
                "alignment": 4,
                "offset": LINUX_LEAF[0],
                "unrelocated_sha256": TARGET_TEXT_PIN[1],
            },
        )
        self.assertEqual(linux["relocations"], [])

        patch = next(
            item for item in config["patch_sites"]
            if item["target_function"] == FUNCTION
        )
        self.assertEqual(
            patch,
            {
                "name": "replace_littlefs_tag_type2",
                "runtime_address": START,
                "expected_size": END - START,
                "expected_sha256": STOCK_SHA256,
                "branch": "b_w",
                "target_function": FUNCTION,
            },
        )

        overlay_path = ROOT / self.production["overlay"]["artifact"]
        component_path = ROOT / self.production["component"]["artifact"]
        self.assertEqual(
            (overlay_path.stat().st_size, sha256(overlay_path)),
            APPLE_OVERLAY_PIN,
        )
        self.assertEqual(
            (component_path.stat().st_size, sha256(component_path)),
            APPLE_COMPONENT_PIN,
        )
        self.assertEqual(
            self.production["overlay"]["functions"][FUNCTION],
            {"offset": APPLE_LEAF[0], "size": TARGET_TEXT_PIN[0]},
        )
        reported_patch = next(
            item for item in self.production["overlay"]["patched_sites"]
            if item["target_function"] == FUNCTION
        )
        replacement = bytes.fromhex(reported_patch["replacement_hex"])
        self.assertEqual(replacement, APPLE_PATCH)
        self.assertEqual(sha256(replacement), APPLE_PATCH_SHA256)
        self.assertEqual(reported_patch["target_address"], APPLE_LEAF[1])
        self.assertEqual(
            {
                key: self.production["component"][key]
                for key in (
                    "source_owned_bytes",
                    "source_owned_in_place_bytes",
                    "generated_patch_site_bytes",
                    "generated_wrapper_bytes",
                    "opaque_base_bytes",
                    "replaced_stock_function_bytes",
                )
            },
            {
                "source_owned_bytes": 165_594,
                "source_owned_in_place_bytes": 182,
                "generated_patch_site_bytes": 121_494,
                "generated_wrapper_bytes": 32,
                "opaque_base_bytes": 3_401_688,
                "replaced_stock_function_bytes": 121_672,
            },
        )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(
            (manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]),
            APPLE_PACKAGE_PIN,
        )
        linux_package = manifest["package"]["profiles"]["linux-clang"]
        self.assertEqual(
            (linux_package["expected_size"], linux_package["expected_sha256"]),
            LINUX_PACKAGE_PIN,
        )
        main = manifest["component_overrides"]["apollo_main"]
        provider = main["provider"]
        self.assertEqual((provider["size"], provider["sha256"]), APPLE_COMPONENT_PIN)
        linux_provider = provider["profiles"]["linux-clang"]
        self.assertEqual(
            (linux_provider["size"], linux_provider["sha256"]),
            LINUX_COMPONENT_PIN,
        )
        regions = {item["name"]: item for item in main["regions"]}
        self.assertEqual(
            {
                key: regions["littlefs_tag_type2_source_replacement"][key]
                for key in ("file_offset", "size", "target_address", "address_status")
            },
            {
                "file_offset": START - APPLICATION_BASE + PACKAGE_PREAMBLE,
                "size": END - START,
                "target_address": START,
                "address_status": "generated_source_entry_replacement",
            },
        )
        self.assertEqual(
            {
                key: regions["apollo_littlefs_tag_type2_source_leaf"][key]
                for key in ("file_offset", "size", "target_address", "address_status")
            },
            {
                "file_offset": (
                    APPLE_COMPONENT_PIN[0]
                    - 54  # nanopb signed-varint source leaf
                    - TARGET_TEXT_PIN[0]
                    - 2  # tag_chunk alignment
                    - 6  # tag_chunk source leaf
                    - 2  # tag_isvalid alignment
                    - 6  # tag_isvalid source leaf
                    - 2  # tag_type1 alignment
                    - 10  # tag_type1 source leaf
                    - 2  # tag_type3 alignment
                    - 6  # tag_type3 source leaf
                    - 2  # tag_id alignment
                    - 6  # tag_id source leaf
                    - 2  # tag_size alignment
                    - 6  # tag_size source leaf
                    - 2  # nanopb fixed64 alignment
                    - 28  # nanopb fixed64 source leaf
                    - 158  # nanopb pb_read source leaf
                    - 2  # nanopb private buf_read alignment
                    - 30  # nanopb private buf_read source leaf
                    - 2  # nanopb private readbyte alignment
                    - 64  # nanopb private readbyte source leaf
                    - 20  # nanopb stream-constructor source leaf
                    - 2  # nanopb private varint32 alignment
                    - 222  # nanopb private varint32 source leaf
                    - 16  # nanopb private varint32 rodata
                    - 2  # nanopb public varint32 alignment
                    - 10  # nanopb public varint32 source leaf
                    - 2  # nanopb skip-string alignment
                    - 34  # nanopb skip-string source leaf
                    - 20_969  # all later admissions through the universal-setting KVDB triplet
                    - 206  # terminal-mode KVDB triplet (leaves, rodata, alignment)
                    - 212  # onboarding-config KVDB sextet (leaves, rodata, alignment)
                    - 376  # ring KVDB triplet (leaves, rodata, alignment)
                    - 21  # AT^NUS handler leaf (leaf, alignment)
                    - 666  # eAT core/sensor cluster (twelve leaves, alignment)
                    - 2_814  # module-configuration KVDB sextet (leaves, rodata, alignment)
                    - 170  # buzzer NVDB quintet (leaves, alignment)
                    - 198  # product-mode NVDB sextet (leaves, alignment)
                    - 254  # MAC NVDB triplet (leaves, alignment)
                    - 142  # advertising-magic NVDB triplet (leaves, alignment)
                    - 4_396  # system-data NVDB thirteen-leaf cluster (leaves, rodata, alignment)
                    - 274  # ULED display-preprocess leaf (leaf, rodata, alignment)
                    - 1_568  # charger-common eleven-leaf cluster (leaves, alignment)
                    - 2_378  # BQ25180 22-leaf charger-driver cluster (leaves, alignment)
                    - 4_634  # BQ27427 33-leaf fuel-gauge cluster (leaves, rodata, alignment)
                    - 254  # Goodix-derived error-handler leaf
                    - 122  # FreeRTOS task-info leaf and alignment
                    - 500  # scheduler-start closure leaves and alignment
                ),
                "size": TARGET_TEXT_PIN[0],
                "target_address": APPLE_LEAF[1],
                "address_status": "source_compiled",
            },
        )

    def test_stock_body_callers_and_dependency_closure_are_exact(self) -> None:
        stock = self.span(START, END)
        self.assertEqual(stock, STOCK)
        self.assertEqual(sha256(stock), STOCK_SHA256)

        records = []
        for address, expected_encoding in CALLERS:
            encoding = self.span(address, address + 4)
            self.assertEqual(encoding.hex(), expected_encoding)
            target = wide_branch_target(
                address,
                *struct.unpack("<HH", encoding),
                link=True,
            )
            self.assertEqual(target, START)
            records.append(struct.pack("<I", address) + encoding)
        self.assertEqual(
            sha256(b"".join(struct.pack("<I", address) for address, _ in CALLERS)),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            sha256(b"".join(bytes.fromhex(value) for _, value in CALLERS)),
            CALLER_ENCODING_SHA256,
        )
        self.assertEqual(sha256(b"".join(records)), CALLER_RECORD_SHA256)

        outgoing = []
        for offset in range(0, len(stock) - 3, 2):
            address = START + offset
            first, second = struct.unpack_from("<HH", stock, offset)
            for link in (True, False):
                target = wide_branch_target(
                    address, first, second, link=link
                )
                if target is not None:
                    outgoing.append((address, link, target))
        self.assertEqual(outgoing, [])

    def test_whole_application_ingress_is_closed_through_final_halfword(
        self,
    ) -> None:
        incoming_bl = []
        incoming_bw = []
        interior = []
        conditional = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            for link, owner in ((True, incoming_bl), (False, incoming_bw)):
                target = wide_branch_target(
                    address, first, second, link=link
                )
                if target is None or not START <= target < END:
                    continue
                if target == START:
                    owner.append((address, self.application[offset:offset + 4].hex()))
                elif not START <= address < END:
                    interior.append((address, target, link))
            target = wide_conditional_target(address, first, second)
            if (
                target is not None
                and START <= target < END
                and not START <= address < END
            ):
                conditional.append((address, target))

        narrow = []
        final_halfword_address = None
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            final_halfword_address = address
            if START <= address < END:
                continue
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_targets(address, halfword):
                if START <= target < END:
                    narrow.append((address, target))
        self.assertEqual(
            final_halfword_address,
            APPLICATION_BASE + len(self.application) - 2,
        )

        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if START <= (value & ~1) < END:
                stored.append((APPLICATION_BASE + offset, value, offset % 4))

        self.assertEqual(incoming_bl, CALLERS)
        self.assertEqual(incoming_bw, [])
        self.assertEqual(interior, [])
        self.assertEqual(conditional, [])
        self.assertEqual(narrow, [])
        self.assertEqual(stored, [])

    def test_production_adapter_matches_pristine_definition_deterministically(
        self,
    ) -> None:
        directed = (
            0x0000_0000,
            0xFFFF_FFFF,
            0x7800_0000,
            0x8000_0000,
            0x7000_0000,
            0x0800_0000,
            0x1234_5678,
            0xA5A5_5A5A,
        )
        for tag in directed:
            expected = (tag & 0x7800_0000) >> 20
            self.assertEqual(self.candidate(tag), expected, hex(tag))
            self.assertEqual(self.candidate(tag), self.pristine(tag), hex(tag))

        # The result depends only on the upper 16 bits. Exercise every one of
        # those combinations with deterministic nonzero lower-bit noise.
        for upper in range(1 << 16):
            lower = (upper * 0x9E37 + 0xBEEF) & 0xFFFF
            tag = (upper << 16) | lower
            candidate = self.candidate(tag)
            pristine = self.pristine(tag)
            self.assertEqual(candidate, pristine, hex(tag))
            self.assertEqual(candidate, (tag & 0x7800_0000) >> 20, hex(tag))

    def test_apple_thumb_object_text_and_no_dependency_closure_are_exact(
        self,
    ) -> None:
        first = self.objects[0].read_bytes()
        second = self.objects[1].read_bytes()
        self.assertEqual(first, second)
        self.assertEqual((len(first), sha256(first)), TARGET_OBJECT_PIN)

        data, sections = self.apollo_overlay.parse_elf32(self.objects[0])
        text = self.apollo_overlay.section_named(sections, SECTION)
        payload = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        self.assertEqual((len(payload), sha256(payload)), TARGET_TEXT_PIN)
        self.assertEqual(payload, TARGET_TEXT)
        self.assertEqual(int(text["alignment"]), 4)

        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        function = next(symbol for symbol in symbols if symbol["name"] == FUNCTION)
        self.assertEqual(function["size"], len(TARGET_TEXT))
        undefined = sorted(
            symbol["name"]
            for symbol in symbols
            if symbol["name"] and symbol["section_index"] == 0
        )
        self.assertEqual(undefined, [])

        text_relocations = []
        metadata_relocations = []
        symtab = self.apollo_overlay.section_named(sections, ".symtab")
        strtab = sections[int(symtab["link"])]
        strings = data[
            int(strtab["offset"]):int(strtab["offset"]) + int(strtab["size"])
        ]
        names = []
        for index in range(int(symtab["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH", data, int(symtab["offset"]) + 16 * index
            )
            names.append(
                self.apollo_overlay.elf_string(strings, fields[0], "symbol")
            )
        for section in sections:
            if int(section["type"]) != 9:
                continue
            target = sections[int(section["info"])]
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II", data, int(section["offset"]) + 8 * index
                )
                record = (offset, information & 0xFF, names[information >> 8])
                if target["name"] == SECTION:
                    text_relocations.append(record)
                else:
                    metadata_relocations.append((target["name"], *record))
        self.assertEqual(text_relocations, [])
        self.assertEqual(
            metadata_relocations,
            [(".ARM.exidx" + SECTION, 0, 42, "")],
        )

        allocated = {
            section["name"]: int(section["size"])
            for section in sections
            if int(section["size"]) and int(section["flags"]) & 2
        }
        self.assertEqual(
            allocated,
            {SECTION: 10, ".ARM.exidx" + SECTION: 8},
        )


if __name__ == "__main__":
    unittest.main()
