#!/usr/bin/env python3
"""Focused production qualification for the private nanopb read pair."""

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
BUF_SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_buf_read.c"
BYTE_SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_readbyte.c"
HEADER = ROOT / "components/shared/nanopb/runtime_nanopb_private_read_pair.h"
FIXTURE = (
    ROOT / "tests/fixtures"
    / "runtime_nanopb_private_read_pair_host.c"
)
AUDIT = (
    ROOT / "docs/research"
    / "nanopb-private-read-pair-source-audit.md"
)
SNAPSHOT = ROOT / "third_party/nanopb"
UPSTREAM = SNAPSHOT / "pb_decode.c"
CONFIG = SNAPSHOT / "g2-config/pb_g2_options.h"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"

PACKAGE_PREAMBLE = 32
APPLICATION_BASE = 0x0043_8000
PACKAGE_PIN = (
    3_523_396,
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
)
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
)
BOOT_PIN = (
    148_599,
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5",
)

BUF_READ = (0x0048_F3A4, 0x0048_F3BE)
BUF_READ_HEX = "10b50c004168436813444360002c02d02000aaf715fc012010bd"
BUF_READ_SHA256 = (
    "9d6c6690294b82bbafba82ec0f63a6bb5b78e4146543db3a30fac92469ace723"
)
PB_READBYTE = (0x0048_F454, 0x0048_F49C)
PB_READBYTE_HEX = (
    "10b50400a068002809d1e068002801d0e06801e0dff81008e060002013e00122"
    "200023689847002809d1e068002801d0e06801e0dff8f407e060002003e0a068"
    "401ea060012010bd"
)
PB_READBYTE_SHA256 = (
    "15c8303c5c1dbf1b3f143142c6169026cb8bc56b37a6291dd0457b3664b67ae5"
)
CONSTRUCTOR = (0x0048_F49C, 0x0048_F4B8)
CONSTRUCTOR_SHA256 = (
    "852314bb8f86dcbd550deb0f51bc285b662e39c1b4fae66690c44a7bf4f7a674"
)
MEMCPY = (0x0043_9BE4, 0x0043_9C8A)
MEMCPY_SHA256 = (
    "8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd"
)
CALLBACK_SLOT = 0x0048_FC78
CALLBACK_VALUE = 0x0048_F3A5
CALLBACK_SLOT_SHA256 = (
    "4be42e91f7757f32aff0acddae22d357d34e83b8f10ef8e9c93339501ea69c3b"
)
ERRORS = (
    (
        0x0048_FC7C,
        0x0078_7C70,
        b"end-of-stream\0",
        "e167d4f2ec31a2197c7bc32affd9865ac8609d7dae984d0916e01f044fcc67b4",
    ),
    (
        0x0048_FC80,
        0x0078_B690,
        b"io error\0",
        "3faaf40b4ee3e3b23823ed9851dc77bf6fc2d7c7c330240eeaed08bd9d084ec1",
    ),
)
READBYTE_CALLERS = (0x0048_F4C4, 0x0048_F4FA, 0x0048_F5CC)
CONSTRUCTOR_CALLERS = (
    0x0045_934E, 0x0045_9F12, 0x0046_07AC, 0x0047_1726,
    0x0047_2122, 0x0048_FBD0, 0x0048_FE1C, 0x0049_4D0A,
    0x0049_56C6, 0x0049_6652, 0x0049_B252, 0x004A_7988,
    0x004D_6C58, 0x004D_84A2, 0x004D_A8F2, 0x004E_3280,
    0x004F_E392, 0x0050_1AD6, 0x0050_1FE8, 0x0051_0AC4,
    0x0055_8A06, 0x0055_A40A, 0x0058_736A, 0x0058_8632,
    0x0059_F5BA, 0x005B_1BCA, 0x005C_E294, 0x005C_E9EC,
    0x005E_E942, 0x005E_EC0E,
)

