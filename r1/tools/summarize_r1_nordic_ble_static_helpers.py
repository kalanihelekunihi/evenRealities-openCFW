#!/usr/bin/env python3
"""Emit exact Nordic BLE/Peer Manager static helpers recovered from the R1 app."""

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

NORDIC_BLE_STATIC_HELPER_FUNCTIONS = [
    {
        "entry": 0x74F20,
        "end_exclusive": 0x74F38,
        "size": 24,
        "symbol": "link_init",
        "source": "components/ble/nrf_ble_gatt/nrf_ble_gatt.c",
        "sha256": "4eaaecd6df86526527dc640f2ee55ac2f887de55b090511be7460eb709ddc39e",
        "callsites": (0x781A0, 0x7821C),
    },
    {
        "entry": 0x87A94,
        "end_exclusive": 0x87AA8,
        "size": 20,
        "symbol": "ram_end_address_get",
        "source": "components/softdevice/common/nrf_sdh_ble.c",
        "sha256": "40c8328336ce8d719dc5be0579c10034500168d1d11263e682dace91cfaf0536",
        "callsites": (0x7A18E, 0x7A1AA),
    },
    {
        "entry": 0x87AAC,
        "end_exclusive": 0x87AC8,
        "size": 28,
        "symbol": "rank_highest",
        "source": "components/ble/peer_manager/peer_manager_handler.c",
        "sha256": "3ee157429905cb4462f979709dc4dfee09b10e17de2f01952b65201197a3ec27",
        "callsites": (0x7FADE, 0x7FC6C),
    },
    {
        "entry": 0x87AC8,
        "end_exclusive": 0x87AF4,
        "size": 44,
        "symbol": "rank_vars_update",
        "source": "components/ble/peer_manager/peer_manager.c",
        "sha256": "1c5d5a0e41d85abc7008181f1b554bc18bd0b9ae134c69f98f719cdbd36ef58c",
        "callsites": (0x809DC, 0x80A4C, 0x80B0A),
    },
    {
        "entry": 0x8EE0A,
        "end_exclusive": 0x8EE3A,
        "size": 42,
        "extent_size": 48,
        "symbol": "set_security_req",
        "source": "components/ble/common/ble_srv_common.c",
        "sha256": "802743d4cbb6058365d35aae1e1134bf567699c88355168539a44288738a2b81",
        "callsites": (0x579CC, 0x579D6, 0x57A42, 0x57ABC, 0x57AC6),
    },
]


def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    functions = []
    for item in NORDIC_BLE_STATIC_HELPER_FUNCTIONS:
        entry = int(item["entry"])
        end = int(item["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        calls = tuple(address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry))
        expected_extent_size = int(item.get("extent_size", item["size"]))
        if len(body) != expected_extent_size or hashlib.sha256(body).hexdigest() != item["sha256"]:
            raise ValueError(f"Nordic BLE static-helper body changed at 0x{entry:08x}")
        if calls != item["callsites"]:
            raise ValueError(f"Nordic BLE static-helper callers changed at 0x{entry:08x}")
        functions.append({
            **item,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "extent_size": expected_extent_size,
            "callsites": [f"0x{address:08x}" for address in calls],
        })

    return {
        "analysis": "Nordic BLE and Peer Manager static-helper closure",
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "extent_bytes": sum(int(item["extent_size"]) for item in functions),
        "functions": functions,
        "provider": {
            "family": "nordic_nrf5_sdk_17_1_0",
            "disposition": "use_nordic_sdk",
            "local_reimplementation_authorized": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
