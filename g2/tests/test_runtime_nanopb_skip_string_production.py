#!/usr/bin/env python3
"""Production contract and retained candidate evidence for nanopb skip-string."""

from __future__ import annotations

import ctypes
import copy
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
CANDIDATE_SOURCE = (
    ROOT / "components/shared/nanopb"
    / "runtime_nanopb_skip_string_candidate.c"
)
CANDIDATE_HEADER = CANDIDATE_SOURCE.with_suffix(".h")
PRODUCTION_SOURCE = (
    ROOT / "components/shared/nanopb"
    / "runtime_nanopb_skip_string.c"
)
PRODUCTION_HEADER = PRODUCTION_SOURCE.with_suffix(".h")
PRODUCTION_SOURCE_PATH = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
PRODUCTION_HEADER_PATH = PRODUCTION_HEADER.relative_to(ROOT).as_posix()
FIXTURE = (
    ROOT / "tests/fixtures"
    / "runtime_nanopb_skip_string_production_host.c"
)
AUDIT = (
    ROOT / "docs/research"
    / "nanopb-skip-string-source-audit.md"
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
BOOT_PIN = (
    148_599,
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5",
)
STOCK_SPAN = (0x0048_F64C, 0x0048_F66C)
STOCK_HEX = (
    "1cb5040069462000fff7abff002801d1002004e0009a00212000fff7aafe16bd"
)
STOCK_SHA256 = (
    "03afe2d60436676fffba342c7b8c9504992fa903d7cba768396fd1de2c6c66cd"
)
PREDECESSOR_SPAN = (0x0048_F628, 0x0048_F64C)
PREDECESSOR_SHA256 = (
    "fae83b1a62a07bb9c7a3d3f6c398bc13433ebe1cd75d01945f83f30e6fcc9c5d"
)
PREDECESSOR_COMPONENT_SHA256 = {
    "apple-clang": (
        "ec17aa0a8e01050d8b30f737e7ca83d4b8842da1d7d33f6b3b74fa199a4f4519"
    ),
    "linux-clang": (
        "f54c433a31f74f74b34709901da696d850b4dd2d0fb743b8166d49256c287303"
    ),
}
SUCCESSOR_SPAN = (0x0048_F66C, 0x0048_F6A0)
SUCCESSOR_SHA256 = (
    "727a94d16ba7b4018c3addee83a6c63e87f0c3f2a3fe6afdb315549d10f53114"
)
PRODUCTION_SUCCESSOR_SHA256 = (
    "3add701f3a3b3fc2740ce96a24ee891fb11560b87be2c7f3542598ce3a1567d2"
)
CALLERS = (0x0048_F6C6,)
CALLER_ENCODING = bytes.fromhex("fff7c1ff")
CALLER_SPAN = (0x0048_F6A0, 0x0048_F6EA)
CALLER_SPAN_SHA256 = (
    "36089daffbbc82abad65d97ae0fd64b58b8ad227ed585aa704611bc30369912d"
)
OUTGOING = (
    (0x0048_F654, 0x0048_F5AE),
    (0x0048_F666, 0x0048_F3BE),
)
UPSTREAM_DEFINITION = (
    8362,
    8661,
    "8da14b4cc741fc15884b11d3447d0c2c529f65c31b3823170837229d36f81585",
)
POINT_RELEASE_DEFINITIONS = {
    "0.4.7": (
        "b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba", 8276, 8575,
        UPSTREAM_DEFINITION[2],
    ),
    "0.4.8": (
        "6cfe48d6f1593f8fa5c0f90437f5e6522587745e", 8276, 8575,
        UPSTREAM_DEFINITION[2],
    ),
    "0.4.9": (
        "98bf4db69897b53434f3d0ba72e0a3ab1a902824", 8362, 8661,
        UPSTREAM_DEFINITION[2],
    ),
}
PROMOTION_BASE = "7e78e38e4401bc095cca266e8708249f6da47780"


def _promotion_history_available() -> bool:
    try:
        completed = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--verify",
             f"{PROMOTION_BASE}^{{commit}}"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


PROMOTION_HISTORY_AVAILABLE = _promotion_history_available()
PROMOTION_HISTORY_SKIP_REASON = (
    "promotion-base revision is unavailable from Git history in this checkout"
)

HISTORICAL_CANDIDATE_PINS = {
    CANDIDATE_SOURCE.relative_to(ROOT).as_posix(): {
        "blob": "c9113221c6f392f48d11e4079876cb5ecb4f2311",
        "size": 1662,
        "sha256": (
            "28d3ec9e4e58f583ed19a0eee08247f5bc5df8c8c01dff418363eaa173b9ac24"
        ),
    },
    CANDIDATE_HEADER.relative_to(ROOT).as_posix(): {
        "blob": "8d3f4901fbaf62c245b34e3bffc9b0564bfe45f9",
        "size": 2023,
        "sha256": (
            "470e84bab1ba1d78630d198f023e28444f6d3ac658e041df23d85425918180e7"
        ),
    },
    "docs/research/nanopb-skip-string-source-candidate-audit.md": {
        "blob": "82cf5bb4ebdb45850937ea5745558f4840960d15",
        "size": 3593,
        "sha256": (
            "682921398e278ba864e394b371bcf75d59b405bbd2d4ebad95028272551220ff"
        ),
    },
}
LOCAL_PINS = {
    FIXTURE: (
        12_432,
        "6e8e22305255a50b93d6d34bf64d0588dc4704ac8a3b60a11dd137c2e5c48e29",
    ),
    AUDIT: (
        6632,
        "e1465b8f8fc220907f811df2c354e91a2e1a4e7149edeb4c56ffa7d94246e2ee",
    ),
}
CANDIDATE_FUNCTION = "open_cfw_nanopb_skip_string_source_candidate"
CANDIDATE_DECODE_SEAM = "open_cfw_nanopb_decode_varint32_stock_candidate"
PRODUCTION_FUNCTION = "open_cfw_nanopb_skip_string"
PRODUCTION_DECODE_PROVIDER = "open_cfw_nanopb_decode_varint32"
READ_PROVIDER = "open_cfw_nanopb_read"
PATCH_NAME = "replace_nanopb_skip_string"
CANDIDATE_SECTION = ".text." + CANDIDATE_FUNCTION
PRODUCTION_SECTION = ".text." + PRODUCTION_FUNCTION
PRODUCTION_EXIDX_SECTION = ".ARM.exidx" + PRODUCTION_SECTION
PRODUCTION_EXIDX = bytes.fromhex("0000000001000000")
OVERLAY_RUNTIME_ADDRESS = 0x0079_4324
BASE_FUNCTION_COUNT = 948
BASE_RELOCATED_COUNT = 379
BASE_PATCH_COUNT = 887
APPLE_CLANG = "/usr/bin/clang"
COMPILER_PROFILES = {
    "apple-clang": {
        "compiler": APPLE_CLANG,
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (
            1044,
            "f059f1c161bb602413d0505e51f6253283bf589622159c0fe4ee4202153e2b72",
        ),
        "text": (
            34,
            "d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920",
        ),
        "relocations": {
            CANDIDATE_SECTION: [
                (8, 10, CANDIDATE_DECODE_SEAM),
                (20, 10, READ_PROVIDER),
            ],
            ".ARM.exidx" + CANDIDATE_SECTION: [(0, 42, "")],
        },
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "object": (
            1044,
            "f059f1c161bb602413d0505e51f6253283bf589622159c0fe4ee4202153e2b72",
        ),
        "text": (
            34,
            "d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920",
        ),
        "relocations": {
            CANDIDATE_SECTION: [
                (8, 10, CANDIDATE_DECODE_SEAM),
                (20, 10, READ_PROVIDER),
            ],
            ".ARM.exidx" + CANDIDATE_SECTION: [(0, 42, "")],
        },
    },
}
TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-fno-ident",
)
PRODUCTION_TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-fno-ident",
)
PROJECTED_PRODUCTION_PROFILES = {
    "apple-clang": {
        "offset": 125_224,
        "relocated_sha256": (
            "3b1a0dbe465d562770e02d5afe04357087a6bfee22342a0f6844986a0161f547"
        ),
        "replacement_sha256": (
            "86ba480676461c25f262f93c3d1cc0e0e6080e6c44c367a261e1ac857ce81c3d"
        ),
    },
    "linux-clang": {
        "offset": 127_048,
        "relocated_sha256": (
            "3b1a0dbe465d562770e02d5afe04357087a6bfee22342a0f6844986a0161f547"
        ),
        "replacement_sha256": (
            "738d3ad448d28a408c0aaa76f7c7188181966ac44bc22afe675bde4fd83a9f7d"
        ),
    },
}
PRODUCTION_BUILD_PROFILES = {
    "apple-clang": {
        "boot_component": (
            149_262,
            "695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267",
        ),
        "main_component": (
            3_690_822,
            "9ed3e77e10dd911ae34e9ba17f691f6988c592723b52a9676b8d414554a21459",
        ),
        "package_artifacts": {
            "package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin": (
                4_469_316,
                "d4c7f82a3e0cfbfc4476f8ca72c1bfd6a3aba5b13d32c6b924686cbc4d78c10d",
            ),
            "build-report.json": (
                2_323,
                "61f0710b2087e55b5849ea254521b9b65c7b7d81ddaaa645803b59eaaa3475b7",
            ),
            "flash-plan.json": (
                1_337_744,
                "642d39802f988c3da5e108c97fdcff82102cfcdfffd75710bd6e0a3017f7758e",
            ),
        },
        "census": (1_822, 2, 5),
        "effective_ownership": (165_946, 121_587, 4_179_797),
    },
    "linux-clang": {
        "boot_component": (
            149_262,
            "fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74",
        ),
        "main_component": (
            3_668_604,
            "378c868e151060a59ab91b0de1a722e8678b8e1da8eede248c5702ccf8902798",
        ),
        "package_artifacts": {
            "package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin": (
                4_447_098,
                "deb4cdb9d869abcb3aee5e122661ee45b541680cf277df5d1a7c6eed67bb7b6e",
            ),
            "build-report.json": (
                2_322,
                "68688074ccfefc2c4fc89ada5fc7bf2f2a2646511e72c87c9fd0696d7326dbb0",
            ),
            "flash-plan.json": (
                644_890,
                "c80cee3329298de9df6b5d23a7feb955a81c0b1fbb7345411263eae067024b72",
            ),
        },
        "census": (903, 2, 5),
        "effective_ownership": (133_769, 93_278, 4_207_731),
    },
}

