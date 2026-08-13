#!/usr/bin/env python3
"""Pin the R1 BLE connection-parameter observer and its product accessors."""

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
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    }


R1_CONNECTION_PARAMETER_FUNCTIONS = (
    _function(
        0x0004CB34, 6, "r1_glasses_connection_handle_get",
        "product glasses-role connection-handle accessor",
        "e144876acc5d13f879e211a20a854160bc17ba433c0b67e296f74cd659921186",
        ((0x00031010, "BL"), (0x0003DFFE, "BL"), (0x0003E30E, "BL"),
         (0x0003E900, "BL"), (0x0003EBCC, "BL"), (0x0003EBD8, "BL"),
         (0x00044F7A, "BL"), (0x00045244, "BL"), (0x00045400, "BL"),
         (0x0004588A, "BL"), (0x0004C6A2, "BL"), (0x0004C6AE, "BL"),
         (0x0004D4FA, "BL"), (0x00051BDE, "BL"), (0x00052198, "BL"),
         (0x0006A850, "BL"), (0x0006A85A, "BL"), (0x0007F364, "BL"),
         (0x0007F3FC, "BL"), (0x00089682, "BL"), (0x00091420, "BL"),
         (0x0009142C, "BL"), (0x00092BB6, "BL"), (0x00092BC4, "BL"),
         (0x00092BDC, "BL"), (0x00092BF8, "BL")),
    ),
    _function(
        0x0004CBA4, 6, "r1_phone_connection_handle_get",
        "product phone-role connection-handle accessor",
        "4af57962177981e766a33cad6cdf80f1a7892884aebd51a147f6bf4fdd7af566",
        ((0x0003E340, "BL"), (0x0003E90E, "BL"), (0x0004523C, "BL"),
         (0x00045392, "BL"), (0x000453F8, "BL"), (0x000459BA, "BL"),
         (0x0004D4BC, "BL"), (0x00051C2A, "BL"), (0x0007F3F4, "BL"),
         (0x0007F446, "BL"), (0x00083544, "BL"), (0x00083560, "BL"),
         (0x000835D2, "BL"), (0x000835EE, "BL"), (0x00083660, "BL"),
         (0x0008367C, "BL"), (0x000836D2, "BL"), (0x000836EA, "BL"),
         (0x00083738, "BL"), (0x00083754, "BL"), (0x000837C6, "BL"),
         (0x000837E2, "BL"), (0x0008387C, "BL"), (0x000838A0, "BL"),
         (0x000838C4, "BL"), (0x00083912, "BL"), (0x00083940, "BL"),
         (0x00083958, "BL"), (0x00083982, "BL"), (0x0008399A, "BL"),
         (0x000839BA, "BL"), (0x000839E4, "BL"), (0x00083C30, "BL"),
         (0x00083C48, "BL"), (0x00083C6C, "BL"), (0x00083C88, "BL"),
         (0x00083D44, "BL"), (0x00084C88, "BL")),
    ),
    _function(
        0x00051AA0, 472, "r1_connection_parameter_ble_observer",
        "BLE connect/disconnect/parameter-update product policy",
        "3b73ea67fb15c04cb02fcebeaeff9bcb04b32b574f3798079f74f84512237cbc",
        (),
    ),
    _function(
        0x00072B80, 14, "r1_connection_parameters_are_fast",
        "maximum-interval speed classifier",
        "b8482c5ec8f9a3e6f9028fb6ed2712777bce3a192c280b5f9b796a3767b4fe1b",
        ((0x00051ADA, "BL"), (0x00051AFC, "BL")),
    ),
)


EXPECTED_LITERALS = {
    0x00051C84: 0x200064B2,
    0x00051C88: 0x200064F6,
    0x00051CE0: 0x000882AD,
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
    for function in R1_CONNECTION_PARAMETER_FUNCTIONS:
        entry = int(function["entry"])
        body = _bytes(image, entry, int(function["size"]))
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"connection-parameter closure changed at 0x{entry:08x}")
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
            raise ValueError(f"connection-parameter literal changed at 0x{address:08x}")
        literals[f"0x{address:08x}"] = f"0x{actual:08x}"

    return {
        "analysis": "R1 product BLE connection-parameter policy",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "literals": literals,
        "behavior": {
            "fast_when_maximum_interval_strictly_below": 50,
            "handled_ble_gap_event_ids": [0x10, 0x11, 0x12],
            "recognized_initial_pairs": [[39, 39], [36, 36]],
            "mismatch_retry_ms": {"actual_slow": 4, "actual_fast": 2000},
            "phone_and_glasses_handles_are_distinct_product_state": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "nordic_ble_event_and_gap_update_external": True,
            "event_loop_timer_external": True,
            "logging_external": True,
            "live_ble_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
