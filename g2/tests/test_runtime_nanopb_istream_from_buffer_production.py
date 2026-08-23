#!/usr/bin/env python3
"""Focused production qualification for the nanopb stream constructor."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "components/shared/nanopb"
    / "runtime_nanopb_istream_from_buffer.c"
)
HEADER = SOURCE.with_suffix(".h")
FIXTURE = (
    ROOT / "tests/fixtures"
    / "runtime_nanopb_istream_from_buffer_production_host.c"
)
SNAPSHOT = ROOT / "third_party/nanopb"
UPSTREAM = SNAPSHOT / "pb_decode.c"
CONFIG = SNAPSHOT / "g2-config/pb_g2_options.h"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
CANDIDATE_PATHS = (
    ROOT / "components/shared/nanopb/runtime_nanopb_istream_from_buffer_candidate.c",
    ROOT / "components/shared/nanopb/runtime_nanopb_istream_from_buffer_candidate.h",
    ROOT / "tests/test_runtime_nanopb_istream_from_buffer_candidate.py",
    ROOT / "tests/fixtures/runtime_nanopb_istream_from_buffer_candidate_host.c",
)

PACKAGE_PREAMBLE = 32
APPLICATION_BASE = 0x0043_8000
PACKAGE_PIN = (
    3_523_396,
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
)
BOOT_PIN = (
    148_599,
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5",
)
CONSTRUCTOR = (0x0048_F49C, 0x0048_F4B8)
CONSTRUCTOR_HEX = (
    "f8b5dff8d8370093019102920021039169461022aaf7a8fb05b000bd"
)
CONSTRUCTOR_SHA256 = (
    "852314bb8f86dcbd550deb0f51bc285b662e39c1b4fae66690c44a7bf4f7a674"
)
SUCCESSOR_PATCH_NAME = "replace_nanopb_decode_varint32_eof"
SUCCESSOR_SPAN = (CONSTRUCTOR[1], 0x0048_F5AE)
SUCCESSOR_STOCK_SHA256 = (
    "8583fa17383d72bbdcab6c2a7a20369dc0598d3ac3061feaf8a7b29dfa520150"
)
CALLBACK_SLOT = 0x0048_FC78
CALLBACK_VALUE = 0x0048_F3A5
COPY_PROVIDER = 0x0043_9C04
CALLERS = (
    0x0045_934E, 0x0045_9F12, 0x0046_07AC, 0x0047_1726,
    0x0047_2122, 0x0048_FBD0, 0x0048_FE1C, 0x0049_4D0A,
    0x0049_56C6, 0x0049_6652, 0x0049_B252, 0x004A_7988,
    0x004D_6C58, 0x004D_84A2, 0x004D_A8F2, 0x004E_3280,
    0x004F_E392, 0x0050_1AD6, 0x0050_1FE8, 0x0051_0AC4,
    0x0055_8A06, 0x0055_A40A, 0x0058_736A, 0x0058_8632,
    0x0059_F5BA, 0x005B_1BCA, 0x005C_E294, 0x005C_E9EC,
    0x005E_E942, 0x005E_EC0E,
)
UPSTREAM_DEFINITION = (
    5114,
    5692,
    "087c2b851d9ea55d5a81d70a37a88385ee7fe8db86daef34ea3d0584183b0b13",
)
LOCAL_PINS = {
    SOURCE: (
        1741,
        "f56a603644c5e9cd85781f8d3be2c69e85e458c48fa7ecd8633d6c6a9dbda3d9",
    ),
    HEADER: (
        1290,
        "b72524945afeec8eb3f304b8a7e0002c0d842598a908ddb82f59cc4894fc773f",
    ),
    FIXTURE: (
        2459,
        "958a15bc1221e9ace5efee090265077ffd2feb35b8667797465801a43ca22ed7",
    ),
}
FUNCTION = "open_cfw_nanopb_istream_from_buffer"
PRODUCTION_SOURCE_PATH = "components/shared/nanopb/runtime_nanopb_istream_from_buffer.c"
PRODUCTION_AUDIT_PATH = (
    "docs/research/nanopb-istream-from-buffer-source-audit.md"
)
PATCH_NAME = "replace_nanopb_istream_from_buffer"
IDENTITY = "open_cfw_nanopb_stock_buffer_read_identity"
IDENTITY_RELOCATIONS = [
    {
        "offset": 0,
        "type": "R_ARM_THM_MOVW_ABS_NC",
        "symbol": IDENTITY,
        "symbol_type": "STT_NOTYPE",
        "target_address": CALLBACK_VALUE,
    },
    {
        "offset": 4,
        "type": "R_ARM_THM_MOVT_ABS",
        "symbol": IDENTITY,
        "symbol_type": "STT_NOTYPE",
        "target_address": CALLBACK_VALUE,
    },
]
SECTION = ".text." + FUNCTION
APPLE_CLANG = "/usr/bin/clang"
APPLE_VERSION = "Apple clang version 21.0.0 (clang-2100.3.30.1)"
LINUX_CLANG = "/home/linuxbrew/.linuxbrew/bin/clang"
LINUX_VERSION_PREFIX = "Homebrew clang version 22.1.8"
OBJECT_PIN = (
    968,
    "8adb6055fcc0b0cf76e1a37773154ec3fd0eac46a037f85d28af804b7fc9e5a2",
)
LINUX_OBJECT_PIN = (
    972,
    "5622e997718fb1414b31fbc14d31dee25e99be05cd3df27e322f3c2b8d148fd7",
)
TEXT_PIN = (
    20,
    "d106ce1009ddcbd4d39a7c56edbcd51f50d4cfa6768f78d224ea988aa9a416d7",
)
LINUX_TEXT_PIN = (
    22,
    "6c23e37c9468d866db2e2cb6bf0ce8e103fb34df1078e740b4b8d5d799c257ff",
)
TARGET_TEXT_HEX = "40f20003c0f200034160002103608260c1607047"
APPLE_LEAF = {
    "size": 20,
    "sha256": "af3357e8178ab650d5476d0ad0fbfee0b44cdb288d9251da909b3ba7a1de92c4",
    "alignment": 4,
    "offset": 124896,
    "unrelocated_sha256": TEXT_PIN[1],
}
LINUX_LEAF = {
    "size": 22,
    "sha256": "59438f30232883560f65ad4e58ff97c05dcdffdb6287fffcb7c1b79487df436d",
    "alignment": 4,
    "offset": 126720,
    "unrelocated_sha256": (
        "6c23e37c9468d866db2e2cb6bf0ce8e103fb34df1078e740b4b8d5d799c257ff"
    ),
}
PROFILE_PATCH_PINS = {
    "apple-clang": (
        "23f332bb",
        "e2e120080f18fdd443e08a5def120575a2eae21139a5276f3f8fbb53e1aea6dd",
    ),
    "linux-clang": (
        "23f3c2be",
        "902daf1332ace8eae1d3f71e324ddbc03ec2542d93530fa876f24228d40c86ed",
    ),
}
APPLE_AGGREGATE = {
    "overlay": (
        165_412,
        "91449e27a73806e1537548657bed4486d77b275e4ee8a58b2bb1ef527c252ada",
    ),
    "component": (
        3_688_808,
        "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c",
    ),
}
LINUX_AGGREGATE = {
    "overlay": (
        145_180,
        "afbcb57a8414e65a18c6c95396a0f32fe454cb2087e6a03d51717196a4854b57",
    ),
    "component": (
        3_668_576,
        "292f55478951dc8d41a8bc5e4cc01f80ae88f9c44350d8fec89958c939a4fac5",
    ),
    "package": (
        4_447_070,
        "be5c62a97b9d31f4df257615c28ce81d79ab186feadb68262f96ac5bc35a1c25",
    ),
}
TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-fno-ident",
)


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def wide_branch_target(
    address: int, first: int, second: int, *, link: bool
) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    immediate = (
        sign << 24
        | (1 ^ (j1 ^ sign)) << 23
        | (1 ^ (j2 ^ sign)) << 22
        | (first & 0x03FF) << 12
        | (second & 0x07FF) << 1
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
        sign << 20
        | ((second >> 11) & 1) << 19
        | ((second >> 13) & 1) << 18
        | (first & 0x003F) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 21
    return address + 4 + immediate


def narrow_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if halfword & 0xF000 == 0xD000 and (halfword >> 8) & 0x0F < 0x0E:
        immediate = halfword & 0xFF
        if immediate & 0x80:
            immediate -= 0x100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return (address + 4 + immediate * 2,)
    return ()


class NanopbIstreamFromBufferProductionTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG", APPLE_CLANG)
        cls.profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE", "apple-clang")
        version = subprocess.run(
            [cls.clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        if cls.profile == "apple-clang":
            reviewed = cls.clang == APPLE_CLANG and version == APPLE_VERSION
        elif cls.profile == "linux-clang":
            reviewed = (
                cls.clang == LINUX_CLANG
                and version.startswith(LINUX_VERSION_PREFIX)
            )
        else:
            reviewed = False
        if not reviewed:
            raise AssertionError(f"unreviewed target compiler: {cls.clang}: {version}")

        cls.temporary = tempfile.TemporaryDirectory(
            prefix=".istream-constructor-production-",
            dir=ROOT / "components/apollo_main/core_overlay",
        )
        temporary = Path(cls.temporary.name)
        cls.objects = [temporary / "production-a.o", temporary / "production-b.o"]
        for output in cls.objects:
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output)],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )

        library = temporary / (
            "constructor.dylib" if sys.platform == "darwin" else "constructor.so"
        )
        command = [
            cls.clang, "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT), "-I", str(SNAPSHOT), "-include", str(CONFIG),
            str(SOURCE), str(FIXTURE), str(UPSTREAM),
            str(SNAPSHOT / "pb_common.c"),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        cls.host_test = (
            cls.library.open_cfw_test_nanopb_istream_from_buffer_production
        )
        cls.host_test.argtypes = []
        cls.host_test.restype = ctypes.c_int

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        cls.apollo_overlay = apollo_overlay
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]
        cls.component_report = apollo_overlay.build(
            root=ROOT,
            config_path=OVERLAY,
            output_dir=temporary / "component-build",
            clang=cls.clang,
            toolchain_profile=cls.profile,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_upstream_and_local_files_are_exact(self) -> None:
        for path, expected in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual((path.stat().st_size, sha256(path)), expected)
        start, end, digest = UPSTREAM_DEFINITION
        definition = UPSTREAM.read_bytes()[start:end]
        self.assertTrue(definition.startswith(b"pb_istream_t pb_istream_from_buffer("))
        self.assertTrue(definition.endswith(b"return stream;\n}"))
        self.assertEqual((len(definition), sha256(definition)), (578, digest))
        self.assertEqual(
            (UPSTREAM.stat().st_size, sha256(UPSTREAM)),
            (
                53_845,
                "e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a",
            ),
        )
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(
            {
                key: provenance["upstream"][key]
                for key in (
                    "selected_tag", "selected_commit", "selected_tree",
                    "declared_library_version",
                )
            },
            {
                "selected_tag": "nanopb-0.4.9",
                "selected_commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
                "selected_tree": "2c4c260bcff3f9f7081238d377274dd385d76582",
                "declared_library_version": "0.4.9",
            },
        )
        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        fixture = FIXTURE.read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2011 Petteri Aimonen", source)
        self.assertIn("Altered production adaptation", source)
        self.assertIn("runtime_nanopb_read.h", header)
        self.assertNotIn("_Static_assert", header)
        self.assertEqual(header.count(FUNCTION), 1)
        for text in (source, header, fixture):
            self.assertNotIn("candidate", text.lower())

    def test_candidate_artifacts_are_removed(self) -> None:
        for path in CANDIDATE_PATHS:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertFalse(path.exists())

    def test_constructor_has_one_bounded_production_registration(self) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertEqual(
            (
                len(config["functions"]),
                len(config["patch_sites"]),
                len(config["relocated_leaves"]),
            ),
            (947, 886, 378),
        )
        self.assertEqual(config["functions"].count(FUNCTION), 1)
        leaves = [
            item for item in config["relocated_leaves"]
            if item["function"] == FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        leaf = leaves[0]
        self.assertEqual(
            {
                key: leaf["source"][key]
                for key in ("path", "license", "origin", "upstream", "evidence")
            },
            {
                "path": PRODUCTION_SOURCE_PATH,
                "license": "Zlib",
                "origin": (
                    "altered production adaptation of authenticated nanopb "
                    "0.4.9 pb_istream_from_buffer, byte-identical at source "
                    "level in authenticated nanopb 0.4.7 through 0.4.9"
                ),
                "upstream": (
                    "https://github.com/nanopb/nanopb/blob/"
                    "98bf4db69897b53434f3d0ba72e0a3ab1a902824/pb_decode.c"
                ),
                "evidence": PRODUCTION_AUDIT_PATH,
            },
        )
        self.assertEqual(
            {
                "size": leaf["source"]["size"],
                "sha256": leaf["source"]["sha256"],
                "upstream_commit": leaf["source"]["upstream_commit"],
            },
            {
                "size": LOCAL_PINS[SOURCE][0],
                "sha256": LOCAL_PINS[SOURCE][1],
                "upstream_commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
            },
        )
        self.assertEqual(leaf["toolchain"]["target"], "thumbv7em-none-eabi")
        self.assertEqual(
            tuple(leaf["toolchain"]["flags"]),
            TARGET_FLAGS[1:],
        )
        self.assertNotIn("-fropi", leaf["toolchain"]["flags"])
        self.assertIs(leaf["strict_relocation_contract"], True)
        self.assertEqual(leaf["relocations"], IDENTITY_RELOCATIONS)
        self.assertEqual(leaf["expected"], APPLE_LEAF)
        linux = leaf["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            linux["reviewed_version_prefix"],
            "Homebrew clang version 22.1.8",
        )
        self.assertEqual(linux["expected"], LINUX_LEAF)
        self.assertEqual(linux["relocations"], IDENTITY_RELOCATIONS)
        patches = [
            item for item in config["patch_sites"]
            if item.get("name") == PATCH_NAME
            or item.get("target_function") == FUNCTION
        ]
        self.assertEqual(len(patches), 1)
        self.assertEqual(
            patches[0],
            {
                "name": PATCH_NAME,
                "runtime_address": CONSTRUCTOR[0],
                "expected_size": CONSTRUCTOR[1] - CONSTRUCTOR[0],
                "expected_sha256": CONSTRUCTOR_SHA256,
                "branch": "b_w",
                "target_function": FUNCTION,
            },
        )
        for profile, expected in (
            ("apple-clang", APPLE_LEAF),
            ("linux-clang", LINUX_LEAF),
        ):
            runtime = 0x0079_4324 + expected["offset"]
            patch = self.apollo_overlay.encode_thumb_b_w(CONSTRUCTOR[0], runtime)
            patch += bytes.fromhex("00bf") * 12
            prefix, digest = PROFILE_PATCH_PINS[profile]
            with self.subTest(profile=profile):
                self.assertEqual(patch[:4].hex(), prefix)
                self.assertEqual(sha256(patch), digest)

    def test_linux_profile_aggregate_and_manifest_pins_are_exact(self) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
        linux = config["toolchain_profiles"]["linux-clang"]
        self.assertEqual(linux["reviewed_version_prefix"], LINUX_VERSION_PREFIX)
        self.assertEqual(
            linux["reviewed_source_root"],
            "/Users/kalani/Repo/SybilSightABCD/openCFW",
        )
        self.assertEqual(
            (
                linux["expected"]["overlay_size"],
                linux["expected"]["overlay_sha256"],
            ),
            LINUX_AGGREGATE["overlay"],
        )
        self.assertEqual(
            (
                linux["expected"]["component_size"],
                linux["expected"]["component_sha256"],
            ),
            LINUX_AGGREGATE["component"],
        )
        self.assertEqual(
            manifest["package"]["profiles"]["linux-clang"],
            {
                "expected_size": LINUX_AGGREGATE["package"][0],
                "expected_sha256": LINUX_AGGREGATE["package"][1],
            },
        )
        provider = manifest["component_overrides"]["apollo_main"]["provider"]
        self.assertEqual(
            provider["profiles"]["linux-clang"],
            {
                "size": LINUX_AGGREGATE["component"][0],
                "sha256": LINUX_AGGREGATE["component"][1],
            },
        )

    def test_stock_body_thirty_callers_and_no_pointer_ingress_are_exact(self) -> None:
        self.assertEqual((len(self.package), sha256(self.package)), PACKAGE_PIN)
        start, end = CONSTRUCTOR
        body = self.application[start - APPLICATION_BASE:end - APPLICATION_BASE]
        self.assertEqual(body.hex(), CONSTRUCTOR_HEX)
        self.assertEqual(sha256(body), CONSTRUCTOR_SHA256)
        slot_offset = CALLBACK_SLOT - APPLICATION_BASE
        self.assertEqual(
            struct.unpack_from("<I", self.application, slot_offset)[0],
            CALLBACK_VALUE,
        )

        results = {"bl": [], "bw": [], "conditional": [], "narrow": []}
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            for name, target in (
                ("bl", wide_branch_target(address, first, second, link=True)),
                ("bw", wide_branch_target(address, first, second, link=False)),
                ("conditional", wide_conditional_target(address, first, second)),
            ):
                if target is not None and start <= target < end:
                    results[name].append((address, target))
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            if start <= address < end:
                continue
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_targets(address, halfword):
                if start <= target < end:
                    results["narrow"].append((address, target))
        self.assertEqual(results["bl"], [(address, start) for address in CALLERS])
        self.assertEqual(results["bw"], [])
        self.assertEqual(results["conditional"], [])
        self.assertEqual(results["narrow"], [])

        pointers = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if start <= (value & ~1) < end:
                pointers.append((APPLICATION_BASE + offset, value, offset % 4))
        self.assertEqual(pointers, [])

        outgoing = []
        for offset in range(0, len(body) - 3, 2):
            target = wide_branch_target(
                start + offset,
                *struct.unpack_from("<HH", body, offset),
                link=True,
            )
            if target is not None:
                outgoing.append((start + offset, target))
        self.assertEqual(outgoing, [(0x0048_F4B0, COPY_PROVIDER)])

    def test_callback_literal_and_source_identity_are_canonical(self) -> None:
        literal_refs = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            pc = (address + 4) & ~3
            if first & 0xF800 == 0x4800:
                target = pc + (first & 0xFF) * 4
                if target == CALLBACK_SLOT:
                    literal_refs.append(address)
            if first in (0xF8DF, 0xF85F):
                displacement = second & 0x0FFF
                target = pc + displacement if first == 0xF8DF else pc - displacement
                if target == CALLBACK_SLOT:
                    literal_refs.append(address)
        self.assertEqual(literal_refs, [0x0048_F3D4, 0x0048_F49E])
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("open_cfw_nanopb_stock_buffer_read_identity", source)
        self.assertNotIn("open_cfw_nanopb_buf_read", source)
        self.assertIn("0x0048F3A5", source)

    def test_no_authenticated_bootloader_homolog(self) -> None:
        boot = BOOT.read_bytes()
        self.assertEqual((len(boot), sha256(boot)), BOOT_PIN)
        start, end = CONSTRUCTOR
        body = self.application[start - APPLICATION_BASE:end - APPLICATION_BASE]
        self.assertNotIn(body, boot)
        for probe in (
            bytes.fromhex("dff8d837009301910292"),
            bytes.fromhex("0021039169461022"),
            struct.pack("<I", CALLBACK_VALUE),
        ):
            self.assertNotIn(probe, boot)

    def test_host_behavior_matches_authenticated_upstream(self) -> None:
        self.assertEqual(self.host_test(), 0)

    def test_apple_target_sret_instructions_are_explicit(self) -> None:
        if self.profile != "apple-clang":
            self.skipTest("instruction spelling is the reviewed Apple-clang contract")
        data, sections = self.apollo_overlay.parse_elf32(self.objects[0])
        text = next(section for section in sections if section["name"] == SECTION)
        body = data[int(text["offset"]):int(text["offset"]) + int(text["size"])]
        self.assertEqual(body.hex(), TARGET_TEXT_HEX)
        self.assertEqual(
            struct.unpack("<10H", body),
            (
                0xF240, 0x0300,  # movw r3, callback low half
                0xF2C0, 0x0300,  # movt r3, callback high half
                0x6041,          # str r1, [r0, #4]: buffer into hidden result
                0x2100,          # movs r1, #0
                0x6003,          # str r3, [r0, #0]: callback
                0x6082,          # str r2, [r0, #8]: message length
                0x60C1,          # str r1, [r0, #12]: NULL error
                0x4770,          # bx lr
            ),
        )

    def test_linked_callback_identity_and_full_span_entry_patch_are_exact(
        self,
    ) -> None:
        report = self.component_report
        aggregate = (
            APPLE_AGGREGATE
            if self.profile == "apple-clang"
            else LINUX_AGGREGATE
        )
        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            aggregate["overlay"],
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]),
            aggregate["component"],
        )
        constructor = next(
            item for item in report["relocated_leaves"]
            if item["extraction"]["function"] == FUNCTION
        )
        runtime = constructor["placement"]["runtime_address"]
        overlay = (ROOT / report["overlay"]["artifact"]).read_bytes()
        placement = constructor["placement"]
        linked = overlay[
            placement["offset"]:placement["offset"] + placement["size"]
        ]
        expected_leaf = APPLE_LEAF if self.profile == "apple-clang" else LINUX_LEAF
        self.assertEqual(
            (len(linked), sha256(linked)),
            (expected_leaf["size"], expected_leaf["sha256"]),
        )

        low_first, low_second, high_first, high_second = struct.unpack_from(
            "<4H", linked
        )
        self.assertEqual((low_second >> 8) & 0xF, 3)
        self.assertEqual((high_second >> 8) & 0xF, 3)
        callback = self.apollo_overlay.thumb_movwt_immediate(
            low_first, low_second
        ) | (
            self.apollo_overlay.thumb_movwt_immediate(high_first, high_second)
            << 16
        )
        self.assertEqual(callback, CALLBACK_VALUE)
        self.assertEqual(callback & 1, 1)
        appended_buf_read = next(
            item for item in report["relocated_leaves"]
            if item["extraction"]["function"] == "open_cfw_nanopb_buf_read"
        )["placement"]["runtime_address"]
        self.assertNotEqual(callback, appended_buf_read | 1)

        patch_report = next(
            item for item in report["overlay"]["patched_sites"]
            if item["name"] == PATCH_NAME
        )
        component = (ROOT / report["component"]["artifact"]).read_bytes()
        offset = patch_report["payload_offset"]
        generated = component[offset:offset + 28]
        patch_pin = PROFILE_PATCH_PINS[self.profile]
        self.assertEqual(generated[:4].hex(), patch_pin[0])
        self.assertEqual(generated[4:], bytes.fromhex("00bf") * 12)
        self.assertEqual(sha256(generated), patch_pin[1])
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                CONSTRUCTOR[0], generated[:4], link=False
            ),
            runtime,
        )
        sites = {
            item["name"]: item for item in report["overlay"]["patched_sites"]
        }
        cluster = [
            sites["replace_nanopb_buf_read"],
            sites["replace_nanopb_read"],
            sites["replace_nanopb_readbyte"],
            patch_report,
        ]
        self.assertEqual(
            [item["runtime_address"] for item in cluster],
            [0x0048_F3A4, 0x0048_F3BE, 0x0048_F454, 0x0048_F49C],
        )
        # These four authenticated nanopb replacements are exactly adjacent.
        # Each predecessor halfword inside the cluster is therefore the
        # preceding full-span patch's final NOP, not the old stock return.
        for preceding, following in zip(cluster, cluster[1:]):
            preceding_bytes = bytes.fromhex(preceding["replacement_hex"])
            following_offset = following["payload_offset"]
            self.assertEqual(
                preceding["payload_offset"] + len(preceding_bytes),
                following_offset,
            )
            self.assertEqual(preceding_bytes[-2:], bytes.fromhex("00bf"))
            self.assertEqual(
                component[following_offset - 2:following_offset],
                preceding_bytes[-2:],
            )
        # The predecessor halfword outside the original contiguous cluster
        # remains byte-for-byte stock.
        cluster_offset = cluster[0]["payload_offset"]
        self.assertEqual(
            component[cluster_offset - 2:cluster_offset],
            self.package[cluster_offset - 2:cluster_offset],
        )

        # The constructor's immediate successor is now the complete private
        # varint32 generated entry patch. Authenticate both the generated
        # replacement and its separately retained official-stock provenance.
        successor = sites[SUCCESSOR_PATCH_NAME]
        successor_offset = offset + (CONSTRUCTOR[1] - CONSTRUCTOR[0])
        successor_size = SUCCESSOR_SPAN[1] - SUCCESSOR_SPAN[0]
        successor_stock = self.package[
            successor_offset:successor_offset + successor_size
        ]
        successor_replacement = bytes.fromhex(successor["replacement_hex"])
        self.assertEqual(
            (
                successor["runtime_address"],
                successor["payload_offset"],
                successor["expected_size"],
                successor["expected_sha256"],
            ),
            (
                SUCCESSOR_SPAN[0],
                successor_offset,
                successor_size,
                SUCCESSOR_STOCK_SHA256,
            ),
        )
        self.assertEqual(successor_stock[:2], bytes.fromhex("f8b5"))
        self.assertEqual(sha256(successor_stock), SUCCESSOR_STOCK_SHA256)
        self.assertEqual(len(successor_replacement), successor_size)
        self.assertEqual(successor_replacement[4:], bytes.fromhex("00bf") * 121)
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                SUCCESSOR_SPAN[0], successor_replacement[:4], link=False
            ),
            successor["target_address"],
        )
        self.assertEqual(
            component[successor_offset:successor_offset + successor_size],
            successor_replacement,
        )

        application = component[PACKAGE_PREAMBLE:]
        callers = []
        for app_offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + app_offset
            target = wide_branch_target(
                address,
                *struct.unpack_from("<HH", application, app_offset),
                link=True,
            )
            if target == CONSTRUCTOR[0]:
                callers.append(address)
        source_replaced_stock_sites = (0x0048_FBD0, 0x0048_FE1C)
        self.assertEqual(
            callers,
            [
                address
                for address in CALLERS
                if address not in source_replaced_stock_sites
            ],
        )

    def test_target_object_and_relocation_closure_are_exact(self) -> None:
        self.assertEqual(self.objects[0].read_bytes(), self.objects[1].read_bytes())
        expected_object = (
            OBJECT_PIN if self.profile == "apple-clang" else LINUX_OBJECT_PIN
        )
        for path in self.objects:
            self.assertEqual((path.stat().st_size, sha256(path)), expected_object)
        data, sections = self.apollo_overlay.parse_elf32(self.objects[0])
        executable = [
            section["name"] for section in sections
            if int(section["size"]) > 0 and int(section["flags"]) & 0x4
        ]
        self.assertEqual(executable, [SECTION])
        writable = [
            section["name"] for section in sections
            if int(section["size"]) > 0 and int(section["flags"]) & 0x3 == 0x3
        ]
        self.assertEqual(writable, [])
        text = next(section for section in sections if section["name"] == SECTION)
        body = data[int(text["offset"]):int(text["offset"]) + int(text["size"])]
        expected_text = TEXT_PIN if self.profile == "apple-clang" else LINUX_TEXT_PIN
        self.assertEqual((len(body), sha256(body)), expected_text)
        self.assertEqual(int(text["alignment"]), 4)

        symbol_table = self.apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH", data, int(symbol_table["offset"]) + index * 16
            )
            symbols.append(
                (self.apollo_overlay.elf_string(strings, fields[0], "symbol"), fields)
            )
        undefined = [name for name, fields in symbols if name and fields[5] == 0]
        self.assertEqual(undefined, [IDENTITY])

        relocations = {}
        for section in sections:
            if int(section["type"]) != 9:
                continue
            target = sections[int(section["info"])]["name"]
            records = []
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II", data, int(section["offset"]) + index * 8
                )
                records.append(
                    (offset, information & 0xFF, symbols[information >> 8][0])
                )
            relocations[target] = records
        self.assertEqual(
            relocations,
            {
                SECTION: [(0, 47, IDENTITY), (4, 48, IDENTITY)],
                ".ARM.exidx" + SECTION: [(0, 42, "")],
            },
        )


if __name__ == "__main__":
    unittest.main()
