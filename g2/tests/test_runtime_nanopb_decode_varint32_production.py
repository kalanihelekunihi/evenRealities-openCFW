#!/usr/bin/env python3
"""Qualification and atomic production contract for nanopb varint32."""

from __future__ import annotations

import hashlib
import ctypes
import copy
import json
import os
from pathlib import Path
import random
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "components/shared/nanopb"
    / "runtime_nanopb_decode_varint32.c"
)
HEADER = SOURCE.with_suffix(".h")
PRODUCTION_SOURCE = SOURCE
PRODUCTION_HEADER = PRODUCTION_SOURCE.with_suffix(".h")
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
HOST_FIXTURE = (
    ROOT / "tests/fixtures/runtime_nanopb_decode_varint32_production_host.c"
)
ORACLE_FIXTURE = (
    ROOT / "tests/fixtures/runtime_nanopb_decode_varint32_upstream_oracle.c"
)
EXIDX_MUTATOR = (
    ROOT / "tests/fixtures/runtime_nanopb_varint32_exidx_mutator.py"
)
AUDIT = (
    ROOT / "docs/research/nanopb-decode-varint32-pair-source-audit.md"
)
SHARED_STREAM_HEADER = (
    ROOT / "components/shared/nanopb/runtime_nanopb_decode_varint.h"
)
SNAPSHOT = ROOT / "third_party/nanopb"
UPSTREAM = SNAPSHOT / "pb_decode.c"
UPSTREAM_LICENSE = SNAPSHOT / "LICENSE.txt"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOTLOADER = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"

PRIVATE_FUNCTION = "open_cfw_nanopb_decode_varint32_eof"
PUBLIC_FUNCTION = "open_cfw_nanopb_decode_varint32"
PRODUCTION_PRIVATE_FUNCTION = "open_cfw_nanopb_decode_varint32_eof"
PRODUCTION_PUBLIC_FUNCTION = "open_cfw_nanopb_decode_varint32"
READBYTE_FUNCTION = "open_cfw_nanopb_readbyte"
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()
HEADER_PATH = HEADER.relative_to(ROOT).as_posix()
PRODUCTION_SOURCE_PATH = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
PRODUCTION_HEADER_PATH = PRODUCTION_HEADER.relative_to(ROOT).as_posix()
LEGACY_CANDIDATE_TOKENS = (
    "components/shared/nanopb/runtime_nanopb_decode_varint32_candidate.c",
    "components/shared/nanopb/runtime_nanopb_decode_varint32_candidate.h",
    "open_cfw_nanopb_decode_varint32_eof_candidate",
    "open_cfw_nanopb_decode_varint32_candidate",
)

PRODUCTION_COUNTS = (684, 632, 115)
PRIVATE_PATCH_NAME = "replace_nanopb_decode_varint32_eof"
PUBLIC_PATCH_NAME = "replace_nanopb_decode_varint32"
PRIVATE_MANIFEST_NAME = "nanopb_decode_varint32_eof_source_replacement"
PUBLIC_MANIFEST_NAME = "nanopb_decode_varint32_source_replacement"
OFFICIAL_PAIR_REGION_NAME = (
    "opaque_application_between_nanopb_istream_from_buffer_and_nanopb_decode_varint"
)
PRIVATE_LEAF_ONLY = "OPENCFW_NANOPB_VARINT32_PRIVATE_LEAF_ONLY"
PUBLIC_LEAF_ONLY = "OPENCFW_NANOPB_VARINT32_PUBLIC_LEAF_ONLY"
PROSPECTIVE_SOURCE_PIN = (
    3_642,
    "6938f17fc8faefdc1006cc05f9b7959e80fba771749ca0d9e67716e9ed0d2e04",
)
PROSPECTIVE_HEADER_PIN = (
    1_543,
    "46ad826405762ed52cee0797b0d93fc22f74b6f92aa012d26adf1b70609c4f7c",
)
PROSPECTIVE_APPLE_PINS = {
    PRODUCTION_PRIVATE_FUNCTION: {
        "size": 222,
        "sha256": "36bb0167f4d3407b99ed2255cc9e77dd60dc1e9070781a257bfea59abc408171",
        "alignment": 4,
        "offset": 124_972,
        "unrelocated_sha256": "5296b608c55171bca9d5f4d162cf53d0e6aa5f724e1cb82499a7311f2a6cc9ff",
        "closure_size": 238,
        "closure_sha256": "2c49567cfe23e36c504586218719c2e590163bec804353c8106680328d64a480",
        "rodata_offset": 222,
    },
    PRODUCTION_PUBLIC_FUNCTION: {
        "size": 10,
        "sha256": "1f0924d25c50933e7cd5aac05d718da6d44b7a20d4af901fa833c555eca6ff1a",
        "alignment": 4,
        "offset": 125_212,
        "unrelocated_sha256": "e9ec8b612503f867aabf2467e3abfac44753c5576a247a00cbc4309e2a023f93",
    },
}
PROSPECTIVE_LINUX_PINS = {
    PRODUCTION_PRIVATE_FUNCTION: {
        "size": 222,
        "sha256": "36bb0167f4d3407b99ed2255cc9e77dd60dc1e9070781a257bfea59abc408171",
        "alignment": 4,
        "offset": 126_796,
        "unrelocated_sha256": "5296b608c55171bca9d5f4d162cf53d0e6aa5f724e1cb82499a7311f2a6cc9ff",
        "closure_size": 238,
        "closure_sha256": "2c49567cfe23e36c504586218719c2e590163bec804353c8106680328d64a480",
        "rodata_offset": 222,
    },
    PRODUCTION_PUBLIC_FUNCTION: {
        "size": 10,
        "sha256": "1f0924d25c50933e7cd5aac05d718da6d44b7a20d4af901fa833c555eca6ff1a",
        "alignment": 4,
        "offset": 127_036,
        "unrelocated_sha256": "e9ec8b612503f867aabf2467e3abfac44753c5576a247a00cbc4309e2a023f93",
    },
}
APPLE_AGGREGATE_PINS = {
    "overlay": (128_264, "742e44dd839010c3c14ae59419fc06bcd50a7fe91e7ba06b4946f5c4154c870b"),
    "component": (3_651_660, "ea39a91f574b464d9071e581f5104d870e1f7e484d52de9b86407f0a90ac5d2e"),
    "package": (4_430_154, "aa71330ceed2775494fb7ff599a23701ef746a25452a8d335574a3bac12674a9"),
    "build_report": (2_323, "e7d7e4b585b0881f7bdef40d4feac5b8d89e445c63f98121d765622b6dcddd6e"),
    "flash_plan": (784_999, "bfb010d525451379189ebfd316051a6fb9fae0a755be6a41f9955d02455803f9"),
}
LINUX_AGGREGATE_PINS = {
    "overlay": (132_888, "7036c0e07a36376e5d98700c922ffeec7a6826388b75060a2b98b4228a411c61"),
    "component": (3_656_284, "d5daf89121f44a61b303fa953da78550edd31e9159cf9b0b397aeb1b5cfef54d"),
    "package": (4_434_778, "63d5cd1d1cbab2c3ece4a48f96b58a0cb14a7487917831f4c6d370b40ed41d90"),
    "build_report": (2_322, "3d0f0968f5f26a550719240a12a0e6f4e083f2ea566940f215f84b2a5f382a9a"),
    "flash_plan": (640_188, "4480ca9a4a4f237a477ccccdc9cb039f071fb2f6547298595e98a91098302a20"),
}

PACKAGE_PREAMBLE = 32
APPLICATION_BASE = 0x0043_8000
PACKAGE_PIN = (
    3_523_396,
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
)
APPLICATION_PIN = (
    3_523_364,
    "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701",
)
BOOTLOADER_PIN = (
    148_599,
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5",
)

PRIVATE_SPAN = (0x0048_F4B8, 0x0048_F5AE)
PUBLIC_SPAN = (0x0048_F5AE, 0x0048_F5B8)
PAIR_SPAN = (PRIVATE_SPAN[0], PUBLIC_SPAN[1])
PREDECESSOR_SPAN = (0x0048_F49C, PRIVATE_SPAN[0])
SUCCESSOR_SPAN = (PUBLIC_SPAN[1], 0x0048_F628)
PRIVATE_HEX = (
    "f8b505000e00140069462800fff7c6ff002808d1a868002803d1002c01d00120"
    "2070002066e09df80000000602d49df800705de007249df8007017f07f076946"
    "2800fff7abff002819d0202c27d33f2c17d2ff219df8000010f07f0f08d03800"
    "c00f00280fd09df80000c9b288420ad10120402c09d2c0b2002834d105e00020"
    "38e00121e6e70020f3e7e868002801d0e86801e0dff83407e86000202ae01c2c"
    "1bd19df8000010f0700f05d09df8000010f07800782806d19df8000010f00f00"
    "a04007430fe0e868002801d0e86801e0dff8f806e86000200ce09df8000010f0"
    "7f00a0400743e41d9df800000006a6d437600120f2bd"
)
PUBLIC_HEX = "80b50022fff781ff02bd"
SPAN_PINS = {
    PRIVATE_SPAN: (
        246,
        "8583fa17383d72bbdcab6c2a7a20369dc0598d3ac3061feaf8a7b29dfa520150",
    ),
    PUBLIC_SPAN: (
        10,
        "48218a658cffd7aeddfb623c9d0e7bd038ceb2a6898e9f8d08b10d5779f4f79b",
    ),
    PAIR_SPAN: (
        256,
        "ba8079feceedc8edeb4603ef86145f1d3b32612d84807891e50115002f2753be",
    ),
    PREDECESSOR_SPAN: (
        28,
        "852314bb8f86dcbd550deb0f51bc285b662e39c1b4fae66690c44a7bf4f7a674",
    ),
    SUCCESSOR_SPAN: (
        112,
        "f93d678981f92603982c9afc6c6f9976ca14d1a7a7e0bfc949d3ff73f2791ff2",
    ),
}

PRIVATE_CALLERS = (
    (0x0048_F5B2, "fff781ff"),
    (0x0048_F682, "fff719ff"),
)
PUBLIC_CALLERS = (
    (0x0048_F654, "fff7abff"),
    (0x0048_F788, "fff711ff"),
    (0x0049_0132, "fff73cfa"),
    (0x0049_0362, "fff724f9"),
    (0x0049_03F6, "fff7daf8"),
    (0x0049_0546, "fff732f8"),
)
CALLER_HASHES = {
    PRIVATE_SPAN: (
        "e3995deb4c5382438e8d98f181bc7755857986616ddd6d3b16a3c6a9b40998ff",
        "fd0bd8b73d094f074682658e3eeb22b83cd39e99e63cc0302278392e9a71dd51",
    ),
    PUBLIC_SPAN: (
        "aa615597f2ec75e7e5892cf230c5b8d941a249e9850e7d70d298826b1d291494",
        "eaeef363b9d085d757bb7abea39db2e424c59fe812ff2cdf6d8a0fa5b826c067",
    ),
}
PRIVATE_OUTGOING = (
    (0x0048_F4C4, 0x0048_F454, "fff7c6ff"),
    (0x0048_F4FA, 0x0048_F454, "fff7abff"),
)
PUBLIC_OUTGOING = ((0x0048_F5B2, 0x0048_F4B8, "fff781ff"),)
ERROR_LITERAL_LOADS = (0x0048_F54C, 0x0048_F588)
ERROR_LITERAL_SLOT = 0x0048_FC84
ERROR_LITERAL_PIN = (
    bytes.fromhex("807c7800"),
    "932b450ffea27c45062b59f6e45c640d894e6eae043fd124b694358e87e00ab4",
)
ERROR_STRING_ADDRESS = 0x0078_7C80
ERROR_STRING_PIN = (
    b"varint overflow\0",
    "e9b62825b028cfc32f718b48de14fcbc783a9009279d2c88cf4394d54767141d",
)
LONG_CONTINUATION_PAYLOAD = b"\x80" * 300 + b"\x00"