UPSTREAM_DEFINITIONS = {
    "buf_read": (
        b"static bool checkreturn buf_read(pb_istream_t *stream, "
        b"pb_byte_t *buf, size_t count)\n{",
        3421,
        3743,
        "34b5a0a938c4cbfe431c24afc0a8f273879eef4ee4853282d4c44708f27f4867",
    ),
    "pb_readbyte": (
        b"static bool checkreturn pb_readbyte(pb_istream_t *stream, "
        b"pb_byte_t *buf)\n{",
        4678,
        5112,
        "5a63231a2b3b2d79004219076ec6b6089c9d4ed2d9487cae9f0488e8c607c650",
    ),
    "pb_istream_from_buffer": (
        b"pb_istream_t pb_istream_from_buffer(const pb_byte_t *buf, "
        b"size_t msglen)\n{",
        5114,
        5692,
        "087c2b851d9ea55d5a81d70a37a88385ee7fe8db86daef34ea3d0584183b0b13",
    ),
}

LOCAL_PINS = {
    BUF_SOURCE: (
        1_685,
        "d7e464755bb4eff09207d33f1eb6b98ea49b43a91291001652d867f27bcd1bec",
    ),
    BYTE_SOURCE: (
        2_065,
        "f0cfa08ee31a67544f225830a023c38dd2c2e2903bfe6466ddcfc0a9dfb4bdbb",
    ),
    HEADER: (
        2_046,
        "00bb2c9885f951a711d60c37b02b77f3e679742ddce4255b0f108cec280535e4",
    ),
    FIXTURE: (
        8_319,
        "b67b60fd323fae5d2619360cba23e426b1d06cccc1bfbb4f15f5973f7a725a52",
    ),
    AUDIT: (
        11_344,
        "f025b71ce15c5b8f959524d34296e985a490cbcd43e81fc2f15428504526d075",
    ),
    UPSTREAM: (
        53_845,
        "e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a",
    ),
}

BUF_FUNCTION = "open_cfw_nanopb_buf_read"
BYTE_FUNCTION = "open_cfw_nanopb_readbyte"
BUF_SECTION = ".text." + BUF_FUNCTION
BYTE_SECTION = ".text." + BYTE_FUNCTION
COPY_SEAM = "__aeabi_memcpy"
END_SEAM = "open_cfw_nanopb_end_of_stream_error"
IO_SEAM = "open_cfw_nanopb_io_error"
TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-fno-ident",
)
APPLE_CLANG = "/usr/bin/clang"
COMPILER_PROFILES = {
    "apple-clang": {
        "compiler": APPLE_CLANG,
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "objects": {
            BUF_FUNCTION: (
                912,
                "fd491e856b03fcfb47646c0cd56e0ad2ebb017b2a64a67b52fcefb8b26a226b2",
            ),
            BYTE_FUNCTION: (
                1_032,
                "354a05cf1decc66a7a12f31f08fe28dd5cec2744a3e75f22f83e957e38991e69",
            ),
        },
        "sections": {
            BUF_SECTION: (
                30,
                "db26e5bd51f3d313907af94bfe545cc9962b867ed18285f2025c401e8613700a",
            ),
            BYTE_SECTION: (
                64,
                "eda66d0ae6274a2078b6eceaefc0e773169d5e15b26bce650a8d48b818e4f2b8",
            ),
        },
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "objects": {
            BUF_FUNCTION: (
                912,
                "fd491e856b03fcfb47646c0cd56e0ad2ebb017b2a64a67b52fcefb8b26a226b2",
            ),
            BYTE_FUNCTION: (
                1_032,
                "354a05cf1decc66a7a12f31f08fe28dd5cec2744a3e75f22f83e957e38991e69",
            ),
        },
        "sections": {
            BUF_SECTION: (
                30,
                "db26e5bd51f3d313907af94bfe545cc9962b867ed18285f2025c401e8613700a",
            ),
            BYTE_SECTION: (
                64,
                "eda66d0ae6274a2078b6eceaefc0e773169d5e15b26bce650a8d48b818e4f2b8",
            ),
        },
    },
}

