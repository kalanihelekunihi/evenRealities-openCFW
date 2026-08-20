#!/usr/bin/env python3
"""Fail-closed audit of the G2 ULED display-preprocess object."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-uled-display-preprocess-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-uled-display-preprocess-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-uled-display-preprocess-provenance.tsv"
PINS = {
    FUNCTION_MAP: "9db88b10a101a620cf38df6f2b54f6dbb79d6a511fc92959539addd3a9451046",
    CLOSURE: "d0b71984e3ce298f9b9da58f2900925efc04431b0b0bf82e4694b02437d1fdc5",
    PROVENANCE: "c1be86a8dfff0a636087a539066de318ce618c685649a6faf2104b99d2c6e427",
}
BODY = (0x0046C73C, 0x0046C984)
BODY_SHA256 = "129ff88839a933f90af5ae9f3417a3ff53f90314dde5b80a5446a7147e6c3869"
POOL = (0x0046CA74, 0x0046CAB4)
POOL_SHA256 = "9f5750f76e457c7d475b1403522a3a45ba0a020fedf1aa6e4d55a74de814afc0"
COMBINED_SHA256 = "29ec9f01a08de4de1205cb2b1e97aeeb0de99d0847452b3de9419e07c84d2aa3"
ENTRY_CALLS = [(0x0046CA64, 0x0046C73C)]
ENTRY_SHA256 = "00df4de9f1d7d3c0c1a53e60fc1c050e4af970111826bbdc2565fbc12b359331"
BODY_CALLS = 23
BODY_CALL_SHA256 = "a61d201f9347d71c44066cdf808e05da05ca24f2035db59b1999c5eb69c81bda"
RAW_INTERIOR_WINDOWS = [
    (0x0048FEA9, 0x0046C879),
    (0x004B34E9, 0x0046C809),
]
WORDS = {
    0x0046CA74: 0x00785A80,
    0x0046CA78: 0x0076ACCC,
    0x0046CA7C: 0x0077ECBC,
    0x0046CA80: 0x006F9CBC,
    0x0046CA84: 0x00785A90,
    0x0046CA88: 0x00776904,
    0x0046CA8C: 0x0077691C,
    0x0046CA90: 0x0077ECD0,
    0x0046CA94: 0x0077ECE4,
    0x0046CA98: 0x0077ECF8,
    0x0046CA9C: 0x007490EC,
    0x0046CAA0: 0x00749114,
    0x0046CAA4: 0x0076ACE8,
    0x0046CAA8: 0x0075F2F0,
    0x0046CAAC: 0x0078D3C4,
    0x0046CAB0: 0x0073DC94,
}
STRINGS = {
    0x00785A80: "ptr_des != NULL",
    0x0076ACCC: "Asserted at expression: %s",
    0x0077ECBC: "buffer_sync_to_fb",
    0x006F9CBC: r"D:\01_workspace\s200_ap510b_iar_git\driver\uled\display_preprocess.c",
    0x00785A90: "ptr_src != NULL",
    0x00776904: "des_width > src_width",
    0x0077691C: "des_hight > src_hight",
    0x0077ECD0: "offset_x % 2 == 0",
    0x0077ECE4: "src_width % 2 == 0",
    0x0077ECF8: "des_width % 2 == 0",
    0x007490EC: "((uint32_t)ptr_des & 0x00000007) == 0",
    0x00749114: "((uint32_t)ptr_src & 0x00000007) == 0",
    0x0075F2F0: "GPU start failed, result = %d\r\n",
    0x0078D3C4: "display",
    0x0073DC94: "[display]GPU start failed, result = %d\r\n",
}
TEMPLATE = bytes.fromhex(
    "19060000000000000000000000000000000000000000000000000000"
)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sl(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def pairs(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def load(name: str, path: Path):
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def cstring(blob: bytes, address: int) -> str:
    offset = address - BASE
    end = blob.find(b"\0", offset)
    return blob[offset:end].decode("ascii")


def thumb_bw_target(blob: bytes, address: int) -> int | None:
    offset = address - BASE
    first, second = struct.unpack_from("<HH", blob, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != 3_523_396 or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1:
        raise AuditError("function inventory changed")
    row = rows[0]
    if (
        int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
    ) != BODY or sha256(sl(blob, *BODY)) != BODY_SHA256:
        raise AuditError("function body changed")
    if sha256(sl(blob, *POOL)) != POOL_SHA256:
        raise AuditError("owned pool changed")
    if sha256(sl(blob, *BODY) + sl(blob, *POOL)) != COMBINED_SHA256:
        raise AuditError("combined object changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"pool word changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    if sl(blob, 0x0076ACE8, 0x0076AD04) != TEMPLATE:
        raise AuditError("GPU descriptor template changed")

    decoder = load(
        "uled_display_preprocess_thumb",
        ROOT / "tools/recover_apollo_embedded_source_paths.py",
    )
    starts = {BODY[0]}
    interiors = set(range(BODY[0] + 2, BODY[1], 2))
    entry = []
    interior_bl = []
    entry_bw = []
    interior_bw = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(blob, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior_bl.append((site, target))
        target = thumb_bw_target(blob, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    if entry != ENTRY_CALLS or pairs(entry) != ENTRY_SHA256 or interior_bl:
        raise AuditError("BL entry/interior closure changed")
    if entry_bw or interior_bw:
        raise AuditError("B.W entry/interior closure changed")

    calls = []
    for site in range(BODY[0], BODY[1] - 3, 2):
        target = decoder._thumb_bl_target(blob, site)
        # 0x46C972 is the second halfword of the valid 32-bit SDIV at
        # [0x46C970,0x46C974), not a BL instruction.
        if target is not None and site != 0x0046C972:
            calls.append((site, target))
    if len(calls) != BODY_CALLS or pairs(calls) != BODY_CALL_SHA256:
        raise AuditError("provider-call closure changed")
    if sl(blob, 0x0046C970, 0x0046C974) != bytes.fromhex("99fbf0f0"):
        raise AuditError("qualified SDIV overlap changed")

    stored = []
    for encoded in (BODY[0], BODY[0] | 1):
        position = blob.find(struct.pack("<I", encoded))
        while position >= 0:
            stored.append((BASE + position, encoded))
            position = blob.find(struct.pack("<I", encoded), position + 1)
    if stored:
        raise AuditError("stored entry pointer appeared")
    encoded_interiors = interiors | {value | 1 for value in interiors}
    raw_windows = [
        (BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded_interiors
    ]
    if raw_windows != RAW_INTERIOR_WINDOWS or any(site % 2 == 0 for site, _ in raw_windows):
        raise AuditError("raw interior overlap qualification changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/uled_display_preprocess.c"
    candidate_sha256 = "2ded39fb95b869de5361340416b85d598194de8c7e7d90f57eefbbde8044b98b"
    expected_patches = {
        "replace_buffer_sync_to_fb": (
            0x0046C73C, 584, BODY_SHA256,
            "open_cfw_uled_buffer_sync_to_fb",
        ),
    }
    patches = {
        row["name"]: row
        for row in overlay["patch_sites"]
        if row.get("name") in expected_patches
    }
    leaves = {
        row["function"]: row
        for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == candidate
    }
    assert_binding = (
        "-DOPEN_CFW_ULED_ASSERT(condition, expression)="
        "do { if (!(condition)) { (void)(expression); for (;;) { } } } while (0)"
    )
    if (
        set(patches) != set(expected_patches)
        or any(
            patches[name]["runtime_address"] != address
            or patches[name]["expected_size"] != size
            or patches[name]["expected_sha256"] != digest
            or patches[name]["branch"] != "b_w"
            or patches[name]["target_function"] != target
            or patches[name].get("profiles") != ["apple-clang"]
            for name, (address, size, digest, target) in expected_patches.items()
        )
        or set(leaves) != {target for *_, target in expected_patches.values()}
        or any(
            leaf["source"]["sha256"] != candidate_sha256
            or leaf.get("profiles") != ["apple-clang"]
            or assert_binding not in leaf["toolchain"]["flags"]
            for leaf in leaves.values()
        )
    ):
        raise AuditError("production display-preprocess routing changed")

    return {
        "surface": {
            "linked_functions": 1,
            "body_bytes": 584,
            "owned_pool_bytes": 64,
            "object_bytes": 648,
            "direct_bl_ingress_sites": 1,
            "direct_provider_calls": 23,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 2,
        },
        "abi": {
            "arguments": [
                "destination", "source", "destination_width",
                "destination_height", "source_width", "source_height",
                "offset_x", "offset_y",
            ],
            "destination_descriptor_bytes": 28,
            "source_region_bytes": 16,
            "destination_control": "0x00000619",
            "pixel_width_divisor": 2,
            "source_format": 9,
            "pointer_alignment": 8,
        },
        "behavior": {
            "preconditions": list(STRINGS.values())[:1] + list(STRINGS.values())[4:12],
            "gpu_success_value": 1,
            "gpu_failure_diagnoses_and_returns": True,
            "success_programs_source_then_offset_then_commit": True,
        },
        "production": {
            "candidate": candidate,
            "candidate_sha256": candidate_sha256,
            "production_routed": True,
            "ownership_bytes": 584,
            "retained_stock_noncode_bytes": 64,
            "toolchain_profiles": ["apple-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
