#!/usr/bin/env python3
"""Pin the R1-specific NFC dock mailbox and field-control policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _function(entry: int, size: int, symbol: str, role: str, sha256: str,
              callers: tuple[tuple[int, str], ...]) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": entry + size,
        "size": size,
        "symbol": symbol,
        "role": role,
        "sha256": sha256,
        "callers": callers,
        "inventory": "ghidra_functions_csv",
        "provider_family": "r1_st25dvxxkc_provider_adapter",
        "source_disposition": "clean_room_adapter_only_use_pinned_provider",
    }


R1_NFC_DOCK_POLICY_FUNCTIONS = (
    _function(
        0x000772A8, 142, "r1_st25dvxxkc_dock_advertisement_send",
        "R1 23-byte dock-advertisement command framing and send orchestration",
        "831d81b9484b6ed2e7551144aa1a831fb9cea0bec4afe5535e0cc7e1cd74ffa3",
        ((0x000774F0, "BL"),),
    ),
    _function(
        0x00077430, 466, "r1_st25dvxxkc_dock_frame_policy",
        "dock identity heartbeat, delay selection, and field-control dispatch",
        "ae5760b9a6ac03ac46642f7e19b90b11b0e630c406e443902ce1cb31c99a30e1",
        ((0x00077C44, "BL"),),
    ),
    _function(
        0x00096A48, 6, "r1_st25dvxxkc_field_seen_get",
        "R1 NFC-field-seen state accessor",
        "8292370a09b6beb685b201c7106057995b3213e3f1681af6649f9a5c52de0d2d",
        ((0x000628BA, "BL"),),
    ),
    _function(
        0x00096A54, 6, "r1_st25dvxxkc_field_seen_set",
        "R1 NFC-field-seen state mutator",
        "0594a3e6604c4c62a70819ee5094ceab26fb2eb8fbb5280fd4b92fff602100ce",
        ((0x000774D2, "BL"),),
    ),
)


EXPECTED_LITERALS = {
    0x0007760C: 0x20006858,
    0x00077760: 0x00032175,
    0x00096A50: 0x20006870,
    0x00096A5C: 0x20006870,
}


def _bytes(image: bytes, start: int, size: int) -> bytes:
    offset = start - LOAD_BASE
    if offset < 0 or offset + size > len(image):
        raise ValueError(f"range outside recovered image: 0x{start:08x}+{size}")
    return image[offset:offset + size]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    functions = []
    for function in R1_NFC_DOCK_POLICY_FUNCTIONS:
        entry = int(function["entry"])
        body = _bytes(image, entry, int(function["size"]))
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"NFC dock-policy closure changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    literals = {}
    for address, expected in EXPECTED_LITERALS.items():
        actual = struct.unpack("<I", _bytes(image, address, 4))[0]
        if actual != expected:
            raise ValueError(f"NFC dock literal changed at 0x{address:08x}")
        literals[f"0x{address:08x}"] = f"0x{actual:08x}"

    return {
        "analysis": "R1 product NFC dock mailbox and field-control policy",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "literals": literals,
        "behavior": {
            "identity_header": [1, 2, 3, 4],
            "mailbox_ready_byte": 0x81,
            "control_packet_bytes": 23,
            "advertisement_subcommand": 3,
            "charge_field_subcommand": 4,
            "heartbeat_stop_after": 60,
            "field_delay_threshold": 44,
            "short_and_long_delay_seconds": [4, 60],
            "charge_field_callback_ticks": 0x800,
            "field_seen_state_address": "0x20006871",
        },
        "boundary": {
            "provider_family": "r1_st25dvxxkc_provider_adapter",
            "source_disposition": "clean_room_adapter_only_use_pinned_provider",
            "st_mailbox_status_and_transport_external": True,
            "delayed_callback_and_logging_external": True,
            "live_nfc_or_timer_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