UPSTREAM_PIN = (
    53_845,
    "e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a",
)
UPSTREAM_DEFINITIONS = (
    (
        (
            b"static bool checkreturn pb_decode_varint32_eof(pb_istream_t *stream, "
            b"uint32_t *dest, bool *eof)\n{"
        ),
        5762,
        7483,
        1721,
        "66833ae2defb892aa17162625ef107bda03be44e73f0b120d48e6d2b52770e2c",
        "81820b320aa6972d6b60317d46b9a8f6a1a236ab4758d31c1c1fb7151ca1e3f6",
    ),
    (
        (
            b"bool checkreturn pb_decode_varint32(pb_istream_t *stream, "
            b"uint32_t *dest)\n{"
        ),
        7485,
        7617,
        132,
        "ef3f2bd19c12b07ca055ab63f8e82ea6f4b34e67aefb277435092e7485834f0f",
        "994860f2242bfaa21fbbc16649382b74c451106f86d8f1d92a5d6b9258aade76",
    ),
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
REVIEWED_COMPILERS = {
    "Apple clang version 21.0.0 (clang-2100.3.30.1)": "/usr/bin/clang",
    "Homebrew clang version 22.1.8": "/home/linuxbrew/.linuxbrew/bin/clang",
}

# Task 2 observes these independently under each reviewed exact compiler root.
# The temporary ``None`` values are an intentional object-qualification RED.
FILE_PINS = {
    SOURCE: PROSPECTIVE_SOURCE_PIN,
    HEADER: PROSPECTIVE_HEADER_PIN,
    HOST_FIXTURE: (6_262, "488e6f3d02640ec437e0ebc5d20870178f431bf0774be8643264d1636fd8ef9f"),
    ORACLE_FIXTURE: (991, "462496c82cbe8129316690894a360f71ac4209ecedf108334b7828f80527e53a"),
    AUDIT: (8_938, "be0511c1dd4162585aa0478c5242c25e0d34d08ea6331d297c67636f784a8893"),
}
PROFILE_PINS = {
    "Apple clang version 21.0.0 (clang-2100.3.30.1)": {
        "object": (1_628, "626893ac400caac8fa733f5740b272d218a1e32572fad4bfa636a4bce142c166"),
        "private_text": (222, "5296b608c55171bca9d5f4d162cf53d0e6aa5f724e1cb82499a7311f2a6cc9ff", 4),
        "public_text": (10, "e9ec8b612503f867aabf2467e3abfac44753c5576a247a00cbc4309e2a023f93", 4),
        "rodata": (16, "e9b62825b028cfc32f718b48de14fcbc783a9009279d2c88cf4394d54767141d", 1),
        "private_relocations": (
            (16, 10, READBYTE_FUNCTION),
            (106, 10, READBYTE_FUNCTION),
            (208, 49, "open_cfw_nanopb_varint32_overflow_error"),
            (212, 50, "open_cfw_nanopb_varint32_overflow_error"),
        ),
        "public_relocations": ((4, 10, PRIVATE_FUNCTION),),
        "exidx": (8, "01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d", 4),
    },
    "Homebrew clang version 22.1.8": {
        "object": (1_628, "626893ac400caac8fa733f5740b272d218a1e32572fad4bfa636a4bce142c166"),
        "private_text": (222, "5296b608c55171bca9d5f4d162cf53d0e6aa5f724e1cb82499a7311f2a6cc9ff", 4),
        "public_text": (10, "e9ec8b612503f867aabf2467e3abfac44753c5576a247a00cbc4309e2a023f93", 4),
        "rodata": (16, "e9b62825b028cfc32f718b48de14fcbc783a9009279d2c88cf4394d54767141d", 1),
        "private_relocations": (
            (16, 10, READBYTE_FUNCTION),
            (106, 10, READBYTE_FUNCTION),
            (208, 49, "open_cfw_nanopb_varint32_overflow_error"),
            (212, 50, "open_cfw_nanopb_varint32_overflow_error"),
        ),
        "public_relocations": ((4, 10, PRIVATE_FUNCTION),),
        "exidx": (8, "01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d", 4),
    },
}

ACTIVE_PRODUCTION_SURFACES = (
    ROOT / "README.md",
    ROOT / "Makefile",
    ROOT / "make.sh",
    ROOT / "components/README.md",
    ROOT / "components/apollo_main/canvas480/NOTICE.md",
    ROOT / "components/apollo_main/canvas480/README.md",
    ROOT / "components/apollo_main/core_overlay/EVIDENCE.md",
    ROOT / "components/apollo_main/core_overlay/NOTICE.md",
    ROOT / "components/apollo_main/core_overlay/overlay.json",
    ROOT / "components/apollo_main/evenai_thumb/NOTICE.md",
    ROOT / "components/apollo_main/evenai_thumb/README.md",
    ROOT / "components/apollo_main/ring_gesture/NOTICE.md",
    ROOT / "components/apollo_main/ring_gesture/overlay.json",
    ROOT / "components/bootloader/core_overlay/EVIDENCE.md",
    ROOT / "components/bootloader/core_overlay/NOTICE.md",
    ROOT / "components/bootloader/core_overlay/overlay.json",
    ROOT / "docs/linux-reproducible-build.md",
    ROOT / "docs/memory-map.md",
    ROOT / "docs/source-coverage.md",
    ROOT / "docs/upstream-inventory.md",
    ROOT / "manifests/g2-2.2.6.10-core-source.json",
    ROOT / "manifests/g2-2.2.6.10-release-pins.json",
    ROOT / "manifests/g2-2.2.6.10-ring-source.json",
    ROOT / "manifests/g2-2.2.6.10.json",
    ROOT / "releases/g2-2.2.6.12/README.md",
    ROOT / "releases/g2-2.2.6.12/build.py",
    ROOT / "releases/g2-2.2.6.12/release.json",
    ROOT / "third_party/littlefs/verify_snapshot.py",
    ROOT / "third_party/nanopb/PROVENANCE.json",
    ROOT / "third_party/nanopb/README.openCFW.md",
    ROOT / "third_party/nanopb/verify_snapshot.py",
    ROOT / "tools/analyze_g2_nanopb_dec_varint.py",
    ROOT / "tools/apollo_overlay.py",
    ROOT / "tools/open_cfw.py",
)
NEIGHBOR_CONSUMERS = {
    ROOT / "components/README.md",
    ROOT / "components/apollo_main/core_overlay/EVIDENCE.md",
    ROOT / "components/apollo_main/core_overlay/NOTICE.md",
    ROOT / "components/apollo_main/core_overlay/overlay.json",
    ROOT / "docs/memory-map.md",
    ROOT / "docs/upstream-inventory.md",
    ROOT / "third_party/littlefs/verify_snapshot.py",
    ROOT / "third_party/nanopb/PROVENANCE.json",
    ROOT / "third_party/nanopb/README.openCFW.md",
    ROOT / "third_party/nanopb/verify_snapshot.py",
    ROOT / "tools/analyze_g2_nanopb_dec_varint.py",
}


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
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return (address + 4 + immediate * 2,)
    return ()


def brace_balanced_definition(source: bytes, signature: bytes) -> tuple[int, int]:
    """Return a C definition without consuming its trailing delimiter."""
    start = source.index(signature)
    opening = source.index(b"{", start)
    depth = 0
    state = "code"
    escaped = False
    index = opening
    while index < len(source):
        current = source[index]
        following = source[index + 1] if index + 1 < len(source) else None
        if state in ("string", "character"):
            if escaped:
                escaped = False
            elif current == ord("\\"):
                escaped = True
            elif current == (ord('"') if state == "string" else ord("'")):
                state = "code"
        elif state == "line-comment":
            if current == ord("\n"):
                state = "code"
        elif state == "block-comment":
            if current == ord("*") and following == ord("/"):
                state = "code"
                index += 1
        elif current == ord("/") and following == ord("/"):
            state = "line-comment"
            index += 1
        elif current == ord("/") and following == ord("*"):
            state = "block-comment"
            index += 1
        elif current == ord('"'):
            state = "string"
        elif current == ord("'"):
            state = "character"
        elif current == ord("{"):
            depth += 1
        elif current == ord("}"):
            depth -= 1
            if depth == 0:
                return start, index + 1
        index += 1
    raise AssertionError(f"unterminated function definition at byte {start}")


def prospective_production_source() -> bytes:
    return SOURCE.read_bytes()


def prospective_production_header() -> bytes:
    return HEADER.read_bytes()


def prospective_leaf_configs(current_overlay: dict) -> list[dict]:
    reference = next(
        leaf for leaf in current_overlay["relocated_leaves"]
        if leaf["function"] == "open_cfw_nanopb_decode_varint"
    )
    source = {
        "path": PRODUCTION_SOURCE_PATH,
        "size": PROSPECTIVE_SOURCE_PIN[0],
        "sha256": PROSPECTIVE_SOURCE_PIN[1],
        "license": "Zlib",
        "origin": (
            "altered production adaptation of authenticated "
            "nanopb 0.4.9 pb_decode_varint32_eof and pb_decode_varint32"
        ),
        "upstream": (
            "https://github.com/nanopb/nanopb/blob/"
            "98bf4db69897b53434f3d0ba72e0a3ab1a902824/pb_decode.c"
        ),
        "upstream_commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
        "evidence": "docs/research/nanopb-decode-varint32-pair-source-audit.md",
    }
    private_relocations = [
        {
            "offset": offset,
            "type": "R_ARM_THM_CALL",
            "symbol": READBYTE_FUNCTION,
            "symbol_type": "STT_NOTYPE",
            "target_function": READBYTE_FUNCTION,
        }
        for offset in (16, 106)
    ] + [
        {
            "offset": offset,
            "type": relocation_type,
            "symbol": "open_cfw_nanopb_varint32_overflow_error",
        }
        for offset, relocation_type in (
            (208, "R_ARM_THM_MOVW_PREL_NC"),
            (212, "R_ARM_THM_MOVT_PREL"),
        )
    ]
    public_relocations = [{
        "offset": 4,
        "type": "R_ARM_THM_CALL",
        "symbol": PRODUCTION_PRIVATE_FUNCTION,
        "symbol_type": "STT_NOTYPE",
        "target_function": PRODUCTION_PRIVATE_FUNCTION,
    }]

    def reviewed_toolchain(leaf_only: str) -> dict:
        toolchain = copy.deepcopy(reference["toolchain"])
        toolchain["flags"].append("-D" + leaf_only)
        return toolchain

    private = {
        "function": PRODUCTION_PRIVATE_FUNCTION,
        "source": copy.deepcopy(source),
        "toolchain": reviewed_toolchain(PRIVATE_LEAF_ONLY),
        "closure": {
            "text_section": ".text." + PRODUCTION_PRIVATE_FUNCTION,
            "rodata": {
                "section": ".rodata.open_cfw_nanopb_varint32_overflow_error",
                "size": 16,
                "sha256": ERROR_STRING_PIN[1],
                "alignment": 1,
                "symbols": [{
                    "name": "open_cfw_nanopb_varint32_overflow_error",
                    "offset": 0,
                    "size": 16,
                }],
            },
        },
        "strict_relocation_contract": True,
        "expected": copy.deepcopy(
            PROSPECTIVE_APPLE_PINS[PRODUCTION_PRIVATE_FUNCTION]
        ),
        "relocations": private_relocations,
        "toolchain_profiles": {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": copy.deepcopy(
                    PROSPECTIVE_LINUX_PINS[PRODUCTION_PRIVATE_FUNCTION]
                ),
                "relocations": copy.deepcopy(private_relocations),
            },
        },
    }
    public = {
        "function": PRODUCTION_PUBLIC_FUNCTION,
        "source": copy.deepcopy(source),
        "toolchain": reviewed_toolchain(PUBLIC_LEAF_ONLY),
        "strict_relocation_contract": True,
        "expected": copy.deepcopy(
            PROSPECTIVE_APPLE_PINS[PRODUCTION_PUBLIC_FUNCTION]
        ),
        "relocations": public_relocations,
        "toolchain_profiles": {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": copy.deepcopy(
                    PROSPECTIVE_LINUX_PINS[PRODUCTION_PUBLIC_FUNCTION]
                ),
                "relocations": copy.deepcopy(public_relocations),
            },
        },
    }
    return [private, public]


def production_topology_fixture() -> tuple[dict, list[dict]]:
    """Return production records with Task 5's manifest replacement projected."""
    overlay = copy.deepcopy(json.loads(OVERLAY.read_text(encoding="utf-8")))
    if PRODUCTION_PRIVATE_FUNCTION not in overlay["functions"]:
        overlay["functions"].extend(
            (PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION)
        )
        overlay["relocated_leaves"].extend(prospective_leaf_configs(overlay))
        overlay["patch_sites"].extend((
            {
                "name": PRIVATE_PATCH_NAME,
                "runtime_address": PRIVATE_SPAN[0],
                "expected_size": PRIVATE_SPAN[1] - PRIVATE_SPAN[0],
                "expected_sha256": SPAN_PINS[PRIVATE_SPAN][1],
                "branch": "b_w",
                "target_function": PRODUCTION_PRIVATE_FUNCTION,
            },
            {
                "name": PUBLIC_PATCH_NAME,
                "runtime_address": PUBLIC_SPAN[0],
                "expected_size": PUBLIC_SPAN[1] - PUBLIC_SPAN[0],
                "expected_sha256": SPAN_PINS[PUBLIC_SPAN][1],
                "branch": "b_w",
                "target_function": PRODUCTION_PUBLIC_FUNCTION,
            },
        ))
    else:
        pair_leaves = [
            leaf for leaf in overlay["relocated_leaves"]
            if leaf["function"] in {
                PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION,
            }
        ]
        overlay["relocated_leaves"] = [
            leaf for leaf in overlay["relocated_leaves"]
            if leaf["function"] not in {
                PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION,
            }
        ] + pair_leaves
        pair_patches = [
            patch for patch in overlay["patch_sites"]
            if patch["name"] in {PRIVATE_PATCH_NAME, PUBLIC_PATCH_NAME}
        ]
        overlay["patch_sites"] = [
            patch for patch in overlay["patch_sites"]
            if patch["name"] not in {PRIVATE_PATCH_NAME, PUBLIC_PATCH_NAME}
        ] + pair_patches

    manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
    regions = copy.deepcopy(
        manifest["component_overrides"]["apollo_main"]["regions"]
    )
    official_indexes = [
        index for index, region in enumerate(regions)
        if region["name"] == OFFICIAL_PAIR_REGION_NAME
    ]
    if official_indexes:
        official_index = official_indexes[0]
        official = regions[official_index]
        private_region = {
            **official,
            "name": PRIVATE_MANIFEST_NAME,
            "function": (
                "Generated entry redirect and full Thumb NOP fill replacing the "
                "complete private nanopb pb_decode_varint32_eof span"
            ),
            "size": 246,
            "target_address": PRIVATE_SPAN[0],
            "address_status": "generated_source_entry_replacement",
            "output": (
                "apollo510b/source-entry-nanopb-decode-varint32-eof-0x0048f4b8.bin"
            ),
        }
        public_region = {
            **official,
            "name": PUBLIC_MANIFEST_NAME,
            "function": (
                "Generated entry redirect and full Thumb NOP fill replacing the "
                "complete public nanopb pb_decode_varint32 span"
            ),
            "file_offset": official["file_offset"] + 246,
            "size": 10,
            "target_address": PUBLIC_SPAN[0],
            "address_status": "generated_source_entry_replacement",
            "output": (
                "apollo510b/source-entry-nanopb-decode-varint32-0x0048f5ae.bin"
            ),
        }
        regions[official_index:official_index + 1] = [
            private_region, public_region,
        ]
    appended_names = {
        "apollo_nanopb_decode_varint32_eof_source_alignment",
        "apollo_nanopb_decode_varint32_eof_source_leaf",
        "apollo_nanopb_decode_varint32_overflow_rodata",
        "apollo_nanopb_decode_varint32_source_alignment",
        "apollo_nanopb_decode_varint32_source_leaf",
    }
    if not appended_names.issubset({region["name"] for region in regions}):
        regions.extend((
        {
            "name": "apollo_nanopb_decode_varint32_eof_source_alignment",
            "function": "Generated zero padding aligning the private nanopb varint32 EOF source leaf",
            "file_offset": 3_648_366,
            "size": 2,
            "target": "apollo510b_internal_mram",
            "target_address": 8_072_014,
            "address_status": "generated_alignment",
            "output": "apollo510b/main-source-nanopb-decode-varint32-eof-alignment-0x007b2b4e.bin",
        },
        {
            "name": "apollo_nanopb_decode_varint32_eof_source_leaf",
            "function": "Zlib nanopb pb_decode_varint32_eof source leaf",
            "file_offset": 3_648_368,
            "size": 222,
            "target": "apollo510b_internal_mram",
            "target_address": 8_072_016,
            "address_status": "source_compiled",
            "output": "apollo510b/main-source-nanopb-decode-varint32-eof-0x007b2b50.bin",
        },
        {
            "name": "apollo_nanopb_decode_varint32_overflow_rodata",
            "function": "Source-owned nanopb varint overflow literal closure",
            "file_offset": 3_648_590,
            "size": 16,
            "target": "apollo510b_internal_mram",
            "target_address": 8_072_238,
            "address_status": "source_compiled",
            "output": "apollo510b/main-source-nanopb-varint32-overflow-0x007b2c2e.bin",
        },
        {
            "name": "apollo_nanopb_decode_varint32_source_alignment",
            "function": "Generated zero padding aligning the public nanopb varint32 source leaf",
            "file_offset": 3_648_606,
            "size": 2,
            "target": "apollo510b_internal_mram",
            "target_address": 8_072_254,
            "address_status": "generated_alignment",
            "output": "apollo510b/main-source-nanopb-decode-varint32-alignment-0x007b2c3e.bin",
        },
        {
            "name": "apollo_nanopb_decode_varint32_source_leaf",
            "function": "Zlib nanopb pb_decode_varint32 source leaf",
            "file_offset": 3_648_608,
            "size": 10,
            "target": "apollo510b_internal_mram",
            "target_address": 8_072_256,
            "address_status": "source_compiled",
            "output": "apollo510b/main-source-nanopb-decode-varint32-0x007b2c40.bin",
        },
        ))
    return overlay, regions


