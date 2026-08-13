#!/usr/bin/env python3
"""Pin the R1 MAC-keyed compiled-default nonvolatile restore boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
RESTORE_TABLE_START = 0x0009A0F8
RESTORE_RECORD_COUNT = 59
RESTORE_RECORD_BYTES = 14
RESTORE_TABLE_SHA256 = "4f0fe353d4a0b2d5ecdfc49a1a6d8c73f790d693c12ca3462ecbacb0bee5cf5c"


R1_NV_COMPILED_RESTORE_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0007C52C,
    "end_exclusive": 0x0007C71A,
    "size": 494,
    "role": "R1 MAC-keyed compiled-default NV restore",
    "symbol": "r1_nv_compiled_default_restore",
    "sha256": "433819b86093c162fa3a677ddec6ff52f19d7d378b714bf9e2c682457d382ae0",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only_security_preserving",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_NV_COMPILED_RESTORE_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - LOAD_BASE:end - LOAD_BASE]
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"]:
        raise ValueError("R1 compiled-default restore body changed")

    callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
    if callers != ((0x00042BBE, "B.W"),):
        raise ValueError(f"R1 compiled-default restore caller set changed: {callers}")
    caller_digest = hashlib.sha256("".join(
        f"{address:08x}:{kind}\n" for address, kind in callers
    ).encode()).hexdigest()

    table_size = RESTORE_RECORD_COUNT * RESTORE_RECORD_BYTES
    table = image[
        RESTORE_TABLE_START - LOAD_BASE:
        RESTORE_TABLE_START - LOAD_BASE + table_size
    ]
    if len(table) != table_size or hashlib.sha256(table).hexdigest() != RESTORE_TABLE_SHA256:
        raise ValueError("R1 compiled-default restore table changed")

    required_bytes = {
        0x0007C552: bytes.fromhex("6ddf"),
        0x0007C630: bytes.fromhex("abf7f3f8"),
        0x0007C64E: bytes.fromhex("f7f76ff9"),
        0x0007C658: bytes.fromhex("f7f76af9"),
        0x0007C682: bytes.fromhex("f7f771f9"),
        0x0007C690: bytes.fromhex("f7f76af9"),
        0x0007C694: bytes.fromhex("f6f7f8ff"),
    }
    for address, expected in required_bytes.items():
        actual = image[address - LOAD_BASE:address - LOAD_BASE + len(expected)]
        if actual != expected:
            raise ValueError(f"R1 compiled-default restore edge changed at 0x{address:08x}")

    diagnostics = {
        0x0007C750: b"[NV_RESTORE] get mac address failed",
        0x0007C7B4: b"[NV_RESTORE] mac=%X%X%X%X%X%X",
        0x0007C81C: b"[NV_RESTORE] index=%d, ring_size=%d, bat_type=%d, adc=%d",
        0x0007C888: b"[NV_RESTORE] not found in restore table",
    }
    for address, expected in diagnostics.items():
        actual = image[address - LOAD_BASE:address - LOAD_BASE + len(expected)]
        if actual != expected:
            raise ValueError(f"R1 compiled-default restore diagnostic changed at 0x{address:08x}")

    return {
        "analysis": "R1 MAC-keyed compiled-default nonvolatile restore boundary",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 494,
        "functions": [{
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
            "caller_digest": caller_digest,
        }],
        "event_route": {
            "internal_storage_event": "0x2005",
            "handler_tail_branch": "0x00042bbe",
            "ble_command": False,
        },
        "restore_table": {
            "start": f"0x{RESTORE_TABLE_START:08x}",
            "end_exclusive": f"0x{RESTORE_TABLE_START + table_size:08x}",
            "record_count": RESTORE_RECORD_COUNT,
            "record_bytes": RESTORE_RECORD_BYTES,
            "match_key_bytes": 12,
            "sha256": RESTORE_TABLE_SHA256,
            "raw_identity_rows_emitted": False,
        },
        "behavior": {
            "only_runs_when_current_battery_type_is_zero_or_ff": True,
            "reads_device_address_through_softdevice": True,
            "match_is_12_formatted_hex_bytes": True,
            "writes_ring_size_battery_type_and_adc_compensation": True,
            "commits_persistent_records": True,
            "status_success": 0,
            "status_existing_configuration": -1,
            "status_no_mac_or_no_match": -2,
        },
        "security": {
            "local_behavior_model": "abstract caller-supplied restore policy only",
            "raw_compiled_identity_table_redistributed": False,
            "live_persistent_restore_enabled": False,
            "identity_logging_enabled": False,
            "rollback_validation_required_before_enablement": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