# These pins deliberately remain unrecorded in the Task 1 RED. Task 2 replaces
# them only after two independent deterministic production compilations.
PRODUCTION_LOCAL_PINS: dict[Path, tuple[int, str] | None] = {
    PRODUCTION_SOURCE: (
        1688,
        "b1f492b0358e51ce89db622e4af13a7f1eef7ffce9fc81fd954609cdcd934876",
    ),
    PRODUCTION_HEADER: (
        1732,
        "807fb52ae19de372024ebea64268aca011e573e9ad6d4247e911b2e037058303",
    ),
}
PRODUCTION_PROFILE_PINS: dict[str, dict[str, tuple[int, str] | None]] = {
    "apple-clang": {
        "object": (
            988,
            "d2bdca5570c8e7a0ee1adfc9decfb3ad54f6c77abe7c7e3f05e0e3dd9f1c5bbe",
        ),
        "text": (
            34,
            "d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920",
        ),
    },
    "linux-clang": {
        "object": (
            988,
            "d2bdca5570c8e7a0ee1adfc9decfb3ad54f6c77abe7c7e3f05e0e3dd9f1c5bbe",
        ),
        "text": (
            34,
            "d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920",
        ),
    },
}

# Task 1 authors these cases without discovering or executing them. Task 3 must
# first build an unmodified positive control, then activate each record against
# a deep-copied configuration or temporary source fixture.
OVERLAY_MUTATION_RECORDS = (
    ("partial_patch_size_4", "skip-string patch must cover exactly 32 bytes", "config"),
    ("patch_branch_bl", "skip-string patch must use non-linking b_w", "config"),
    ("fixed_decode_target_address", "decode provider must use target_function", "config"),
    ("fixed_read_target_address", "read provider must use target_function", "config"),
    ("providers_swapped", "skip-string provider order differs", "config"),
    ("decode_call_omitted", "skip-string relocation closure differs", "config"),
    ("extra_undefined_symbol", "unexpected undefined symbol", "source"),
    ("shifted_stock_span", "skip-string stock span differs", "config"),
    ("concatenated_neighbor_hash", "skip-string stock hash differs", "config"),
    ("leaf_without_patch", "missing skip-string patch", "config"),
    ("patch_without_leaf", "missing skip-string relocated leaf", "config"),
    ("writable_allocated_section", "unexpected writable allocated section", "source"),
    ("size_too_large_rodata", "unexpected skip-string rodata closure", "source"),
    ("unreviewed_compiler_profile", "unreviewed target compiler", "profile"),
)


class SkipStringIntegrationResult(ctypes.Structure):
    _fields_ = [
        ("bytes_left", ctypes.c_uint64),
        ("consumed", ctypes.c_uint64),
        ("callback_offset", ctypes.c_uint64),
        ("counts", ctypes.c_uint64 * 16),
        ("status", ctypes.c_uint32),
        ("calls", ctypes.c_uint32),
        ("error", ctypes.c_uint32),
        ("state_unchanged", ctypes.c_uint32),
        ("null_calls", ctypes.c_uint32),
    ]

    def comparable(self) -> tuple[object, ...]:
        return (
            self.status,
            self.bytes_left,
            self.consumed,
            self.callback_offset,
            self.calls,
            tuple(self.counts),
            self.error,
            self.state_unchanged,
            self.null_calls,
        )


def production_overlay_records(
    config: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    leaves = [
        item for item in config["relocated_leaves"]
        if item.get("function") == PRODUCTION_FUNCTION
    ]
    patches = [
        item for item in config["patch_sites"]
        if item.get("name") == PATCH_NAME
    ]
    if len(leaves) != 1 or len(patches) != 1:
        raise AssertionError("production skip-string records are not unique")
    return leaves[0], patches[0]


def active_leaf_profile_record(
    leaf: dict[str, object], profile: str,
) -> dict[str, object] | None:
    """Return the selected non-canonical leaf profile, failing closed."""

    if profile == "apple-clang":
        return None
    profiles = leaf.get("toolchain_profiles")
    if not isinstance(profiles, dict):
        raise AssertionError("production leaf toolchain_profiles are missing")
    selected = profiles.get(profile)
    if not isinstance(selected, dict):
        raise AssertionError(
            f"production leaf profile {profile!r} is missing or invalid"
        )
    return selected


def active_leaf_field_owner(
    leaf: dict[str, object], profile: str, field: str,
) -> dict[str, object]:
    """Return the record whose value survives leaf-profile resolution."""

    selected = active_leaf_profile_record(leaf, profile)
    if selected is not None and field in selected:
        return selected
    return leaf


def active_leaf_relocations(
    leaf: dict[str, object], profile: str,
) -> list[dict[str, object]]:
    owner = active_leaf_field_owner(leaf, profile, "relocations")
    relocations = owner.get("relocations")
    if not isinstance(relocations, list) or not all(
        isinstance(item, dict) for item in relocations
    ):
        raise AssertionError("production leaf relocations are missing or invalid")
    return relocations


def active_leaf_expected(
    leaf: dict[str, object], profile: str,
) -> dict[str, object]:
    owner = active_leaf_field_owner(leaf, profile, "expected")
    expected = owner.get("expected")
    if not isinstance(expected, dict):
        raise AssertionError("production leaf expected pins are missing or invalid")
    return expected


def active_leaf_toolchain_field_owner(
    leaf: dict[str, object], profile: str, field: str,
) -> dict[str, object]:
    """Return the active owner of one effective toolchain field."""

    selected = active_leaf_profile_record(leaf, profile)
    if selected is not None and field in selected:
        return selected
    toolchain = leaf.get("toolchain")
    if not isinstance(toolchain, dict):
        raise AssertionError("production leaf toolchain is missing or invalid")
    return toolchain


def active_leaf_reviewed_compiler_field(
    leaf: dict[str, object], profile: str,
) -> tuple[dict[str, object], str]:
    """Locate the effective exact-version or version-prefix compiler pin."""

    selected = active_leaf_profile_record(leaf, profile)
    for owner in (selected, leaf.get("toolchain")):
        if owner is None:
            continue
        if not isinstance(owner, dict):
            raise AssertionError("production leaf toolchain is invalid")
        fields = [
            field for field in (
                "reviewed_version", "reviewed_version_prefix",
            )
            if field in owner
        ]
        if len(fields) > 1:
            raise AssertionError("production compiler pin is ambiguous")
        if fields:
            return owner, fields[0]
    raise AssertionError("production compiler pin is missing")


def clear_active_overlay_expected(
    config: dict[str, object], profile: str,
) -> None:
    """Disable aggregate pins in both canonical and selected profile records."""

    config["expected"] = {}
    if profile == "apple-clang":
        return
    profiles = config.get("toolchain_profiles")
    if not isinstance(profiles, dict):
        raise AssertionError("overlay toolchain_profiles are missing")
    selected = profiles.get(profile)
    if not isinstance(selected, dict):
        raise AssertionError(
            f"overlay profile {profile!r} is missing or invalid"
        )
    selected["expected"] = {}


def apply_overlay_mutation(
    original: dict[str, object], name: str, *, profile: str = "apple-clang",
) -> dict[str, object]:
    """Return one late-bound Task 3 mutation of a valid production config."""

    config = copy.deepcopy(original)
    leaf, patch = production_overlay_records(config)
    relocations = active_leaf_relocations(leaf, profile)

    if name == "partial_patch_size_4":
        patch["expected_size"] = 4
        patch["expected_sha256"] = sha256(bytes.fromhex(STOCK_HEX)[:4])
    elif name == "patch_branch_bl":
        patch["branch"] = "bl"
    elif name in ("fixed_decode_target_address", "fixed_read_target_address"):
        index = 0 if name.startswith("fixed_decode") else 1
        relocation = relocations[index]
        relocation.pop("target_function", None)
        relocation["target_address"] = 0x0048_F5AE if index == 0 else 0x0048_F3BE
    elif name == "providers_swapped":
        providers = (READ_PROVIDER, PRODUCTION_DECODE_PROVIDER)
        for relocation, provider in zip(relocations, providers):
            relocation["symbol"] = provider
            relocation["target_function"] = provider
    elif name == "decode_call_omitted":
        del relocations[0]
    elif name == "shifted_stock_span":
        application = OFFICIAL.read_bytes()[PACKAGE_PREAMBLE:]
        start, end = STOCK_SPAN
        shifted = application[
            start + 2 - APPLICATION_BASE:end - APPLICATION_BASE
        ]
        patch["runtime_address"] = start + 2
        patch["expected_size"] = len(shifted)
        patch["expected_sha256"] = sha256(shifted)
    elif name == "concatenated_neighbor_hash":
        application = OFFICIAL.read_bytes()[PACKAGE_PREAMBLE:]
        start = STOCK_SPAN[0]
        end = SUCCESSOR_SPAN[1]
        concatenated = application[start - APPLICATION_BASE:end - APPLICATION_BASE]
        patch["expected_sha256"] = sha256(concatenated)
    elif name == "leaf_without_patch":
        config["patch_sites"].remove(patch)
    elif name == "patch_without_leaf":
        config["relocated_leaves"].remove(leaf)
        config["functions"].remove(PRODUCTION_FUNCTION)
    else:
        raise KeyError(
            f"{name} needs a Task 3 temporary source/profile fixture"
        )
    return config


def validate_skip_string_task3_preflight(
    config: dict[str, object],
    *,
    source_bytes: bytes | None = None,
    header_bytes: bytes | None = None,
) -> None:
    """Reject skip-string-specific mutations before the general builder."""

    source_bytes = (
        PRODUCTION_SOURCE.read_bytes() if source_bytes is None else source_bytes
    )
    header_bytes = (
        PRODUCTION_HEADER.read_bytes() if header_bytes is None else header_bytes
    )
    source_pin = PRODUCTION_LOCAL_PINS[PRODUCTION_SOURCE]
    header_pin = PRODUCTION_LOCAL_PINS[PRODUCTION_HEADER]
    if source_pin is None or (len(source_bytes), sha256(source_bytes)) != source_pin:
        raise AssertionError("production source SHA-256 differs")
    if header_pin is None or (len(header_bytes), sha256(header_bytes)) != header_pin:
        raise AssertionError("production header SHA-256 differs")

    leaves = [
        item for item in config["relocated_leaves"]
        if item.get("function") == PRODUCTION_FUNCTION
    ]
    patches = [
        item for item in config["patch_sites"]
        if item.get("name") == PATCH_NAME
    ]
    if not leaves:
        raise AssertionError("missing skip-string relocated leaf")
    if not patches:
        raise AssertionError("missing skip-string patch")
    if len(leaves) != 1 or len(patches) != 1:
        raise AssertionError("production skip-string records are not unique")
    leaf, patch = leaves[0], patches[0]

    if leaf.get("source", {}).get("path") != PRODUCTION_SOURCE_PATH:
        raise AssertionError("skip-string production source path differs")
    if (
        leaf.get("source", {}).get("size"),
        leaf.get("source", {}).get("sha256"),
    ) != source_pin:
        raise AssertionError("skip-string production source pin differs")
    if leaf.get("strict_relocation_contract") is not True:
        raise AssertionError("skip-string strict relocation contract is required")

    relocations = leaf.get("relocations")
    expected_providers = (PRODUCTION_DECODE_PROVIDER, READ_PROVIDER)
    if not isinstance(relocations, list) or len(relocations) != 2:
        raise AssertionError("skip-string relocation closure differs")
    observed_providers = tuple(
        item.get("target_function") for item in relocations
    )
    if observed_providers != expected_providers:
        if observed_providers == tuple(reversed(expected_providers)):
            raise AssertionError("skip-string provider order differs")
        if relocations[0].get("target_function") is None:
            raise AssertionError("decode provider must use target_function")
        if relocations[1].get("target_function") is None:
            raise AssertionError("read provider must use target_function")
        raise AssertionError("skip-string provider identity differs")
    expected_relocations = (
        (8, "R_ARM_THM_CALL", PRODUCTION_DECODE_PROVIDER, "STT_NOTYPE"),
        (20, "R_ARM_THM_CALL", READ_PROVIDER, "STT_NOTYPE"),
    )
    observed_relocations = tuple(
        (
            item.get("offset"),
            item.get("type"),
            item.get("symbol"),
            item.get("symbol_type"),
        )
        for item in relocations
    )
    if observed_relocations != expected_relocations:
        raise AssertionError("skip-string relocation closure differs")
    if any("target_address" in item for item in relocations):
        raise AssertionError("skip-string dependencies cannot use target_address")

    if patch.get("runtime_address") != STOCK_SPAN[0]:
        raise AssertionError("skip-string stock span differs")
    if patch.get("expected_size") != STOCK_SPAN[1] - STOCK_SPAN[0]:
        raise AssertionError("skip-string patch must cover exactly 32 bytes")
    if patch.get("expected_sha256") != STOCK_SHA256:
        raise AssertionError("skip-string stock hash differs")
    if patch.get("branch") != "b_w":
        raise AssertionError("skip-string patch must use non-linking b_w")
    if patch.get("target_function") != PRODUCTION_FUNCTION:
        raise AssertionError("skip-string patch target differs")

    leaf_functions = [item.get("function") for item in config["relocated_leaves"]]
    leaf_index = leaf_functions.index(PRODUCTION_FUNCTION)
    if leaf_index == 0 or leaf_functions[leaf_index - 1] != (
        PRODUCTION_DECODE_PROVIDER
    ):
        raise AssertionError("skip-string relocated tail order differs")
    patch_names = [item.get("name") for item in config["patch_sites"]]
    if not (
        patch_names.index("replace_nanopb_decode_varint32")
        < patch_names.index(PATCH_NAME)
        < patch_names.index("replace_cmbacktrace_get_cur_thread_name")
    ):
        raise AssertionError("skip-string patch order differs")

    patch_spans = []
    for item in config["patch_sites"]:
        start = item.get("runtime_address")
        size = item.get("expected_size")
        expected_hex = item.get("expected_hex")
        if isinstance(expected_hex, str):
            try:
                size = len(bytes.fromhex(expected_hex))
            except ValueError:
                continue
        if isinstance(start, int) and isinstance(size, int) and size > 0:
            patch_spans.append((start, start + size, item.get("name")))
    for index, (start, end, name) in enumerate(patch_spans):
        for other_start, other_end, other_name in patch_spans[index + 1:]:
            if start < other_end and other_start < end:
                raise AssertionError(
                    f"patch overlap: {name} and {other_name}"
                )


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


def historical_git_bytes(arguments: tuple[str, ...], label: str) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(ROOT), *arguments],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AssertionError(f"{label} is unavailable from Git history") from exc
    if completed.returncode != 0:
        raise AssertionError(f"{label} is unavailable from Git history")
    return completed.stdout


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


