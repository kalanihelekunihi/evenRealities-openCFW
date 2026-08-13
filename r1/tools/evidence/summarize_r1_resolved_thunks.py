#!/usr/bin/env python3
"""Pin R1 branch-only thunks whose destinations already have accepted ownership."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

RESOLVED_THUNKS = (
    {
        "entry": 0x29D58, "target": 0x2B91C, "size": 4,
        "symbol": "goodix_provider_entry_thunk", "provider": "goodix_gh3x2x_candidate",
        "sha256": "5369da3475924b136084c9ea7d7ffb227e82b82fa688514febeb529840b738cf",
        "callsites": (0x2AD60,),
    },
    {
        "entry": 0x6F8F6, "target": 0x509B0, "size": 4,
        "symbol": "r1_goodix_board_line_prepare_thunk", "provider": "r1_goodix_provider_adapter",
        "sha256": "6504c3dd834dceb1308723768c59882aee98a92e1871097b5c98ddaae7bd3112",
        "callsites": (0x2D986,),
    },
    {
        "entry": 0x8A7F0, "target": 0x5A9F8, "size": 4,
        "symbol": "r1_activity_daily_cache_refresh_metadata_thunk", "provider": "r1_product_specific",
        "sha256": "48e55172c73a11cb770e7959a8d4ba7921479309f764a1d1f700b6046ca2d189",
        "callsites": (0x9270E,),
    },
    {
        "entry": 0x8D534, "target": 0x5AD08, "size": 4,
        "symbol": "r1_heart_rate_daily_cache_refresh_metadata_thunk", "provider": "r1_product_specific",
        "sha256": "d3819a08a80b6d96fb3e412bc1f6aa997ffa620983e0d8c86cda507ce3bf710b",
        "callsites": (0x926FE,),
    },
    {
        "entry": 0x8D884, "target": 0x5AF44, "size": 4,
        "symbol": "r1_hrv_daily_cache_refresh_metadata_thunk", "provider": "r1_product_specific",
        "sha256": "9834b354a6e6496ecf5dbc2a67e3ed20a8d90c9d82d8815425ab5bd0716354f9",
        "callsites": (0x92716,),
    },
    {
        "entry": 0x8E54E, "target": 0x5BB14, "size": 4,
        "symbol": "r1_spo2_daily_cache_refresh_metadata_thunk", "provider": "r1_product_specific",
        "sha256": "dffa470e88d4e39089f6b1a385e5117912651154a49205fe0f6a1964e9f08085",
        "callsites": (0x92702,),
    },
    {
        "entry": 0x8E558, "target": 0x5BCD4, "size": 4,
        "symbol": "r1_stress_daily_cache_refresh_metadata_thunk", "provider": "r1_product_specific",
        "sha256": "36abc19673406800e8abfb0abf1bdd904e19ff2badfb0af3e9a6655f7bcac8aa",
        "callsites": (0x9270A,),
    },
    {
        "entry": 0x8E69C, "target": 0x5BE64, "size": 4,
        "symbol": "r1_temperature_daily_cache_refresh_metadata_thunk", "provider": "r1_product_specific",
        "sha256": "0dca46584331f0e760693db166f54c36f4559b0a2a1c99548e31cbabadd065cb",
        "callsites": (0x92706,),
    },
)


def decode_branch_target(body: bytes, address: int) -> tuple[int, str]:
    if len(body) != 4:
        raise ValueError("resolved thunk must contain one 32-bit Thumb branch")
    first, second = struct.unpack("<HH", body)
    if first & 0xF800 != 0xF000:
        raise ValueError("resolved thunk does not begin with a Thumb-2 branch")
    if second & 0xD000 == 0xD000:
        kind = "BL"
    elif second & 0xD000 == 0x9000:
        kind = "B.W"
    else:
        raise ValueError("resolved thunk has an unsupported Thumb-2 encoding")
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 - (j1 ^ sign)
    i2 = 1 - (j2 ^ sign)
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22) |
                 ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1))
    if sign:
        immediate -= 1 << 25
    return address + 4 + immediate, kind


def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")
    output: list[dict[str, object]] = []
    for item in RESOLVED_THUNKS:
        entry = int(item["entry"])
        size = int(item["size"])
        body = image[entry - LOAD_BASE:entry - LOAD_BASE + size]
        target, kind = decode_branch_target(body, entry)
        calls = tuple(address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry))
        if hashlib.sha256(body).hexdigest() != item["sha256"]:
            raise ValueError(f"resolved thunk body changed at 0x{entry:08x}")
        if target != item["target"] or kind != "B.W" or calls != item["callsites"]:
            raise ValueError(f"resolved thunk topology changed at 0x{entry:08x}")
        output.append({
            **item,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{entry + size:08x}",
            "target": f"0x{target:08x}",
            "branch_kind": kind,
            "callsites": [f"0x{address:08x}" for address in calls],
        })
    return {
        "analysis": "branch-only thunks with already accepted target ownership",
        "image_sha256": digest,
        "function_count": len(output),
        "function_bytes": sum(int(item["size"]) for item in RESOLVED_THUNKS),
        "functions": output,
        "local_reimplementation_required": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
