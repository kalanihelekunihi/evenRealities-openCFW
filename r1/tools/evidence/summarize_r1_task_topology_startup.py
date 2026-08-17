#!/usr/bin/env python3
"""Pin the Ghidra-omitted R1 task-topology startup dispatcher."""

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

EXECUTABLE_START = 0x00046B20
EXECUTABLE_END = 0x00046B84
ENVELOPE_END = 0x00046BAC

R1_TASK_TOPOLOGY_STARTUP_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": EXECUTABLE_START,
    "end_exclusive": ENVELOPE_END,
    "size": ENVELOPE_END - EXECUTABLE_START,
    "symbol": "r1_task_topology_startup_plan_build",
    "sha256": "f6c8b8a76aa9208b6a16d0437a6a01f27fdfed719a160d196af39b2a33403be4",
    "callers": ((0x00045DA0, "BL"),),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

STATE_BLOCK_LITERALS = (
    0x200066D8, 0x20006630, 0x20006590, 0x200065BC, 0x200065E0,
    0x20006568, 0x2000668C, 0x20006608, 0x20006664, 0x200066B0,
)
NORMAL_GROUP_ORDER = (0, 1, 2, 3, 10, 4, 7, 5, 9)
FACTORY_GROUP_ORDER = (0, 1, 2, 3, 10, 4, 7, 6, 9)


def _local_calls(image: bytes, target: int) -> tuple[tuple[int, str], ...]:
    return tuple(
        item for item in direct_thumb_branches_to(image, DEFAULT_BASE, target)
        if EXECUTABLE_START <= item[0] < EXECUTABLE_END
    )


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")
    function = R1_TASK_TOPOLOGY_STARTUP_FUNCTIONS[0]
    envelope = image[EXECUTABLE_START - DEFAULT_BASE:
                     ENVELOPE_END - DEFAULT_BASE]
    executable = image[EXECUTABLE_START - DEFAULT_BASE:
                       EXECUTABLE_END - DEFAULT_BASE]
    callers = tuple(direct_thumb_branches_to(
        image, DEFAULT_BASE, EXECUTABLE_START))
    literals = struct.unpack_from(
        "<10I", image, EXECUTABLE_END - DEFAULT_BASE)
    if len(envelope) != 140 or \
            hashlib.sha256(envelope).hexdigest() != function["sha256"] or \
            len(executable) != 100 or \
            hashlib.sha256(executable).hexdigest() != \
            "32c34c30488b792c3e6af4b4d411adb9fba635857e81fcf2ee0354304b455f82" or \
            callers != function["callers"] or \
            literals != STATE_BLOCK_LITERALS or \
            executable.count(b"\x80\x47") != 9 or \
            _local_calls(image, 0x00065740) != ((0x00046B22, "BL"),) or \
            _local_calls(image, 0x0005DAB4) != ((0x00046B26, "BL"),) or \
            _local_calls(image, 0x0007BA24) != ((0x00046B5E, "BL"),) or \
            _local_calls(image, 0x0007D814) != (
                (0x00046B30, "BL"), (0x00046B72, "BL")) or \
            _local_calls(image, 0x0007D8A6) != (
                (0x00046B36, "BL"), (0x00046B7C, "B.W")):
        raise ValueError("R1 task-topology startup changed")

    return {
        "analysis": "R1 task-topology startup dispatcher",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": len(envelope),
        "executable_bytes": len(executable),
        "ghidra_function_count": 0,
        "manual_supplement_count": 1,
        "function": {
            **function,
            "entry": f"0x{EXECUTABLE_START:08x}",
            "end_exclusive": f"0x{ENVELOPE_END:08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        },
        "executable": {
            "start": f"0x{EXECUTABLE_START:08x}",
            "end_exclusive": f"0x{EXECUTABLE_END:08x}",
            "bytes": len(executable),
            "sha256": hashlib.sha256(executable).hexdigest(),
        },
        "startup_policy": {
            "preinitializers": ("firmware_event_loop", "watchdog_registry"),
            "normal_groups": NORMAL_GROUP_ORDER,
            "factory_groups": FACTORY_GROUP_ORDER,
            "configuration_marker": 0x55,
            "initial_thread_priority": 8,
            "final_thread_priority": 0x35,
            "indirect_task_creators": 9,
        },
        "state_block_literals": tuple(
            f"0x{address:08x}" for address in literals),
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "cmsis_freertos_reimplemented": False,
            "task_creator_pointers_exposed": False,
            "state_block_addresses_exposed": False,
            "live_task_creation_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2,
                     sort_keys=True))


if __name__ == "__main__":
    main()
