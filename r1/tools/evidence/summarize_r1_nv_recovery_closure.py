#!/usr/bin/env python3
"""Pin the R1-owned nonvolatile recovery/report/merge closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_ENTRY_SHA256 = "8bd9e43e86aefb51394aa641311dc15eb4add92eb8b9bcd9996c1145472f8f69"
EXPECTED_BODY_SHA256 = "e02a1e3a725492dc0847c40422cdad1dbda32008ba7d6eaeb09575ea059a1357"
EXPECTED_CALLMAP_SHA256 = "004db3a5f8c868b6d8561bb36cf189a7e033e5b7ab946066d3841bac8eb77a4f"


def _function(
    entry: int,
    end_exclusive: int,
    symbol: str,
    sha256: str,
    inventory: str = "ghidra_function",
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": end_exclusive - entry,
        "segments": ((entry, end_exclusive),),
        "symbol": symbol,
        "sha256": sha256,
        "inventory": inventory,
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only_security_preserving",
    }


R1_NV_RECOVERY_FUNCTIONS = (
    _function(
        0x0007B634, 0x0007B80E, "r1_nv_recovery_report_builder",
        "a52a3645704c7dd3a770fa785c01275370ca0e532abbe03bb320ba888c9f02bd",
    ),
    _function(
        0x0007BBE8, 0x0007BC96, "r1_nv_recovery_report_sender",
        "2485c9f81628c30a724b584256143ae463ad1d21fad9b408570a6ecfd5d556fc",
        "manual_provenance_supplement",
    ),
    _function(
        0x0007BD68, 0x0007C140, "r1_nv_recovery_fill_only_merge",
        "62b4081caf575abf6acfb3f9d09d5a1ea30370a6c0d4005b13146102f2cc8758",
    ),
    _function(
        0x0007C450, 0x0007C4BC, "r1_nv_recovery_command_dispatch",
        "5b5f75179f6420c7951024f2b5c215cec131b9591db56bd77a698fe8524786dd",
        "manual_provenance_supplement",
    ),
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {image_digest}")

    ordered = tuple(sorted(R1_NV_RECOVERY_FUNCTIONS, key=lambda item: item["entry"]))
    entry_digest = hashlib.sha256(b"".join(
        int(item["entry"]).to_bytes(4, "little") for item in ordered
    )).hexdigest()
    if entry_digest != EXPECTED_ENTRY_SHA256:
        raise ValueError("R1 NV-recovery entry set changed")

    output = []
    bodies = []
    callmap = []
    for item in ordered:
        entry = int(item["entry"])
        end = int(item["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        if len(body) != item["size"] or hashlib.sha256(body).hexdigest() != item["sha256"]:
            raise ValueError(f"R1 NV-recovery body changed at 0x{entry:08x}")
        bodies.append(body)
        calls = tuple(address for address, _ in direct_thumb_branches_to(
            image, LOAD_BASE, entry
        ))
        callmap.append([f"0x{entry:08x}", [f"0x{x:08x}" for x in calls]])
        output.append({
            **item,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callsites": [f"0x{x:08x}" for x in calls],
            "segments": [{
                "start": f"0x{entry:08x}",
                "end_exclusive": f"0x{end:08x}",
                "size": end - entry,
            }],
        })

    body_digest = hashlib.sha256(b"".join(bodies)).hexdigest()
    callmap_digest = hashlib.sha256(json.dumps(
        callmap, separators=(",", ":")
    ).encode()).hexdigest()
    if body_digest != EXPECTED_BODY_SHA256 or callmap_digest != EXPECTED_CALLMAP_SHA256:
        raise ValueError("R1 NV-recovery aggregate changed")

    expected_calls = {
        0x0007B634: (0x0007BC02,),
        0x0007BBE8: (0x0007C4B6, 0x0008478A),
        0x0007BD68: (0x0007C46E,),
        0x0007C450: (0x000841FA,),
    }
    for item in output:
        entry = int(item["entry"], 16)
        actual = tuple(int(value, 16) for value in item["callsites"])
        if actual != expected_calls[entry]:
            raise ValueError(f"R1 NV-recovery caller map changed at 0x{entry:08x}")

    markers = {
        0x0007B844: b"[NV_RECOVER] nv_recover is NULL",
        0x0007B890: b"[NV_RECOVER] invalid battery_type: %d",
        0x0007C1C8: b"[NV_RECOVER] crc mismatch, expected: %d, calc: %d",
        0x0007C228: b"[NV_RECOVER] set battery type: %d",
        0x0007C320: b"[NV_RECOVER] set product bsn: %d %d %d",
        0x0007C42C: b"[NV_RECOVER] set acc cal: %d %d %d",
    }
    for address, expected in markers.items():
        actual = image[address - LOAD_BASE:address - LOAD_BASE + len(expected)]
        if actual != expected:
            raise ValueError(f"R1 NV-recovery marker changed at 0x{address:08x}")

    return {
        "analysis": "R1 nonvolatile recovery/report/merge closure",
        "image": str(image_path),
        "image_sha256": image_digest,
        "entry_set_sha256": entry_digest,
        "body_set_sha256": body_digest,
        "callmap_sha256": callmap_digest,
        "function_count": len(output),
        "function_bytes": sum(int(item["size"]) for item in output),
        "ghidra_function_count": sum(
            item["inventory"] == "ghidra_function" for item in output
        ),
        "ghidra_function_bytes": sum(
            int(item["size"]) for item in output
            if item["inventory"] == "ghidra_function"
        ),
        "manual_supplement_count": sum(
            item["inventory"] == "manual_provenance_supplement" for item in output
        ),
        "manual_supplement_bytes": sum(
            int(item["size"]) for item in output
            if item["inventory"] == "manual_provenance_supplement"
        ),
        "functions": output,
        "protocol": {
            "command": 2,
            "body_bytes": 116,
            "checksum": "CRC-16/MODBUS",
            "checksum_initial": "0xffff",
            "checksum_polynomial_reflected": "0xa001",
        },
        "records": {
            "configuration": {"name": "nv_r1", "bytes": 124},
            "power": {"name": "power", "bytes": 4},
            "ring_size": {"name": "r_size", "bytes": 1},
        },
        "security": {
            "normal_ble_command_enabled": False,
            "local_implementation": "bounded pure report builder and fill-only merge planner",
            "transport_sender_implemented": False,
            "persistent_commit_implemented_by_planner": False,
            "identity_logging_allowed": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
