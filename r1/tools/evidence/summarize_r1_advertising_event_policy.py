#!/usr/bin/env python3
"""Pin the Ghidra-omitted R1 advertising-event policy callback."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE
from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
CALLBACK_POINTER_ADDRESS = 0x00048AC4
STATUS_PUBLISH_TARGET = 0x0005E1CC

R1_ADVERTISING_EVENT_POLICY_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0007CBC8,
    "end_exclusive": 0x0007CC54,
    "size": 140,
    "symbol": "r1_advertising_event_plan_build",
    "sha256": "623c35b360ba9ee09bb2077d2c5adc11a57cd3152c68763071bf66d935562d81",
    "callers": (),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

EXPECTED_STRINGS = {
    0x0007CC5C: b"[RING]Fast advertising.",
    0x0007CC74: b"Fast advertising.",
    0x0007CC88: b"[RING]Slow advertising.",
    0x0007CCA0: b"Slow advertising.",
}


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_ADVERTISING_EVENT_POLICY_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
    callers = tuple(
        address for address, _kind in
        direct_thumb_branches_to(image, DEFAULT_BASE, entry)
    )
    callback_pointer = struct.unpack_from(
        "<I", image, CALLBACK_POINTER_ADDRESS - DEFAULT_BASE
    )[0]
    status_sites = tuple(
        (address, kind) for address, kind in
        direct_thumb_branches_to(image, DEFAULT_BASE, STATUS_PUBLISH_TARGET)
        if entry <= address < end
    )
    strings = {
        address: image[address - DEFAULT_BASE:
                       address - DEFAULT_BASE + len(expected)]
        for address, expected in EXPECTED_STRINGS.items()
    }
    log_literals = tuple(struct.unpack_from(
        "<II", image, end - DEFAULT_BASE
    ))
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"] or \
            callback_pointer != entry + 1 or \
            status_sites != ((0x0007CC48, "B.W"),) or \
            strings != EXPECTED_STRINGS or \
            log_literals != (0x000C44FC, 0x000C441C):
        raise ValueError("R1 advertising-event policy changed")

    return {
        "analysis": "R1 advertising-event policy callback",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": int(function["size"]),
        "ghidra_function_count": 0,
        "manual_supplement_count": 1,
        "function": {
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [],
        },
        "registration": {
            "callback_pointer_address": f"0x{CALLBACK_POINTER_ADDRESS:08x}",
            "callback_thumb_pointer": f"0x{callback_pointer:08x}",
            "direct_callers_expected": 0,
        },
        "status_publish": {
            "tail_callsite": "0x0007cc48",
            "target": f"0x{STATUS_PUBLISH_TARGET:08x}",
        },
        "behavior": {
            "event_0": {"publish": True, "active": False, "mode": 0},
            "event_3": {"publish": True, "active": True, "mode": 1,
                        "log": "Fast advertising."},
            "event_4": {"publish": True, "active": True, "mode": 2,
                        "log": "Slow advertising."},
            "other_events": {"publish": False, "log": False},
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "nordic_advertising_reimplemented": False,
            "logging_reimplemented": False,
            "status_transport_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