OVERLAY_RUNTIME_BASE = 0x0079_4324
PROFILE_PINS = {
    "apple-clang": {
        BUF_FUNCTION: {
            "offset": 124_800,
            "relocated": "f312e087cf1fbecf19bd5fa0052d3a63ca91287c811de169aaf2a09322e0115e",
            "patch_prefix": "23f37ebb",
            "patch_sha256": "7b95b1a632ce6362c74c2a3f3ae2e9ef15f5abb6800d1dd8ca1dd4586b4f73ac",
        },
        BYTE_FUNCTION: {
            "offset": 124_832,
            "relocated": "f3395a19a7406016e6b1f1daf14969dee91ccde4e9a98ba4eeaba0016e131871",
            "patch_prefix": "23f336bb",
            "patch_sha256": "ed8460907148368a780a57a2abab8bb48cc80a78b980c38b0097e1b81ce1967e",
        },
    },
    "linux-clang": {
        BUF_FUNCTION: {
            "offset": 126_624,
            "relocated": "a6b4d3a4e969f078683f1cde3a4043b70d8495d577f550ae35c6c2789ff470de",
            "patch_prefix": "23f30ebf",
            "patch_sha256": "db7d0da006d031b33b6858a4b829d68403c9039f66d2ac4db576b00bdef94bec",
        },
        BYTE_FUNCTION: {
            "offset": 126_656,
            "relocated": "f3395a19a7406016e6b1f1daf14969dee91ccde4e9a98ba4eeaba0016e131871",
            "patch_prefix": "23f3c6be",
            "patch_sha256": "b571a49431ddbdd7c71059acf67da1227af1eecba58b09fafea45177eda87fd0",
        },
    },
}


def resolve_compiler_profile(
    compiler: str, version: str, configured_profile: str | None
) -> tuple[str, dict]:
    matches = [
        (profile, record)
        for profile, record in COMPILER_PROFILES.items()
        if compiler == record["compiler"] and version == record["version"]
    ]
    if len(matches) != 1:
        raise AssertionError(f"unreviewed target compiler: {compiler}: {version}")
    profile, record = matches[0]
    if configured_profile is not None and configured_profile != profile:
        raise AssertionError(
            "configured toolchain profile does not match reviewed compiler: "
            f"{configured_profile}: {profile}"
        )
    return profile, record


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
        sign << 24 |
        (1 ^ (j1 ^ sign)) << 23 |
        (1 ^ (j2 ^ sign)) << 22 |
        (first & 0x03FF) << 12 |
        (second & 0x07FF) << 1
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
        sign << 20 |
        ((second >> 11) & 1) << 19 |
        ((second >> 13) & 1) << 18 |
        (first & 0x003F) << 12 |
        (second & 0x07FF) << 1
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


class NanopbPrivateReadPairProductionTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG", APPLE_CLANG)
        version = subprocess.run(
            [cls.clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        cls.profile, cls.compiler_profile = resolve_compiler_profile(
            cls.clang,
            version,
            os.environ.get("OPENCFW_TOOLCHAIN_PROFILE"),
        )

        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-nanopb-private-read-pair-production-"
        )
        temporary = Path(cls.temporary.name)
        cls.objects = {}
        for function, source in (
            (BUF_FUNCTION, BUF_SOURCE), (BYTE_FUNCTION, BYTE_SOURCE)
        ):
            outputs = [
                temporary / f"{function}-a.o",
                temporary / f"{function}-b.o",
            ]
            for output in outputs:
                subprocess.run(
                    [cls.clang, *TARGET_FLAGS, "-c", str(source), "-o", str(output)],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            cls.objects[function] = outputs

        library = temporary / (
            "private-read-pair.dylib" if sys.platform == "darwin"
            else "private-read-pair.so"
        )
        command = [
            cls.clang, "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT), "-I", str(SNAPSHOT), "-include", str(CONFIG),
            str(BUF_SOURCE), str(BYTE_SOURCE), str(FIXTURE), str(UPSTREAM),
            str(SNAPSHOT / "pb_common.c"),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        cls.host_test = cls.library.open_cfw_test_nanopb_private_read_pair
        cls.host_test.argtypes = []
        cls.host_test.restype = ctypes.c_int

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        cls.apollo_overlay = apollo_overlay
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - APPLICATION_BASE:end - APPLICATION_BASE]

    def test_authenticated_upstream_and_production_files_are_pinned(self) -> None:
        for path, expected in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual((path.stat().st_size, sha256(path)), expected)

        source = UPSTREAM.read_bytes()
        for name, (signature, start, end, digest) in UPSTREAM_DEFINITIONS.items():
            with self.subTest(definition=name):
                definition = source[start:end]
                self.assertTrue(definition.startswith(signature))
                self.assertTrue(definition.endswith(b"}"))
                self.assertEqual(sha256(definition), digest)

        verification = subprocess.run(
            [sys.executable, str(VERIFIER)], cwd=ROOT, check=True,
            capture_output=True, text=True,
        )
        self.assertEqual(
            verification.stdout,
            "nanopb 0.4.9 compatibility snapshot verification passed\n",
        )
        sources = BUF_SOURCE.read_text(encoding="utf-8") + BYTE_SOURCE.read_text(
            encoding="utf-8"
        )
        header = HEADER.read_text(encoding="utf-8")
        audit = AUDIT.read_text(encoding="utf-8")
        for token in (
            "Altered production source",
            "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
            "does not prove the vendor's",
            "historical point release",
            "[0x0048F3A4,0x0048F3BE)",
            "[0x0048F454,0x0048F49C)",
        ):
            self.assertIn(token, sources)
        for token in (
            "0x00439BE4", "open_cfw_nanopb_end_of_stream_error",
            "open_cfw_nanopb_io_error", "canonical odd Thumb",
            "runtime_nanopb_decode_varint.h",
        ):
            self.assertIn(token, header)
        for token in (
            "production source", "Complete ingress and identity topology",
            "Retaining these addresses preserves error-pointer identity",
            "full-span entry", "patches at the two authenticated stock bodies",
            "exact-root Linux aggregate pins",
        ):
            self.assertIn(token, audit)

        for path in (BUF_SOURCE, BYTE_SOURCE, HEADER, FIXTURE, AUDIT):
            self.assertNotIn(
                "candidate", path.read_text(encoding="utf-8").lower(), path
            )

    def test_pair_is_registered_as_bounded_production_source(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertEqual(
            (
                len(overlay["functions"]),
                len(overlay["patch_sites"]),
                len(overlay["relocated_leaves"]),
            ),
            (975, 914, 406),
        )
        self.assertEqual(overlay["functions"].count(BUF_FUNCTION), 1)
        self.assertEqual(overlay["functions"].count(BYTE_FUNCTION), 1)
        leaves = {item["function"]: item for item in overlay["relocated_leaves"]}
        source_paths = {
            BUF_FUNCTION: BUF_SOURCE.relative_to(ROOT).as_posix(),
            BYTE_FUNCTION: BYTE_SOURCE.relative_to(ROOT).as_posix(),
        }
        source_files = {BUF_FUNCTION: BUF_SOURCE, BYTE_FUNCTION: BYTE_SOURCE}
        relocation_configs = {
            BUF_FUNCTION: [{
                "offset": 18,
                "type": "R_ARM_THM_CALL",
                "symbol": COPY_SEAM,
                "symbol_type": "STT_NOTYPE",
                "target_address": MEMCPY[0],
            }],
            BYTE_FUNCTION: [
                {
                    "offset": 32,
                    "type": "R_ARM_THM_MOVW_ABS_NC",
                    "symbol": END_SEAM,
                    "symbol_type": "STT_NOTYPE",
                    "target_address": ERRORS[0][1],
                },
                {
                    "offset": 36,
                    "type": "R_ARM_THM_MOVT_ABS",
                    "symbol": END_SEAM,
                    "symbol_type": "STT_NOTYPE",
                    "target_address": ERRORS[0][1],
                },
                {
                    "offset": 50,
                    "type": "R_ARM_THM_MOVW_ABS_NC",
                    "symbol": IO_SEAM,
                    "symbol_type": "STT_NOTYPE",
                    "target_address": ERRORS[1][1],
                },
                {
                    "offset": 54,
                    "type": "R_ARM_THM_MOVT_ABS",
                    "symbol": IO_SEAM,
                    "symbol_type": "STT_NOTYPE",
                    "target_address": ERRORS[1][1],
                },
            ],
        }
        for function in (BUF_FUNCTION, BYTE_FUNCTION):
            leaf = leaves[function]
            self.assertTrue(leaf["strict_relocation_contract"])
            source_file = source_files[function]
            self.assertEqual(
                {
                    key: leaf["source"][key]
                    for key in ("path", "size", "sha256", "license")
                },
                {
                    "path": source_paths[function],
                    "size": source_file.stat().st_size,
                    "sha256": sha256(source_file),
                    "license": "Zlib",
                },
            )
            self.assertEqual(leaf["relocations"], relocation_configs[function])
            for profile, profile_pins in PROFILE_PINS.items():
                selected = (
                    leaf if profile == "apple-clang"
                    else leaf["toolchain_profiles"][profile]
                )
                pins = profile_pins[function]
                section = BUF_SECTION if function == BUF_FUNCTION else BYTE_SECTION
                self.assertEqual(
                    selected["expected"],
                    {
                        "size": COMPILER_PROFILES[profile]["sections"][section][0],
                        "sha256": pins["relocated"],
                        "alignment": 4,
                        "offset": pins["offset"],
                        "unrelocated_sha256": (
                            COMPILER_PROFILES[profile]["sections"][section][1]
                        ),
                    },
                )
                self.assertEqual(selected["relocations"], relocation_configs[function])

        patches = {item.get("target_function"): item for item in overlay["patch_sites"]}
        self.assertEqual(
            patches[BUF_FUNCTION],
            {
                "name": "replace_nanopb_buf_read",
                "runtime_address": BUF_READ[0],
                "expected_size": BUF_READ[1] - BUF_READ[0],
                "expected_sha256": BUF_READ_SHA256,
                "branch": "b_w",
                "target_function": BUF_FUNCTION,
            },
        )
        self.assertEqual(
            patches[BYTE_FUNCTION],
            {
                "name": "replace_nanopb_readbyte",
                "runtime_address": PB_READBYTE[0],
                "expected_size": PB_READBYTE[1] - PB_READBYTE[0],
                "expected_sha256": PB_READBYTE_SHA256,
                "branch": "b_w",
                "target_function": BYTE_FUNCTION,
            },
        )
        for profile, profile_pins in PROFILE_PINS.items():
            for function, stock_span in (
                (BUF_FUNCTION, BUF_READ), (BYTE_FUNCTION, PB_READBYTE)
            ):
                pins = profile_pins[function]
                runtime = OVERLAY_RUNTIME_BASE + pins["offset"]
                patch = self.apollo_overlay.encode_thumb_b_w(stock_span[0], runtime)
                patch += b"\x00\xbf" * ((stock_span[1] - stock_span[0] - 4) // 2)
                self.assertEqual(patch[:4].hex(), pins["patch_prefix"])
                self.assertEqual(sha256(patch), pins["patch_sha256"])
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        stock_span[0], patch[:4], link=False
                    ),
                    runtime,
                )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        component = manifest["component_overrides"]["apollo_main"]
        self.assertEqual(
            {
                key: component["provider"][key]
                for key in ("kind", "path", "size", "sha256")
            },
            {
                "kind": "source_build",
                "path": "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin",
                "size": 3_690_822,
                "sha256": "125cfeb1bda76cbb2cc7d7d1e6fab92e00c63c4f00f5fa8a893c6f33912a55f3",
            },
        )
        regions = {item["name"]: item for item in component["regions"]}
        expected_regions = {
            "nanopb_buf_read_source_replacement": (
                357_316, 26, BUF_READ[0], "generated_source_entry_replacement",
            ),
            "nanopb_readbyte_source_replacement": (
                357_492, 72, PB_READBYTE[0], "generated_source_entry_replacement",
            ),
            "apollo_nanopb_buf_read_source_alignment": (
                3_648_194, 2, 0x007B_2AA2, "generated_alignment",
            ),
            "apollo_nanopb_buf_read_source_leaf": (
                3_648_196, 30, 0x007B_2AA4, "source_compiled",
            ),
            "apollo_nanopb_readbyte_source_alignment": (
                3_648_226, 2, 0x007B_2AC2, "generated_alignment",
            ),
            "apollo_nanopb_readbyte_source_leaf": (
                3_648_228, 64, 0x007B_2AC4, "source_compiled",
            ),
        }
        for name, expected in expected_regions.items():
            region = regions[name]
            self.assertEqual(
                (
                    region["file_offset"], region["size"],
                    region["target_address"], region["address_status"],
                ),
                expected,
            )
            self.assertEqual(region["target"], "apollo510b_internal_mram")

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        selection = provenance["selection"]
        record = selection["production_private_read_pair"]
        self.assertEqual(
            record["local_sources"],
            [
                {
                    "function": BUF_FUNCTION,
                    "path": source_paths[BUF_FUNCTION],
                    "size": BUF_SOURCE.stat().st_size,
                    "sha256": sha256(BUF_SOURCE),
                },
                {
                    "function": BYTE_FUNCTION,
                    "path": source_paths[BYTE_FUNCTION],
                    "size": BYTE_SOURCE.stat().st_size,
                    "sha256": sha256(BYTE_SOURCE),
                },
            ],
        )
        self.assertEqual(record["local_header_size"], HEADER.stat().st_size)
        self.assertEqual(record["local_header_sha256"], sha256(HEADER))
        self.assertEqual(
            (
                record["evidence"],
                record["evidence_size"],
                record["evidence_sha256"],
            ),
            (
                "docs/research/nanopb-private-read-pair-source-audit.md",
                AUDIT.stat().st_size,
                sha256(AUDIT),
            ),
        )
        self.assertEqual(
            record["toolchain_profiles"]["apple-clang"],
            {
                "buf_read": {
                    "offset": 124_800,
                    "runtime_address": "0x007B2AA4",
                    "size": 30,
                    "unrelocated_sha256": (
                        COMPILER_PROFILES["apple-clang"]["sections"][BUF_SECTION][1]
                    ),
                    "relocated_sha256": PROFILE_PINS["apple-clang"][BUF_FUNCTION]["relocated"],
                    "entry_patch_sha256": PROFILE_PINS["apple-clang"][BUF_FUNCTION]["patch_sha256"],
                },
                "pb_readbyte": {
                    "offset": 124_832,
                    "runtime_address": "0x007B2AC4",
                    "size": 64,
                    "unrelocated_sha256": (
                        COMPILER_PROFILES["apple-clang"]["sections"][BYTE_SECTION][1]
                    ),
                    "relocated_sha256": PROFILE_PINS["apple-clang"][BYTE_FUNCTION]["relocated"],
                    "entry_patch_sha256": PROFILE_PINS["apple-clang"][BYTE_FUNCTION]["patch_sha256"],
                },
            },
        )
        self.assertIn("forty-three bounded altered", selection["integration_status"])
        for path in (PROVENANCE, VERIFIER, MAKEFILE):
            text = path.read_text(encoding="utf-8")
            for stale in (
                "private_read_pair_candidate",
                "open_cfw_nanopb_buf_read_source_candidate",
                "open_cfw_nanopb_readbyte_source_candidate",
            ):
                self.assertNotIn(stale, text, path)

    def test_stock_bodies_literals_and_outgoing_seams_are_exact(self) -> None:
        self.assertEqual((len(self.package), sha256(self.package)), PACKAGE_PIN)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        for span, expected_hex, digest in (
            (BUF_READ, BUF_READ_HEX, BUF_READ_SHA256),
            (PB_READBYTE, PB_READBYTE_HEX, PB_READBYTE_SHA256),
        ):
            body = self.span(*span)
            self.assertEqual(body.hex(), expected_hex)
            self.assertEqual(sha256(body), digest)
        self.assertEqual(sha256(self.span(*CONSTRUCTOR)), CONSTRUCTOR_SHA256)
        self.assertEqual(sha256(self.span(*MEMCPY)), MEMCPY_SHA256)

        buf_outgoing = []
        body = self.span(*BUF_READ)
        for offset in range(0, len(body) - 3, 2):
            target = wide_branch_target(
                BUF_READ[0] + offset,
                *struct.unpack_from("<HH", body, offset),
                link=True,
            )
            if target is not None:
                buf_outgoing.append((BUF_READ[0] + offset, target))
        self.assertEqual(buf_outgoing, [(0x0048_F3B6, MEMCPY[0])])

        slot = self.span(CALLBACK_SLOT, CALLBACK_SLOT + 4)
        self.assertEqual(struct.unpack("<I", slot)[0], CALLBACK_VALUE)
        self.assertEqual(sha256(slot), CALLBACK_SLOT_SHA256)
        for slot_address, value, error_bytes, digest in ERRORS:
            slot = self.span(slot_address, slot_address + 4)
            self.assertEqual(struct.unpack("<I", slot)[0], value)
            observed = self.span(value, value + len(error_bytes))
            self.assertEqual(observed, error_bytes)
            self.assertEqual(sha256(observed), digest)

    def test_whole_image_entry_identity_and_interior_topology_are_exact(self) -> None:
        spans = {"buf": BUF_READ, "byte": PB_READBYTE, "ctor": CONSTRUCTOR}
        results = {
            name: {"bl": [], "bw": [], "conditional": [], "narrow": []}
            for name in spans
        }
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            bl = wide_branch_target(address, first, second, link=True)
            bw = wide_branch_target(address, first, second, link=False)
            conditional = wide_conditional_target(address, first, second)
            for name, (start, end) in spans.items():
                if bl is not None and start <= bl < end:
                    results[name]["bl"].append((address, bl))
                if bw is not None and start <= bw < end:
                    results[name]["bw"].append((address, bw))
                if (
                    conditional is not None and start <= conditional < end and
                    not start <= address < end
                ):
                    results[name]["conditional"].append((address, conditional))

        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            targets = narrow_targets(
                address, struct.unpack_from("<H", self.application, offset)[0]
            )
            for name, (start, end) in spans.items():
                if start <= address < end:
                    continue
                for target in targets:
                    if start <= target < end:
                        results[name]["narrow"].append((address, target))

        self.assertEqual(results["buf"]["bl"], [])
        self.assertEqual(
            results["byte"]["bl"],
            [(address, PB_READBYTE[0]) for address in READBYTE_CALLERS],
        )
        self.assertEqual(
            results["ctor"]["bl"],
            [(address, CONSTRUCTOR[0]) for address in CONSTRUCTOR_CALLERS],
        )
        for name in results:
            self.assertEqual(results[name]["bw"], [], name)
            self.assertEqual(results[name]["conditional"], [], name)
            self.assertEqual(results[name]["narrow"], [], name)

        stored = {name: [] for name in spans}
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            canonical = value & ~1
            for name, (start, end) in spans.items():
                if start <= canonical < end:
                    stored[name].append(
                        (APPLICATION_BASE + offset, value, offset % 4)
                    )
        self.assertEqual(stored["buf"], [(CALLBACK_SLOT, CALLBACK_VALUE, 0)])
        self.assertEqual(stored["byte"], [])
        self.assertEqual(stored["ctor"], [])

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
                displacement = second & 0xFFF
                target = pc + displacement if first == 0xF8DF else pc - displacement
                if target == CALLBACK_SLOT:
                    literal_refs.append(address)
        self.assertEqual(literal_refs, [0x0048_F3D4, 0x0048_F49E])

    def test_no_authenticated_bootloader_homolog(self) -> None:
        boot = BOOT.read_bytes()
        self.assertEqual((len(boot), sha256(boot)), BOOT_PIN)
        for body in (
            self.span(*BUF_READ), self.span(*PB_READBYTE), self.span(*CONSTRUCTOR)
        ):
            self.assertNotIn(body, boot)
        for probe in (
            bytes.fromhex("10b50c004168436813444360002c02d02000"),
            bytes.fromhex("a068002809d1e068002801d0"),
            bytes.fromhex("01222000236898470028"),
            bytes.fromhex("0093019102920021039169461022"),
            b"end-of-stream\0", b"io error\0", b"varint overflow\0",
        ):
            self.assertNotIn(probe, boot)

    def test_host_behavior_matches_authenticated_upstream(self) -> None:
        self.assertEqual(self.host_test(), 0)

    def test_target_objects_and_relocation_closure_are_exact(self) -> None:
        parsed = {}
        for function, paths in self.objects.items():
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())
            expected_section = ".text." + function
            for path in paths:
                self.assertEqual(
                    (path.stat().st_size, sha256(path)),
                    self.compiler_profile["objects"][function],
                )
                data, sections = self.apollo_overlay.parse_elf32(path)
                executable = [
                    section["name"] for section in sections
                    if int(section["size"]) > 0 and int(section["flags"]) & 0x4
                ]
                self.assertEqual(executable, [expected_section])
                writable = [
                    section["name"] for section in sections
                    if int(section["size"]) > 0 and int(section["flags"]) & 0x3 == 0x3
                ]
                self.assertEqual(writable, [])
                section = next(item for item in sections if item["name"] == expected_section)
                body = data[
                    int(section["offset"]):int(section["offset"]) + int(section["size"])
                ]
                self.assertEqual(
                    (len(body), sha256(body)),
                    self.compiler_profile["sections"][expected_section],
                )
                self.assertEqual(int(section["alignment"]), 4)
            parsed[function] = self.apollo_overlay.parse_elf32(paths[0])

        expected_undefined = {
            BUF_FUNCTION: [COPY_SEAM],
            BYTE_FUNCTION: [END_SEAM, IO_SEAM],
        }
        expected_relocations = {
            BUF_FUNCTION: {BUF_SECTION: [(18, 10, COPY_SEAM)]},
            BYTE_FUNCTION: {
                BYTE_SECTION: [
                    (32, 47, END_SEAM), (36, 48, END_SEAM),
                    (50, 47, IO_SEAM), (54, 48, IO_SEAM),
                ]
            },
        }
        for function, (data, sections) in parsed.items():
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
            self.assertEqual(undefined, expected_undefined[function])
            relocations = {}
            exidx = []
            for section in sections:
                if int(section["type"]) != 9:
                    continue
                target = sections[int(section["info"])]["name"]
                records = []
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II", data, int(section["offset"]) + index * 8
                    )
                    records.append((offset, information & 0xFF, symbols[information >> 8][0]))
                if target.startswith(".text."):
                    relocations[target] = records
                elif target.startswith(".ARM.exidx"):
                    exidx.append((target, records))
            self.assertEqual(relocations, expected_relocations[function])
            self.assertEqual(
                exidx,
                [(".ARM.exidx.text." + function, [(0, 42, "")])],
            )

    def test_compiler_profile_selection_fails_closed(self) -> None:
        for profile, record in COMPILER_PROFILES.items():
            self.assertEqual(
                resolve_compiler_profile(
                    record["compiler"], record["version"], profile
                ),
                (profile, record),
            )
            self.assertEqual(
                resolve_compiler_profile(
                    record["compiler"], record["version"], None
                ),
                (profile, record),
            )
            with self.assertRaisesRegex(
                AssertionError,
                "configured toolchain profile does not match reviewed compiler",
            ):
                resolve_compiler_profile(
                    record["compiler"],
                    record["version"],
                    "linux-clang" if profile == "apple-clang" else "apple-clang",
                )
            with self.assertRaisesRegex(
                AssertionError,
                "configured toolchain profile does not match reviewed compiler",
            ):
                resolve_compiler_profile(
                    record["compiler"], record["version"], "unknown-profile"
                )

        with self.assertRaisesRegex(AssertionError, "unreviewed target compiler"):
            resolve_compiler_profile(
                "/unreviewed/clang",
                COMPILER_PROFILES["apple-clang"]["version"],
                None,
            )
        with self.assertRaisesRegex(AssertionError, "unreviewed target compiler"):
            resolve_compiler_profile(
                COMPILER_PROFILES["apple-clang"]["compiler"],
                "unreviewed clang version",
                None,
            )


if __name__ == "__main__":
    unittest.main()
