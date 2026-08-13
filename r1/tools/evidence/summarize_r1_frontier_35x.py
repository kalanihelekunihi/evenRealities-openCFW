#!/usr/bin/env python3
"""Pin the five-function 348...354-byte R1 ownership frontier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_FRONTIER_35X_PRODUCT_FUNCTIONS: tuple[dict[str, Any], ...] = (
    {"entry": 0x00033DBC, "end_exclusive": 0x00033F1E, "size": 354,
     "inventory": "ghidra_functions_csv",
     "sha256": "52c100f23a936a8344170aed0c63d53b3f3ede79b9e7c2aee01e59f21b6a5176",
     "symbol": "r1_ble_thread_message_encode",
     "role": "BLE-to-thread allocated message envelope and queue handoff",
     "callers": ((0x0005D650, "BL"),)},
    {"entry": 0x0008216C, "end_exclusive": 0x000822CC, "size": 352,
     "inventory": "ghidra_functions_csv",
     "sha256": "a858402f6e9667b3cce7992510f8497101c7560a09a3c3ba87d08a22c1c01368",
     "symbol": "r1_peer_bond_diagnostic_plan",
     "role": "Peer Manager bonding diagnostic with LTK output redacted",
     "callers": ((0x0007F488, "BL"), (0x0007F632, "B.W"))},
    {"entry": 0x000425B0, "end_exclusive": 0x00042710, "size": 352,
     "inventory": "ghidra_functions_csv",
     "sha256": "dc30b28db92809ab9c15f66cc5e01ad9d59e0b8e84dd73d8c569f5df0602fc39",
     "symbol": "r1_user_profile_plan_transition",
     "role": "12-byte user-profile event consumer and provider reinitialization policy",
     "callers": ()},
    {"entry": 0x0006A714, "end_exclusive": 0x0006A870, "size": 348,
     "inventory": "ghidra_functions_csv",
     "sha256": "eb3d69ee62b4c1d8d73a8d8da8d4b1d82d80c5c9a77cbc89fee1cf1b5c4fa6fe",
     "symbol": "r1_glasses_status_plan_command",
     "role": "glasses wear/status lifecycle and delayed-action policy",
     "callers": ((0x0004E368, "BL"), (0x0006267E, "B.W"))},
)

GOMORE_FRONTIER_35X_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00094384, "end_exclusive": 0x000944E2, "size": 350,
    "inventory": "ghidra_functions_csv",
    "sha256": "bd4728f0616cfce144cbe113dc5c4583fbe7481fd3cdf036146edad24176c214",
    "symbol": "", "role": "GoMore sensor-update and monotonic-timestamp orchestrator",
    "callers": ((0x0006ACAE, "BL"), (0x0006C2A2, "BL")),
},)

ALL_FUNCTIONS = R1_FRONTIER_35X_PRODUCT_FUNCTIONS + GOMORE_FRONTIER_35X_FUNCTIONS


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")
    rows = []
    for function in ALL_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"frontier function changed: 0x{entry:08x}")
        rows.append({**function, "entry": f"0x{entry:08x}",
                     "end_exclusive": f"0x{end:08x}",
                     "callers": [{"callsite": f"0x{x:08x}", "kind": kind}
                                 for x, kind in callers]})
    return {
        "analysis": "348...354-byte ownership frontier",
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(rows),
        "function_bytes": sum(int(row["size"]) for row in rows),
        "product_function_count": len(R1_FRONTIER_35X_PRODUCT_FUNCTIONS),
        "gomore_function_count": len(GOMORE_FRONTIER_35X_FUNCTIONS),
        "functions": rows,
        "safety": {
            "ltk_bytes_exposed": False,
            "live_ble_or_rtos_operation": False,
            "live_power_or_touch_operation": False,
            "gomore_provider_reimplemented": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
