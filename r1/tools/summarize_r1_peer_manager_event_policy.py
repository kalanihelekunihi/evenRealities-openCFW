#!/usr/bin/env python3
"""Pin the R1 product policy around Nordic Peer Manager events.

This is an ownership and behavior census. Nordic Peer Manager remains upstream,
and the recovered diagnostic path that prints bonding keys is not admitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000

R1_PEER_MANAGER_EVENT_FUNCTIONS = (
    {
        "entry": 0x0007F2B0,
        "end_exclusive": 0x0007FA0E,
        "size": 1052,
        "segments": ((0x0007F2B0, 0x0007F6AA), (0x0007F9EC, 0x0007FA0E)),
        "symbol": "r1_peer_manager_event_policy",
        "sha256": "b0521a6e459b45cdca31158563487448bf5a260bd5140a6398845507bcb5087b",
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    },
)


def _body(image: bytes, item: dict[str, Any]) -> bytes:
    return b"".join(
        image[start - LOAD_BASE:end - LOAD_BASE]
        for start, end in item["segments"]
    )


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {image_digest}")

    item = R1_PEER_MANAGER_EVENT_FUNCTIONS[0]
    body = _body(image, item)
    body_digest = hashlib.sha256(body).hexdigest()
    if len(body) != item["size"] or body_digest != item["sha256"]:
        raise ValueError("R1 Peer Manager event-policy body changed")

    callback_pointer = int.from_bytes(
        image[0x0004E51C - LOAD_BASE:0x0004E520 - LOAD_BASE], "little"
    )
    if callback_pointer != 0x0007F2B1:
        raise ValueError("R1 Peer Manager callback registration pointer changed")

    expected_edges = {
        0x0007FDE4: (0x0007F2B8,),
        0x0007FA5C: (0x0007F2BE, 0x0007FDD8, 0x00087AC0),
        0x0007F276: (0x0007F66E,),
        0x00080A98: (0x0007F440, 0x00082186),
        0x0008216C: (0x0007F488, 0x0007F632),
    }
    for target, expected in expected_edges.items():
        actual = tuple(address for address, _ in direct_thumb_branches_to(
            image, LOAD_BASE, target
        ))
        if actual != expected:
            raise ValueError(
                f"R1 Peer Manager edge set changed for 0x{target:08x}"
            )

    markers = {
        0x0007F6C0: b"[RING]phone connect:PM_EVT_CONN_SEC_SUCCEEDED",
        0x0007F808: b"[RING]This is a new device connecting for the first time\n",
        0x0007F878: b"[RING]encrypted get sec auth flag will notify",
        0x0007F8D0: b"[RING]encrypted not get sec auth flag will wait",
        0x0007F94C: b"[RING]New Bond, add the peer to the whitelist if possible",
        0x000BE3C0: b"[RING]PM_EVT_CONN_SEC_CONFIG_REQ",
    }
    for address, expected in markers.items():
        actual = image[address - LOAD_BASE:address - LOAD_BASE + len(expected)]
        if actual != expected:
            raise ValueError(
                f"R1 Peer Manager evidence marker changed at 0x{address:08x}"
            )

    return {
        "analysis": "R1 product Peer Manager event policy",
        "image": str(image_path),
        "image_sha256": image_digest,
        "function_count": 1,
        "function_bytes": len(body),
        "body_sha256": body_digest,
        "function": {
            **item,
            "entry": "0x0007f2b0",
            "end_exclusive": "0x0007fa0e",
            "segments": [
                {
                    "start": f"0x{start:08x}",
                    "end_exclusive": f"0x{end:08x}",
                    "size": end - start,
                }
                for start, end in item["segments"]
            ],
        },
        "registration": {
            "configuration_function": "0x0004e4b4",
            "pm_register_callsite": "0x0004e50e",
            "callback_pointer_address": "0x0004e51c",
            "callback_pointer": "0x0007f2b1",
        },
        "providers": {
            "standard_event_handler": "pm_handler_on_pm_evt",
            "flash_clean_handler": "pm_handler_flash_clean",
            "bonding_data_loader": "pm_peer_data_bonding_load",
            "security_config_reply": "pm_conn_sec_config_reply",
        },
        "security": {
            "allow_repairing": True,
            "new_bond_whitelist_mutation_recovered": False,
            "bond_is_product_authorization": False,
            "recovered_ltk_logging_path": "0x0008216c",
            "recovered_ltk_logging_admitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
