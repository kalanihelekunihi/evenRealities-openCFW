#!/usr/bin/env python3
"""Pin the R1 product callback around Nordic buttonless-DFU events."""

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

R1_BUTTONLESS_DFU_EVENT_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0005232C,
    "end_exclusive": 0x00052498,
    "size": 364,
    "role": "R1 advertising/disconnect policy around Nordic buttonless-DFU events",
    "symbol": "r1_buttonless_dfu_event_policy",
    "sha256": "0e16e5502df7200684ef2bd4aa90bdca0aeb726f7938f8e4374d487273e39357",
    "callers": (),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

CALLBACK_POINTER_ADDRESS = 0x0004C944
CALLBACK_THUMB_POINTER = 0x0005232D


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_BUTTONLESS_DFU_EVENT_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - LOAD_BASE:end - LOAD_BASE]
    callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"]:
        raise ValueError("R1 buttonless-DFU event callback changed")

    pointer = struct.unpack_from(
        "<I", image, CALLBACK_POINTER_ADDRESS - LOAD_BASE
    )[0]
    if pointer != CALLBACK_THUMB_POINTER:
        raise ValueError("R1 buttonless-DFU callback registration changed")

    # Pin the three event-0 product/provider seams inside the complete body.
    calls = {
        0x000523A2: (bytes.fromhex("f6f720fb"), "r1_advertising_params_init", 0x000489E6),
        0x000523AE: (bytes.fromhex("fff726fa"), "ble_advertising_modes_config_set", 0x000517FE),
        0x000523B6: (bytes.fromhex("fff73ffd"), "ble_conn_state_for_each_connected", 0x00051E38),
    }
    for callsite, (expected, _, _) in calls.items():
        actual = image[callsite - LOAD_BASE:callsite - LOAD_BASE + len(expected)]
        if actual != expected:
            raise ValueError(f"R1 buttonless-DFU policy edge changed at 0x{callsite:08x}")

    diagnostics = {
        0x000524A0: b"[RING]Device is preparing to enter bootloader mode.",
        0x00052544: b"[RING]Device will enter bootloader mode.",
        0x00052594: b"[RING]Request to enter bootloader mode failed asynchroneously.",
        0x00052610: b"[RING]Request to send a response to client failed.",
        0x00052674: b"[RING]Unknown event from ble_dfu_buttonless.",
    }
    for address, expected in diagnostics.items():
        actual = image[address - LOAD_BASE:address - LOAD_BASE + len(expected)]
        if actual != expected:
            raise ValueError(
                f"R1 buttonless-DFU diagnostic changed at 0x{address:08x}"
            )

    return {
        "analysis": "R1 product policy around Nordic buttonless-DFU events",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 364,
        "ghidra_function_count": 0,
        "manual_supplement_count": 1,
        "functions": [{
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [],
        }],
        "registration": {
            "initializer": "0x0004c92c",
            "nordic_init_target": "0x000520e4",
            "callback_pointer_address": f"0x{CALLBACK_POINTER_ADDRESS:08x}",
            "callback_thumb_pointer": f"0x{pointer:08x}",
            "direct_callers_expected": 0,
        },
        "event_policy": {
            "0_prepare": {
                "disable_advertising_on_disconnect": True,
                "disconnect_all_connected_links": True,
                "report_disconnected_link_count": True,
            },
            "1_enter": "diagnostic only",
            "2_enter_failed": "diagnostic only",
            "3_response_send_error": "diagnostic only",
            "other": "unknown-event diagnostic only",
        },
        "dependencies": {
            "event_0_calls": [
                {"callsite": f"0x{callsite:08x}", "symbol": symbol,
                 "target": f"0x{target:08x}"}
                for callsite, (_, symbol, target) in calls.items()
            ],
            "nordic_operations_executed_by_clean_planner": False,
            "logger_admitted": False,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "nordic_buttonless_dfu_remains_upstream": True,
            "reset_or_bootloader_handoff_admitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
