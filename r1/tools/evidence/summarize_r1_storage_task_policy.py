#!/usr/bin/env python3
"""Pin the Ghidra-omitted group-0 R1 storage task policy."""

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

R1_STORAGE_TASK_POLICY_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00046954,
    "end_exclusive": 0x00046A2C,
    "size": 216,
    "symbol": "r1_storage_task_plan_startup",
    "sha256": "61783b8da754a2b95093818781cc1328f25b6143d9dcd983b285bb119f979e33",
    "callers": (),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

EXPECTED_CALLS = {
    0x000923B4: ((0x00046958, "BL"),),
    0x0007D3B4: ((0x00046962, "BL"),),
    0x00045D00: ((0x0004696E, "BL"),),
    0x00065B4C: ((0x0004697A, "BL"),),
    0x00092440: ((0x00046980, "BL"),),
    0x0005DB14: ((0x0004698A, "BL"),),
    0x0007D780: ((0x000469AC, "BL"),),
    0x0008D888: ((0x000469E4, "BL"),),
    0x0007D310: ((0x000469F2, "BL"),),
    0x000923A4: ((0x00046A06, "BL"),),
    0x0007D154: ((0x00046A0C, "BL"),),
}


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_STORAGE_TASK_POLICY_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
    callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, entry))
    calls = {
        target: tuple(
            (address, kind)
            for address, kind in direct_thumb_branches_to(image, DEFAULT_BASE, target)
            if entry <= address < end
        )
        for target in EXPECTED_CALLS
    }
    creator_pointer = struct.unpack_from(
        "<I", image, 0x00046A6C - DEFAULT_BASE)[0]
    delayed_callback_pointer = struct.unpack_from(
        "<I", image, 0x00046A20 - DEFAULT_BASE)[0]
    registry_name = image[
        0x00046A24 - DEFAULT_BASE:0x00046A2C - DEFAULT_BASE
    ]
    callback_prefix = image[
        0x0007CA70 - DEFAULT_BASE:0x0007CA7C - DEFAULT_BASE
    ]
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"] or calls != EXPECTED_CALLS or \
            creator_pointer != 0x00046955 or \
            delayed_callback_pointer != 0x0007CA71 or \
            registry_name != b"storage\0" or \
            callback_prefix.hex() != "0022114642f2050010f040bf":
        raise ValueError("R1 group-0 storage task policy changed")

    return {
        "analysis": "R1 group-0 storage task policy",
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
            "creator_pointer_address": "0x00046a6c",
            "task_thumb_pointer": "0x00046955",
            "registry_name": "storage",
        },
        "startup": {
            "sync_group": 0,
            "queue_capacity": 10,
            "queue_record_bytes": 16,
            "delayed_callback": "0x0007ca71",
            "delayed_event": "0x2005",
            "delay_ticks": 3072,
            "watchdog_ticks": 10000,
        },
        "flags": {
            "wait_mask": "0x00ffffff",
            "dispatch_flag": "0x00400000",
            "suspend_flag": "0x00800000",
            "queue_drain_nonblocking": True,
        },
        "corrected_distinction": {
            "service_task": "0x000926dc..<0x000927ba",
            "service_sync_group": 7,
            "service_queue_capacity": 50,
            "service_registry_name": "service",
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "cmsis_provider_reimplemented": False,
            "event_dispatch_reimplemented": False,
            "live_storage_task_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
