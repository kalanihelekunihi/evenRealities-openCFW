#!/usr/bin/env python3
"""Pin four Ghidra-omitted YHM2710 policy/transport entries."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE
from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_YHM2710_TRANSPORT_ENTRY_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {
        "entry": 0x000350E0,
        "end_exclusive": 0x0003510A,
        "size": 42,
        "symbol": "yhm2710_set_charging_event",
        "sha256": "14f761cd6c8124fd2847335f8d6a9073ae753cdbf2ffbe5eae3b064eedb4bde9",
        "callers": ((0x00050614, "B.W"),),
        "inventory": "manual_provenance_supplement",
        "provider_family": "yhmicros_yhm2710_candidate",
        "source_disposition": "clean_room_reimplementation_owner_authorized",
    },
    {
        "entry": 0x00050614,
        "end_exclusive": 0x00050618,
        "size": 4,
        "symbol": "yhm2710_set_charging_event",
        "sha256": "b47cb87d023eba0bd8c62727498eff741711fa1bd136b9930084637425cc3f9d",
        "callers": ((0x000463CA, "BL"),),
        "inventory": "manual_provenance_supplement",
        "provider_family": "yhmicros_yhm2710_candidate",
        "source_disposition": "clean_room_reimplementation_owner_authorized",
    },
    {
        "entry": 0x000507CC,
        "end_exclusive": 0x000507FA,
        "size": 46,
        "symbol": "yhm2710_register_read",
        "sha256": "9391d38a9bd7c3659670f94676017935dd0401f36a4c20f282ef2276df2e0832",
        "callers": ((0x0003540E, "B.W"),),
        "inventory": "manual_provenance_supplement",
        "provider_family": "yhmicros_yhm2710_candidate",
        "source_disposition": "clean_room_reimplementation_owner_authorized",
    },
    {
        "entry": 0x00050804,
        "end_exclusive": 0x00050832,
        "size": 46,
        "symbol": "yhm2710_register_write",
        "sha256": "a8bfd276bfa23466703d61cbf43a24db694d6ddedc550c096108ee92ea94b553",
        "callers": ((0x00035762, "B.W"),),
        "inventory": "manual_provenance_supplement",
        "provider_family": "yhmicros_yhm2710_candidate",
        "source_disposition": "clean_room_reimplementation_owner_authorized",
    },
)

EXPECTED_LOCAL_CALLS = {
    0x000350E0: {
        0x0003540C: ((0x000350EE, "BL"),),
        0x00035760: ((0x00035104, "BL"),),
    },
    0x00050614: {
        0x000350E0: ((0x00050614, "B.W"),),
    },
    0x000507CC: {
        0x000507A0: ((0x000507D4, "BL"),),
        0x00050608: ((0x000507D8, "BL"),),
        0x00085D2C: ((0x000507EE, "BL"),),
        0x00050558: ((0x000507F6, "B.W"),),
    },
    0x00050804: {
        0x000507A0: ((0x0005080C, "BL"),),
        0x00050608: ((0x00050810, "BL"),),
        0x00085DA8: ((0x00050826, "BL"),),
        0x00050558: ((0x0005082E, "B.W"),),
    },
}


def _local_calls(
    image: bytes, start: int, end: int, target: int,
) -> tuple[tuple[int, str], ...]:
    return tuple(
        item for item in direct_thumb_branches_to(image, DEFAULT_BASE, target)
        if start <= item[0] < end
    )


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    functions = []
    for function in R1_YHM2710_TRANSPORT_ENTRY_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - DEFAULT_BASE:end - DEFAULT_BASE]
        callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, start))
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"] or \
                any(_local_calls(image, start, end, target) != expected
                    for target, expected in EXPECTED_LOCAL_CALLS[start].items()):
            raise ValueError(f"R1 YHM2710 entry changed at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": tuple(
                {"address": f"0x{address:08x}", "kind": kind}
                for address, kind in callers),
        })

    return {
        "analysis": "R1 YHM2710 omitted policy and transport entries",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 4,
        "function_bytes": sum(
            int(item["size"])
            for item in R1_YHM2710_TRANSPORT_ENTRY_FUNCTIONS),
        "ghidra_function_count": 0,
        "manual_supplement_count": 4,
        "functions": functions,
        "charging_event_contract": {
            "register": 3,
            "set_mask": 8,
            "preserve_other_bits": True,
            "thunk_entry": "0x00050614",
            "target_entry": "0x000350e0",
        },
        "transport_contract": {
            "read_entry": "0x000507cc",
            "read_public_veneer": "0x0003540c",
            "read_operation": "device_slot_04",
            "write_entry": "0x00050804",
            "write_public_veneer": "0x00035760",
            "write_operation": "device_slot_04_write",
            "common_release_tail": "0x00050558",
            "completion_callback_optional": True,
        },
        "boundary": {
            "provider_family": "yhmicros_yhm2710_candidate",
            "source_disposition":
                "clean_room_reimplementation_owner_authorized",
            "opaque_yhm2710_binary_used": False,
            "live_transport_exposed_by_evidence_tool": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2,
                     sort_keys=True))


if __name__ == "__main__":
    main()
