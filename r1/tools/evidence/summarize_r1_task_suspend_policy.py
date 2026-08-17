#!/usr/bin/env python3
"""Pin the Ghidra-omitted R1 all-task suspend and barrier policies."""

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

R1_TASK_SUSPEND_POLICY_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x00046D10,
        "end_exclusive": 0x00046DCC,
        "size": 188,
        "symbol": "r1_task_suspend_broadcast_plan_build",
        "sha256": "27aaed8b4c2f758025abee09a50088b081b72de1e49188f0385f398683f845b1",
        "callers": ((0x00046BF2, "BL"),),
        "inventory": "manual_provenance_supplement",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
    {
        "entry": 0x00046DCC,
        "end_exclusive": 0x00046E64,
        "size": 152,
        "symbol": "r1_task_suspend_barrier_plan_build",
        "sha256": "9147a124d72ca9559e39ce1df6ef9dbbb964486f1487c83fc3a57d0126709cc6",
        "callers": ((0x00045DB8, "BL"),),
        "inventory": "manual_provenance_supplement",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
)

BROADCAST_STATE_BLOCKS = (
    0x20006608, 0x200066D8, 0x2000668C, 0x20006630, 0x20006664,
    0x20006590, 0x200065BC, 0x200065E0, 0x20006568, 0x200066B0,
)
BARRIER_STATE_BLOCKS = (
    0x200066D8, 0x20006630, 0x20006590, 0x200065BC, 0x200065E0,
    0x2000668C, 0x20006608, 0x20006664, 0x20006568, 0x200066B0,
)
BROADCAST_GROUPS_NORMAL = (5, 0, 7, 1, 9, 2, 3, 10, 4)
BROADCAST_GROUPS_FACTORY = (6, 0, 7, 1, 9, 2, 3, 10, 4)
BARRIER_GROUPS_NORMAL = (0, 1, 2, 3, 10, 7, 5, 9, 4)
BARRIER_GROUPS_FACTORY = (0, 1, 2, 3, 10, 7, 6, 9, 4)


def _local_calls(image: bytes, target: int, start: int, end: int) -> tuple[tuple[int, str], ...]:
    return tuple(
        (address, kind)
        for address, kind in direct_thumb_branches_to(image, DEFAULT_BASE, target)
        if start <= address < end
    )


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    functions = []
    for function in R1_TASK_SUSPEND_POLICY_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
        callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"R1 task suspend policy changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"address": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    broadcast_literals = struct.unpack_from(
        "<10I", image, 0x00046DA4 - DEFAULT_BASE)
    barrier_literals = struct.unpack_from(
        "<10I", image, 0x00046E3C - DEFAULT_BASE)
    broadcast_thread_calls = _local_calls(image, 0x0007D6F4, 0x00046D10, 0x00046DCC)
    barrier_helper_calls = _local_calls(image, 0x00046A74, 0x00046DCC, 0x00046E64)
    configuration_calls = (
        _local_calls(image, 0x0007BA24, 0x00046D10, 0x00046DCC) +
        _local_calls(image, 0x0007BA24, 0x00046DCC, 0x00046E64)
    )
    if broadcast_literals != BROADCAST_STATE_BLOCKS or \
            barrier_literals != BARRIER_STATE_BLOCKS or \
            tuple(address for address, _ in broadcast_thread_calls) != (
                0x00046D26, 0x00046D34, 0x00046D42, 0x00046D50, 0x00046D5E,
                0x00046D6C, 0x00046D7A, 0x00046D88, 0x00046D96,
            ) or \
            tuple(address for address, _ in barrier_helper_calls) != (
                0x00046DD4, 0x00046DDE, 0x00046DE8, 0x00046DF2, 0x00046DFC,
                0x00046E06, 0x00046E18, 0x00046E22, 0x00046E30,
            ) or \
            configuration_calls != ((0x00046D12, "BL"), (0x00046E0A, "BL")):
        raise ValueError("R1 task suspend call topology changed")

    return {
        "analysis": "R1 all-task suspend and acknowledgment-barrier policies",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 2,
        "function_bytes": 340,
        "ghidra_function_count": 0,
        "manual_supplement_count": 2,
        "functions": functions,
        "configuration_marker": 0x55,
        "thread_suspend_flag": "0x00800000",
        "broadcast": {
            "normal_groups": BROADCAST_GROUPS_NORMAL,
            "factory_groups": BROADCAST_GROUPS_FACTORY,
            "normal_acknowledgment_mask": "0x000006bf",
            "factory_acknowledgment_mask": "0x000006df",
            "wait_performed_by_function": False,
        },
        "barrier": {
            "normal_groups": BARRIER_GROUPS_NORMAL,
            "factory_groups": BARRIER_GROUPS_FACTORY,
            "per_group_wait_ticks": 0x5000,
            "helper": "0x00046a74",
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "cmsis_provider_reimplemented": False,
            "thread_handles_exposed": False,
            "live_suspend_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
