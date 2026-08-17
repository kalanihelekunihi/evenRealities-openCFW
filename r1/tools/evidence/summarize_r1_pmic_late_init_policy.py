#!/usr/bin/env python3
"""Pin the Ghidra-omitted R1 NFC/PMIC late-initialization policy."""

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

R1_PMIC_LATE_INIT_POLICY_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00096A7C,
    "end_exclusive": 0x00096AD0,
    "size": 84,
    "symbol": "r1_pmic_late_init_plan_build",
    "sha256": "c3244e2b6c136ada745280e2d792ef78f315e56612988ea17e920e4b8afd443f",
    "callers": ((0x00092512, "BL"),),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

EXPECTED_CALLS = {
    0x000504D8: ((0x00096A84, "BL"),),
    0x00078530: ((0x00096A8A, "BL"),),
    0x00077764: ((0x00096A8E, "BL"),),
    0x000504C0: ((0x00096A92, "BL"),),
    0x00042EC4: ((0x00096A98, "BL"),),
    0x0005083C: ((0x00096A9E, "BL"),),
    0x00077220: ((0x00096AA4, "BL"),),
    0x0007BA24: ((0x00096AA8, "BL"),),
    0x00065B4C: ((0x00096AB8, "BL"),),
}


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_PMIC_LATE_INIT_POLICY_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
    callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, entry))
    calls = {
        target: tuple(
            (address, kind) for address, kind in
            direct_thumb_branches_to(image, DEFAULT_BASE, target)
            if entry <= address < end
        )
        for target in EXPECTED_CALLS
    }
    literals = tuple(struct.unpack_from(
        "<IIII", image, 0x00096AC0 - DEFAULT_BASE
    ))
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            callers != function["callers"] or calls != EXPECTED_CALLS or \
            literals != (0x20006870, 0x00042EC5, 0x00042D2F, 0x00042ED9):
        raise ValueError("R1 PMIC late-initialization policy changed")

    return {
        "analysis": "R1 NFC/PMIC late-initialization policy",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": int(function["size"]),
        "ghidra_function_count": 0,
        "manual_supplement_count": 1,
        "function": {
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"address": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        },
        "call_order": [
            "acquire_nfc_i2c5_resource",
            "delay_50_milliseconds",
            "configure_st25dvxxkc",
            "release_nfc_i2c5_resource",
            "run_charge_i2c_event_zero",
            "install_yhm_callback_0x00042ec5",
            "install_device_callback_0x00042d2f",
            "read_configuration_byte_0x70",
        ],
        "state": {
            "ready_flag": "0x20006870",
            "ready_flag_cleared_before_calls": True,
        },
        "factory_branch": {
            "configuration_marker": 0x55,
            "callback": "0x00042ed9",
            "delay_ticks": 1024,
            "context": 0,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "nfc_provider_reimplemented": False,
            "shared_resource_reimplemented": False,
            "timer_reimplemented": False,
            "live_initialization_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
