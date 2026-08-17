#!/usr/bin/env python3
"""Pin the R1 touch recovery-timer callback and registered task-event plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_TOUCH_RECOVERY_TIMER_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00046EAC,
    "end_exclusive": 0x00046EF4,
    "size": 72,
    "role": "clear touch recovery latch and post task open-event bit 2",
    "symbol": "r1_touch_recovery_timer_callback",
    "sha256": "9d328097ca50117b08d6ca156979e387453ea6d873a1d6922252359a6d07afbd",
    "callers": (),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

CALLBACK_POINTER_ADDRESS = 0x00046898
CALLBACK_THUMB_POINTER = 0x00046EAD


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_TOUCH_RECOVERY_TIMER_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - LOAD_BASE:end - LOAD_BASE]
    callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"]:
        raise ValueError("R1 touch recovery-timer callback changed")

    pointer = struct.unpack_from(
        "<I", image, CALLBACK_POINTER_ADDRESS - LOAD_BASE
    )[0]
    if pointer != CALLBACK_THUMB_POINTER:
        raise ValueError("R1 touch recovery-timer pointer changed")

    edges = {
        0x00046EAE: bytes.fromhex("2bf0e5fc"),  # clear latch -> 0x7287c
        0x00046EEE: bytes.fromhex("02204cf008bb"),  # event bit 2 -> 0x93504
    }
    for address, expected in edges.items():
        actual = image[address - LOAD_BASE:address - LOAD_BASE + len(expected)]
        if actual != expected:
            raise ValueError(f"R1 touch recovery edge changed at 0x{address:08x}")

    return {
        "analysis": "R1 touch recovery-timer callback",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 72,
        "ghidra_function_count": 0,
        "manual_supplement_count": 1,
        "functions": [{
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [],
        }],
        "registration": {
            "dispatcher_pointer_address": f"0x{CALLBACK_POINTER_ADDRESS:08x}",
            "callback_thumb_pointer": f"0x{pointer:08x}",
            "direct_callers_expected": 0,
        },
        "behavior": {
            "clear_recovery_pending_latch": True,
            "post_touch_task_event_flags": "0x00000002",
            "logging_only_between_actions": True,
        },
        "clean_room": {
            "planner": "src/r1_iqs7211e.c::r1_touch_recovery_timer_plan_build",
            "latch_or_rtos_operation_executed": False,
            "logging_admitted": False,
            "live_hardware_access": False,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "cmsis_or_iqs_provider_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
