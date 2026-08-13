#!/usr/bin/env python3
"""Emit the exact R1 FreeRTOS stack-overflow configuration callback seam."""

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

FREERTOS_STACK_OVERFLOW_FUNCTIONS = [
    {
        "entry": 0x00095BFC,
        "end_exclusive": 0x00095C44,
        "size": 72,
        "symbol": "r1_freertos_stack_overflow_hook_configuration",
        "provider_family": "r1_provider_configuration_glue",
        "sha256": "bcfd3bdbdaad628a3ac9e550e4bd7b5a14f25d994357e84a5e250d2ebfddf8da",
        "callsites": (0x000965E4,),
    },
]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    functions: list[dict[str, Any]] = []
    for function in FREERTOS_STACK_OVERFLOW_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"FreeRTOS stack-overflow callback changed at 0x{entry:08x}")
        actual_callsites = tuple(
            address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry)
        )
        if actual_callsites != function["callsites"]:
            raise ValueError(
                f"stack-overflow callback callers changed: {actual_callsites} != "
                f"{function['callsites']}"
            )
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callsites": [f"0x{address:08x}" for address in actual_callsites],
        })

    expected_strings = {
        0x00095C44: b"[RING]Stack overflow in task: %s\n\0",
        0x00095C70: b"Stack overflow in task: %s\n\0",
    }
    for address, expected in expected_strings.items():
        actual = image[address - LOAD_BASE:address - LOAD_BASE + len(expected)]
        if actual != expected:
            raise ValueError(f"stack-overflow diagnostic changed at 0x{address:08x}")

    return {
        "analysis": "R1 FreeRTOS stack-overflow configuration callback seam",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "recovered_configuration": {
            "configCHECK_FOR_STACK_OVERFLOW": 2,
            "sentinel_word": "0xa5a5a5a5",
            "sentinel_words_checked": 4,
        },
        "recovered_behavior": {
            "reports_task_name": True,
            "drains_provider_log_until_empty": True,
            "returns": False,
            "diagnostic": "Stack overflow in task: %s",
        },
        "source_lineage": {
            "status": "r1_application_configuration_over_freertos_provider",
            "provider": "Nordic SDK-bundled FreeRTOS 10.0.0",
            "local_callback_authorized": True,
            "provider_implementation_authorized": False,
        },
        "safety": {
            "static_parser_only": True,
            "freertos_provider_reimplementation_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
