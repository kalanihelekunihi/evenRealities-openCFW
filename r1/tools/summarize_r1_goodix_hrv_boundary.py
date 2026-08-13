#!/usr/bin/env python3
"""Pin the recovered Goodix GH_HRV_pre lifecycle provider boundary.

This is an ownership census only. It emits no HRV algorithm implementation
and does not convert recovered vendor behavior into clean-room product source.
"""

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
EXPECTED_ENTRY_SHA256 = "5d00efc0a826654ac002cee73aeeda84e69f6c81fc991f3956a5bba88072e94c"
EXPECTED_BODY_SHA256 = "aaba0810ef55686cf7586f7cdacac44216270be51917646ec1f75ba803ca390e"
EXPECTED_CALLMAP_SHA256 = "0ee900c0e4ed7d80407fa9fc77c285df7853da797a3e298e6601f118e144a60a"


def _function(
    entry: int,
    end_exclusive: int,
    role: str,
    sha256: str,
    callsites: tuple[int, ...],
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": end_exclusive - entry,
        "segments": ((entry, end_exclusive),),
        "role": role,
        "sha256": sha256,
        "callsites": callsites,
        "provider_family": "goodix_gh3x2x_candidate",
        "source_disposition": "vendor_source_required_not_redistributable",
    }


GOODIX_HRV_FUNCTIONS = (
    _function(0x0002CAC6, 0x0002CAD8, "GH_HRV cleanup dispatcher wrapper",
              "27c7d76e02dad56ace113457e230a47d5a69b94b7bc28ca5cd89249471ab3a10", ()),
    _function(0x0002CC5C, 0x0002CC8A, "GH_HRV output dispatcher wrapper",
              "1c99f01aebe38c71aa7d6f148663edbf2d593f4465905be6afe0b6a7c46868dc", ()),
    _function(0x0006DA9C, 0x0006DAA0, "GH_HRV configuration getter",
              "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587",
              (0x0006DF30,)),
    _function(0x0006DAA4, 0x0006DAC2, "GH_HRV ABI-version copier",
              "f595f1227bb91f1d67c7de7117688a31213f4514c70638950a78c4797702ffd5",
              (0x0006DF4E,)),
    _function(0x0006DAD0, 0x0006DB4E, "GH_HRV lifecycle cleanup",
              "886b5c54d82852ec40178761ec3cc672329c136712dbd8701f9d39791ec89e95",
              (0x0006DB58,)),
    _function(0x0006DB58, 0x0006DB5C, "GH_HRV cleanup thunk",
              "b401802475194a1daaaa8f9c76d050008c57c4f579161e884655d31a683de4ca",
              (0x0002CACC,)),
    _function(0x0006DB5C, 0x0006DEFA, "GH_HRV lifecycle initializer",
              "ae78ff00fe0b4c0eff52bf5110a3080e69d8e5de76135c124af8436e749e8344",
              (0x0006DF58,)),
    _function(0x0006DF14, 0x0006DF60, "GH_HRV output wrapper",
              "b092cfc73f83ad7a4a6d152564c6b555d02614decd7d9097a0f48203e2b54e3b",
              (0x0002CC68,)),
    _function(0x0006DF60, 0x0006DF9A, "GH_HRV version builder",
              "3f1a1e8b1dbb1338e45fd0df817491c0ffd54189e53828ed3ba313aa3a64a6b0",
              (0x0002A14C, 0x0006DF2C)),
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {image_digest}")

    ordered = tuple(sorted(GOODIX_HRV_FUNCTIONS, key=lambda item: item["entry"]))
    entry_digest = hashlib.sha256(b"".join(
        int(item["entry"]).to_bytes(4, "little") for item in ordered
    )).hexdigest()
    bodies = []
    callmap = []
    output = []
    for item in ordered:
        entry = int(item["entry"])
        end = int(item["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        calls = tuple(address for address, _ in direct_thumb_branches_to(
            image, LOAD_BASE, entry
        ))
        if len(body) != item["size"] or \
                hashlib.sha256(body).hexdigest() != item["sha256"] or \
                calls != item["callsites"]:
            raise ValueError(f"Goodix GH_HRV boundary changed at 0x{entry:08x}")
        bodies.append(body)
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
    if entry_digest != EXPECTED_ENTRY_SHA256 or \
            body_digest != EXPECTED_BODY_SHA256 or \
            callmap_digest != EXPECTED_CALLMAP_SHA256:
        raise ValueError("Goodix GH_HRV aggregate changed")

    for address, marker in {
        0x0006DAC4: b"pv_v1.1.0",
        0x0006DEFC: b"pv_v1.1.0",
        0x0006DF9C: b"GH_HRV_pre",
        0x0006DFAC: b"_v1.0.1.0",
        0x0006DFBC: b"ed953ff3",
    }.items():
        actual = image[address - LOAD_BASE:address - LOAD_BASE + len(marker)]
        if actual != marker:
            raise ValueError(f"Goodix GH_HRV identity changed at 0x{address:08x}")

    return {
        "analysis": "Goodix GH_HRV_pre lifecycle provider-boundary closure",
        "image": str(image_path),
        "image_sha256": image_digest,
        "entry_set_sha256": entry_digest,
        "body_set_sha256": body_digest,
        "callmap_sha256": callmap_digest,
        "function_count": len(output),
        "function_bytes": sum(int(item["size"]) for item in output),
        "newly_classified_count": 7,
        "newly_classified_bytes": 1154,
        "functions": output,
        "identity": {
            "component": "Goodix GH_HRV_pre",
            "component_version": "v1.0.1.0",
            "component_hash": "ed953ff3",
            "private_abi_version": "pv_v1.1.0",
            "initializer": "0x0006db5c",
            "output_wrapper": "0x0006df14",
        },
        "boundary": {
            "provider_family": "goodix_gh3x2x_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "local_algorithm_reimplementation_authorized": False,
            "licensed_provider_required": True,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
