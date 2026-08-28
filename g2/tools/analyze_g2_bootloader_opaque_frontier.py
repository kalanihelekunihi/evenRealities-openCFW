#!/usr/bin/env python3
"""Fail-closed census and admission boundary for the G2 bootloader qsort frontier."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]
RUN_BASE = 0x00410000
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
CENSUS = ROOT / "tools/manifests/g2-bootloader-opaque-frontier.tsv"
BOUNDARY = (
    ROOT / "research/admission/bootloader_opaque_frontier/"
    "runtime_bootloader_qsort_boundary.c"
)
BOUNDARY_HEADER = BOUNDARY.with_suffix(".h")
GENERIC_PROVIDER = (
    ROOT / "research/candidates/target_runtime/runtime_target_scalar_candidate.c"
)

OFFICIAL_PIN = (148599, "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5")
FILE_PINS = {
    CENSUS: (1868, "5562fedd60b909d5ce55841f43d868eb02b7ab0b6ca3d977e74b0f8ca31d6eb9"),
    BOUNDARY: (1261, "5fa3de0c7a72d5b0bead2b3d2bd631cec09ddfcf9a1f5a7ec522f77c749ac966"),
    BOUNDARY_HEADER: (1653, "16b99cb8816deea5cadf16322279464c9a4fcc622422896e165df9c9d2baa7a3"),
    GENERIC_PROVIDER: (12567, "aad6d15e8b64fe9f8fb9ae4611bb8663c1fa6a67bdc75c3e3cbc853a7b22093b"),
}

SPANS = {
    "earliest_complete_opaque_body": (
        0x0042308E, 0x004232C8,
        "80102228cb6a9eb99cd5bf229d5ca450331b2521a39e23e4e0671f7f928dbc46",
    ),
    "sequential_opaque_region": (
        0x00424120, 0x00426506,
        "fc2983e5f8dc3fff4bb4c1df407539aba19244b55b7f5c92fb68e1d196274bdb",
    ),
    "qsort_introsort_core": (
        0x00423A48, 0x00423D08,
        "9c13dd0e980154026e6c64019ce90997dcbd5abafb79aabbbf7d3def82215bb8",
    ),
    "qsort_public_wrapper": (
        0x00423D08, 0x00423D20,
        "ebab1f26584cfab24667fa6bd4a9c63641d5676a46affda15c6478a5d697d474",
    ),
    "post_mspi_source_leaf_opaque_region": (
        0x00426536, 0x00434477,
        "9ac323d625e2a97c102dac8b35e8a5c6b1366f732f340f49896c2486ad699d13",
    ),
}

EXPECTED_CALLERS = {
    0x00423A48: (0x00423BD0, 0x00423C58, 0x00423D1A),
    0x00423D08: (0x0041FA22,),
}

EXPECTED_CORE_HELPER_CALLS = {
    0x0041568C: (0x00423B30, 0x00423B3A, 0x00423B44),
    0x00423864: (0x00423AEE, 0x00423B0E, 0x00423C34, 0x00423C4E, 0x00423C9A),
    0x004238BA: (0x00423ADE, 0x00423C42),
    0x00423928: (0x00423CD4,),
    0x00423972: (0x00423A68, 0x00423A7C, 0x00423A90, 0x00423AA0),
    0x004239C2: (0x00423C7A, 0x00423CAC),
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def decode_thumb_bl(image: bytes, address: int) -> int | None:
    offset = address - RUN_BASE
    if offset < 0 or offset + 4 > len(image):
        return None
    first = int.from_bytes(image[offset:offset + 2], "little")
    second = int.from_bytes(image[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def direct_callers(image: bytes, target: int) -> tuple[int, ...]:
    return tuple(
        address
        for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
        if decode_thumb_bl(image, address) == target
    )


def audit(
    official_path: Path = OFFICIAL,
    core_manifest_path: Path = CORE_MANIFEST,
    census_path: Path = CENSUS,
    boundary_path: Path = BOUNDARY,
    boundary_header_path: Path = BOUNDARY_HEADER,
) -> dict:
    image = official_path.read_bytes()
    require((len(image), digest(image)) == OFFICIAL_PIN, "official bootloader pin changed")

    selected_pins = {
        census_path: FILE_PINS[CENSUS],
        boundary_path: FILE_PINS[BOUNDARY],
        boundary_header_path: FILE_PINS[BOUNDARY_HEADER],
        GENERIC_PROVIDER: FILE_PINS[GENERIC_PROVIDER],
    }
    for path, expected in selected_pins.items():
        payload = path.read_bytes()
        require((len(payload), digest(payload)) == expected, f"file pin changed: {path}")

    rows = list(csv.DictReader(census_path.read_text(encoding="utf-8").splitlines(), delimiter="\t"))
    require(tuple(row["name"] for row in rows) == (
        "earliest_complete_opaque_body", "sequential_opaque_region",
        "qsort_introsort_core", "qsort_public_wrapper",
        "post_mspi_source_leaf_opaque_region", "generic_mit_qsort",
    ), "frontier census rows changed")
    indexed = {row["name"]: row for row in rows}
    for name, (start, end, expected_hash) in SPANS.items():
        body = image[start - RUN_BASE:end - RUN_BASE]
        require(len(body) == end - start, f"span truncated: {name}")
        require(digest(body) == expected_hash, f"span identity changed: {name}")
        row = indexed[name]
        require(int(row["start"], 16) == start, f"census start changed: {name}")
        require(int(row["end"], 16) == end, f"census end changed: {name}")
        require(int(row["size"]) == end - start, f"census size changed: {name}")
        require(row["sha256"] == expected_hash, f"census hash changed: {name}")

    for target, expected in EXPECTED_CALLERS.items():
        require(direct_callers(image, target) == expected, f"caller closure changed: {target:#x}")
        odd = struct.pack("<I", target | 1)
        require(odd not in image, f"unexpected stored entry pointer appeared: {target:#x}")
    for target, expected in EXPECTED_CORE_HELPER_CALLS.items():
        callers = tuple(address for address in direct_callers(image, target)
                        if 0x00423A48 <= address < 0x00423D08)
        require(callers == expected, f"qsort helper graph changed: {target:#x}")

    core = image[0x00423A48 - RUN_BASE:0x00423D08 - RUN_BASE]
    wrapper = image[0x00423D08 - RUN_BASE:0x00423D20 - RUN_BASE]
    require(core[:6].hex() == "2de9f54fa3b0", "qsort core frame changed")
    require(core[-8:].hex() == "2a4639464846e5e7", "qsort core tail changed")
    require(wrapper.hex() == "002800d170471cb51c0004d0009313460a46fff795fe13bd", "qsort wrapper ABI changed")

    boundary_text = boundary_path.read_text(encoding="utf-8")
    header_text = boundary_header_path.read_text(encoding="utf-8")
    for token in (
        "SPDX-License-Identifier: MIT", "0x00423A48U", "0x00423D20U",
        "0x0041FA22U", "0x0041F9F1U", "EXACT_PROVIDER_UNSUPPORTED",
        "redistribution authority unresolved",
    ):
        require(token in boundary_text + header_text, f"typed boundary token missing: {token}")
    generic_text = GENERIC_PROVIDER.read_text(encoding="utf-8")
    require("SPDX-License-Identifier: MIT" in generic_text, "generic qsort license changed")
    require("void open_cfw_target_qsort(" in generic_text, "generic qsort disappeared")
    require("for (outer = 1U; outer < count; ++outer)" in generic_text,
            "generic qsort is no longer the reviewed insertion-sort oracle")

    manifest = json.loads(core_manifest_path.read_text(encoding="utf-8"))
    regions = manifest["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    core_name = "bootloader_memory_qsort_core_423a48_source_in_place"
    wrapper_name = "bootloader_memory_qsort_423d08_source_in_place"
    successor_name = "bootloader_hw_global_service_423d20_source_in_place"
    for name in (core_name, wrapper_name, successor_name):
        require(name in by_name, f"production region disappeared: {name}")
    qsort_core = by_name[core_name]
    qsort_wrapper = by_name[wrapper_name]
    successor = by_name[successor_name]
    require((qsort_core["target_address"], qsort_core["size"], qsort_core["address_status"])
            == (0x00423A48, 704, "source_compiled"), "production qsort core changed")
    require((qsort_wrapper["target_address"], qsort_wrapper["size"], qsort_wrapper["address_status"])
            == (0x00423D08, 24, "source_compiled"), "production qsort wrapper changed")
    require((successor["target_address"], successor["size"],
             successor["address_status"])
            == (0x00423D20, 56, "source_compiled"),
            "qsort local successor ownership changed")
    require(not any("qsort_boundary" in json.dumps(row) for row in regions),
            "typed unsupported boundary was incorrectly production-routed")

    return {
        "component": "G2 Apollo bootloader opaque frontier",
        "status": "superseded-by-exact-source-admission",
        "selected_frontier": {
            "start": 0x00423A48,
            "end": 0x00423D20,
            "bytes": 728,
            "core_bytes": 704,
            "wrapper_bytes": 24,
            "sole_public_caller": 0x0041FA22,
        },
        "census": {
            "earliest_complete_opaque_body_bytes": 570,
            "sequential_parent_region_bytes": 9190,
            "post_mspi_parent_region_bytes": 57153,
        },
        "provider": {
            "family": "openCFW clean-room exact qsort",
            "exact_release": "not required for clean-room admission",
            "source_license": "GPL-3.0-or-later",
            "binary_redistribution_authority": "source-built output under GPL-3.0-or-later",
            "generic_mit_candidate": "behavior-oracle-only",
        },
        "production": {
            "routed": True,
            "official_bytes_retained": False,
            "local_successor": {
                "start": successor["target_address"],
                "end": successor["target_address"] + successor["size"],
                "address_status": successor["address_status"],
            },
        },
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official", type=Path, default=OFFICIAL)
    parser.add_argument("--core-manifest", type=Path, default=CORE_MANIFEST)
    parser.add_argument("--census", type=Path, default=CENSUS)
    parser.add_argument("--boundary", type=Path, default=BOUNDARY)
    parser.add_argument("--boundary-header", type=Path, default=BOUNDARY_HEADER)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit(args.official, args.core_manifest, args.census,
                   args.boundary, args.boundary_header)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Bootloader opaque frontier: typed exact-provider boundary retained")
        print("  selected qsort cluster: 728 bytes at 0x00423a48")
        print("  production routing: exact source in place")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Bootloader opaque-frontier audit failed: {exc}") from exc
