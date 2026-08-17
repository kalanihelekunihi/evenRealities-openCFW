#!/usr/bin/env python3
"""Pin the R1-owned wear-fusion callbacks, arithmetic, and decision closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _function(
    entry: int, size: int, symbol: str, role: str, sha256: str,
    callers: tuple[tuple[int, str], ...],
    pointer_refs: tuple[int, ...] = (),
    inventory: str = "ghidra_functions_csv",
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": entry + size,
        "size": size,
        "symbol": symbol,
        "role": role,
        "sha256": sha256,
        "callers": callers,
        "pointer_refs": pointer_refs,
        "inventory": inventory,
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    }


R1_WEAR_FUSION_FUNCTIONS = (
    _function(
        0x0003CD80, 146, "r1_wear_motion_topic_callback",
        "motion-topic callback and wear-fusion dispatcher",
        "f116ced7cb0afb9e407c46d6303a75599c9777d518a574cea49e6e4195f121be",
        (),
    ),
    _function(
        0x0003CE1C, 36, "r1_wear_optical_history_topic_callback",
        "bounded five-slot optical-history ingestion",
        "d18576349aeb0054258b21a50509c1750ba53bb0d99b24067db248e848fc0e11",
        (), (0x0003D1A4,), "manual_provenance_supplement",
    ),
    _function(
        0x0003CE44, 94, "r1_wear_living_topic_callback",
        "living-object callback and timestamp capture",
        "d6c2c908e569d860d2cb8f8ddef5d451725261bbef9861e1f2e1e81c1c6ad84a",
        (),
    ),
    _function(
        0x0003CEEC, 378, "r1_wear_motion_statistics",
        "motion mean and population-variance producer",
        "80b734b5c2cb4c64f422ebd7c2ca9473160fef4224879a04a1b85658dac77f7e",
        ((0x0003CDBC, "BL"),),
    ),
    _function(
        0x0003D06C, 72, "r1_wear_optical_history_range",
        "five-slot optical-history range helper",
        "57d87392bb9452ec09f0fcb09a403ca8588c64ba5768ca6336c47157408995d1",
        ((0x0003D28C, "BL"),),
    ),
    _function(
        0x0003D0C0, 42, "r1_wear_probe_teardown",
        "wear-probe subscription and timeout teardown",
        "d6ae14c1275550283ca9072f6e55ac7beb5e1e42596aa632b9da832fbd6dbe25",
        ((0x0003D16E, "B.W"), (0x0004C530, "BL"), (0x0004C6CC, "B.W")),
    ),
    _function(
        0x0003D0FC, 54, "r1_wear_raw_hr_probe_start",
        "raw-HR subscription and 3,000-tick timeout planning",
        "e187ba8f33090625a1d65bcc11071ec97abf2be57f11e2f79853045c3c86a4db",
        ((0x0004C534, "BL"), (0x0004C606, "B.W")), (),
        "manual_provenance_supplement",
    ),
    _function(
        0x0003D150, 74, "r1_wear_adt_status_topic_callback",
        "ADT status, charge gate, subscription, and 7,000-tick timeout planning",
        "8b80b47e0392b33c91571cea03a14a645a8783fe179c9118e1031e121730e6e9",
        (), (0x0004C60C,), "manual_provenance_supplement",
    ),
    _function(
        0x0003D1B8, 86, "r1_wear_sleep_status_topic_callback",
        "sleep-status edge and pending-decision update",
        "7e74a0b8b339e52d84c1a55b4c8e3485157ceec66466fe4a44c7ab289799e2b4",
        (), (0x0004C630,), "manual_provenance_supplement",
    ),
    _function(
        0x0003D268, 294, "r1_wear_on_decision",
        "optical-or-motion suspected-wear transition",
        "57cc089fca628777de825cb9c557c0657bc6b7f7f224e26a7740a0153866dae2",
        ((0x0003CE0C, "BL"),),
    ),
    _function(
        0x0003D45C, 480, "r1_wear_off_decision",
        "living, low-IR, and stationary-table wear-off transition",
        "8511cd323737b80efcc86f314395b7f4a89f0b29710947b9b1276243e40efac9",
        ((0x0003CDCA, "BL"),),
    ),
)


EXPECTED_LITERALS = {
    0x0003D644: 0x0003CE45,
    0x0003D660: 9_050_000,
    0x0003D664: 0x42200000,
    0x0003D668: 0xBB8CFFFF,
    0x0003D66C: 0x00137FFF,
    0x0004C614: 0x0003CD81,
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
    for function in R1_WEAR_FUSION_FUNCTIONS:
        entry = int(function["entry"])
        body = _bytes(image, entry, int(function["size"]))
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"wear-fusion closure changed at 0x{entry:08x}")
        for pointer_address in function["pointer_refs"]:
            pointer = struct.unpack("<I", _bytes(image, pointer_address, 4))[0]
            if pointer != entry + 1:
                raise ValueError(
                    f"wear-fusion callback pointer changed at "
                    f"0x{pointer_address:08x}"
                )
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
            "pointer_refs": [
                f"0x{address:08x}" for address in function["pointer_refs"]
            ],
        })

    literals = {}
    for address, expected in EXPECTED_LITERALS.items():
        actual = struct.unpack("<I", _bytes(image, address, 4))[0]
        if actual != expected:
            raise ValueError(f"wear-fusion literal changed at 0x{address:08x}")
        literals[f"0x{address:08x}"] = f"0x{actual:08x}"

    return {
        "analysis": "R1 product-owned wear-fusion closure",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "ghidra_function_count": sum(
            item["inventory"] == "ghidra_functions_csv"
            for item in R1_WEAR_FUSION_FUNCTIONS
        ),
        "manual_supplement_count": sum(
            item["inventory"] == "manual_provenance_supplement"
            for item in R1_WEAR_FUSION_FUNCTIONS
        ),
        "functions": functions,
        "callback_thumb_literals": {
            "motion": "0x0004c614 -> 0x0003cd81",
            "living": "0x0003d644 -> 0x0003ce45",
            "optical_history": "0x0003d1a4 -> 0x0003ce1d",
            "adt_status": "0x0004c60c -> 0x0003d151",
            "sleep_status": "0x0004c630 -> 0x0003d1b9",
        },
        "literals": literals,
        "behavior": {
            "internal_states": {"0": "not worn", "1": "suspected worn", "2": "living-confirmed worn"},
            "minimum_motion_samples": 10,
            "optical_history_slots": 5,
            "wear_on_ir_strictly_above": 9_050_000,
            "wear_on_ir_range_minimum": 100_000,
            "wear_on_motion_variance_strictly_above": 2_000.0,
            "living_window_ticks_inclusive": 0x800,
            "wear_off_ir_strictly_below": 9_050_000,
            "wear_off_ir_decisions": 5,
            "wear_off_absolute_mean_y_strict_bounds": [972.0, 1076.0],
            "wear_off_variance_strictly_below": 40.0,
            "wear_off_stationary_decisions": 60,
            "raw_hr_timeout_ticks": 3_000,
            "adt_timeout_ticks": 7_000,
            "optical_history_copy_bounded_slots": 5,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "sensor_stream_framework_external": True,
            "goodix_algorithms_external": True,
            "live_sensor_or_ble_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