class StableUnittestIdentityCase(unittest.TestCase):
    """Keep RED evidence identities stable across reviewed Python versions."""

    def __str__(self) -> str:
        return (
            f"{self._testMethodName} "
            f"({self.__class__.__module__}.{self.__class__.__qualname__})"
        )


class NanopbSkipStringCandidateTests(unittest.TestCase):
    """Retain candidate evidence while qualifying its renamed production form."""

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
            prefix="open-cfw-nanopb-skip-string-historical-candidate-"
        )
        temporary = Path(cls.temporary.name)
        cls.objects = [temporary / "production-a.o", temporary / "production-b.o"]
        for output in cls.objects:
            subprocess.run(
                [
                    cls.clang, *PRODUCTION_TARGET_FLAGS, "-c",
                    str(PRODUCTION_SOURCE), "-o", str(output),
                ],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )

        library = temporary / (
            "skip-string.dylib" if sys.platform == "darwin" else "skip-string.so"
        )
        command = [
            cls.clang, "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT), "-I", str(SNAPSHOT), "-include", str(CONFIG),
            "-DOPENCFW_SKIP_STRING_CANDIDATE_ORACLE=1",
            str(PRODUCTION_SOURCE), str(FIXTURE), str(UPSTREAM),
            str(SNAPSHOT / "pb_common.c"),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        cls.host_test = cls.library.open_cfw_test_nanopb_skip_string_candidate
        cls.host_test.argtypes = []
        cls.host_test.restype = ctypes.c_int

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        import analyze_g2_nanopb_point_release
        cls.apollo_overlay = apollo_overlay
        cls.release_audit = analyze_g2_nanopb_point_release
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @unittest.skipUnless(PROMOTION_HISTORY_AVAILABLE, PROMOTION_HISTORY_SKIP_REASON)
    def test_authenticated_upstream_and_local_files_are_exact(self) -> None:
        for path, expected in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual((path.stat().st_size, sha256(path)), expected)
        repository_root = Path(
            historical_git_bytes(
                ("rev-parse", "--show-toplevel"),
                "historical candidate repository",
            ).decode("utf-8", errors="strict").strip()
        ).resolve()
        self.assertEqual(repository_root, ROOT.parent.resolve())
        resolved_revision = historical_git_bytes(
            ("rev-parse", "--verify", f"{PROMOTION_BASE}^{{commit}}"),
            "historical candidate revision",
        ).decode("ascii", errors="strict").strip()
        self.assertEqual(resolved_revision, PROMOTION_BASE)
        for path, record in HISTORICAL_CANDIDATE_PINS.items():
            self.assertTrue(
                "_candidate" in path or "-candidate-" in path,
                path,
            )
            git_path = (ROOT.relative_to(repository_root) / path).as_posix()
            resolved_blob = historical_git_bytes(
                ("rev-parse", f"{PROMOTION_BASE}:{git_path}"),
                f"historical candidate path {path}",
            ).decode("ascii", errors="strict").strip()
            self.assertEqual(resolved_blob, record["blob"])
            object_type = historical_git_bytes(
                ("cat-file", "-t", record["blob"]),
                f"historical candidate object {path}",
            ).decode("ascii", errors="strict").strip()
            self.assertEqual(object_type, "blob")
            content = historical_git_bytes(
                ("cat-file", "blob", record["blob"]),
                f"historical candidate blob {path}",
            )
            self.assertEqual(
                (len(content), sha256(content)),
                (record["size"], record["sha256"]),
            )
        historical_audit = AUDIT.read_text(encoding="utf-8")
        self.assertIn(CANDIDATE_FUNCTION, historical_audit)
        self.assertIn(CANDIDATE_DECODE_SEAM, historical_audit)

        start, end, digest = UPSTREAM_DEFINITION
        definition = UPSTREAM.read_bytes()[start:end]
        self.assertTrue(
            definition.startswith(
                b"bool checkreturn pb_skip_string(pb_istream_t *stream)\n{"
            )
        )
        self.assertTrue(
            definition.endswith(b"return pb_read(stream, NULL, (size_t)length);\n}")
        )
        self.assertEqual((len(definition), sha256(definition)), (299, digest))
        self.assertEqual(
            (UPSTREAM.stat().st_size, sha256(UPSTREAM)),
            (
                53_845,
                "e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a",
            ),
        )

        for release, (commit, span_start, span_end, span_digest) in (
            POINT_RELEASE_DEFINITIONS.items()
        ):
            with self.subTest(release=release):
                record = self.release_audit.UPSTREAM_RELEASES[release]
                self.assertEqual(record["commit"], commit)
                self.assertEqual(span_end - span_start, 299)
                self.assertEqual(span_digest, digest)

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["upstream"]["selected_tag"], "nanopb-0.4.9")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            POINT_RELEASE_DEFINITIONS["0.4.9"][0],
        )

    def test_candidate_is_absent_from_every_production_registration(self) -> None:
        source_path = CANDIDATE_SOURCE.relative_to(ROOT).as_posix()
        for path in (OVERLAY, MANIFEST, MAKEFILE, PROVENANCE, VERIFIER):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(source_path, text, path)
            self.assertNotIn(CANDIDATE_FUNCTION, text, path)
            self.assertNotIn(CANDIDATE_DECODE_SEAM, text, path)
        self.assertTrue(CANDIDATE_SOURCE.name.endswith("_candidate.c"))
        self.assertTrue(CANDIDATE_HEADER.name.endswith("_candidate.h"))
        self.assertFalse(CANDIDATE_SOURCE.exists())
        self.assertFalse(CANDIDATE_HEADER.exists())

    def test_stock_body_single_caller_and_complete_outgoing_closure(self) -> None:
        self.assertEqual((len(self.package), sha256(self.package)), PACKAGE_PIN)
        start, end = STOCK_SPAN
        body = self.application[start - APPLICATION_BASE:end - APPLICATION_BASE]
        self.assertEqual(body.hex(), STOCK_HEX)
        self.assertEqual(sha256(body), STOCK_SHA256)
        for span, digest in (
            (PREDECESSOR_SPAN, PREDECESSOR_SHA256),
            (SUCCESSOR_SPAN, SUCCESSOR_SHA256),
            (CALLER_SPAN, CALLER_SPAN_SHA256),
        ):
            adjacent = self.application[
                span[0] - APPLICATION_BASE:span[1] - APPLICATION_BASE
            ]
            self.assertEqual(sha256(adjacent), digest)
        caller_offset = CALLERS[0] - APPLICATION_BASE
        self.assertEqual(
            self.application[caller_offset:caller_offset + 4],
            CALLER_ENCODING,
        )

        ingress = {"bl": [], "bw": [], "conditional": [], "narrow": []}
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            for name, target in (
                ("bl", wide_branch_target(address, first, second, link=True)),
                ("bw", wide_branch_target(address, first, second, link=False)),
                ("conditional", wide_conditional_target(address, first, second)),
            ):
                if target is not None and start <= target < end:
                    ingress[name].append((address, target))
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            if start <= address < end:
                continue
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_targets(address, halfword):
                if start <= target < end:
                    ingress["narrow"].append((address, target))
        self.assertEqual(ingress["bl"], [(CALLERS[0], start)])
        self.assertEqual(ingress["bw"], [])
        self.assertEqual(ingress["conditional"], [])
        self.assertEqual(ingress["narrow"], [])

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
        self.assertEqual(tuple(outgoing), OUTGOING)

    def test_target_abi_removes_only_tautological_upstream_guard(self) -> None:
        source = PRODUCTION_SOURCE.read_text(encoding="utf-8")
        header = PRODUCTION_HEADER.read_text(encoding="utf-8")
        self.assertIn(PRODUCTION_DECODE_PROVIDER, source)
        self.assertIn("open_cfw_nanopb_read(stream, NULL, (size_t)length)", source)
        self.assertNotIn("size too large", source)
        self.assertIn("sizeof(size_t) == 4U", header)
        self.assertIn("sizeof(uint32_t) == 4U", header)
        self.assertIn("sizeof(size_t) == sizeof(uint32_t)", header)
        self.assertNotIn("0x0048F5AE", header)
        self.assertNotIn("0x0048F3BE", header)

    def test_no_authenticated_bootloader_homolog(self) -> None:
        boot = BOOT.read_bytes()
        self.assertEqual((len(boot), sha256(boot)), BOOT_PIN)
        start, end = STOCK_SPAN
        body = self.application[start - APPLICATION_BASE:end - APPLICATION_BASE]
        self.assertNotIn(body, boot)
        for probe in (body[:8], body[-8:], body[:12], body[-12:]):
            self.assertNotIn(probe, boot)

    def test_host_behavior_matches_authenticated_upstream_contract(self) -> None:
        self.assertEqual(self.host_test(), 0)

    def test_target_object_and_relocation_closure_are_exact(self) -> None:
        self.assertEqual(self.objects[0].read_bytes(), self.objects[1].read_bytes())
        pins = PRODUCTION_PROFILE_PINS[self.profile]
        self.assertIsNotNone(pins["object"])
        self.assertIsNotNone(pins["text"])
        self.assertEqual(pins["text"], self.compiler_profile["text"])
        self.assertNotEqual(pins["object"], self.compiler_profile["object"])
        for path in self.objects:
            self.assertEqual(
                (path.stat().st_size, sha256(path)),
                pins["object"],
            )
        data, sections = self.apollo_overlay.parse_elf32(self.objects[0])
        executable = [
            section["name"] for section in sections
            if int(section["size"]) > 0 and int(section["flags"]) & 0x4
        ]
        self.assertEqual(executable, [PRODUCTION_SECTION])
        writable = [
            section["name"] for section in sections
            if int(section["size"]) > 0 and int(section["flags"]) & 0x3 == 0x3
        ]
        self.assertEqual(writable, [])
        text = next(
            section for section in sections
            if section["name"] == PRODUCTION_SECTION
        )
        body = data[int(text["offset"]):int(text["offset"]) + int(text["size"])]
        self.assertEqual((len(body), sha256(body)), pins["text"])
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
        self.assertEqual(
            undefined,
            [PRODUCTION_DECODE_PROVIDER, READ_PROVIDER],
        )

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
        self.assertEqual(relocations, {
            PRODUCTION_SECTION: [
                (8, 10, PRODUCTION_DECODE_PROVIDER),
                (20, 10, READ_PROVIDER),
            ],
            PRODUCTION_EXIDX_SECTION: [(0, 42, "")],
        })

    def test_compiler_profile_selection_fails_closed(self) -> None:
        for profile, record in COMPILER_PROFILES.items():
            self.assertEqual(
                resolve_compiler_profile(
                    record["compiler"], record["version"], profile
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
            with self.assertRaisesRegex(
                AssertionError, "unreviewed target compiler"
            ):
                resolve_compiler_profile(
                    record["compiler"] + "-other", record["version"], profile
                )
            with self.assertRaisesRegex(
                AssertionError, "unreviewed target compiler"
            ):
                resolve_compiler_profile(
                    record["compiler"], record["version"] + ".1", profile
                )


class NanopbSkipStringProductionContractTests(StableUnittestIdentityCase):
    maxDiff = None

    def test_active_profile_mutation_helpers_reach_effective_leaf(self) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        baseline = json.loads(OVERLAY.read_text(encoding="utf-8"))
        for profile in ("apple-clang", "linux-clang"):
            with self.subTest(profile=profile):
                config = copy.deepcopy(baseline)
                leaf, _ = production_overlay_records(config)

                relocations = active_leaf_relocations(leaf, profile)
                relocation_offset = int(relocations[0]["offset"]) + 2
                relocations[0]["offset"] = relocation_offset

                expected = active_leaf_expected(leaf, profile)
                placement_offset = int(expected["offset"]) + 2
                expected["offset"] = placement_offset

                compiler_owner, compiler_field = (
                    active_leaf_reviewed_compiler_field(leaf, profile)
                )
                compiler_owner[compiler_field] = "Unreviewed clang"

                effective = apollo_overlay.resolve_leaf_profile(leaf, profile)
                self.assertEqual(
                    effective["relocations"][0]["offset"], relocation_offset
                )
                self.assertEqual(
                    effective["expected"]["offset"], placement_offset
                )
                self.assertEqual(
                    effective["toolchain"][compiler_field],
                    "Unreviewed clang",
                )

                clear_active_overlay_expected(config, profile)
                self.assertEqual(config["expected"], {})
                if profile != "apple-clang":
                    self.assertEqual(
                        config["toolchain_profiles"][profile]["expected"],
                        {},
                    )

        synthetic_leaf = {
            "function": "profile_helper_probe",
            "toolchain": {
                "reviewed_version_prefix": "canonical compiler",
                "flags": ["canonical flags"],
                "target": "canonical target",
                "include_dirs": ["canonical include"],
            },
            "expected": {"offset": 0},
            "relocations": [{"offset": 0}],
            "closure": {"probe": "canonical closure"},
            "toolchain_profiles": {
                "linux-clang": {
                    "reviewed_version": "profile compiler",
                    "flags": ["profile flags"],
                    "target": "profile target",
                    "include_dirs": ["profile include"],
                    "expected": {"offset": 2},
                    "relocations": [{"offset": 2}],
                    "closure": {"probe": "profile closure"},
                },
            },
        }
        selected = synthetic_leaf["toolchain_profiles"]["linux-clang"]
        for field in ("expected", "relocations", "closure"):
            self.assertIs(
                active_leaf_field_owner(
                    synthetic_leaf, "linux-clang", field
                ),
                selected,
            )
        for field in ("flags", "target", "include_dirs"):
            self.assertIs(
                active_leaf_toolchain_field_owner(
                    synthetic_leaf, "linux-clang", field
                ),
                selected,
            )
        compiler_owner, compiler_field = active_leaf_reviewed_compiler_field(
            synthetic_leaf, "linux-clang"
        )
        self.assertIs(compiler_owner, selected)
        self.assertEqual(compiler_field, "reviewed_version")
        effective = apollo_overlay.resolve_leaf_profile(
            synthetic_leaf, "linux-clang"
        )
        self.assertEqual(effective["closure"]["probe"], "profile closure")
        self.assertEqual(effective["toolchain"]["flags"], ["profile flags"])
        self.assertEqual(effective["toolchain"]["target"], "profile target")
        self.assertEqual(
            effective["toolchain"]["include_dirs"], ["profile include"]
        )

    def _assert_production_source_header_and_object_contract(self) -> None:
        for path, pin in PRODUCTION_LOCAL_PINS.items():
            if pin is None:
                self.fail(
                    "unrecorded production pin:\n"
                    + path.relative_to(ROOT).as_posix()
                )
            self.assertEqual((path.stat().st_size, sha256(path)), pin)

        source = PRODUCTION_SOURCE.read_text(encoding="utf-8")
        header = PRODUCTION_HEADER.read_text(encoding="utf-8")
        combined = source + header
        for token in (
            "Copyright (c) 2011 Petteri Aimonen",
            "Permission is granted",
            "altered",
            PRODUCTION_FUNCTION,
            PRODUCTION_DECODE_PROVIDER,
            READ_PROVIDER,
            "open_cfw_nanopb_read(stream, NULL, (size_t)length)",
        ):
            self.assertIn(token, combined)
        for token in (
            "runtime_nanopb_decode_varint32.h",
            "sizeof(size_t) == 4U",
            "sizeof(uint32_t) == 4U",
            "sizeof(size_t) == sizeof(uint32_t)",
        ):
            self.assertIn(token, header)
        self.assertNotIn("_candidate", combined)
        self.assertNotIn("size too large", combined)
        self.assertNotIn("0x0048F5AE", combined)
        self.assertNotIn("0x0048F3BE", combined)

        clang = os.environ.get("OPENCFW_CLANG", APPLE_CLANG)
        version = subprocess.run(
            [clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        profile, _ = resolve_compiler_profile(
            clang,
            version,
            os.environ.get("OPENCFW_TOOLCHAIN_PROFILE"),
        )
        pins = PRODUCTION_PROFILE_PINS[profile]
        if pins["object"] is None or pins["text"] is None:
            self.fail(f"unrecorded production compiler pins:\n{profile}")

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        with tempfile.TemporaryDirectory(
            prefix="open-cfw-nanopb-skip-string-production-object-"
        ) as temporary:
            objects = [
                Path(temporary) / "production-a.o",
                Path(temporary) / "production-b.o",
            ]
            for output in objects:
                subprocess.run(
                    [
                        clang, *PRODUCTION_TARGET_FLAGS, "-c",
                        str(PRODUCTION_SOURCE), "-o", str(output),
                    ],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(objects[0].read_bytes(), objects[1].read_bytes())
            for output in objects:
                self.assertEqual(
                    (output.stat().st_size, sha256(output)),
                    pins["object"],
                )

            data, sections = apollo_overlay.parse_elf32(objects[0])
            sections_by_name = {
                str(section["name"]): section for section in sections
            }
            allocated = {
                name: int(section["size"])
                for name, section in sections_by_name.items()
                if int(section["size"]) and int(section["flags"]) & 0x2
            }
            self.assertEqual(
                set(allocated),
                {PRODUCTION_SECTION, PRODUCTION_EXIDX_SECTION},
            )
            writable = [
                name for name, section in sections_by_name.items()
                if int(section["size"]) and int(section["flags"]) & 0x3 == 0x3
            ]
            self.assertEqual(writable, [])
            self.assertFalse(any(name.startswith(".rodata") for name in allocated))

            text = sections_by_name[PRODUCTION_SECTION]
            body = data[
                int(text["offset"]):int(text["offset"]) + int(text["size"])
            ]
            self.assertEqual((len(body), sha256(body)), pins["text"])
            self.assertEqual(int(text["alignment"]), 4)
            exidx = sections_by_name[PRODUCTION_EXIDX_SECTION]
            exidx_body = data[
                int(exidx["offset"]):int(exidx["offset"]) + int(exidx["size"])
            ]
            self.assertEqual(exidx_body, PRODUCTION_EXIDX)

            symbols = apollo_overlay.parse_elf32_symbols(data, sections)
            undefined = sorted(
                str(symbol["name"])
                for symbol in symbols
                if symbol["name"] and int(symbol["section_index"]) == 0
            )
            self.assertEqual(
                undefined,
                sorted((PRODUCTION_DECODE_PROVIDER, READ_PROVIDER)),
            )
            symbol = next(
                item for item in symbols
                if item["name"] == PRODUCTION_FUNCTION
            )
            self.assertEqual(int(symbol["binding"]), 1)
            self.assertEqual(int(symbol["type"]), 2)
            self.assertEqual(int(symbol["size"]), len(body))

            symbol_table = apollo_overlay.section_named(sections, ".symtab")
            string_table = sections[int(symbol_table["link"])]
            strings = data[
                int(string_table["offset"]):
                int(string_table["offset"]) + int(string_table["size"])
            ]
            symbol_names = []
            for index in range(int(symbol_table["size"]) // 16):
                name_offset = struct.unpack_from(
                    "<I", data, int(symbol_table["offset"]) + index * 16
                )[0]
                symbol_names.append(
                    apollo_overlay.elf_string(strings, name_offset, "symbol")
                )
            observed = {}
            for section in sections:
                if int(section["type"]) != 9:
                    continue
                target = str(sections[int(section["info"])]["name"])
                records = []
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II", data, int(section["offset"]) + index * 8
                    )
                    records.append((
                        offset,
                        information & 0xFF,
                        symbol_names[information >> 8],
                    ))
                observed[target] = records
            self.assertEqual(observed, {
                PRODUCTION_SECTION: [
                    (8, 10, PRODUCTION_DECODE_PROVIDER),
                    (20, 10, READ_PROVIDER),
                ],
                PRODUCTION_EXIDX_SECTION: [(0, 42, "")],
            })

    def _assert_registered_overlay_and_builder_contract(
        self, config: dict[str, object]
    ) -> None:
        leaf, patch = production_overlay_records(config)
        self.assertEqual(config["functions"].count(PRODUCTION_FUNCTION), 1)
        self.assertEqual(
            set(leaf["toolchain_profiles"]),
            {"linux-clang", "apple-terminate-record"},
        )
        self.assertEqual(len(config["functions"]), BASE_FUNCTION_COUNT + 1)
        self.assertEqual(
            len(config["relocated_leaves"]), BASE_RELOCATED_COUNT + 1
        )
        self.assertEqual(len(config["patch_sites"]), BASE_PATCH_COUNT + 1)
        leaf_functions = [
            item["function"] for item in config["relocated_leaves"]
        ]
        leaf_index = leaf_functions.index(PRODUCTION_FUNCTION)
        self.assertEqual(
            leaf_functions[leaf_index - 1], PRODUCTION_DECODE_PROVIDER
        )
        for collection in ("isolated_leaves", "in_place_leaves"):
            self.assertFalse(any(
                item.get("function") == PRODUCTION_FUNCTION
                for item in config.get(collection, [])
            ))

        self.assertEqual(leaf["source"]["path"], PRODUCTION_SOURCE_PATH)
        source_pin = PRODUCTION_LOCAL_PINS[PRODUCTION_SOURCE]
        self.assertIsNotNone(source_pin)
        self.assertEqual(
            (leaf["source"]["size"], leaf["source"]["sha256"]),
            source_pin,
        )
        self.assertEqual(leaf["source"]["license"], "Zlib")
        self.assertIn("altered", leaf["source"]["origin"])
        self.assertEqual(
            leaf["source"]["upstream_commit"],
            POINT_RELEASE_DEFINITIONS["0.4.9"][0],
        )
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertNotIn("closure", leaf)
        self.assertEqual(leaf["toolchain"]["target"], "thumbv7em-none-eabi")
        self.assertEqual(
            tuple(leaf["toolchain"]["flags"]),
            PRODUCTION_TARGET_FLAGS[1:],
        )
        expected_relocations = [
            {
                "offset": 8,
                "type": "R_ARM_THM_CALL",
                "symbol": PRODUCTION_DECODE_PROVIDER,
                "symbol_type": "STT_NOTYPE",
                "target_function": PRODUCTION_DECODE_PROVIDER,
            },
            {
                "offset": 20,
                "type": "R_ARM_THM_CALL",
                "symbol": READ_PROVIDER,
                "symbol_type": "STT_NOTYPE",
                "target_function": READ_PROVIDER,
            },
        ]
        self.assertEqual(leaf["relocations"], expected_relocations)
        self.assertFalse(any(
            "target_address" in relocation
            for relocation in leaf["relocations"]
        ))
        for profile, projected in PROJECTED_PRODUCTION_PROFILES.items():
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
            self.assertEqual(expected["size"], 34)
            self.assertEqual(expected["alignment"], 4)
            self.assertEqual(expected["offset"], projected["offset"])
            self.assertEqual(
                expected["unrelocated_sha256"],
                "d3216f569354900680dae5d78350af7668be4d8fbdae64a47afc4f440b0df920",
            )
            self.assertEqual(
                expected["sha256"], projected["relocated_sha256"]
            )
            self.assertEqual(relocations, expected_relocations)
        self.assertEqual(patch, {
            "name": PATCH_NAME,
            "runtime_address": STOCK_SPAN[0],
            "expected_size": STOCK_SPAN[1] - STOCK_SPAN[0],
            "expected_sha256": STOCK_SHA256,
            "branch": "b_w",
            "target_function": PRODUCTION_FUNCTION,
        })
        serialized = json.dumps({"leaf": leaf, "patch": patch}, sort_keys=True)
        self.assertNotIn("_candidate", serialized)
        registrations = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (OVERLAY, MANIFEST, MAKEFILE, PROVENANCE, VERIFIER)
        )
        self.assertNotIn(
            "components/shared/nanopb/runtime_nanopb_skip_string_candidate.c",
            registrations,
        )
        self.assertNotIn(CANDIDATE_FUNCTION, registrations)
        self.assertNotIn(CANDIDATE_DECODE_SEAM, registrations)
        patch_names = [item.get("name") for item in config["patch_sites"]]
        self.assertLess(
            patch_names.index("replace_nanopb_decode_varint32"),
            patch_names.index(PATCH_NAME),
        )
        self.assertLess(
            patch_names.index(PATCH_NAME),
            patch_names.index("replace_cmbacktrace_get_cur_thread_name"),
        )

        clang = os.environ.get("OPENCFW_CLANG", APPLE_CLANG)
        version = subprocess.run(
            [clang, "--version"], check=True, capture_output=True, text=True
        ).stdout.splitlines()[0]
        profile, _ = resolve_compiler_profile(
            clang, version, os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
        )
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        build_root = ROOT / "build"
        build_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="open-cfw-nanopb-skip-string-overlay-",
            dir=build_root,
        ) as temporary:
            output = Path(temporary)
            report = apollo_overlay.build(
                root=ROOT,
                config_path=OVERLAY,
                output_dir=output,
                clang=clang,
                toolchain_profile=profile,
            )
            extracted = next(
                item for item in report["relocated_leaves"]
                if item["extraction"]["function"] == PRODUCTION_FUNCTION
            )
            placement = int(extracted["placement"]["offset"])
            runtime = int(extracted["placement"]["runtime_address"])
            self.assertEqual(runtime, OVERLAY_RUNTIME_ADDRESS + placement)
            self.assertEqual(extracted["extraction"]["relocation_count"], 2)
            self.assertEqual(
                [
                    item["target_function"]
                    for item in extracted["extraction"]["relocations"]
                ],
                [PRODUCTION_DECODE_PROVIDER, READ_PROVIDER],
            )
            self.assertNotIn("rodata", extracted["extraction"])

            patched = next(
                item for item in report["overlay"]["patched_sites"]
                if item["name"] == PATCH_NAME
            )
            replacement = bytes.fromhex(patched["replacement_hex"])
            self.assertEqual(len(replacement), 32)
            first, second = struct.unpack("<HH", replacement[:4])
            self.assertEqual(
                wide_branch_target(
                    STOCK_SPAN[0], first, second, link=False
                ),
                runtime,
            )
            self.assertIsNone(
                wide_branch_target(STOCK_SPAN[0], first, second, link=True)
            )
            self.assertEqual(replacement[4:], b"\x00\xbf" * 14)
            self.assertEqual(
                sha256(replacement),
                PROJECTED_PRODUCTION_PROFILES[profile][
                    "replacement_sha256"
                ],
            )

            component = (output / "ota_s200_firmware_ota.bin").read_bytes()
            official = OFFICIAL.read_bytes()
            caller_offset = PACKAGE_PREAMBLE + CALLERS[0] - APPLICATION_BASE
            self.assertEqual(
                component[caller_offset:caller_offset + 4],
                b"\x00\xbf\x00\xbf",
            )
            self.assertNotEqual(
                component[caller_offset:caller_offset + 4],
                official[caller_offset:caller_offset + 4],
            )
            for span, digest in (
                ((0x0048_F628, STOCK_SPAN[0]),
                 PREDECESSOR_COMPONENT_SHA256[profile]),
                (SUCCESSOR_SPAN, PRODUCTION_SUCCESSOR_SHA256),
            ):
                start, end = span
                body = component[
                    PACKAGE_PREAMBLE + start - APPLICATION_BASE:
                    PACKAGE_PREAMBLE + end - APPLICATION_BASE
                ]
                self.assertEqual(sha256(body), digest)

            application = component[PACKAGE_PREAMBLE:]
            leaf_end = runtime + int(extracted["extraction"]["size"])
            protected_start = runtime - int(extracted["placement"]["padding_before"])
            ingress = []
            for offset in range(0, len(application) - 3, 2):
                address = APPLICATION_BASE + offset
                if runtime <= address < leaf_end:
                    continue
                first, second = struct.unpack_from("<HH", application, offset)
                for kind, target in (
                    ("bl", wide_branch_target(address, first, second, link=True)),
                    ("bw", wide_branch_target(address, first, second, link=False)),
                    ("conditional", wide_conditional_target(address, first, second)),
                ):
                    if target is not None and protected_start <= target < leaf_end:
                        ingress.append((address, target, kind))
            for offset in range(0, len(application) - 1, 2):
                address = APPLICATION_BASE + offset
                if runtime <= address < leaf_end:
                    continue
                halfword = struct.unpack_from("<H", application, offset)[0]
                for target in narrow_targets(address, halfword):
                    if protected_start <= target < leaf_end:
                        ingress.append((address, target, "narrow"))
            self.assertEqual(
                ingress,
                [
                    (STOCK_SPAN[0], runtime, "bw"),
                    (0x007B_2C9E, runtime, "bw"),
                ],
            )
            stored = []
            for offset in range(len(application) - 3):
                value = struct.unpack_from("<I", application, offset)[0]
                if protected_start <= (value & ~1) < leaf_end:
                    stored.append((APPLICATION_BASE + offset, value))
            self.assertEqual(stored, [])

    def test_production_source_exists(self) -> None:
        if not PRODUCTION_SOURCE.is_file():
            self.fail("missing production source:\n" + PRODUCTION_SOURCE_PATH)
        if not PRODUCTION_HEADER.is_file():
            self.fail("missing production header:\n" + PRODUCTION_HEADER_PATH)
        self._assert_production_source_header_and_object_contract()

    def test_overlay_registers_leaf_and_full_span_patch(self) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = [
            item for item in config["relocated_leaves"]
            if item.get("function") == PRODUCTION_FUNCTION
        ]
        patches = [
            item for item in config["patch_sites"]
            if item.get("name") == PATCH_NAME
        ]
        missing = []
        if not leaves:
            missing.append(PRODUCTION_FUNCTION)
        if not patches:
            missing.append(PATCH_NAME)
        if missing:
            self.fail(
                "missing production overlay registrations:\n"
                + ", ".join(missing)
            )
        self._assert_registered_overlay_and_builder_contract(config)


class NanopbSkipStringProductionMutationTests(StableUnittestIdentityCase):
    """Exercise Task 3 mutations only after a real-builder positive control."""

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.baseline = json.loads(OVERLAY.read_text(encoding="utf-8"))
        cls.clang = os.environ.get("OPENCFW_CLANG", APPLE_CLANG)
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        cls.profile, cls.compiler_profile = resolve_compiler_profile(
            cls.clang, version, os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
        )
        build_root = ROOT / "build"
        build_root.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-nanopb-skip-string-task3-",
            dir=build_root,
        )
        cls.temporary_path = Path(cls.temporary.name)
        validate_skip_string_task3_preflight(cls.baseline)
        cls.control = cls._build(cls.baseline, "positive-control")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def _build(
        cls, config: dict[str, object], label: str,
    ) -> dict[str, object]:
        config_path = cls.temporary_path / f"{label}.json"
        config_path.write_text(
            json.dumps(config, indent=2) + "\n",
            encoding="utf-8",
        )
        return cls.apollo_overlay.build(
            root=ROOT,
            config_path=config_path,
            output_dir=cls.temporary_path / f"{label}-output",
            clang=cls.clang,
            toolchain_profile=cls.profile,
        )

    @classmethod
    def _source_mutation(
        cls,
        config: dict[str, object],
        label: str,
        source_text: str,
        *,
        header_bytes: bytes | None = None,
    ) -> dict[str, object]:
        source_root = cls.temporary_path / f"{label}-source"
        source_root.mkdir()
        source_path = source_root / PRODUCTION_SOURCE.name
        header_path = source_root / PRODUCTION_HEADER.name
        source_path.write_text(source_text, encoding="utf-8")
        header_path.write_bytes(
            PRODUCTION_HEADER.read_bytes()
            if header_bytes is None
            else header_bytes
        )
        leaf, _ = production_overlay_records(config)
        leaf["source"]["path"] = source_path.relative_to(ROOT).as_posix()
        leaf["source"]["size"] = source_path.stat().st_size
        leaf["source"]["sha256"] = sha256(source_path)
        include_dirs_owner = active_leaf_toolchain_field_owner(
            leaf, cls.profile, "include_dirs"
        )
        include_dirs_owner["include_dirs"] = [
            "components/shared/nanopb"
        ]
        clear_active_overlay_expected(config, cls.profile)
        return config

    def test_real_builder_uses_resolved_active_profile(self) -> None:
        self.assertEqual(
            self.control["toolchain"],
            {
                **self.control["toolchain"],
                "executable": self.clang,
                "profile": self.profile,
                "version": self.compiler_profile["version"],
            },
        )

    def test_unmodified_real_builder_positive_control_is_exact(self) -> None:
        leaf = next(
            item for item in self.control["relocated_leaves"]
            if item["extraction"]["function"] == PRODUCTION_FUNCTION
        )
        patch = next(
            item for item in self.control["overlay"]["patched_sites"]
            if item["name"] == PATCH_NAME
        )
        expected = self.baseline["expected"]
        if self.profile != "apple-clang":
            expected = self.baseline["toolchain_profiles"][self.profile][
                "expected"
            ]
        projected = PROJECTED_PRODUCTION_PROFILES[self.profile]
        self.assertEqual(
            (self.control["overlay"]["size"], self.control["overlay"]["sha256"]),
            (
                expected["overlay_size"],
                expected["overlay_sha256"],
            ),
        )
        self.assertEqual(
            (
                self.control["component"]["size"],
                self.control["component"]["sha256"],
            ),
            (
                expected["component_size"],
                expected["component_sha256"],
            ),
        )
        self.assertEqual(leaf["placement"]["offset"], projected["offset"])
        self.assertEqual(
            leaf["extraction"]["sha256"],
            projected["relocated_sha256"],
        )
        self.assertEqual(
            sha256(bytes.fromhex(patch["replacement_hex"])),
            projected["replacement_sha256"],
        )

    def test_task_specific_preflight_mutations_fail_closed(self) -> None:
        config_mutations = {
            name: message
            for name, message, kind in OVERLAY_MUTATION_RECORDS
            if kind == "config"
        }
        self.assertEqual(
            set(config_mutations),
            {
                "partial_patch_size_4",
                "patch_branch_bl",
                "fixed_decode_target_address",
                "fixed_read_target_address",
                "providers_swapped",
                "decode_call_omitted",
                "shifted_stock_span",
                "concatenated_neighbor_hash",
                "leaf_without_patch",
                "patch_without_leaf",
            },
        )
        for name, message in config_mutations.items():
            with self.subTest(mutation=name):
                mutated = apply_overlay_mutation(self.baseline, name)
                with self.assertRaisesRegex(AssertionError, message):
                    validate_skip_string_task3_preflight(mutated)

        missing_strict = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(missing_strict)
        leaf["strict_relocation_contract"] = False
        with self.assertRaisesRegex(
            AssertionError, "skip-string strict relocation contract is required"
        ):
            validate_skip_string_task3_preflight(missing_strict)

        reordered = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(reordered)
        reordered["relocated_leaves"].remove(leaf)
        reordered["relocated_leaves"].insert(-3, leaf)
        with self.assertRaisesRegex(
            AssertionError, "skip-string relocated tail order differs"
        ):
            validate_skip_string_task3_preflight(reordered)

        overlap = copy.deepcopy(self.baseline)
        overlap["patch_sites"].append({
            "name": "task3_overlap_probe",
            "runtime_address": STOCK_SPAN[0] + 2,
            "expected_size": 4,
            "expected_sha256": "0" * 64,
            "branch": "b_w",
            "target_function": PRODUCTION_FUNCTION,
        })
        with self.assertRaisesRegex(AssertionError, "patch overlap"):
            validate_skip_string_task3_preflight(overlap)

        with self.assertRaisesRegex(
            AssertionError, "production source SHA-256 differs"
        ):
            validate_skip_string_task3_preflight(
                self.baseline,
                source_bytes=PRODUCTION_SOURCE.read_bytes() + b"\n",
            )
        with self.assertRaisesRegex(
            AssertionError, "production header SHA-256 differs"
        ):
            validate_skip_string_task3_preflight(
                self.baseline,
                header_bytes=PRODUCTION_HEADER.read_bytes() + b"\n",
            )

    def test_real_builder_source_elf_and_profile_mutations_fail_closed(self) -> None:
        source = PRODUCTION_SOURCE.read_text(encoding="utf-8")
        cases: list[tuple[str, dict[str, object], str]] = []
        self.assertEqual(
            {
                name for name, _message, kind in OVERLAY_MUTATION_RECORDS
                if kind != "config"
            },
            {
                "extra_undefined_symbol",
                "writable_allocated_section",
                "size_too_large_rodata",
                "unreviewed_compiler_profile",
            },
        )

        wrong_source_hash = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(wrong_source_hash)
        leaf["source"]["sha256"] = "0" * 64
        cases.append((
            "wrong-source-hash",
            wrong_source_hash,
            "source SHA-256 differs from config",
        ))

        wrong_source_size = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(wrong_source_size)
        leaf["source"]["size"] += 1
        cases.append((
            "wrong-source-size",
            wrong_source_size,
            "source size differs from config",
        ))

        wrong_section_source = source.replace(
            "bool open_cfw_nanopb_skip_string(",
            "__attribute__((section(\".text.task3_wrong_skip_string\")))\n"
            "bool open_cfw_nanopb_skip_string(",
            1,
        )
        cases.append((
            "wrong-text-section",
            self._source_mutation(
                copy.deepcopy(self.baseline),
                "wrong-text-section",
                wrong_section_source,
            ),
            "expected one .text.open_cfw_nanopb_skip_string section",
        ))

        wrong_offset = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(wrong_offset)
        active_leaf_relocations(leaf, self.profile)[0]["offset"] = 10
        cases.append((
            "wrong-relocation-offset",
            wrong_offset,
            "relocation list differs from reviewed config",
        ))

        wrong_type = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(wrong_type)
        active_leaf_relocations(leaf, self.profile)[0][
            "type"
        ] = "R_ARM_THM_JUMP24"
        cases.append((
            "wrong-relocation-type",
            wrong_type,
            "relocation list differs from reviewed config",
        ))

        wrong_symbol = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(wrong_symbol)
        active_leaf_relocations(leaf, self.profile)[1][
            "symbol"
        ] = "open_cfw_nanopb_wrong_provider"
        cases.append((
            "wrong-relocation-symbol",
            wrong_symbol,
            "must bind its exact symbol to the same target_function name",
        ))

        weak_source = source.replace(
            '#include "runtime_nanopb_skip_string.h"',
            '#include "runtime_nanopb_skip_string.h"\n'
            '#pragma weak open_cfw_nanopb_read',
            1,
        )
        cases.append((
            "wrong-relocation-binding",
            self._source_mutation(
                copy.deepcopy(self.baseline),
                "wrong-relocation-binding",
                weak_source,
            ),
            "must reference a global undefined symbol",
        ))

        swapped = apply_overlay_mutation(
            self.baseline, "providers_swapped", profile=self.profile
        )
        cases.append((
            "providers-swapped",
            swapped,
            "relocation list differs from reviewed config",
        ))
        omitted = apply_overlay_mutation(
            self.baseline, "decode_call_omitted", profile=self.profile
        )
        cases.append((
            "provider-omitted",
            omitted,
            "strict external symbol metadata count differs",
        ))

        extra_provider_source = source.replace(
            "bool open_cfw_nanopb_skip_string(",
            "bool open_cfw_nanopb_task3_extra_provider(\n"
            "    struct open_cfw_nanopb_istream *stream\n"
            ");\n\n"
            "bool open_cfw_nanopb_skip_string(",
            1,
        ).replace(
            "    return open_cfw_nanopb_read(stream, NULL, (size_t)length);",
            "    if (!open_cfw_nanopb_task3_extra_provider(stream)) {\n"
            "        return false;\n"
            "    }\n\n"
            "    return open_cfw_nanopb_read(stream, NULL, (size_t)length);",
            1,
        )
        cases.append((
            "extra-undefined-provider",
            self._source_mutation(
                copy.deepcopy(self.baseline),
                "extra-undefined-provider",
                extra_provider_source,
            ),
            "strict external symbol metadata count differs",
        ))

        missing_strict = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(missing_strict)
        leaf["strict_relocation_contract"] = False
        cases.append((
            "missing-strict-contract",
            missing_strict,
            "symbol_type requires strict_relocation_contract",
        ))

        writable_source = (
            source
            + "\nvolatile uint32_t "
            "open_cfw_nanopb_task3_writable_allocation;\n"
        )
        cases.append((
            "writable-allocated-section",
            self._source_mutation(
                copy.deepcopy(self.baseline),
                "writable-allocated-section",
                writable_source,
            ),
            "strict relocation contract rejects unexpected allocated sections",
        ))

        rodata_source = (
            source
            + '\nconst char open_cfw_nanopb_task3_size_error[] = '
            '"size too large";\n'
        )
        cases.append((
            "size-too-large-rodata",
            self._source_mutation(
                copy.deepcopy(self.baseline),
                "size-too-large-rodata",
                rodata_source,
            ),
            "strict relocation contract rejects unexpected allocated sections",
        ))

        extra_allocated_source = (
            source
            + "\nbool open_cfw_nanopb_task3_extra_allocated_function(void)\n"
            "{\n"
            "    return true;\n"
            "}\n"
        )
        cases.append((
            "extra-allocated-text",
            self._source_mutation(
                copy.deepcopy(self.baseline),
                "extra-allocated-text",
                extra_allocated_source,
            ),
            "strict relocation contract rejects unexpected allocated sections",
        ))

        non_cantunwind = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(non_cantunwind)
        flags_owner = active_leaf_toolchain_field_owner(
            leaf, self.profile, "flags"
        )
        flags = flags_owner["flags"]
        if not isinstance(flags, list):
            self.fail("production toolchain flags are missing or invalid")
        flags.remove("-fno-unwind-tables")
        flags.append("-funwind-tables")
        cases.append((
            "non-cantunwind-companion",
            non_cantunwind,
            "CANTUNWIND companion.*differs",
        ))

        wrong_unrelocated = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(wrong_unrelocated)
        active_leaf_expected(leaf, self.profile)[
            "unrelocated_sha256"
        ] = "0" * 64
        cases.append((
            "wrong-unrelocated-text-pin",
            wrong_unrelocated,
            "unrelocated SHA-256 differs from reviewed pin",
        ))

        displaced = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(displaced)
        expected = active_leaf_expected(leaf, self.profile)
        expected["offset"] += 2
        cases.append((
            "nondeterministic-tail-placement",
            displaced,
            "offset differs from reviewed",
        ))

        unreviewed_compiler = copy.deepcopy(self.baseline)
        leaf, _ = production_overlay_records(unreviewed_compiler)
        compiler_owner, compiler_field = active_leaf_reviewed_compiler_field(
            leaf, self.profile
        )
        compiler_owner[compiler_field] = "Unreviewed clang"
        cases.append((
            "unreviewed-compiler",
            unreviewed_compiler,
            "compiler version differs from the reviewed toolchain family",
        ))

        for label, config, expected_error in cases:
            with self.subTest(mutation=label):
                clear_active_overlay_expected(config, self.profile)
                with self.assertRaisesRegex(
                    self.apollo_overlay.BuildError,
                    expected_error,
                ):
                    self._build(config, label)


class NanopbSkipStringProductionOwnershipTests(StableUnittestIdentityCase):
    @unittest.skipUnless(PROMOTION_HISTORY_AVAILABLE, PROMOTION_HISTORY_SKIP_REASON)
    def test_manifest_splits_stock_span_and_appends_leaf(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG", APPLE_CLANG)
        version = subprocess.run(
            [clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        profile, _ = resolve_compiler_profile(
            clang, version, os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
        )
        expected_build = PRODUCTION_BUILD_PROFILES[profile]
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        regions = main["regions"]
        predecessor = [
            region
            for region in regions
            if region["file_offset"] == 357_996 and region["size"] == 382
        ]
        if predecessor and predecessor[0]["address_status"] == "official_blob":
            self.fail("predecessor 382-byte region is still official_blob")

        expected_records = {
            "nanopb_skip_string_source_replacement": (
                357_996,
                32,
                0x0048_F64C,
                "generated_source_entry_replacement",
                "apollo510b/source-entry-nanopb-skip-string-0x0048f64c.bin",
            ),
            "apollo_nanopb_skip_string_source_alignment": (
                3_648_618,
                2,
                0x007B_2C4A,
                "generated_alignment",
                "apollo510b/main-source-nanopb-skip-string-alignment-0x007b2c4a.bin",
            ),
            "apollo_nanopb_skip_string_source_leaf": (
                3_648_620,
                34,
                0x007B_2C4C,
                "source_compiled",
                "apollo510b/main-source-nanopb-skip-string-0x007b2c4c.bin",
            ),
        }
        by_name = {region["name"]: region for region in regions}
        for name, expected in expected_records.items():
            record = by_name[name]
            self.assertEqual(
                (
                    record["file_offset"],
                    record["size"],
                    record["target_address"],
                    record["address_status"],
                    record["output"],
                ),
                expected,
            )

        self.assertEqual(len(regions), 1818)
        self.assertEqual(regions[0]["file_offset"], 0)
        for left, right in zip(regions, regions[1:]):
            self.assertEqual(
                left["file_offset"] + left["size"],
                right["file_offset"],
            )
        self.assertEqual(
            regions[-1]["file_offset"] + regions[-1]["size"],
            main["provider"]["size"],
        )
        for region in regions:
            if "target_address" in region:
                self.assertEqual(
                    region["target_address"],
                    APPLICATION_BASE + region["file_offset"] - PACKAGE_PREAMBLE,
                )
        official_overlap = [
            region
            for region in regions
            if region["address_status"] == "official_blob"
            and region["target_address"] < STOCK_SPAN[1]
            and STOCK_SPAN[0]
            < region["target_address"] + region["size"]
        ]
        self.assertEqual(official_overlap, [])

        ownership: dict[str, tuple[int, int]] = {}
        for status in {region["address_status"] for region in regions}:
            selected = [
                region for region in regions
                if region["address_status"] == status
            ]
            ownership[status] = (
                len(selected),
                sum(region["size"] for region in selected),
            )
        self.assertEqual(
            ownership,
            {
                "container_only": (1, 32),
    "generated_alignment": (182, 366),
    "generated_source_entry_replacement": (842, 118_700),
    "generated_source_exact_load_image": (1, 6),
    "generated_source_exact_replacement": (7, 134),
    "official_blob": (265, 3_404_306),
    "source_compiled": (437, 164_764),
            },
        )

        historical_manifest = json.loads(historical_git_bytes(
            (
                "show",
                f"{PROMOTION_BASE}:openCFW/manifests/g2-2.2.6.10-core-source.json",
            ),
            "predecessor source manifest",
        ))
        self.assertEqual(
            manifest["component_overrides"]["apollo_bootloader"],
            historical_manifest["component_overrides"]["apollo_bootloader"],
        )

        sys.path.insert(0, str(ROOT / "tools"))
        import open_cfw

        build_environment = os.environ.copy()
        build_environment["OPENCFW_CLANG"] = clang
        build_environment["OPENCFW_TOOLCHAIN_PROFILE"] = profile
        for script in (
            "components/bootloader/core_overlay/build_component.py",
            "components/apollo_main/core_overlay/build_component.py",
        ):
            completed = subprocess.run(
                [sys.executable, script],
                cwd=ROOT,
                env=build_environment,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

        boot_component = (
            ROOT / "components/bootloader/core_overlay/build"
            / "ota_s200_bootloader.bin"
        ).read_bytes()
        self.assertEqual(
            (len(boot_component), sha256(boot_component)),
            expected_build["boot_component"],
        )
        component_path = (
            ROOT / "components/apollo_main/core_overlay/build"
            / "ota_s200_firmware_ota.bin"
        )
        component = component_path.read_bytes()
        self.assertEqual(
            (len(component), sha256(component)),
            expected_build["main_component"],
        )
        self.assertEqual(
            sha256(component[358_028:358_378]),
            "0ad76b15e6571c8fd731574abf8fa25744c21731f3b619dec39033525ae4aa8e",
        )
        self.assertNotEqual(
            component[358_028:358_378],
            OFFICIAL.read_bytes()[358_028:358_378],
        )
        self.assertNotIn(UPSTREAM.read_bytes(), component)

        rollback_raw = bytearray(
            component[PACKAGE_PREAMBLE:]
        )
        rollback_offset = 357_996 - PACKAGE_PREAMBLE
        rollback_raw[rollback_offset:rollback_offset + 32] = bytes.fromhex(
            STOCK_HEX
        )
        rollback_component = open_cfw.wrap_main_image(bytes(rollback_raw))
        self.assertEqual(
            rollback_component[
                PACKAGE_PREAMBLE + STOCK_SPAN[0] - APPLICATION_BASE:
                PACKAGE_PREAMBLE + STOCK_SPAN[1] - APPLICATION_BASE
            ],
            OFFICIAL.read_bytes()[
                PACKAGE_PREAMBLE + STOCK_SPAN[0] - APPLICATION_BASE:
                PACKAGE_PREAMBLE + STOCK_SPAN[1] - APPLICATION_BASE
            ],
        )
        self.assertEqual(
            rollback_component[
                PACKAGE_PREAMBLE:
                PACKAGE_PREAMBLE + STOCK_SPAN[0] - APPLICATION_BASE
            ],
            component[
                PACKAGE_PREAMBLE:
                PACKAGE_PREAMBLE + STOCK_SPAN[0] - APPLICATION_BASE
            ],
        )
        self.assertEqual(
            rollback_component[
                PACKAGE_PREAMBLE + STOCK_SPAN[1] - APPLICATION_BASE:
            ],
            component[PACKAGE_PREAMBLE + STOCK_SPAN[1] - APPLICATION_BASE:],
        )

        build_parent = ROOT / "build"
        build_parent.mkdir(exist_ok=True)
        outputs: list[dict[str, bytes]] = []
        for label in ("a", "b"):
            with tempfile.TemporaryDirectory(
                prefix=f"open-cfw-skip-string-package-{label}-",
                dir=build_parent,
            ) as raw:
                output = Path(raw)
                open_cfw.build(MANIFEST, output, toolchain_profile=profile)
                outputs.append({
                    name: (output / name).read_bytes()
                    for name in (
                        "package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin",
                        "build-report.json",
                        "flash-plan.json",
                    )
                })
        self.assertEqual(outputs[0], outputs[1])
        pins = expected_build["package_artifacts"]
        for name, expected in pins.items():
            self.assertEqual(
                (len(outputs[0][name]), sha256(outputs[0][name])),
                expected,
            )
        report = json.loads(outputs[0]["build-report.json"])
        plan = json.loads(outputs[0]["flash-plan.json"])
        self.assertEqual(
            (
                report["placed_region_count"],
                report["unresolved_region_count"],
                report["container_region_count"],
            ),
            expected_build["census"],
        )
        self.assertEqual(
            (
                len(plan["flash_regions"]),
                len(plan["unresolved_flash_regions"]),
                len(plan["container_only_regions"]),
            ),
            expected_build["census"],
        )
        plan_ownership: dict[str, tuple[int, int]] = {}
        all_plan_regions = (
            plan["flash_regions"]
            + plan["unresolved_flash_regions"]
            + plan["container_only_regions"]
        )
        for status in {region["address_status"] for region in all_plan_regions}:
            selected = [
                region for region in all_plan_regions
                if region["address_status"] == status
            ]
            plan_ownership[status] = (
                len(selected),
                sum(region["size"] for region in selected),
            )
        if profile == "apple-clang":
            self.assertEqual(
                plan_ownership,
                {
                    "confirmed_from_record_table": (4, 211_824),
                    "confirmed_from_vector_and_ota_code": (1, 55_752),
                    "container_only": (5, 268),
                    "generated_alignment": (123, 243),
                    "generated_source_entry_replacement": (740, 99_846),
                    "generated_source_exact_load_image": (1, 6),
                    "generated_source_exact_replacement": (7, 134),
                    "inferred_from_vector_table": (1, 34_432),
                    "official_blob": (228, 3_571_759),
                    "source_compiled": (298, 146_335),
                    "unknown": (2, 326_044),
                },
            )
        source_owned_bytes = sum(
            region["size"]
            for region in plan["flash_regions"]
            if region["address_status"] == "source_compiled"
        )
        generated_flash_bytes = sum(
            region["size"]
            for region in plan["flash_regions"]
            if region["address_status"].startswith("generated_")
        )
        merged = open_cfw.load_manifest(MANIFEST)
        provider_bytes = 0
        for component_record in merged["components"]:
            provider = component_record["provider"]
            selected = open_cfw.profile_pins(provider, profile)
            provider_bytes += int((selected or provider)["size"])
        package_name = (
            "package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
        )
        package_envelope_bytes = pins[package_name][0] - provider_bytes
        main_preamble_bytes = next(
            region["size"]
            for region in main["regions"]
            if region["name"] == "ota_preamble"
        )
        generated_bytes = (
            generated_flash_bytes
            + package_envelope_bytes
            + main_preamble_bytes
        )
        opaque_bytes = pins[package_name][0] - source_owned_bytes - generated_bytes
        self.assertEqual(
            (source_owned_bytes, generated_bytes, opaque_bytes),
            expected_build["effective_ownership"],
        )
        plan_by_name = {
            region["region"]: region for region in plan["flash_regions"]
        }
        expected_plan_regions = {
            "nanopb_skip_string_source_replacement": (
                PROJECTED_PRODUCTION_PROFILES[profile]["replacement_sha256"]
            ),
        }
        if profile == "apple-clang":
            expected_plan_regions.update({
                "apollo_nanopb_skip_string_source_alignment": (
                    "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"
                ),
                "apollo_nanopb_skip_string_source_leaf": (
                    PROJECTED_PRODUCTION_PROFILES[profile]["relocated_sha256"]
                ),
            })
        else:
            self.assertIn("apollo_main_source_appended", plan_by_name)
        self.assertEqual(
            {
                name: plan_by_name[name]["sha256"]
                for name in expected_plan_regions
            },
            expected_plan_regions,
        )
        self.assertFalse(any(
            "pb_decode.c" in region["artifact"]
            for region in all_plan_regions
            if "artifact" in region
        ))
        self.assertNotIn(
            UPSTREAM.read_bytes(),
            outputs[0][
                "package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
            ],
        )


class NanopbSkipStringProductionIntegrationTests(StableUnittestIdentityCase):
    maxDiff = None

    def _build_host_library(
        self,
        clang: str,
        output: Path,
        sources: list[Path],
        define: str | None = None,
    ) -> None:
        command = [
            clang,
            "-O2", "-Wall", "-Wextra", "-Werror",
            "-I", str(ROOT),
            "-I", str(SNAPSHOT),
            "-include", str(CONFIG),
        ]
        if define is not None:
            command.append(f"-D{define}=1")
        command.extend(str(path) for path in sources)
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(output)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(output)))
        subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_real_provider_integration_matches_upstream(self) -> None:
        for path, relative in (
            (PRODUCTION_SOURCE, PRODUCTION_SOURCE_PATH),
            (PRODUCTION_HEADER, PRODUCTION_HEADER_PATH),
        ):
            if not path.is_file():
                self.fail(
                    "missing production integration prerequisite:\n" + relative
                )

        providers = [
            ROOT / "components/shared/nanopb/runtime_nanopb_decode_varint32.c",
            ROOT / "components/shared/nanopb/runtime_nanopb_readbyte.c",
            ROOT / "components/shared/nanopb/runtime_nanopb_read.c",
            UPSTREAM,
            SNAPSHOT / "pb_common.c",
            FIXTURE,
        ]
        for provider in providers:
            self.assertTrue(
                provider.is_file(),
                "missing real-provider integration file:\n"
                + provider.relative_to(ROOT).as_posix(),
            )

        clang = os.environ.get("OPENCFW_CLANG", APPLE_CLANG)
        suffix = ".dylib" if sys.platform == "darwin" else ".so"
        with tempfile.TemporaryDirectory(
            prefix="open-cfw-nanopb-skip-string-integration-"
        ) as temporary:
            temporary_path = Path(temporary)
            real_library_path = temporary_path / ("real" + suffix)
            seam_library_path = temporary_path / ("seam" + suffix)
            self._build_host_library(
                clang,
                real_library_path,
                [PRODUCTION_SOURCE, *providers],
            )
            self._build_host_library(
                clang,
                seam_library_path,
                [PRODUCTION_SOURCE, FIXTURE],
                "OPENCFW_SKIP_STRING_PRODUCTION_SEAM_PROBE",
            )

            seam_library = ctypes.CDLL(str(seam_library_path))
            seam_test = (
                seam_library.open_cfw_test_nanopb_skip_string_production_seams
            )
            seam_test.argtypes = []
            seam_test.restype = ctypes.c_int
            self.assertEqual(seam_test(), 0)

            library = ctypes.CDLL(str(real_library_path))
            canonical_test = (
                library.open_cfw_test_nanopb_skip_string_canonical_buffer
            )
            canonical_test.argtypes = []
            canonical_test.restype = ctypes.c_int
            self.assertEqual(canonical_test(), 0)

            runners = (
                library.open_cfw_test_nanopb_skip_string_run_production,
                library.open_cfw_test_nanopb_skip_string_run_upstream,
            )
            for runner in runners:
                runner.argtypes = [
                    ctypes.POINTER(ctypes.c_uint8),
                    ctypes.c_size_t,
                    ctypes.c_size_t,
                    ctypes.c_uint32,
                    ctypes.c_uint32,
                    ctypes.c_size_t,
                    ctypes.c_uint32,
                    ctypes.POINTER(SkipStringIntegrationResult),
                ]
                runner.restype = None

            def run(
                runner: ctypes._CFuncPtr,
                payload: bytes,
                *,
                budget: int | None = None,
                fail_call: int = 0,
                mutate_call: int = 0,
                mutated_budget: int = 0,
                sticky: int = 0,
            ) -> tuple[object, ...]:
                storage = (ctypes.c_uint8 * max(1, len(payload)))()
                if payload:
                    storage[:len(payload)] = payload
                result = SkipStringIntegrationResult()
                runner(
                    storage,
                    len(payload),
                    len(payload) if budget is None else budget,
                    fail_call,
                    mutate_call,
                    mutated_budget,
                    sticky,
                    ctypes.byref(result),
                )
                return result.comparable()

            def encode(value: int) -> bytes:
                encoded = bytearray()
                while value >= 0x80:
                    encoded.append((value & 0x7F) | 0x80)
                    value >>= 7
                encoded.append(value)
                return bytes(encoded)

            cases: list[tuple[str, bytes, dict[str, int]]] = []
            for length in (0, 1, 3, 15, 16, 17, 127, 128, 300):
                encoded = encode(length)
                payload = bytes(index & 0xFF for index in range(length))
                cases.append((f"length-{length}", encoded + payload, {}))
                cases.append((
                    f"budget-longer-{length}",
                    encoded + payload + b"\xa5",
                    {},
                ))

            valid_five = b"\x80\x80\x80\x80\x01"
            for stop in range(len(valid_five)):
                cases.append((f"truncated-length-{stop}", valid_five[:stop], {}))
                cases.append((
                    f"short-length-budget-{stop}",
                    valid_five,
                    {"budget": stop},
                ))
            cases.extend((
                ("fifth-byte-overflow", b"\x80\x80\x80\x80\x10", {}),
                ("extension-overflow", b"\x80\x80\x80\x80\x80\x01", {}),
                ("sticky-fifth-overflow", b"\x80\x80\x80\x80\x10", {"sticky": 1}),
            ))

            encoded_seventeen = encode(17)
            payload_seventeen = bytes(range(17))
            for stop in range(18):
                cases.append((
                    f"truncated-payload-{stop}",
                    encoded_seventeen + payload_seventeen[:stop],
                    {},
                ))
            full_seventeen = encoded_seventeen + payload_seventeen
            for call in range(1, 4):
                cases.append((
                    f"callback-failure-{call}",
                    full_seventeen,
                    {"fail_call": call},
                ))
            for call in range(1, 4):
                cases.append((
                    f"callback-budget-mutation-{call}",
                    full_seventeen,
                    {"mutate_call": call, "mutated_budget": call & 1},
                ))
            cases.extend((
                ("payload-budget-short", b"\x03\x11\x22\x33", {"budget": 3}),
                ("payload-budget-equal", b"\x03\x11\x22\x33", {"budget": 4}),
                ("payload-budget-long", b"\x03\x11\x22\x33", {"budget": 5}),
                ("sticky-end-of-stream", b"\x03\x11\x22", {"sticky": 1}),
                ("sticky-io", b"\x03\x11\x22\x33", {"fail_call": 2, "sticky": 1}),
            ))

            for name, payload, arguments in cases:
                with self.subTest(name=name):
                    observed = [run(runner, payload, **arguments) for runner in runners]
                    self.assertEqual(observed[0], observed[1])

            empty = run(runners[0], b"\x00")
            self.assertEqual(empty[:5], (1, 0, 1, 1, 1))
            self.assertEqual(empty[5][:1], (1,))
            self.assertEqual(empty[6:], (0, 1, 0))

            three = run(runners[0], b"\x03\x11\x22\x33")
            self.assertEqual(three[:5], (1, 0, 4, 4, 2))
            self.assertEqual(three[5][:2], (1, 3))
            self.assertEqual(three[6:], (0, 1, 0))

            truncated = run(runners[0], b"\x03\x11\x22")
            self.assertEqual(truncated[:5], (0, 2, 1, 1, 1))
            self.assertEqual(truncated[6:], (1, 1, 0))

            io_failure = run(
                runners[0], b"\x03\x11\x22\x33", fail_call=2
            )
            self.assertEqual(io_failure[:5], (0, 3, 1, 1, 2))
            self.assertEqual(io_failure[5][:2], (1, 3))
            self.assertEqual(io_failure[6:], (2, 1, 0))

            overflow = run(runners[0], b"\x80\x80\x80\x80\x10")
            self.assertEqual(overflow[:5], (0, 0, 5, 5, 5))
            self.assertEqual(overflow[6:], (3, 1, 0))
            sticky = run(runners[0], b"\x03\x11\x22", sticky=1)
            self.assertEqual(sticky[6], 4)


if __name__ == "__main__":
    unittest.main()
