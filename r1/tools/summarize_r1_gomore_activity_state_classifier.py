#!/usr/bin/env python3
"""Pin the private GoMore activity-state window-classifier closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
EXPECTED_ENTRY_SHA256 = "47cb99f74ac44c03e214f1d4cd35c568602e050f075ddce5d8cc4ca479b17144"
EXPECTED_BODY_SHA256 = "6b381f9cd413c1f30230f816f8bee1c12972e6838258e5d6173566c3de19ba54"
EXPECTED_CALLMAP_SHA256 = "fec22d001832d8150466a57e8a63be30d24ff22c70bdbe4825ec0ad0b9222cfb"


def _function(
    entry: int,
    end_exclusive: int,
    symbol: str,
    sha256: str,
    callsites: tuple[int, ...],
    *,
    segments: tuple[tuple[int, int], ...] | None = None,
) -> dict[str, Any]:
    body_segments = segments or ((entry, end_exclusive),)
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": sum(end - start for start, end in body_segments),
        "segments": body_segments,
        "symbol": symbol,
        "sha256": sha256,
        "callsites": callsites,
        "provider_family": "gomore_health_algorithm_candidate",
        "source_disposition": "vendor_source_required_not_redistributable",
    }


GOMORE_ACTIVITY_STATE_FUNCTIONS = (
    _function(
        0x0006138C,
        0x000616E6,
        "gomore_activity_state_window_classifier_candidate",
        "304129c450524d72d526b45c9e2e3e16852347b6cc73657f985b72002eaff823",
        (0x000604E2, 0x000604F6),
        segments=(
            (0x0006138C, 0x000613F2),
            (0x000613FA, 0x00061698),
            (0x000616A0, 0x000616BA),
            (0x000616C2, 0x000616E6),
        ),
    ),
    _function(
        0x00064A98,
        0x00064B06,
        "gomore_activity_state_range_statistic_candidate",
        "c4518fe6d5bf5afb4c00f0903171e1bbd3ab3829e825ffdaf2ce36442c42d0fd",
        (0x00096EE4,),
    ),
    _function(
        0x0006859C,
        0x0006871A,
        "gomore_activity_state_peak_statistic_candidate",
        "f51b6fb0e4ec3526df1060b79b85725995a9311b8bfb0ceb3f12767f9f76b6e6",
        (0x00096EC2, 0x00096ED4, 0x00096F58, 0x00096F6A),
    ),
    _function(
        0x00069FA8,
        0x0006A014,
        "gomore_activity_state_crossing_interval_candidate",
        "a211cf0971b9982c16c65f8a2d8c7efbb9ba58b6470139b78e27642f7f1829e9",
        (0x00096EAA,),
    ),
    _function(
        0x00093FAC,
        0x0009405A,
        "gomore_activity_state_input_conditioner_candidate",
        "bef53b6ab483345a60798b28fe67a4a8945348ce089a80eff97b9dd692e9cb4a",
        (0x000613E4,),
    ),
    _function(
        0x00096E74,
        0x00096F8E,
        "gomore_activity_state_window_decision_candidate",
        "99682e234eac35fc5b435801470c0cf0f9ffe8d45e839c542dd7557c1d497a8a",
        (0x00061546,),
    ),
)


EXPECTED_JUMP_TABLES = (
    (0x000613F2, bytes.fromhex("0416070b160f1300")),
    (0x00061698, bytes.fromhex("040707070a0a0a00")),
    (0x000616BA, bytes.fromhex("040e04040e040400")),
)
EXPECTED_LITERAL_POOL = (
    0x000616E8,
    0x00061720,
    "00261d959d5aae5d8556180f5f8e9d1e63ae1ca24dd1e114b6fedf272273b1d4",
)


def _mapped(image: bytes, start: int, end: int) -> bytes:
    return image[start - LOAD_BASE:end - LOAD_BASE]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {image_digest}")

    ordered = tuple(sorted(GOMORE_ACTIVITY_STATE_FUNCTIONS, key=lambda item: item["entry"]))
    entry_digest = hashlib.sha256(b"".join(
        int(item["entry"]).to_bytes(4, "little") for item in ordered
    )).hexdigest()
    bodies: list[bytes] = []
    callmap: list[list[Any]] = []
    output = []
    for item in ordered:
        entry = int(item["entry"])
        body = b"".join(_mapped(image, start, end) for start, end in item["segments"])
        calls = tuple(address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != item["size"] or \
                hashlib.sha256(body).hexdigest() != item["sha256"] or \
                calls != item["callsites"]:
            raise ValueError(f"GoMore activity-state closure changed at 0x{entry:08x}")
        bodies.append(body)
        callmap.append([f"0x{entry:08x}", [f"0x{x:08x}" for x in calls]])
        output.append({
            **item,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(item['end_exclusive']):08x}",
            "callsites": [f"0x{x:08x}" for x in calls],
            "segments": [{
                "start": f"0x{start:08x}",
                "end_exclusive": f"0x{end:08x}",
                "size": end - start,
            } for start, end in item["segments"]],
        })

    body_digest = hashlib.sha256(b"".join(bodies)).hexdigest()
    callmap_digest = hashlib.sha256(json.dumps(
        callmap, separators=(",", ":")
    ).encode()).hexdigest()
    if entry_digest != EXPECTED_ENTRY_SHA256 or \
            body_digest != EXPECTED_BODY_SHA256 or \
            callmap_digest != EXPECTED_CALLMAP_SHA256:
        raise ValueError("GoMore activity-state aggregate changed")

    jump_tables = []
    for start, expected in EXPECTED_JUMP_TABLES:
        actual = _mapped(image, start, start + len(expected))
        if actual != expected:
            raise ValueError(f"GoMore activity-state jump table changed at 0x{start:08x}")
        jump_tables.append({
            "address": f"0x{start:08x}",
            "bytes": actual.hex(),
            "entry_count": 7,
        })

    literal_start, literal_end, literal_sha = EXPECTED_LITERAL_POOL
    literal_digest = hashlib.sha256(_mapped(image, literal_start, literal_end)).hexdigest()
    if literal_digest != literal_sha:
        raise ValueError("GoMore activity-state literal pool changed")

    return {
        "analysis": "GoMore activity-state window-classifier provider boundary",
        "image": str(image_path),
        "image_sha256": image_digest,
        "entry_set_sha256": entry_digest,
        "body_set_sha256": body_digest,
        "callmap_sha256": callmap_digest,
        "function_count": len(output),
        "function_bytes": sum(int(item["size"]) for item in output),
        "functions": output,
        "state_machine": {
            "state_count": 7,
            "window_samples": 25,
            "decision_samples": 250,
            "jump_tables": jump_tables,
            "literal_pool": {
                "start": f"0x{literal_start:08x}",
                "end_exclusive": f"0x{literal_end:08x}",
                "sha256": literal_digest,
            },
        },
        "boundary": {
            "provider_family": "gomore_health_algorithm_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "local_classifier_reimplementation_authorized": False,
            "licensed_provider_required": True,
            "shared_toolchain_math_included": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
