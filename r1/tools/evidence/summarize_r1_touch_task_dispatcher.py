#!/usr/bin/env python3
"""Pin the noncontiguous R1 touch-task event dispatcher and provider boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


R1_TOUCH_TASK_DISPATCHER_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00046650,
    "end_exclusive": 0x0004FB3E,
    "size": 578,
    "role": "touch-task event-bit, lifecycle, diagnostic, and factory-marker dispatcher",
    "symbol": "r1_iqs7211e_touch_task_dispatcher",
    "sha256": "3019299c9c23cbed488c51229722b18cf0166ccae126bef2cdc3a49b615fab00",
    "caller_count": 1,
    "caller_digest": "5def9232b25d02d77e13f78dc9840b3bd30ce0adeeb028fcad7478c9d2d4aae2",
    "inventory": "ghidra_functions_csv",
    "segments": (
        (0x00046650, 0x000467FA),
        (0x0004FA8C, 0x0004FAA4),
        (0x0004FAA8, 0x0004FAC0),
        (0x0004FAC4, 0x0004FADE),
        (0x0004FAE4, 0x0004FAFE),
        (0x0004FB04, 0x0004FB1E),
        (0x0004FB24, 0x0004FB3E),
    ),
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in R1_TOUCH_TASK_DISPATCHER_FUNCTIONS:
        entry = int(function["entry"])
        segments = tuple(function["segments"])
        body = b"".join(
            image[start - LOAD_BASE:end - LOAD_BASE]
            for start, end in segments
        )
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"touch-task dispatcher body mismatch at 0x{entry:08x}")
        callers = direct_thumb_branches_to(image, LOAD_BASE, entry)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"touch-task dispatcher caller set mismatch at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in segments
            ],
        })

    return {
        "analysis": "R1 IQS7211E touch-task event-dispatch adapter",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 578,
        "functions": functions,
        "callgraph": {
            "direct_callsite": "0x00092822",
            "dispatch_parameter": "event-bit mask",
        },
        "event_bits": {
            "0x000001": "ready/IRQ worker",
            "0x000002": "hardware open and shared-power acquisition",
            "0x000004": "hardware close and optional ATI-recovery restart scheduling",
            "0x000010": "ALP ATI diagnostic log",
            "0x000020": "trackpad ATI diagnostic log",
            "0x000040": "factory marker 1 transaction",
            "0x000080": "factory marker 2 transaction",
            "0x000100": "factory marker 3 transaction with one-byte result",
            "0x000200": "factory marker 4 transaction with two-byte result",
            "0x000400": "factory marker 5 transaction with one-byte result",
            "0x000800": "factory marker 6 transaction with four-byte result",
            "0x400000": "deferred callback path",
            "0x800000": "fatal task/storage path",
        },
        "factory_transactions": {
            "count": 6,
            "marker_values": [1, 2, 3, 4, 5, 6],
            "communication_begin": "0x00046f60",
            "provider_communication_end": "0x0002f866",
            "communication_close": "0x00046f54",
        },
        "boundary": {
            "provider_family": "r1_iqs7211e_provider_adapter",
            "source_disposition": "clean_room_adapter_only_use_pinned_provider",
            "iqs7211e_controller_or_register_logic_reimplemented": False,
            "nordic_or_cmsis_rtos_reimplemented": False,
            "shared_power_provider_reimplemented": False,
            "logging_frontend_reimplemented": False,
            "unresolved_hardware_wrappers_admitted": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_gpio_or_i2c_access": False,
            "factory_command_sender_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