def validate_atomic_production_topology(
    overlay: dict,
    manifest_regions: list[dict],
) -> None:
    """Fail closed on non-atomic varint32-pair production configurations."""
    observed_counts = (
        len(overlay.get("functions", [])),
        len(overlay.get("patch_sites", [])),
        len(overlay.get("relocated_leaves", [])),
    )
    if observed_counts != PRODUCTION_COUNTS:
        raise AssertionError(
            "production overlay inventory must be exactly 683 functions, "
            "631 patch sites, and 114 relocated leaves"
        )

    functions = overlay["functions"]
    if (
        functions.count(PRODUCTION_PRIVATE_FUNCTION) != 1
        or functions.count(PRODUCTION_PUBLIC_FUNCTION) != 1
    ):
        raise AssertionError(
            "production function registry must contain both varint32 symbols exactly once"
        )

    pair_leaves = [
        leaf for leaf in overlay["relocated_leaves"]
        if leaf.get("function") in {
            PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION,
        }
    ]
    source_pair_leaves = [
        leaf for leaf in overlay["relocated_leaves"]
        if leaf.get("source", {}).get("path") == PRODUCTION_SOURCE_PATH
    ]
    if len(pair_leaves) != 2:
        if len(source_pair_leaves) == 1:
            raise AssertionError(
                "the two varint32 bodies must not be combined into one relocated leaf"
            )
        raise AssertionError(
            "varint32 production requires two distinct relocated leaves"
        )
    if len(source_pair_leaves) != 2 or any(
        leaf.get("function") not in {
            PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION,
        }
        for leaf in source_pair_leaves
    ):
        raise AssertionError(
            "the production varint32 translation unit must source exactly two leaves"
        )
    if [leaf["function"] for leaf in pair_leaves] != [
        PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION,
    ]:
        raise AssertionError(
            "varint32 relocated leaves must be ordered private then public"
        )

    private_leaf, public_leaf = pair_leaves
    for leaf, function in (
        (private_leaf, PRODUCTION_PRIVATE_FUNCTION),
        (public_leaf, PRODUCTION_PUBLIC_FUNCTION),
    ):
        if leaf.get("source", {}).get("path") != PRODUCTION_SOURCE_PATH:
            raise AssertionError(
                f"{function} must be selected from the production translation unit"
            )
        source = leaf["source"]
        if not {
            "path", "size", "sha256", "license", "origin", "upstream",
            "upstream_commit", "evidence",
        }.issubset(source):
            raise AssertionError(
                f"{function} requires complete source provenance fields"
            )
        if leaf.get("strict_relocation_contract") is not True:
            raise AssertionError(
                f"{function} requires a strict relocation contract"
            )
        if not {
            "size", "sha256", "alignment", "offset", "unrelocated_sha256",
        }.issubset(leaf.get("expected", {})):
            raise AssertionError(f"{function} requires complete Apple leaf pins")
        linux = leaf.get("toolchain_profiles", {}).get("linux-clang")
        if linux is None:
            raise AssertionError(
                f"{function} requires independently recorded Linux production pins"
            )
        if linux.get("reviewed_version_prefix") != "Homebrew clang version 22.1.8":
            raise AssertionError(f"{function} has an unreviewed Linux compiler family")
        if linux.get("expected") != PROSPECTIVE_LINUX_PINS[function]:
            raise AssertionError(f"{function} Linux leaf pins differ from Task 7 evidence")
        selected_section = leaf.get("closure", {}).get(
            "text_section", ".text." + function
        )
        if selected_section != ".text." + function:
            raise AssertionError(
                f"{function} must be selected from its own function section"
            )

    private_calls = [
        relocation for relocation in private_leaf.get("relocations", [])
        if relocation.get("type") == "R_ARM_THM_CALL"
    ]
    if len(private_calls) != 2 or any(
        relocation.get("symbol") != READBYTE_FUNCTION
        or relocation.get("target_function") != READBYTE_FUNCTION
        or "target_address" in relocation
        for relocation in private_calls
    ):
        raise AssertionError(
            "private varint32 leaf must call source-owned readbyte twice by target_function"
        )
    public_calls = [
        relocation for relocation in public_leaf.get("relocations", [])
        if relocation.get("type") == "R_ARM_THM_CALL"
    ]
    if len(public_calls) != 1 or any(
        relocation.get("symbol") != PRODUCTION_PRIVATE_FUNCTION
        or relocation.get("target_function") != PRODUCTION_PRIVATE_FUNCTION
        or "target_address" in relocation
        for relocation in public_calls
    ):
        raise AssertionError(
            "public varint32 leaf must call the private source leaf by target_function"
        )
    reviewed_records = {
        leaf["function"]: leaf
        for leaf in prospective_leaf_configs(
            json.loads(OVERLAY.read_text(encoding="utf-8"))
        )
    }
    for leaf in pair_leaves:
        if leaf != reviewed_records[leaf["function"]]:
            raise AssertionError(
                f"{leaf['function']} must match its complete builder-reviewed leaf record"
            )

    pair_patches = [
        patch for patch in overlay["patch_sites"]
        if patch.get("runtime_address", -1) < PAIR_SPAN[1]
        and patch.get("runtime_address", -1) + patch.get("expected_size", 0)
        > PAIR_SPAN[0]
    ]
    if len(pair_patches) != 2:
        if any(
            patch.get("runtime_address") == PAIR_SPAN[0]
            and patch.get("expected_size") == PAIR_SPAN[1] - PAIR_SPAN[0]
            for patch in pair_patches
        ):
            raise AssertionError(
                "the varint32 pair must not use one combined 256-byte entry patch"
            )
        raise AssertionError(
            "varint32 production requires two distinct full-span entry patches"
        )
    expected_patches = (
        (
            PRIVATE_PATCH_NAME, PRIVATE_SPAN, SPAN_PINS[PRIVATE_SPAN][1],
            PRODUCTION_PRIVATE_FUNCTION,
        ),
        (
            PUBLIC_PATCH_NAME, PUBLIC_SPAN, SPAN_PINS[PUBLIC_SPAN][1],
            PRODUCTION_PUBLIC_FUNCTION,
        ),
    )
    pair_patches.sort(key=lambda patch: patch["runtime_address"])
    if (
        pair_patches[0]["runtime_address"]
        + pair_patches[0]["expected_size"]
        > pair_patches[1]["runtime_address"]
    ):
        raise AssertionError("varint32 entry patches must not overlap")
    for patch, (name, span, digest, function) in zip(
        pair_patches, expected_patches
    ):
        if (
            patch.get("name") != name
            or patch.get("runtime_address") != span[0]
            or patch.get("expected_size") != span[1] - span[0]
            or patch.get("branch") != "b_w"
            or patch.get("target_function") != function
        ):
            raise AssertionError(
                f"{name} must be an exact full-span b_w entry patch"
            )
        if patch.get("expected_sha256") != digest:
            owner = "private" if span == PRIVATE_SPAN else "public"
            raise AssertionError(
                f"{owner} patch must authenticate exactly the {span[1] - span[0]}-byte stock body"
            )

    if (
        pair_patches[0]["runtime_address"] + pair_patches[0]["expected_size"]
        != pair_patches[1]["runtime_address"]
        or PREDECESSOR_SPAN[1] != pair_patches[0]["runtime_address"]
        or pair_patches[1]["runtime_address"] + pair_patches[1]["expected_size"]
        != SUCCESSOR_SPAN[0]
    ):
        raise AssertionError(
            "varint32 patches must be adjacent, non-overlapping, and preserve both neighbors"
        )
    overwritten_stock_calls = [
        address for address, _ in PRIVATE_CALLERS + PUBLIC_CALLERS
        if PAIR_SPAN[0] <= address < PAIR_SPAN[1]
    ]
    public_patch_end = (
        pair_patches[1]["runtime_address"] + pair_patches[1]["expected_size"]
    )
    if overwritten_stock_calls != [0x0048_F5B2] or not (
        pair_patches[1]["runtime_address"] <= overwritten_stock_calls[0]
        and overwritten_stock_calls[0] + 4 <= public_patch_end
    ):
        raise AssertionError(
            "the public full-span patch must erase the only stock call into the overwritten pair"
        )

    overlay_runtime_address = (
        overlay["run_base"]
        + (overlay["base"]["size"] + overlay["alignment"] - 1)
        // overlay["alignment"] * overlay["alignment"]
        - overlay["preamble_bytes"]
    )
    sys.path.insert(0, str(ROOT / "tools"))
    import apollo_overlay
    leaves_by_function = {leaf["function"]: leaf for leaf in pair_leaves}
    for patch in pair_patches:
        leaf = leaves_by_function[patch["target_function"]]
        target = overlay_runtime_address + leaf["expected"]["offset"]
        replacement = (
            apollo_overlay.encode_thumb_b_w(patch["runtime_address"], target)
            + b"\x00\xbf" * ((patch["expected_size"] - 4) // 2)
        )
        if len(replacement) != patch["expected_size"]:
            raise AssertionError("varint32 entry replacement must fill its complete span")
        if wide_branch_target(
            patch["runtime_address"],
            *struct.unpack("<HH", replacement[:4]),
            link=False,
        ) != target:
            raise AssertionError("varint32 entry B.W must target its exact relocated leaf")
        if replacement[4:] != b"\x00\xbf" * ((patch["expected_size"] - 4) // 2):
            raise AssertionError("varint32 entry replacement tail must contain only Thumb NOPs")

    official_overlap = [
        region for region in manifest_regions
        if region.get("address_status") == "official_blob"
        and region.get("target_address", -1) < PAIR_SPAN[1]
        and region.get("target_address", -1) + region.get("size", 0) > PAIR_SPAN[0]
    ]
    if official_overlap:
        raise AssertionError(
            "no official manifest seam may survive inside either varint32 stock body"
        )
    generated = [
        region for region in manifest_regions
        if region.get("target_address") in {PRIVATE_SPAN[0], PUBLIC_SPAN[0]}
    ]
    if [
        (
            region.get("name"), region.get("file_offset"),
            region.get("target_address"),
            region.get("size"), region.get("address_status"),
        )
        for region in generated
    ] != [
        (
            PRIVATE_MANIFEST_NAME, 357_592, PRIVATE_SPAN[0], 246,
            "generated_source_entry_replacement",
        ),
        (
            PUBLIC_MANIFEST_NAME, 357_838, PUBLIC_SPAN[0], 10,
            "generated_source_entry_replacement",
        ),
    ]:
        raise AssertionError(
            "manifest must own two ordered generated varint32 entry-replacement regions"
        )


class NanopbDecodeVarint32ProductionTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    def span(self, span: tuple[int, int]) -> bytes:
        start, end = span
        return self.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def require_source(self) -> None:
        if not SOURCE.is_file() or not HEADER.is_file():
            self.skipTest("production source is not available")

    def test_candidate_sources_exist(self) -> None:
        # This exact assertion and test identity are the owned Task 0 RED.
        self.assertTrue(SOURCE.is_file())
        self.assertTrue(HEADER.is_file())

    def test_contract_fixtures_exist_and_pin_both_abis(self) -> None:
        self.assertTrue(HOST_FIXTURE.is_file())
        self.assertTrue(ORACLE_FIXTURE.is_file())

    def test_upstream_oracle_compiles_exports_and_executes_without_candidate(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        self.assertIn(version, REVIEWED_COMPILERS)
        self.assertEqual(clang, REVIEWED_COMPILERS[version])
        host_flags = (
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT), "-I", str(SNAPSHOT),
            "-include", str(SNAPSHOT / "g2-config/pb_g2_options.h"),
        )
        with tempfile.TemporaryDirectory(prefix="open-cfw-varint32-oracle-") as temporary:
            temporary_path = Path(temporary)
            oracle_object = temporary_path / "oracle.o"
            oracle_program = temporary_path / "oracle-host"
            compile_result = subprocess.run(
                [clang, *host_flags, "-c", str(ORACLE_FIXTURE), "-o", str(oracle_object)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
            symbols = subprocess.run(
                ["nm", "-g", str(oracle_object)],
                cwd=ROOT, check=True, capture_output=True, text=True,
            ).stdout
            self.assertIn("open_cfw_test_nanopb_decode_varint32_eof_oracle", symbols)
            self.assertIn("open_cfw_test_nanopb_decode_varint32_oracle_abi", symbols)
            link_result = subprocess.run(
                [
                    clang, *host_flags, str(ORACLE_FIXTURE),
                    str(SNAPSHOT / "pb_common.c"), "-x", "c", "-",
                    "-o", str(oracle_program),
                ],
                cwd=ROOT,
                input=(
                    "extern int open_cfw_test_nanopb_decode_varint32_oracle_abi(void);\n"
                    "int main(void) {\n"
                    "    return open_cfw_test_nanopb_decode_varint32_oracle_abi();\n"
                    "}\n"
                ),
                capture_output=True,
                text=True,
            )
            self.assertEqual(link_result.returncode, 0, link_result.stderr)
            run_result = subprocess.run(
                [str(oracle_program)], cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(run_result.returncode, 0, run_result.stderr)

    def test_exact_stock_pair_neighbors_and_literal_closure(self) -> None:
        self.assertEqual((len(self.package), sha256(self.package)), PACKAGE_PIN)
        self.assertEqual((len(self.application), sha256(self.application)), APPLICATION_PIN)
        self.assertEqual(PRIVATE_SPAN[1], PUBLIC_SPAN[0])
        self.assertEqual(PREDECESSOR_SPAN[1], PRIVATE_SPAN[0])
        self.assertEqual(PUBLIC_SPAN[1], SUCCESSOR_SPAN[0])
        self.assertEqual(self.span(PRIVATE_SPAN).hex(), PRIVATE_HEX)
        self.assertEqual(self.span(PUBLIC_SPAN).hex(), PUBLIC_HEX)
        self.assertEqual(self.span(PAIR_SPAN), bytes.fromhex(PRIVATE_HEX + PUBLIC_HEX))
        for span, expected in SPAN_PINS.items():
            body = self.span(span)
            self.assertEqual((len(body), sha256(body)), expected)

        literal = self.application[
            ERROR_LITERAL_SLOT - APPLICATION_BASE:
            ERROR_LITERAL_SLOT - APPLICATION_BASE + 4
        ]
        self.assertEqual((literal, sha256(literal)), ERROR_LITERAL_PIN)
        string = self.application[
            ERROR_STRING_ADDRESS - APPLICATION_BASE:
            ERROR_STRING_ADDRESS - APPLICATION_BASE + len(ERROR_STRING_PIN[0])
        ]
        self.assertEqual((string, sha256(string)), ERROR_STRING_PIN)
        self.assertEqual(struct.unpack("<I", literal)[0], ERROR_STRING_ADDRESS)

        loads = []
        private = self.span(PRIVATE_SPAN)
        for offset in range(0, len(private) - 3, 2):
            address = PRIVATE_SPAN[0] + offset
            first, second = struct.unpack_from("<HH", private, offset)
            if first == 0xF8DF:
                target = ((address + 4) & ~3) + (second & 0x0FFF)
                if target == ERROR_LITERAL_SLOT:
                    loads.append(address)
        self.assertEqual(tuple(loads), ERROR_LITERAL_LOADS)

    def test_whole_image_callers_encodings_and_ingress_closure(self) -> None:
        self.assertEqual(
            wide_branch_target(0x1000, 0xF000, 0xF800, link=True),
            0x1004,
        )
        self.assertEqual(
            wide_branch_target(0x1000, 0xF000, 0xB800, link=False),
            0x1004,
        )
        self.assertEqual(
            wide_conditional_target(0x1000, 0xF000, 0x8000),
            0x1004,
        )
        self.assertEqual(narrow_targets(0x1000, 0xE000), (0x1004,))
        self.assertEqual(narrow_targets(0x1000, 0xD000), (0x1004,))
        self.assertEqual(narrow_targets(0x1000, 0xB100), (0x1004,))

        expected_by_span = {
            PRIVATE_SPAN: PRIVATE_CALLERS,
            PUBLIC_SPAN: PUBLIC_CALLERS,
        }
        for target_span, expected in expected_by_span.items():
            start, end = target_span
            direct = {"bl": [], "bw": [], "conditional": [], "narrow": []}
            interior = []
            for offset in range(0, len(self.application) - 3, 2):
                address = APPLICATION_BASE + offset
                first, second = struct.unpack_from("<HH", self.application, offset)
                encoding = self.application[offset:offset + 4].hex()
                for name, target in (
                    ("bl", wide_branch_target(address, first, second, link=True)),
                    ("bw", wide_branch_target(address, first, second, link=False)),
                    ("conditional", wide_conditional_target(address, first, second)),
                ):
                    if target is None or start <= address < end:
                        continue
                    if target == start:
                        direct[name].append((address, encoding))
                    elif start < target < end:
                        interior.append((name, address, target, encoding))
            for offset in range(0, len(self.application) - 1, 2):
                address = APPLICATION_BASE + offset
                if start <= address < end:
                    continue
                halfword = struct.unpack_from("<H", self.application, offset)[0]
                for target in narrow_targets(address, halfword):
                    if target == start:
                        direct["narrow"].append((address, f"{halfword:04x}"))
                    elif start < target < end:
                        interior.append(("narrow", address, target, f"{halfword:04x}"))

            self.assertEqual(tuple(direct["bl"]), expected)
            self.assertEqual(direct["bw"], [])
            self.assertEqual(direct["conditional"], [])
            self.assertEqual(direct["narrow"], [])
            self.assertEqual(interior, [])
            address_hash, record_hash = CALLER_HASHES[target_span]
            self.assertEqual(
                sha256(b"".join(struct.pack("<I", address) for address, _ in expected)),
                address_hash,
            )
            self.assertEqual(
                sha256(b"".join(
                    struct.pack("<I", address) + bytes.fromhex(encoding)
                    for address, encoding in expected
                )),
                record_hash,
            )

        stored = []
        for offset in range(len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            canonical = value & ~1
            if any(start <= canonical < end for start, end in (PRIVATE_SPAN, PUBLIC_SPAN)):
                stored.append((APPLICATION_BASE + offset, value, offset % 4))
        self.assertEqual(stored, [])

    def test_private_and_public_outgoing_call_closure(self) -> None:
        for span, expected in (
            (PRIVATE_SPAN, PRIVATE_OUTGOING),
            (PUBLIC_SPAN, PUBLIC_OUTGOING),
        ):
            body = self.span(span)
            calls = []
            for offset in range(0, len(body) - 3, 2):
                address = span[0] + offset
                first, second = struct.unpack_from("<HH", body, offset)
                target = wide_branch_target(address, first, second, link=True)
                if target is not None:
                    calls.append((address, target, body[offset:offset + 4].hex()))
            self.assertEqual(tuple(calls), expected)

    def test_canonical_upstream_authority_and_definition_boundaries(self) -> None:
        upstream = UPSTREAM.read_bytes()
        self.assertEqual((len(upstream), sha256(upstream)), UPSTREAM_PIN)
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["license"], "Zlib")
        self.assertEqual(provenance["upstream"]["selected_tag"], "nanopb-0.4.9")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
        )
        self.assertEqual(
            provenance["upstream"]["selected_tree"],
            "2c4c260bcff3f9f7081238d377274dd385d76582",
        )
        self.assertEqual(
            (UPSTREAM_LICENSE.stat().st_size, sha256(UPSTREAM_LICENSE)),
            (898, "e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d"),
        )

        for signature, expected_start, expected_end, size, digest, bad_digest in UPSTREAM_DEFINITIONS:
            with self.subTest(signature=signature):
                start, end = brace_balanced_definition(upstream, signature)
                self.assertEqual((start, end), (expected_start, expected_end))
                definition = upstream[start:end]
                self.assertEqual((len(definition), sha256(definition)), (size, digest))
                self.assertEqual(upstream[end:end + 2], b"\n\n")
                delimiter_inclusive = upstream[start:end + 2]
                self.assertEqual((len(delimiter_inclusive), sha256(delimiter_inclusive)), (size + 2, bad_digest))
                self.assertNotEqual(sha256(delimiter_inclusive), digest)

    def test_authenticated_bootloader_excludes_all_three_exact_bodies(self) -> None:
        bootloader = BOOTLOADER.read_bytes()
        self.assertEqual((len(bootloader), sha256(bootloader)), BOOTLOADER_PIN)
        for span in (PRIVATE_SPAN, PUBLIC_SPAN, PAIR_SPAN):
            body = self.span(span)
            self.assertEqual(bootloader.count(body), 0)

    def test_qualified_candidate_names_are_excluded_from_production_surfaces(self) -> None:
        overlay_paths = (
            ROOT / "components/apollo_main/core_overlay/overlay.json",
            ROOT / "components/bootloader/core_overlay/overlay.json",
            ROOT / "components/apollo_main/ring_gesture/overlay.json",
        )
        manifests = tuple(sorted((ROOT / "manifests").glob("*.json")))
        package_recipes = (
            ROOT / "Makefile",
            ROOT / "make.sh",
            ROOT / "tools/open_cfw.py",
        )
        production_lists_and_allowlists = (
            PROVENANCE,
            VERIFIER,
            SNAPSHOT / "README.openCFW.md",
        )
        coverage_claims = (
            ROOT / "docs/source-coverage.md",
            ROOT / "docs/memory-map.md",
            ROOT / "README.md",
            ROOT / "components/README.md",
            ROOT / "components/apollo_main/core_overlay/EVIDENCE.md",
        )
        tokens = LEGACY_CANDIDATE_TOKENS
        self.assertEqual(len(ACTIVE_PRODUCTION_SURFACES), len(set(ACTIVE_PRODUCTION_SURFACES)))
        for path in ACTIVE_PRODUCTION_SURFACES:
            self.assertTrue(path.is_file(), path.relative_to(ROOT))
        self.assertTrue(set(overlay_paths).issubset(ACTIVE_PRODUCTION_SURFACES))
        self.assertTrue(set(manifests).issubset(ACTIVE_PRODUCTION_SURFACES))
        self.assertTrue(set(package_recipes).issubset(ACTIVE_PRODUCTION_SURFACES))
        self.assertTrue(
            set(production_lists_and_allowlists).issubset(ACTIVE_PRODUCTION_SURFACES)
        )
        self.assertTrue(set(coverage_claims).issubset(ACTIVE_PRODUCTION_SURFACES))

        neighboring_leaf_tokens = (
            "open_cfw_nanopb_istream_from_buffer",
            "open_cfw_nanopb_decode_svarint",
            "runtime_nanopb_istream_from_buffer.c",
            "runtime_nanopb_decode_svarint.c",
        )
        discovered_neighbors = set()
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix not in {".json", ".md", ".py"}:
                continue
            relative = path.relative_to(ROOT)
            if (
                "build" in relative.parts or
                relative.parts[0] == "tests" or
                relative.parts[:2] == ("docs", "research") or
                relative.parts[:2] == ("docs", "superpowers") or
                relative.parts[:2] == ("components", "shared")
            ):
                continue
            text = path.read_text(encoding="utf-8")
            if any(token in text for token in neighboring_leaf_tokens):
                discovered_neighbors.add(path)
        self.assertEqual(discovered_neighbors, NEIGHBOR_CONSUMERS)
        self.assertTrue(NEIGHBOR_CONSUMERS.issubset(ACTIVE_PRODUCTION_SURFACES))

        for path in ACTIVE_PRODUCTION_SURFACES:
            text = path.read_text(encoding="utf-8")
            for token in tokens:
                self.assertNotIn(token, text, path.relative_to(ROOT))

    def test_atomic_production_registration_is_complete(self) -> None:
        # Source, object, oracle, and legacy-candidate exclusion evidence remain
        # independently green while Task 5 still owns manifest replacement.
        self.assertTrue(
            PRODUCTION_SOURCE.is_file(),
            "production varint32 source is absent before atomic registration",
        )
        self.assertTrue(
            PRODUCTION_HEADER.is_file(),
            "production varint32 header is absent before atomic registration",
        )
        production_text = (
            PRODUCTION_SOURCE.read_text(encoding="utf-8")
            + PRODUCTION_HEADER.read_text(encoding="utf-8")
        )
        self.assertNotIn(
            "_candidate", production_text,
            "production source/header must not contain _candidate names",
        )
        self.assertIn(PRODUCTION_PRIVATE_FUNCTION + "(", production_text)
        self.assertIn(PRODUCTION_PUBLIC_FUNCTION + "(", production_text)

        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        validate_atomic_production_topology(overlay, regions)

    def test_manifest_owns_exact_builder_regions_and_remains_reversible(self) -> None:
        manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
        apollo = manifest["component_overrides"]["apollo_main"]
        regions = apollo["regions"]
        self.assertEqual(len(regions), 1022)
        self.assertEqual(
            (apollo["provider"]["size"], apollo["provider"]["sha256"]),
            APPLE_AGGREGATE_PINS["component"],
        )
        self.assertEqual(
            (
                manifest["package"]["expected_size"],
                manifest["package"]["expected_sha256"],
            ),
            APPLE_AGGREGATE_PINS["package"],
        )

        expected = (
            (
                PRIVATE_MANIFEST_NAME, 357_592, PRIVATE_SPAN[0], 246,
                "generated_source_entry_replacement",
                "apollo510b/source-entry-nanopb-decode-varint32-eof-0x0048f4b8.bin",
            ),
            (
                PUBLIC_MANIFEST_NAME, 357_838, PUBLIC_SPAN[0], 10,
                "generated_source_entry_replacement",
                "apollo510b/source-entry-nanopb-decode-varint32-0x0048f5ae.bin",
            ),
            (
                "apollo_nanopb_decode_varint32_eof_source_alignment",
                3_648_366, 0x007B_2B4E, 2, "generated_alignment",
                "apollo510b/main-source-nanopb-decode-varint32-eof-alignment-0x007b2b4e.bin",
            ),
            (
                "apollo_nanopb_decode_varint32_eof_source_leaf",
                3_648_368, 0x007B_2B50, 222, "source_compiled",
                "apollo510b/main-source-nanopb-decode-varint32-eof-0x007b2b50.bin",
            ),
            (
                "apollo_nanopb_decode_varint32_overflow_rodata",
                3_648_590, 0x007B_2C2E, 16, "source_compiled",
                "apollo510b/main-source-nanopb-varint32-overflow-0x007b2c2e.bin",
            ),
            (
                "apollo_nanopb_decode_varint32_source_alignment",
                3_648_606, 0x007B_2C3E, 2, "generated_alignment",
                "apollo510b/main-source-nanopb-decode-varint32-alignment-0x007b2c3e.bin",
            ),
            (
                "apollo_nanopb_decode_varint32_source_leaf",
                3_648_608, 0x007B_2C40, 10, "source_compiled",
                "apollo510b/main-source-nanopb-decode-varint32-0x007b2c40.bin",
            ),
        )
        observed = tuple(
            (
                region["name"], region["file_offset"],
                region["target_address"], region["size"],
                region["address_status"], region["output"],
            )
            for region in regions
            if region["name"] in {item[0] for item in expected}
        )
        self.assertEqual(observed, expected)
        self.assertEqual(len({item[-1] for item in observed}), len(observed))

        ordered = sorted(regions, key=lambda region: region["file_offset"])
        self.assertEqual(ordered[0]["file_offset"], 0)
        for previous, following in zip(ordered, ordered[1:]):
            self.assertEqual(
                previous["file_offset"] + previous["size"],
                following["file_offset"],
                (previous["name"], following["name"]),
            )
        self.assertEqual(
            ordered[-1]["file_offset"] + ordered[-1]["size"],
            apollo["provider"]["size"],
        )
        self.assertFalse(any(
            region["address_status"] == "official_blob"
            and region.get("target_address", -1) < PAIR_SPAN[1]
            and region.get("target_address", -1) + region["size"] > PAIR_SPAN[0]
            for region in regions
        ))

        component = (
            ROOT / apollo["provider"]["path"]
        ).read_bytes()
        artifact_pins = (
            LINUX_AGGREGATE_PINS
            if os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") == "linux-clang"
            else APPLE_AGGREGATE_PINS
        )
        self.assertEqual(
            (len(component), sha256(component)), artifact_pins["component"]
        )
        official = OFFICIAL.read_bytes()
        reconstructed = bytearray(component[:len(official)])
        for region in regions:
            start = region["file_offset"]
            end = min(start + region["size"], len(official))
            if end > start:
                reconstructed[start:end] = official[start:end]
        self.assertEqual(bytes(reconstructed), official)

        boot = manifest["component_overrides"]["apollo_bootloader"]
        self.assertEqual(
            (boot["provider"]["size"], boot["provider"]["sha256"]),
            (
                149_262,
                "695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267",
            ),
        )

    def test_real_builder_accepts_production_leaf_records_twice(self) -> None:
        source = prospective_production_source()
        header = prospective_production_header()
        self.assertEqual((len(source), sha256(source)), PROSPECTIVE_SOURCE_PIN)
        self.assertEqual((len(header), sha256(header)), PROSPECTIVE_HEADER_PIN)
        self.assertNotIn(b"_candidate", source + header)

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        self.assertIn(version, REVIEWED_COMPILERS)
        self.assertEqual(clang, REVIEWED_COMPILERS[version])
        for function in (
            PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION,
        ):
            self.assertNotEqual(
                PROSPECTIVE_APPLE_PINS[function]["offset"],
                PROSPECTIVE_LINUX_PINS[function]["offset"],
            )
        profile = (
            "linux-clang"
            if version == "Homebrew clang version 22.1.8"
            else None
        )
        requested_profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
        if requested_profile is not None:
            self.assertEqual(requested_profile, profile or "apple-clang")
        aggregate_pins = (
            LINUX_AGGREGATE_PINS if profile == "linux-clang"
            else APPLE_AGGREGATE_PINS
        )

        build_root = ROOT / "build"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="open-cfw-varint32-real-control-", dir=build_root
        ) as temporary:
            temporary_path = Path(temporary)
            reports = [
                apollo_overlay.build(
                    root=ROOT,
                    config_path=OVERLAY,
                    output_dir=temporary_path / f"current-build-{index}",
                    clang=clang,
                    toolchain_profile=profile,
                )
                for index in range(2)
            ]
            current_report = reports[0]
            current_overlay_path = ROOT / current_report["overlay"]["artifact"]
            current_overlay_bytes = current_overlay_path.read_bytes()
            second_overlay_path = ROOT / reports[1]["overlay"]["artifact"]
            self.assertEqual(current_overlay_bytes, second_overlay_path.read_bytes())
            self.assertEqual(
                (len(current_overlay_bytes), sha256(current_overlay_bytes)),
                (
                    current_report["overlay"]["size"],
                    current_report["overlay"]["sha256"],
                ),
            )

            pair_functions = (
                PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION,
            )
            leaf_reports = [
                report for function in pair_functions
                for report in current_report["relocated_leaves"]
                if report["extraction"]["function"] == function
            ]
            self.assertEqual(
                [report["extraction"]["function"] for report in leaf_reports],
                list(pair_functions),
            )
            linked_reports = [
                report for function in pair_functions
                for report in current_report["overlay"]["link"][
                    "relocated_functions"
                ]
                if report["function"] == function
            ]
            self.assertEqual(
                [report["function"] for report in linked_reports],
                list(pair_functions),
            )
            for linked, report, function in zip(
                linked_reports, leaf_reports, pair_functions,
            ):
                self.assertEqual(linked["function"], function)
                for field in (
                    "offset", "size", "alignment", "padding_before",
                    "runtime_address", "runtime_address_hex",
                ):
                    self.assertEqual(linked[field], report["placement"][field])
            self.assertEqual(
                (len(current_overlay_bytes), sha256(current_overlay_bytes)),
                aggregate_pins["overlay"],
            )
            component_path = ROOT / current_report["component"]["artifact"]
            second_component_path = ROOT / reports[1]["component"]["artifact"]
            self.assertEqual(
                component_path.read_bytes(), second_component_path.read_bytes()
            )
            self.assertEqual(
                (component_path.stat().st_size, sha256(component_path)),
                aggregate_pins["component"],
            )
            production_config, projected_regions = production_topology_fixture()
            validate_atomic_production_topology(production_config, projected_regions)

            sys.path.insert(0, str(ROOT / "tools"))
            import open_cfw

            projected_manifest = json.loads(
                CORE_MANIFEST.read_text(encoding="utf-8")
            )
            apollo = projected_manifest["component_overrides"]["apollo_main"]
            apollo["provider"].update({
                "path": current_report["component"]["artifact"],
                "size": APPLE_AGGREGATE_PINS["component"][0],
                "sha256": APPLE_AGGREGATE_PINS["component"][1],
            })
            apollo["regions"] = projected_regions
            projected_manifest["package"].update({
                "expected_size": APPLE_AGGREGATE_PINS["package"][0],
                "expected_sha256": APPLE_AGGREGATE_PINS["package"][1],
            })
            manifest_directory = ROOT / "manifests"
            with tempfile.NamedTemporaryFile(
                "w", suffix=".json", prefix="task4-varint32-",
                dir=manifest_directory, delete=False,
            ) as manifest_file:
                json.dump(projected_manifest, manifest_file, indent=2)
                manifest_file.write("\n")
                projected_manifest_path = Path(manifest_file.name)
            try:
                package_roots = [
                    temporary_path / f"package-projection-{index}"
                    for index in range(2)
                ]
                for package_root in package_roots:
                    open_cfw.build(
                        projected_manifest_path,
                        package_root,
                        toolchain_profile=profile,
                    )
            finally:
                projected_manifest_path.unlink(missing_ok=True)

            package_paths = [
                package_root / "package"
                / projected_manifest["package"]["output_name"]
                for package_root in package_roots
            ]
            package_bytes = [path.read_bytes() for path in package_paths]
            self.assertEqual(package_bytes[0], package_bytes[1])
            self.assertEqual(
                (len(package_bytes[0]), sha256(package_bytes[0])),
                aggregate_pins["package"],
            )
            canonical_report_bytes = []
            for package_root in package_roots:
                canonical_report = json.loads(
                    (package_root / "build-report.json").read_text(
                        encoding="utf-8"
                    )
                )
                canonical_report["manifest"] = (
                    "manifests/g2-2.2.6.10-core-source.json"
                )
                canonical_report_bytes.append((
                    json.dumps(canonical_report, indent=2, sort_keys=True) + "\n"
                ).encode("utf-8"))
            self.assertEqual(
                canonical_report_bytes[0], canonical_report_bytes[1]
            )
            self.assertEqual(
                (
                    len(canonical_report_bytes[0]),
                    sha256(canonical_report_bytes[0]),
                ),
                aggregate_pins["build_report"],
            )
            flash_plan_bytes = [
                (package_root / "flash-plan.json").read_bytes()
                for package_root in package_roots
            ]
            self.assertEqual(flash_plan_bytes[0], flash_plan_bytes[1])
            self.assertEqual(
                (len(flash_plan_bytes[0]), sha256(flash_plan_bytes[0])),
                aggregate_pins["flash_plan"],
            )

    def test_real_builder_rejects_mutated_production_configs(self) -> None:
        """Exercise the real full-overlay path for every production seam."""
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        self.assertIn(version, REVIEWED_COMPILERS)
        self.assertEqual(clang, REVIEWED_COMPILERS[version])
        profile = (
            "linux-clang"
            if version == "Homebrew clang version 22.1.8"
            else None
        )
        aggregate_pins = (
            LINUX_AGGREGATE_PINS if profile == "linux-clang"
            else APPLE_AGGREGATE_PINS
        )
        baseline = json.loads(OVERLAY.read_text(encoding="utf-8"))
        baseline_regions = json.loads(
            CORE_MANIFEST.read_text(encoding="utf-8")
        )["component_overrides"]["apollo_main"]["regions"]
        build_root = ROOT / "build"
        build_root.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(
            prefix="open-cfw-varint32-real-mutations-", dir=build_root
        ) as temporary:
            temporary_path = Path(temporary)

            def leaf(config: dict, function: str) -> dict:
                return next(
                    item for item in config["relocated_leaves"]
                    if item["function"] == function
                )

            def patch(config: dict, name: str) -> dict:
                return next(
                    item for item in config["patch_sites"]
                    if item["name"] == name
                )

            def selected_leaf_contract(config: dict, function: str) -> dict:
                selected = leaf(config, function)
                if profile is None:
                    return selected
                return selected["toolchain_profiles"][profile]

            build_index = 0

            def real_build(
                config: dict,
                label: str,
                *,
                compiler: str = clang,
                environment: dict[str, str] | None = None,
            ) -> dict:
                nonlocal build_index
                build_index += 1
                config_path = temporary_path / f"{build_index:02d}-{label}.json"
                config_path.write_text(
                    json.dumps(config, indent=2) + "\n", encoding="utf-8"
                )
                with mock.patch.dict(
                    os.environ, environment or {}, clear=False
                ):
                    return apollo_overlay.build(
                        root=ROOT,
                        config_path=config_path,
                        output_dir=temporary_path / f"{build_index:02d}-{label}",
                        clang=compiler,
                        toolchain_profile=profile,
                    )

            def guarded_build(config: dict, label: str) -> dict:
                validate_atomic_production_topology(
                    config, copy.deepcopy(baseline_regions)
                )
                return real_build(config, label)

            control = guarded_build(copy.deepcopy(baseline), "control")
            self.assertEqual(
                (control["overlay"]["size"], control["overlay"]["sha256"]),
                aggregate_pins["overlay"],
            )

            def unrelated_leaf_preserver(label: str) -> dict:
                preserved = copy.deepcopy(baseline["relocated_leaves"][0])
                preserved["function"] = "open_cfw_varint32_mutation_" + label
                if "closure" in preserved:
                    preserved["closure"]["text_section"] = (
                        ".text." + preserved["function"]
                    )
                return preserved

            def unrelated_patch_preserver(label: str) -> dict:
                preserved = copy.deepcopy(baseline["patch_sites"][0])
                preserved["name"] = "varint32_mutation_patch_" + label
                return preserved

            topology_mutations: list[tuple[str, object, str]] = []

            def topology(
                label: str, mutate: object, expected_message: str
            ) -> None:
                topology_mutations.append((label, mutate, expected_message))

            def combined_patch(config: dict) -> None:
                config["patch_sites"] = [
                    item for item in config["patch_sites"]
                    if item["name"] not in {
                        PRIVATE_PATCH_NAME, PUBLIC_PATCH_NAME,
                    }
                ]
                config["patch_sites"].append({
                    "name": "replace_nanopb_decode_varint32_pair",
                    "runtime_address": PAIR_SPAN[0],
                    "expected_size": PAIR_SPAN[1] - PAIR_SPAN[0],
                    "expected_sha256": SPAN_PINS[PAIR_SPAN][1],
                    "branch": "b_w",
                    "target_function": PRODUCTION_PRIVATE_FUNCTION,
                })
                config["patch_sites"].append(
                    unrelated_patch_preserver("combined-patch")
                )

            topology(
                "combined-patch",
                combined_patch,
                "the varint32 pair must not use one combined 256-byte entry patch",
            )

            def combined_leaf(config: dict) -> None:
                combined = copy.deepcopy(
                    leaf(config, PRODUCTION_PRIVATE_FUNCTION)
                )
                combined["toolchain"]["flags"].remove(
                    "-D" + PRIVATE_LEAF_ONLY
                )
                config["relocated_leaves"] = [
                    item for item in config["relocated_leaves"]
                    if item["function"] not in {
                        PRODUCTION_PRIVATE_FUNCTION,
                        PRODUCTION_PUBLIC_FUNCTION,
                    }
                ]
                config["relocated_leaves"].extend((
                    combined,
                    unrelated_leaf_preserver("combined-leaf"),
                ))

            topology(
                "combined-leaf",
                combined_leaf,
                "the two varint32 bodies must not be combined into one relocated leaf",
            )

            for removed in (
                PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION,
            ):
                def one_sided(config: dict, removed: str = removed) -> None:
                    config["functions"].remove(removed)
                    config["relocated_leaves"] = [
                        item for item in config["relocated_leaves"]
                        if item["function"] != removed
                    ]
                    config["patch_sites"] = [
                        item for item in config["patch_sites"]
                        if item.get("target_function") != removed
                    ]
                    preserved = unrelated_leaf_preserver(
                        "one-sided-" + removed.rsplit("_", 1)[-1]
                    )
                    config["functions"].append(preserved["function"])
                    config["relocated_leaves"].append(preserved)
                    config["patch_sites"].append(
                        unrelated_patch_preserver(
                            "one-sided-" + removed.rsplit("_", 1)[-1]
                        )
                    )

                topology(
                    "one-sided-" + removed.rsplit("_", 1)[-1],
                    one_sided,
                    "production function registry must contain both varint32 symbols exactly once",
                )

            def public_fixed_address(config: dict) -> None:
                relocation = leaf(
                    config, PRODUCTION_PUBLIC_FUNCTION
                )["relocations"][0]
                relocation.pop("target_function")
                relocation["target_address"] = PRIVATE_SPAN[0]

            topology(
                "public-fixed-address",
                public_fixed_address,
                "public varint32 leaf must call the private source leaf by target_function",
            )

            def private_fixed_addresses(config: dict) -> None:
                for relocation in leaf(
                    config, PRODUCTION_PRIVATE_FUNCTION
                )["relocations"][:2]:
                    relocation.pop("target_function")
                    relocation["target_address"] = 0x0048_F454

            topology(
                "private-fixed-addresses",
                private_fixed_addresses,
                "private varint32 leaf must call source-owned readbyte twice by target_function",
            )

            def only_one_patch(config: dict) -> None:
                config["patch_sites"].remove(
                    patch(config, PUBLIC_PATCH_NAME)
                )
                config["patch_sites"].append(
                    unrelated_patch_preserver("two-leaves-one-patch")
                )

            topology(
                "two-leaves-one-patch",
                only_one_patch,
                "varint32 production requires two distinct full-span entry patches",
            )

            def concatenated_stock_hash(config: dict) -> None:
                patch(config, PRIVATE_PATCH_NAME)["expected_sha256"] = (
                    SPAN_PINS[PAIR_SPAN][1]
                )

            topology(
                "concatenated-stock-hash",
                concatenated_stock_hash,
                "private patch must authenticate exactly the 246-byte stock body",
            )

            def partial_stock_hash(config: dict) -> None:
                patch(config, PRIVATE_PATCH_NAME)["expected_sha256"] = sha256(
                    self.span((PRIVATE_SPAN[0], PRIVATE_SPAN[0] + 64))
                )

            topology(
                "partial-stock-hash",
                partial_stock_hash,
                "private patch must authenticate exactly the 246-byte stock body",
            )

            def overlapping_patch(config: dict) -> None:
                patch(config, PUBLIC_PATCH_NAME)["runtime_address"] = (
                    PRIVATE_SPAN[1] - 2
                )

            topology(
                "overlapping-patch",
                overlapping_patch,
                "varint32 entry patches must not overlap",
            )

            def wrong_stock_hash(config: dict) -> None:
                patch(config, PUBLIC_PATCH_NAME)["expected_sha256"] = "0" * 64

            topology(
                "wrong-stock-hash",
                wrong_stock_hash,
                "public patch must authenticate exactly the 10-byte stock body",
            )

            def swapped_leaf_order(config: dict) -> None:
                private_index = next(
                    index for index, item in enumerate(config["relocated_leaves"])
                    if item["function"] == PRODUCTION_PRIVATE_FUNCTION
                )
                public_index = next(
                    index for index, item in enumerate(config["relocated_leaves"])
                    if item["function"] == PRODUCTION_PUBLIC_FUNCTION
                )
                config["relocated_leaves"][private_index], config[
                    "relocated_leaves"
                ][public_index] = (
                    config["relocated_leaves"][public_index],
                    config["relocated_leaves"][private_index],
                )

            topology(
                "swapped-leaf-order",
                swapped_leaf_order,
                "varint32 relocated leaves must be ordered private then public",
            )

            for label, mutate, expected_message in topology_mutations:
                config = copy.deepcopy(baseline)
                mutate(config)
                with self.subTest(mutation=label), self.assertRaisesRegex(
                    AssertionError,
                    "^" + re.escape(expected_message) + "$",
                ):
                    guarded_build(config, label)

            builder_mutations: list[tuple[str, object, str]] = []

            def builder(label: str, mutate: object, pattern: str) -> None:
                builder_mutations.append((label, mutate, pattern))

            def wrong_source_hash(config: dict) -> None:
                leaf(config, PRODUCTION_PRIVATE_FUNCTION)["source"]["sha256"] = (
                    "0" * 64
                )

            builder(
                "source-hash",
                wrong_source_hash,
                rf"components/shared/nanopb/runtime_nanopb_decode_varint32\.c: relocated closure {PRODUCTION_PRIVATE_FUNCTION} source SHA-256 differs from config",
            )

            def wrong_text_section(config: dict) -> None:
                leaf(config, PRODUCTION_PRIVATE_FUNCTION)["closure"][
                    "text_section"
                ] = ".text.open_cfw_nanopb_decode_varint32_missing"

            builder(
                "text-section",
                wrong_text_section,
                rf"relocated closure {PRODUCTION_PRIVATE_FUNCTION} expected one \.text\.open_cfw_nanopb_decode_varint32_missing section, observed 0",
            )

            def wrong_relocation_offset(config: dict) -> None:
                selected_leaf_contract(
                    config, PRODUCTION_PRIVATE_FUNCTION
                )["relocations"][0][
                    "offset"
                ] += 2

            builder(
                "relocation-offset",
                wrong_relocation_offset,
                rf"relocated closure {PRODUCTION_PRIVATE_FUNCTION} relocation list differs from reviewed config: expected .* observed .*",
            )

            def wrong_relocation_type(config: dict) -> None:
                selected_leaf_contract(
                    config, PRODUCTION_PRIVATE_FUNCTION
                )["relocations"][0][
                    "type"
                ] = "R_ARM_THM_JUMP24"

            builder(
                "relocation-type",
                wrong_relocation_type,
                rf"relocated closure {PRODUCTION_PRIVATE_FUNCTION} strict external symbol metadata differs for 'open_cfw_nanopb_readbyte': expected global/default/STT_NOTYPE",
            )

            def wrong_relocation_symbol(config: dict) -> None:
                selected_leaf_contract(
                    config, PRODUCTION_PRIVATE_FUNCTION
                )["relocations"][0][
                    "symbol"
                ] = PRODUCTION_PRIVATE_FUNCTION

            builder(
                "relocation-symbol",
                wrong_relocation_symbol,
                rf"relocated closure {PRODUCTION_PRIVATE_FUNCTION} relocation 0 must bind its exact symbol to the same target_function name",
            )

            def swapped_call_target(config: dict) -> None:
                relocation = selected_leaf_contract(
                    config, PRODUCTION_PRIVATE_FUNCTION
                )["relocations"][0]
                relocation["symbol"] = PRODUCTION_PUBLIC_FUNCTION
                relocation["target_function"] = PRODUCTION_PUBLIC_FUNCTION

            builder(
                "swapped-target-function",
                swapped_call_target,
                rf"relocated closure {PRODUCTION_PRIVATE_FUNCTION} relocation 0 targets unavailable prior overlay function '{PRODUCTION_PUBLIC_FUNCTION}'",
            )

            def missing_literal_closure(config: dict) -> None:
                leaf(config, PRODUCTION_PRIVATE_FUNCTION).pop("closure")

            builder(
                "missing-rodata-closure",
                missing_literal_closure,
                rf"relocated leaf {PRODUCTION_PRIVATE_FUNCTION} relocation 2 has unsupported appended-leaf type 'R_ARM_THM_MOVW_PREL_NC'",
            )

            def mutated_literal_closure(config: dict) -> None:
                leaf(config, PRODUCTION_PRIVATE_FUNCTION)["closure"]["rodata"][
                    "sha256"
                ] = "0" * 64

            builder(
                "mutated-rodata-closure",
                mutated_literal_closure,
                rf"relocated closure {PRODUCTION_PRIVATE_FUNCTION} rodata differs from reviewed size, SHA-256, or alignment pins",
            )

            effective_private_pins = (
                PROSPECTIVE_LINUX_PINS[PRODUCTION_PRIVATE_FUNCTION]
                if profile == "linux-clang"
                else PROSPECTIVE_APPLE_PINS[PRODUCTION_PRIVATE_FUNCTION]
            )
            for field, value in (
                ("size", effective_private_pins["size"] - 2),
                ("sha256", "0" * 64),
                ("alignment", 2),
                ("offset", effective_private_pins["offset"] + 2),
                ("unrelocated_sha256", "0" * 64),
            ):
                def pin_mutation(
                    config: dict, field: str = field, value: object = value
                ) -> None:
                    expected = selected_leaf_contract(
                        config, PRODUCTION_PRIVATE_FUNCTION
                    )["expected"]
                    expected[field] = value
                    if field == "alignment":
                        expected["offset"] = effective_private_pins["offset"] - 2

                expected_pattern = (
                    rf"relocated closure {PRODUCTION_PRIVATE_FUNCTION} has invalid or violated text alignment 4"
                    if field == "alignment"
                    else rf"relocated leaf {PRODUCTION_PRIVATE_FUNCTION} offset differs from reviewed {effective_private_pins['offset'] + 2}: observed {effective_private_pins['offset']}"
                    if field == "offset"
                    else rf"relocated leaf {PRODUCTION_PRIVATE_FUNCTION} unrelocated SHA-256 differs from reviewed pin"
                    if field == "unrelocated_sha256"
                    else rf"relocated closure {PRODUCTION_PRIVATE_FUNCTION} output differs from reviewed pins: expected .* observed .*"
                )
                builder("private-pin-" + field, pin_mutation, expected_pattern)

            for label, mutate, expected_pattern in builder_mutations:
                config = copy.deepcopy(baseline)
                mutate(config)
                with self.subTest(mutation=label), self.assertRaisesRegex(
                    apollo_overlay.BuildError, "^" + expected_pattern + "$"
                ):
                    real_build(config, label)

            for mode, expected_pattern in (
                (
                    "personality-data",
                    rf"selected-function CANTUNWIND companion \.ARM\.exidx\.text\.{PRODUCTION_PRIVATE_FUNCTION} differs from the reviewed canonical row",
                ),
                (
                    "cross-function",
                    rf"selected-function CANTUNWIND companion \.ARM\.exidx\.text\.{PRODUCTION_PRIVATE_FUNCTION} does not bind canonically to the selected text section",
                ),
                (
                    "extra-relocation",
                    rf"selected-function CANTUNWIND companion \.ARM\.exidx\.text\.{PRODUCTION_PRIVATE_FUNCTION} must have one REL entry",
                ),
            ):
                config = copy.deepcopy(baseline)
                if mode == "cross-function":
                    leaf(config, PRODUCTION_PRIVATE_FUNCTION)["toolchain"][
                        "flags"
                    ].remove("-D" + PRIVATE_LEAF_ONLY)
                with self.subTest(exidx_mutation=mode), self.assertRaisesRegex(
                    apollo_overlay.BuildError, "^" + expected_pattern + "$"
                ):
                    real_build(
                        config,
                        "exidx-" + mode,
                        compiler=str(EXIDX_MUTATOR),
                        environment={
                            "OPENCFW_REAL_CLANG": clang,
                            "OPENCFW_EXIDX_MUTATION": mode,
                        },
                    )

            wrapper = temporary_path / "writable-injection.c"
            wrapper.write_text(
                '#include "' + str(PRODUCTION_SOURCE) + '"\n'
                '__attribute__((used, section(".data.open_cfw_varint32_mutation")))\n'
                'volatile unsigned open_cfw_varint32_mutation = 1;\n',
                encoding="utf-8",
            )
            config = copy.deepcopy(baseline)
            wrapper_source = wrapper.read_bytes()
            wrapper_record = {
                **leaf(config, PRODUCTION_PRIVATE_FUNCTION)["source"],
                "path": wrapper.relative_to(ROOT).as_posix(),
                "size": len(wrapper_source),
                "sha256": sha256(wrapper_source),
            }
            for function in (
                PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION,
            ):
                leaf(config, function)["source"] = copy.deepcopy(wrapper_record)
            with self.assertRaisesRegex(
                apollo_overlay.BuildError,
                rf"^relocated closure {PRODUCTION_PRIVATE_FUNCTION} strict relocation contract rejects unexpected allocated sections: \.data\.open_cfw_varint32_mutation$",
            ):
                real_build(config, "writable-section-injection")

    def test_atomic_production_contract_rejects_wrong_topologies(self) -> None:
        baseline_overlay, baseline_regions = production_topology_fixture()
        current_overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertEqual(
            baseline_overlay.get("name"), current_overlay["name"],
            "prospective control must derive from the actual current overlay",
        )
        validate_atomic_production_topology(baseline_overlay, baseline_regions)

        def unrelated_leaf_preserver(label: str) -> dict:
            leaf = copy.deepcopy(baseline_overlay["relocated_leaves"][0])
            leaf["function"] = "open_cfw_varint32_mutation_leaf_" + label
            if "closure" in leaf:
                leaf["closure"]["text_section"] = ".text." + leaf["function"]
            return leaf

        def unrelated_patch_preserver(label: str) -> dict:
            patch = copy.deepcopy(baseline_overlay["patch_sites"][0])
            patch["name"] = "varint32_mutation_patch_" + label
            return patch

        def expect_rejection(
            overlay: dict,
            regions: list[dict],
            message: str,
        ) -> None:
            with self.assertRaisesRegex(
                AssertionError, "^" + re.escape(message) + "$"
            ):
                validate_atomic_production_topology(overlay, regions)

        overlay = copy.deepcopy(baseline_overlay)
        del overlay["patch_sites"][-2:]
        overlay["patch_sites"].extend((
            {
                "name": "replace_nanopb_decode_varint32_pair",
                "runtime_address": PAIR_SPAN[0],
                "expected_size": 256,
                "expected_sha256": SPAN_PINS[PAIR_SPAN][1],
                "branch": "b_w",
                "target_function": PRODUCTION_PRIVATE_FUNCTION,
            },
            unrelated_patch_preserver("combined_pair_count_preserver"),
        ))
        expect_rejection(
            overlay, baseline_regions,
            "the varint32 pair must not use one combined 256-byte entry patch",
        )

        overlay = copy.deepcopy(baseline_overlay)
        del overlay["relocated_leaves"][-2:]
        combined_leaf = copy.deepcopy(baseline_overlay["relocated_leaves"][-2])
        combined_leaf["function"] = "open_cfw_nanopb_decode_varint32_pair"
        combined_leaf["closure"]["text_section"] = (
            ".text.open_cfw_nanopb_decode_varint32_pair"
        )
        overlay["relocated_leaves"].extend((
            combined_leaf,
            unrelated_leaf_preserver("combined_pair_count_preserver"),
        ))
        expect_rejection(
            overlay, baseline_regions,
            "the two varint32 bodies must not be combined into one relocated leaf",
        )

        overlay = copy.deepcopy(baseline_overlay)
        extra_function = "open_cfw_nanopb_decode_varint32_extra"
        extra_leaf = copy.deepcopy(overlay["relocated_leaves"][-2])
        extra_leaf["function"] = extra_function
        overlay["relocated_leaves"][0] = extra_leaf
        overlay["functions"][0] = extra_function
        expect_rejection(
            overlay, baseline_regions,
            "the production varint32 translation unit must source exactly two leaves",
        )

        overlay = copy.deepcopy(baseline_overlay)
        overlay["relocated_leaves"][-2]["source"].pop("license")
        expect_rejection(
            overlay, baseline_regions,
            f"{PRODUCTION_PRIVATE_FUNCTION} requires complete source provenance fields",
        )

        overlay = copy.deepcopy(baseline_overlay)
        overlay["relocated_leaves"][-1]["expected"]["offset"] += 2
        expect_rejection(
            overlay, baseline_regions,
            f"{PRODUCTION_PUBLIC_FUNCTION} must match its complete builder-reviewed leaf record",
        )

        for retained in (
            PRODUCTION_PRIVATE_FUNCTION, PRODUCTION_PUBLIC_FUNCTION,
        ):
            overlay = copy.deepcopy(baseline_overlay)
            removed = (
                PRODUCTION_PUBLIC_FUNCTION
                if retained == PRODUCTION_PRIVATE_FUNCTION
                else PRODUCTION_PRIVATE_FUNCTION
            )
            overlay["functions"].remove(removed)
            preserver = unrelated_leaf_preserver(
                retained.rsplit("_", 1)[-1] + "_one_sided"
            )
            overlay["functions"].append(preserver["function"])
            removed_leaf = next(
                leaf for leaf in overlay["relocated_leaves"]
                if leaf.get("function") == removed
            )
            overlay["relocated_leaves"].remove(removed_leaf)
            overlay["relocated_leaves"].append(preserver)
            removed_patch = next(
                patch for patch in overlay["patch_sites"]
                if patch.get("target_function") == removed
            )
            overlay["patch_sites"].remove(removed_patch)
            overlay["patch_sites"].append(
                unrelated_patch_preserver(
                    retained.rsplit("_", 1)[-1] + "_one_sided"
                )
            )
            expect_rejection(
                overlay, baseline_regions,
                "production function registry must contain both varint32 symbols exactly once",
            )

        overlay = copy.deepcopy(baseline_overlay)
        public_relocation = overlay["relocated_leaves"][-1]["relocations"][0]
        public_relocation.pop("target_function")
        public_relocation["target_address"] = PRIVATE_SPAN[0]
        expect_rejection(
            overlay, baseline_regions,
            "public varint32 leaf must call the private source leaf by target_function",
        )

        overlay = copy.deepcopy(baseline_overlay)
        for relocation in overlay["relocated_leaves"][-2]["relocations"][:2]:
            relocation.pop("target_function")
            relocation["target_address"] = 0x0048_F454
        expect_rejection(
            overlay, baseline_regions,
            "private varint32 leaf must call source-owned readbyte twice by target_function",
        )

        regions = copy.deepcopy(baseline_regions)
        current_manifest = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
        current_regions = current_manifest[
            "component_overrides"
        ]["apollo_main"]["regions"]
        private_current = next(
            region for region in current_regions
            if region["name"] == PRIVATE_MANIFEST_NAME
        )
        official_pair = {
            **private_current,
            "name": OFFICIAL_PAIR_REGION_NAME,
            "function": (
                "Official Apollo nanopb bytes after source-replaced "
                "pb_istream_from_buffer and before source-replaced "
                "pb_decode_varint"
            ),
            "size": PAIR_SPAN[1] - PAIR_SPAN[0],
            "address_status": "official_blob",
            "output": "apollo510b/main-opaque-0x0048f4b8.bin",
        }
        regions.insert(2, copy.deepcopy(official_pair))
        expect_rejection(
            baseline_overlay, regions,
            "no official manifest seam may survive inside either varint32 stock body",
        )

        overlay = copy.deepcopy(baseline_overlay)
        overlay["patch_sites"].pop()
        overlay["patch_sites"].append(
            unrelated_patch_preserver("two_leaves_one_patch")
        )
        expect_rejection(
            overlay, baseline_regions,
            "varint32 production requires two distinct full-span entry patches",
        )

        for digest in (
            SPAN_PINS[PAIR_SPAN][1],
            sha256(self.span((PRIVATE_SPAN[0], PRIVATE_SPAN[0] + 64))),
        ):
            overlay = copy.deepcopy(baseline_overlay)
            overlay["patch_sites"][-2]["expected_sha256"] = digest
            expect_rejection(
                overlay, baseline_regions,
                "private patch must authenticate exactly the 246-byte stock body",
            )

    def test_planned_isolated_host_and_thumb_compilation_contract(self) -> None:
        self.assertEqual(
            REVIEWED_COMPILERS,
            {
                "Apple clang version 21.0.0 (clang-2100.3.30.1)": "/usr/bin/clang",
                "Homebrew clang version 22.1.8": "/home/linuxbrew/.linuxbrew/bin/clang",
            },
        )
        for flag in (
            "--target=thumbv7em-none-eabi", "-ffreestanding", "-fropi",
            "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror",
        ):
            self.assertIn(flag, TARGET_FLAGS)
        self.require_source()

        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        self.assertIn(version, REVIEWED_COMPILERS)
        self.assertEqual(clang, REVIEWED_COMPILERS[version])
        with tempfile.TemporaryDirectory(prefix="open-cfw-varint32-contract-") as temporary:
            temporary_path = Path(temporary)
            target = temporary_path / "candidate.o"
            subprocess.run(
                [
                    clang, *TARGET_FLAGS, "-include", str(HEADER),
                    "-c", str(SOURCE), "-o", str(target),
                ],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            host_flags = (
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-I", str(ROOT), "-I", str(SNAPSHOT),
                "-include", str(SNAPSHOT / "g2-config/pb_g2_options.h"),
            )
            for unit in (SOURCE, HOST_FIXTURE, ORACLE_FIXTURE):
                forced_header = (
                    ("-include", str(HEADER)) if unit == SOURCE else ()
                )
                subprocess.run(
                    [clang, *host_flags, *forced_header, "-fsyntax-only", str(unit)],
                    cwd=ROOT, check=True, capture_output=True, text=True,
                )
            host_program = temporary_path / "candidate-host"
            subprocess.run(
                [
                    clang, *host_flags, "-include", str(HEADER),
                    str(SOURCE), str(HOST_FIXTURE), str(ORACLE_FIXTURE),
                    str(SNAPSHOT / "pb_common.c"),
                    "-o", str(host_program),
                ],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            subprocess.run(
                [str(host_program)], cwd=ROOT, check=True,
                capture_output=True, text=True,
            )

            sys.path.insert(0, str(ROOT / "tools"))
            import apollo_overlay
            data, sections = apollo_overlay.parse_elf32(target)
            symtab = apollo_overlay.section_named(sections, ".symtab")
            strtab = sections[int(symtab["link"])]
            strings = data[
                int(strtab["offset"]):int(strtab["offset"]) + int(strtab["size"])
            ]
            symbols = []
            for index in range(int(symtab["size"]) // 16):
                fields = struct.unpack_from(
                    "<IIIBBH", data, int(symtab["offset"]) + index * 16
                )
                symbols.append((apollo_overlay.elf_string(strings, fields[0], "symbol"), fields))
            undefined = sorted(
                name for name, fields in symbols if name and fields[5] == 0
            )
            self.assertEqual(undefined, [READBYTE_FUNCTION])
            defined = {
                name: fields for name, fields in symbols if name and fields[5] != 0
            }
            for function in (PRIVATE_FUNCTION, PUBLIC_FUNCTION):
                fields = defined[function]
                self.assertEqual(fields[3] >> 4, 1, f"{function} must be global")
                self.assertEqual(fields[3] & 0x0F, 2, f"{function} must be a function")

            executable = {
                section["name"] for section in sections
                if int(section["size"]) > 0 and int(section["flags"]) & 0x4
            }
            private_section = ".text." + PRIVATE_FUNCTION
            public_section = ".text." + PUBLIC_FUNCTION
            self.assertEqual(executable, {private_section, public_section})
            writable = [
                section["name"] for section in sections
                if int(section["size"]) > 0 and int(section["flags"]) & 0x3 == 0x3
            ]
            self.assertEqual(writable, [])
            self.assertEqual(data.count(ERROR_STRING_PIN[0]), 1)

            relocation_calls: dict[str, list[str]] = {}
            for section in sections:
                if int(section["type"]) != 9:
                    continue
                target_section = sections[int(section["info"])]["name"]
                calls = []
                for index in range(int(section["size"]) // 8):
                    _, information = struct.unpack_from(
                        "<II", data, int(section["offset"]) + index * 8
                    )
                    if information & 0xFF == 10:
                        calls.append(symbols[information >> 8][0])
                if calls:
                    relocation_calls[target_section] = calls
            self.assertEqual(
                relocation_calls,
                {
                    private_section: [READBYTE_FUNCTION, READBYTE_FUNCTION],
                    public_section: [PRIVATE_FUNCTION],
                },
            )

    def test_candidate_license_abi_and_shared_stream_contract(self) -> None:
        self.require_source()
        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn(
            '#include "runtime_nanopb_decode_varint32.h"',
            source,
        )
        for marker in (
            "Copyright (c) 2011 Petteri Aimonen",
            "Altered source versions must be plainly marked as such",
            "altered source",
        ):
            self.assertIn(marker, source)
            self.assertIn(marker, header)
        self.assertIn('#include "runtime_nanopb_decode_varint.h"', header)
        self.assertNotIn("struct open_cfw_nanopb_istream {", header)
        self.assertNotIn("struct open_cfw_nanopb_istream {", source)
        shared = SHARED_STREAM_HEADER.read_text(encoding="utf-8")
        self.assertEqual(shared.count("struct open_cfw_nanopb_istream {"), 1)
        self.assertIn(
            f"bool {PRIVATE_FUNCTION}(\n    struct open_cfw_nanopb_istream *stream,\n    uint32_t *destination,\n    bool *eof\n);",
            header,
        )
        self.assertIn(
            f"bool {PUBLIC_FUNCTION}(\n    struct open_cfw_nanopb_istream *stream,\n    uint32_t *destination\n);",
            header,
        )
        self.assertIn(READBYTE_FUNCTION, source)
        self.assertIn(PRIVATE_FUNCTION, source)
        self.assertIn(PUBLIC_FUNCTION, source)
        self.assertIn(
            f"return {PRIVATE_FUNCTION}(\n        stream, destination, NULL\n    );",
            source,
        )
        self.assertNotIn("uint_fast", source)
        self.assertTrue(AUDIT.is_file())
        audit = AUDIT.read_text(encoding="utf-8")
        self.assertIn("production-source audit", audit)
        self.assertIn("independently", audit)
        self.assertIn("current Apple production", audit)
        self.assertIn("[0x0048F4B8,0x0048F5AE)", audit)
        self.assertIn("[0x0048F5AE,0x0048F5B8)", audit)
        self.assertIn("not proof", audit.lower())

    def test_deterministic_profile_object_and_complete_section_closure(self) -> None:
        self.require_source()
        for path, pin in FILE_PINS.items():
            self.assertIsNotNone(pin, f"unrecorded file pin: {path.relative_to(ROOT)}")
            assert pin is not None
            self.assertEqual((path.stat().st_size, sha256(path)), pin)
        self.assertIsNotNone(PROFILE_PINS["Homebrew clang version 22.1.8"])

        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        self.assertIn(version, PROFILE_PINS)
        self.assertEqual(clang, REVIEWED_COMPILERS[version])
        pins = PROFILE_PINS[version]
        assert pins is not None

        with tempfile.TemporaryDirectory(prefix="open-cfw-varint32-objects-") as temporary:
            outputs = []
            for index in range(2):
                output = Path(temporary) / f"candidate-{index}.o"
                result = subprocess.run(
                    [
                        clang, *TARGET_FLAGS, "-include", str(HEADER),
                        "-c", str(SOURCE), "-o", str(output),
                    ],
                    cwd=ROOT, capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                outputs.append(output.read_bytes())
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual((len(outputs[0]), sha256(outputs[0])), pins["object"])

            sys.path.insert(0, str(ROOT / "tools"))
            import apollo_overlay
            data, sections = apollo_overlay.parse_elf32(Path(temporary) / "candidate-0.o")
            symbols = apollo_overlay.parse_elf32_symbols(data, sections)
            by_name = {section["name"]: section for section in sections}
            private_section_name = ".text." + PRIVATE_FUNCTION
            public_section_name = ".text." + PUBLIC_FUNCTION
            rodata_name = ".rodata.open_cfw_nanopb_varint32_overflow_error"

            for section_name, pin_name in (
                (private_section_name, "private_text"),
                (public_section_name, "public_text"),
                (rodata_name, "rodata"),
            ):
                section = by_name[section_name]
                payload = data[
                    int(section["offset"]):int(section["offset"]) + int(section["size"])
                ]
                self.assertEqual(
                    (len(payload), sha256(payload), int(section["alignment"])),
                    pins[pin_name],
                )

            defined = {symbol["name"]: symbol for symbol in symbols if symbol["name"]}
            for function, section_name in (
                (PRIVATE_FUNCTION, private_section_name),
                (PUBLIC_FUNCTION, public_section_name),
            ):
                symbol = defined[function]
                self.assertEqual(symbol["type"], 2)
                self.assertEqual(symbol["binding"], 1)
                self.assertEqual(symbol["visibility"], 0)
                self.assertEqual(symbol["section_index"], by_name[section_name]["index"])
                self.assertEqual(symbol["value"], 1)
                self.assertEqual(symbol["size"], by_name[section_name]["size"])
            undefined = sorted(
                symbol["name"] for symbol in symbols
                if symbol["name"] and symbol["section_index"] == 0
            )
            self.assertEqual(undefined, [READBYTE_FUNCTION])

            relocations: dict[str, tuple[tuple[int, int, str], ...]] = {}
            for section in sections:
                if int(section["type"]) != 9 or int(section["size"]) == 0:
                    continue
                target = sections[int(section["info"])]["name"]
                records = []
                for offset in range(
                    int(section["offset"]),
                    int(section["offset"]) + int(section["size"]),
                    8,
                ):
                    relocation_offset, information = struct.unpack_from("<II", data, offset)
                    records.append((
                        relocation_offset,
                        information & 0xFF,
                        symbols[information >> 8]["name"],
                    ))
                relocations[target] = tuple(records)
            private_exidx = ".ARM.exidx" + private_section_name
            public_exidx = ".ARM.exidx" + public_section_name
            self.assertEqual(relocations[private_section_name], pins["private_relocations"])
            self.assertEqual(relocations[public_section_name], pins["public_relocations"])
            self.assertEqual(relocations[private_exidx], ((0, 42, ""),))
            self.assertEqual(relocations[public_exidx], ((0, 42, ""),))
            self.assertEqual(
                set(relocations),
                {private_section_name, public_section_name, private_exidx, public_exidx},
            )

            for function_section, exidx_name in (
                (by_name[private_section_name], private_exidx),
                (by_name[public_section_name], public_exidx),
            ):
                exidx = by_name[exidx_name]
                payload = data[
                    int(exidx["offset"]):int(exidx["offset"]) + int(exidx["size"])
                ]
                self.assertEqual(payload, b"\0\0\0\0\1\0\0\0")
                self.assertEqual(
                    (len(payload), sha256(payload), int(exidx["alignment"])),
                    pins["exidx"],
                )
                self.assertEqual(
                    apollo_overlay.authenticated_cantunwind_companion_indexes(
                        data, sections, symbols, function_section
                    ),
                    frozenset({int(exidx["index"])}),
                )

                # The production extractor may discard only this authenticated
                # CANTUNWIND/PREL31 metadata. Reject cross-function companions,
                # personality/exception data, and extra relocation records.
                altered_sections = copy.deepcopy(sections)
                altered_sections[int(exidx["index"])]["link"] = by_name[
                    public_section_name if function_section["name"] == private_section_name
                    else private_section_name
                ]["index"]
                with self.assertRaises(apollo_overlay.BuildError):
                    apollo_overlay.authenticated_cantunwind_companion_indexes(
                        data, altered_sections, symbols, function_section
                    )
                altered_sections = copy.deepcopy(sections)
                relocation = next(
                    item for item in altered_sections
                    if item["name"] == ".rel" + exidx_name
                )
                relocation["size"] = 16
                with self.assertRaises(apollo_overlay.BuildError):
                    apollo_overlay.authenticated_cantunwind_companion_indexes(
                        data, altered_sections, symbols, function_section
                    )

            allocated = {
                section["name"]: int(section["size"])
                for section in sections
                if int(section["size"]) and int(section["flags"]) & 2
            }
            self.assertEqual(allocated, {
                private_section_name: pins["private_text"][0],
                private_exidx: pins["exidx"][0],
                public_section_name: pins["public_text"][0],
                public_exidx: pins["exidx"][0],
                rodata_name: pins["rodata"][0],
            })
            writable = [
                section["name"] for section in sections
                if int(section["size"]) and int(section["flags"]) & 3 == 3
            ]
            self.assertEqual(writable, [])

    def build_differential_library(
        self,
        output: Path,
        candidate_source: Path = SOURCE,
    ) -> None:
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        self.assertIn(version, REVIEWED_COMPILERS)
        self.assertEqual(clang, REVIEWED_COMPILERS[version])
        shared_flags = (
            ("-dynamiclib",)
            if version.startswith("Apple clang version 21.0.0")
            else ("-shared", "-fPIC")
        )
        subprocess.run(
            [
                clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                *shared_flags, "-I", str(ROOT), "-I", str(SOURCE.parent),
                "-I", str(SNAPSHOT),
                "-include", str(SNAPSHOT / "g2-config/pb_g2_options.h"),
                str(candidate_source), str(HOST_FIXTURE), str(ORACLE_FIXTURE),
                str(SNAPSHOT / "pb_common.c"), "-o", str(output),
            ],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )

    def test_differential_behavior_against_pristine_private_and_public(self) -> None:
        self.require_source()

        class Result(ctypes.Structure):
            _fields_ = [
                ("value", ctypes.c_uint32),
                ("bytes_left", ctypes.c_uint64),
                ("callback_offset", ctypes.c_uint64),
                ("consumed", ctypes.c_uint64),
                ("status", ctypes.c_uint32),
                ("calls", ctypes.c_uint32),
                ("error", ctypes.c_uint32),
                ("eof", ctypes.c_uint32),
            ]

        with tempfile.TemporaryDirectory(prefix="open-cfw-varint32-diff-") as temporary:
            library_path = Path(temporary) / "varint32.dylib"
            self.build_differential_library(library_path)
            library = ctypes.CDLL(str(library_path))
            runners = (
                library.open_cfw_test_nanopb_run_production_varint32,
                library.open_cfw_test_nanopb_run_upstream_varint32,
            )
            for runner in runners:
                runner.argtypes = [
                    ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
                    ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32,
                    ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32,
                    ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result),
                ]

            def run(
                runner: object,
                payload: bytes,
                *,
                budget: int | None = None,
                fail_call: int = 0,
                mutate_call: int = 0,
                mutated_budget: int = 0,
                sticky: int = 0,
                public: int = 0,
                initial_eof: int = 0,
                sentinel: int = 0xA5A55A5A,
            ) -> tuple[int, ...]:
                array = (ctypes.c_uint8 * max(1, len(payload)))()
                if payload:
                    array[:len(payload)] = payload
                result = Result()
                runner(
                    array, len(payload), len(payload) if budget is None else budget,
                    fail_call, mutate_call, mutated_budget, sticky, public,
                    initial_eof, sentinel, ctypes.byref(result),
                )
                return tuple(getattr(result, name) for name, _ in Result._fields_)

            cases: list[tuple[str, bytes, dict[str, int]]] = []
            for value in range(256):
                cases.append((f"one-byte-{value}", bytes([value]), {}))

            def encode(value: int) -> bytes:
                encoded = bytearray()
                while value >= 0x80:
                    encoded.append((value & 0x7F) | 0x80)
                    value >>= 7
                encoded.append(value)
                return bytes(encoded)

            boundaries = (
                0, 1, 0x7F, 0x80, 0x3FFF, 0x4000, 0x1FFFFF,
                0x200000, 0x0FFFFFFF, 0x10000000, 0x7FFFFFFF,
                0x80000000, 0xFFFFFFFF,
            )
            for value in boundaries:
                cases.append((f"boundary-{value:08x}", encode(value), {}))
            seed = 0x4832_049
            generator = random.Random(seed)
            for index in range(512):
                value = generator.getrandbits(32)
                cases.append((f"seed-{seed:x}-case-{index}-value-{value:08x}", encode(value), {}))

            # Noncanonical zero extensions and canonical negative sign extensions.
            for count in range(1, 10):
                cases.append((f"zero-extension-{count}", b"\x80" * count + b"\x00", {}))
            for count in range(5, 10):
                cases.append((f"negative-extension-{count}", b"\xff" * (count - 1) + (b"\x01" if count == 10 else b"\x7f"), {}))
            cases.extend((
                ("negative-32-ten-byte", b"\xff" * 9 + b"\x01", {}),
                ("invalid-positive-extension", b"\x80" * 5 + b"\x01", {}),
                ("invalid-negative-extension", b"\xff" * 5 + b"\x02", {}),
                ("unconditional-64-overflow", b"\xff" * 9 + b"\x81\x00", {}),
                ("sticky-eof", b"", {"sticky": 1}),
                ("sticky-io", b"\x00", {"fail_call": 1, "sticky": 1}),
                ("sticky-fifth-overflow", b"\x80\x80\x80\x80\x10", {"sticky": 1}),
                ("sticky-extension-overflow", b"\x80" * 5 + b"\x01", {"sticky": 1}),
                ("sticky-64-overflow", b"\xff" * 9 + b"\x81\x00", {"sticky": 1}),
                ("long-continuation-300", LONG_CONTINUATION_PAYLOAD, {}),
                ("sticky-long-continuation-300", LONG_CONTINUATION_PAYLOAD, {"sticky": 1}),
            ))

            # Exhaust the fifth-byte high-nibble rule for both terminal and continued forms.
            for byte in range(256):
                cases.append((f"fifth-byte-{byte:02x}", b"\x80\x80\x80\x80" + bytes([byte]), {}))

            # Every truncation and independently shortened budget/callback failure.
            long_valid = b"\xff" * 9 + b"\x01"
            for stop in range(len(long_valid)):
                cases.append((f"truncate-{stop}", long_valid[:stop], {}))
                cases.append((f"budget-{stop}", long_valid, {"budget": stop}))
            for call in range(1, len(long_valid) + 1):
                cases.append((f"callback-failure-{call}", long_valid, {"fail_call": call}))
                cases.append((f"callback-budget-mutation-{call}", long_valid, {"mutate_call": call, "mutated_budget": call & 1}))

            for public in (0, 1):
                for initial_eof in (0, 1):
                    for name, payload, kwargs in cases:
                        with self.subTest(name=name, public=public, initial_eof=initial_eof):
                            parameters = dict(kwargs)
                            parameters.update(public=public, initial_eof=initial_eof)
                            candidate = run(runners[0], payload, **parameters)
                            upstream = run(runners[1], payload, **parameters)
                            self.assertEqual(candidate, upstream, f"seed={seed:#x} case={name}")

            # Handwritten expectations prevent a mutually wrong differential harness.
            self.assertEqual(run(runners[0], b"\x00")[:7], (0, 0, 1, 1, 1, 1, 0))
            self.assertEqual(run(runners[0], b"", initial_eof=0), (
                0xA5A55A5A, 0, 0, 0, 0, 0, 1, 1,
            ))
            self.assertEqual(run(runners[0], b"\x80", fail_call=1), (
                0xA5A55A5A, 1, 0, 0, 0, 1, 2, 0,
            ))
            self.assertEqual(run(runners[0], b"\x80", sticky=1), (
                0xA5A55A5A, 0, 1, 1, 0, 1, 4, 0,
            ))
            overflow = run(runners[0], b"\x80\x80\x80\x80\x10")
            self.assertEqual(overflow, (0xA5A55A5A, 0, 5, 5, 0, 5, 3, 0))
            sticky_overflow = run(
                runners[0], b"\x80\x80\x80\x80\x10", sticky=1
            )
            self.assertEqual(sticky_overflow[6], 4)
            for payload in (
                b"", b"\x00", b"\x80\x80\x80\x80\x10",
                b"\x80" * 5 + b"\x01", b"\xff" * 9 + b"\x81\x00",
            ):
                parameters = {"sticky": 1}
                if payload == b"\x00":
                    parameters["fail_call"] = 1
                self.assertEqual(run(runners[0], payload, **parameters)[6], 4)
            for byte in range(256):
                result = run(
                    runners[0], b"\x80\x80\x80\x80" + bytes([byte])
                )
                accepted_nibble = (byte & 0x70) == 0 or (byte & 0x78) == 0x78
                if not accepted_nibble:
                    self.assertEqual((result[4], result[6]), (0, 3), f"fifth={byte:#x}")
                elif byte & 0x80:
                    self.assertEqual((result[4], result[6]), (0, 1), f"fifth={byte:#x}")
                else:
                    self.assertEqual((result[4], result[6]), (1, 0), f"fifth={byte:#x}")
            self.assertEqual(run(runners[0], b"\x96\x01", public=1), (
                150, 0, 2, 2, 1, 2, 0, 0,
            ))

            for public in (0, 1):
                for initial_eof in (0, 1):
                    for sticky, expected_error in ((0, 3), (1, 4)):
                        self.assertEqual(
                            run(
                                runners[0], LONG_CONTINUATION_PAYLOAD,
                                public=public, initial_eof=initial_eof,
                                sticky=sticky,
                            ),
                            (
                                0xA5A55A5A,
                                len(LONG_CONTINUATION_PAYLOAD) - 11,
                                11,
                                11,
                                0,
                                11,
                                expected_error,
                                initial_eof,
                            ),
                        )

    def test_long_continuation_guard_is_non_vacuously_qualified(self) -> None:
        self.assertGreaterEqual(len(LONG_CONTINUATION_PAYLOAD), 301)
        source = SOURCE.read_text(encoding="utf-8")
        guard = "if (bit_position >= 64U || !valid_extension) {"
        self.assertEqual(source.count(guard), 1)

        class Result(ctypes.Structure):
            _fields_ = [
                ("value", ctypes.c_uint32),
                ("bytes_left", ctypes.c_uint64),
                ("callback_offset", ctypes.c_uint64),
                ("consumed", ctypes.c_uint64),
                ("status", ctypes.c_uint32),
                ("calls", ctypes.c_uint32),
                ("error", ctypes.c_uint32),
                ("eof", ctypes.c_uint32),
            ]

        with tempfile.TemporaryDirectory(prefix="open-cfw-varint32-mutant-") as temporary:
            temporary_path = Path(temporary)
            mutant = temporary_path / SOURCE.name
            mutant.write_text(
                source.replace(guard, "if (!valid_extension) {"),
                encoding="utf-8",
            )
            library_path = temporary_path / "varint32-mutant.dylib"
            self.build_differential_library(library_path, mutant)
            library = ctypes.CDLL(str(library_path))
            runner = library.open_cfw_test_nanopb_run_production_varint32
            runner.argtypes = [
                ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
                ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32,
                ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32,
                ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result),
            ]
            payload = (ctypes.c_uint8 * len(LONG_CONTINUATION_PAYLOAD))(
                *LONG_CONTINUATION_PAYLOAD
            )
            output = Result()
            runner(
                payload,
                len(LONG_CONTINUATION_PAYLOAD),
                len(LONG_CONTINUATION_PAYLOAD),
                0, 0, 0, 0, 0, 1, 0xA5A55A5A,
                ctypes.byref(output),
            )
            expected = (
                0xA5A55A5A,
                len(LONG_CONTINUATION_PAYLOAD) - 11,
                11, 11, 0, 11, 3, 1,
            )
            observed = tuple(
                getattr(output, name) for name, _ in Result._fields_
            )
            self.assertEqual(
                observed,
                (0, 0, 301, 301, 1, 301, 0, 1),
            )
            self.assertNotEqual(observed, expected)
            self.assertGreater(output.calls, 11)


if __name__ == "__main__":
    unittest.main()
