#!/usr/bin/env python3
"""Pin the R1 reset-reason decoder and Nordic RESETREAS adapter closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_RESET_REASON_FUNCTIONS = (
    {
        "entry": 0x77E98,
        "extents": ((0x77E98, 0x77EE8),),
        "size": 80,
        "symbol": "r1_reset_reason_nordic_adapter",
        "sha256": "5d24b57782f7b573907ef704ee7c3b77eb3e1288b6c5e39d11f3bd2ebc9efda5",
        "callsites": (0x75FE4,),
    },
    {
        "entry": 0x8198C,
        "extents": ((0x8198C, 0x81BF8), (0x81FB8, 0x8203E)),
        "size": 754,
        "symbol": "r1_reset_reason_decode_and_report",
        "sha256": "1b23f0b5846eac38c0c83c905937dcdae6e3bba0c6ff3411b0b96f5a2ad0764f",
        "callsites": (0x77EDC,),
    },
)


def flash_bytes(image: bytes, start: int, end: int) -> bytes:
    offset = start - LOAD_BASE
    if offset < 0 or end - LOAD_BASE > len(image):
        raise ValueError(f"extent outside image: 0x{start:08x}..<0x{end:08x}")
    return image[offset:end - LOAD_BASE]


def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    output = []
    for function in R1_RESET_REASON_FUNCTIONS:
        entry = int(function["entry"])
        body = b"".join(
            flash_bytes(image, int(start), int(end))
            for start, end in function["extents"]
        )
        calls = tuple(
            address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry)
        )
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                calls != function["callsites"]:
            raise ValueError(f"R1 reset-reason function changed at 0x{entry:08x}")
        item = dict(function)
        item.update(
            entry=f"0x{entry:08x}",
            extents=[
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in function["extents"]
            ],
            callsites=[f"0x{address:08x}" for address in calls],
        )
        output.append(item)

    register_literal = int.from_bytes(flash_bytes(image, 0x77EE8, 0x77EEC), "little")
    if register_literal != 0x40000400:
        raise ValueError("RESETREAS register literal changed")

    return {
        "analysis": "R1 reset-reason clean-room closure",
        "image_sha256": digest,
        "function_count": len(output),
        "function_bytes": sum(int(item["size"]) for item in output),
        "functions": output,
        "resetreas": {
            "register": "0x40000400",
            "recognized_mask": "0x0007000f",
            "bits": {
                "pin": "0x00000001",
                "watchdog": "0x00000002",
                "software": "0x00000004",
                "lockup": "0x00000008",
                "system_off_gpio": "0x00010000",
                "system_off_lpcomp": "0x00020000",
                "system_off_debug": "0x00040000",
            },
            "zero_means": "power_on_or_brownout",
            "clear_policy": "write_raw_mask_back_after_decode",
        },
        "software_reset_trace": {
            "program_counter": True,
            "return_address": True,
            "persist_tag": True,
            "reboot_caller_only_when_persist_tag": 2,
        },
        "source_boundary": {
            "decoder": "r1_product_specific clean_room_behavior_only",
            "register_adapter": (
                "r1_nordic_sdk_provider_adapter "
                "clean_room_adapter_only_use_nordic_sdk"
            ),
            "provider": "Nordic nrf_power_resetreas_get/clear",
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
