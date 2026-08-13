#!/usr/bin/env python3
"""Pin the composite R1 PMIC-charged notification orchestration routine."""

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

R1_PMIC_CHARGED_NOTIFICATION_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00096CC8,
    "end_exclusive": 0x00096DB4,
    "size": 374,
    "role": "R1 PMIC-charged retry, mailbox, and completion orchestration",
    "symbol": "r1_pmic_charged_notification_plan",
    "sha256": "a00d2417c36d598e48d0372052fabccf0444ea0ced5a0252ba33983ad912a34f",
    "ranges": ((0x00047F10, 0x00047F9A), (0x00096CC8, 0x00096DB4)),
    "callers": ((0x00046218, "BL"), (0x000463D4, "BL")),
    "inventory": "ghidra_functions_csv",
},)


def flash_bytes(image: bytes, start: int, end: int) -> bytes:
    if start < LOAD_BASE or end < start or end - LOAD_BASE > len(image):
        raise ValueError(f"range outside recovered image: 0x{start:08x}...0x{end:08x}")
    return image[start - LOAD_BASE:end - LOAD_BASE]


def word(image: bytes, address: int) -> int:
    return struct.unpack("<I", flash_bytes(image, address, address + 4))[0]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    function = R1_PMIC_CHARGED_NOTIFICATION_FUNCTIONS[0]
    ranges = tuple(function["ranges"])
    bodies = [flash_bytes(image, start, end) for start, end in ranges]
    body = b"".join(bodies)
    callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, int(function["entry"])))
    scatter_callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, 0x00047F10))
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"] or \
            scatter_callers != ((0x00096D66, "B.W"),):
        raise ValueError("PMIC-charged composite function changed")

    pointer_literals = {
        "retry_callback_scatter": word(image, 0x00047F9C),
        "post_charge_callback": word(image, 0x00047FA0),
        "device_callback": word(image, 0x00047FA4),
        "retry_callback_main": word(image, 0x00096DFC),
    }
    if pointer_literals != {
        "retry_callback_scatter": 0x00096A61,
        "post_charge_callback": 0x00042D29,
        "device_callback": 0x00042D2F,
        "retry_callback_main": 0x00096A61,
    }:
        raise ValueError(f"PMIC-charged callback literals changed: {pointer_literals}")

    verified_ranges = []
    for (start, end), bytes_ in zip(ranges, bodies):
        verified_ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "bytes": len(bytes_),
            "sha256": hashlib.sha256(bytes_).hexdigest(),
        })

    return {
        "analysis": "R1 PMIC-charged notification policy closure",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": len(body),
        "composite_body_sha256": hashlib.sha256(body).hexdigest(),
        "verified_ranges": verified_ranges,
        "callers": [
            {"callsite": f"0x{address:08x}", "kind": kind}
            for address, kind in callers
        ],
        "scatter_transfer": {"callsite": "0x00096d66", "kind": "B.W"},
        "pointer_literals": {
            key: f"0x{value:08x}" for key, value in pointer_literals.items()
        },
        "retry_policy": {
            "marker": "0xa5",
            "current_sense_millivolts_strictly_below": 50,
            "battery_millivolts_strictly_below": 4200,
            "largest_old_counter_retried": 12,
            "counter_update": "UInt8 post-increment with wrap",
            "recovery_gpio_pulse_milliseconds": 200,
            "retry_delay_milliseconds": 409,
            "not_charging_retains_incremented_counter": True,
            "full_or_failed_gate_clears_counter": True,
        },
        "completion_policy": {
            "interrupt_touch_close_mask": "0x08",
            "mailbox_enable_on_first_zero_status": True,
            "charge_event_uses_second_status_after_enable": True,
            "post_charge_delay_milliseconds": 5120,
            "marker_not_charging_thread_flag": "0x10",
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "clean_room_api": "r1_pmic_plan_charged_notification",
            "nordic_gpio_or_cmsis_reimplemented": False,
            "st25dvxxkc_reimplemented": False,
            "delayed_event_loop_reimplemented_here": False,
            "touch_or_device_registry_reimplemented": False,
        },
        "safety": {
            "pure_planner_only": True,
            "live_gpio_operation": False,
            "live_mailbox_operation": False,
            "live_timer_operation": False,
            "live_thread_flag_operation": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
