#!/usr/bin/env python3
"""Pin the recovered R1-owned touch-slider and gesture-event closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
EXPECTED_ENTRY_SHA256 = "08f08fa200dde8e491ca2da997bfd1f6d0b6494cc0704dd0290e560705018e1b"
EXPECTED_BODY_SHA256 = "64631eaf61847891223d8ce5122b2e346a37671f0cdb7fc176397ca2030def56"
EXPECTED_CALLMAP_SHA256 = "3d51a985edc7ada69fba1170b109092e1373d04c8749febfc048314427c4c8e8"


def _function(
    entry: int,
    end_exclusive: int,
    size: int,
    symbol: str,
    sha256: str,
    segments: tuple[tuple[int, int], ...] = (),
    inventory: str = "ghidra_function",
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": size,
        "symbol": symbol,
        "sha256": sha256,
        "segments": segments or ((entry, end_exclusive),),
        "inventory": inventory,
        "provider_family": "r1_product_specific",
        "source_disposition": "clean_room_behavior_only",
    }


R1_TOUCH_SLIDER_FUNCTIONS = (
    _function(0x0003E938, 0x0003EBEA, 690, "r1_touch_gesture_dispatch",
              "b6105b04be4e6873f9301c4b2739aab719e0db9d8fc73f7c7adfdbbd54719f58"),
    _function(0x00059AAC, 0x00059B9A, 238, "r1_touch_slider_velocity_filter",
              "9c877e924dfdb3c4d38f2ef9ff48ce7baf1e5c8df19aebee8cc4cae4b1e35e79"),
    _function(0x00067460, 0x0006746C, 12, "r1_touch_slider_callback_setter",
              "b06ad4bcbdbbf930fe88e226fde9343cde2d31d42ee43fd3e80d226b0050d9a6"),
    _function(0x0008E758, 0x0008E79E, 70, "r1_touch_slider_calibration",
              "9d363f56a0f31d2183f5b5d1d5ea0499892a582597e8cbd14ab45c1e12d86b6a"),
    _function(0x0008E7B0, 0x0008E7C6, 22, "r1_touch_service_callback_registration",
              "9d78c32f82cfa6ca8f4f17b1e3be4cea8ae04dde4babd238117495fcf1e567ce"),
    _function(0x0008E9D0, 0x0008EA02, 50, "r1_touch_pending_tap_timeout",
              "6572114f1e891893fb80578b4f4c447f7f29e231af26507fc56899de0af8cc21"),
    _function(0x00092C70, 0x00092CB2, 66, "r1_touch_release_debounce",
              "7e753a5ab8f09841e9f6e76a22b8f2b139de673b88f79e694eb58538111bace4"),
    _function(0x00092CBC, 0x00093380, 1422, "r1_touch_slider_state_machine",
              "ed8a35a345c36fa8abfb8138cb319b1e66a7b14e8b053b8f953207f0b9c9376f",
              ((0x00092CBC, 0x000930D8), (0x0009320C, 0x00093320),
               (0x00093322, 0x00093380))),
    _function(0x00093388, 0x0009338C, 4, "r1_touch_slider_callback_setter_thunk",
              "817c2ebdcd8790bd188e45cb0809b0377f0d75eeb41ffe178f6ed3a0a5137ba8"),
    _function(0x000933FC, 0x00093404, 8, "r1_touch_ready_irq_callback",
              "6e3b81f60465c39caab1c2558030ece7f01dc58c8ba3601d76e7f75a4caa3ab1",
              inventory="manual_provenance_supplement"),
    _function(0x00093404, 0x00093410, 12, "r1_touch_ready_callback_setter",
              "2c4a4590ce88f18e808679d296bfc3af714d6d5bc29e8fe47a1d8231693f709c"),
    _function(0x00093424, 0x000934D8, 180, "r1_touch_synthetic_release_dispatch",
              "104c9484bf53405dd94b3774a26f37282bf11e523cb8b3a1a6e30140817684ce"),
    _function(0x00093504, 0x0009350E, 10, "r1_touch_task_event_post",
              "3d02749e0b7009bc72d03ab15613efe14c5ac0439746bb1b7da5a339da4327bb"),
)


def _body(image: bytes, function: dict[str, Any]) -> bytes:
    return b"".join(
        image[start - LOAD_BASE:end - LOAD_BASE]
        for start, end in function["segments"]
    )


def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    ordered = tuple(sorted(R1_TOUCH_SLIDER_FUNCTIONS, key=lambda item: item["entry"]))
    entry_digest = hashlib.sha256(b"".join(
        int(item["entry"]).to_bytes(4, "little") for item in ordered
    )).hexdigest()
    if entry_digest != EXPECTED_ENTRY_SHA256:
        raise ValueError("R1 touch-slider entry set changed")

    output = []
    bodies = []
    callmap = []
    for function in ordered:
        entry = int(function["entry"])
        body = _body(image, function)
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"R1 touch-slider body changed at 0x{entry:08x}")
        bodies.append(body)
        calls = tuple(address for address, _ in direct_thumb_branches_to(
            image, LOAD_BASE, entry))
        callmap.append([f"0x{entry:08x}", [f"0x{x:08x}" for x in calls]])
        output.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callsites": [f"0x{address:08x}" for address in calls],
            "segments": [
                {"start": f"0x{start:08x}",
                 "end_exclusive": f"0x{end:08x}", "size": end - start}
                for start, end in function["segments"]
            ],
        })

    body_digest = hashlib.sha256(b"".join(bodies)).hexdigest()
    callmap_digest = hashlib.sha256(json.dumps(
        callmap, separators=(",", ":")
    ).encode()).hexdigest()
    if body_digest != EXPECTED_BODY_SHA256 or \
            callmap_digest != EXPECTED_CALLMAP_SHA256:
        raise ValueError("R1 touch-slider aggregate changed")

    callback_pointer = image[0x0008E7CC - LOAD_BASE:0x0008E7D0 - LOAD_BASE]
    if callback_pointer != (0x00092CBD).to_bytes(4, "little"):
        raise ValueError("R1 slider callback pointer changed")

    initial_config = bytes.fromhex(
        "000000000000e80300000a00b400000000000000000000000000000000000000"
        "0000000000000000000070430000c84300000000000000000000000000000000"
    )
    return {
        "analysis": "R1 product-owned touch-slider and gesture-event closure",
        "image": str(path),
        "image_sha256": digest,
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
        "manual_supplement_count": 1,
        "manual_supplement_bytes": 8,
        "functions": output,
        "identity": {
            "callback_pointer_address": "0x0008e7cc",
            "callback_pointer": "0x00092cbd",
            "slider_state_machine": "0x00092cbc",
            "gesture_dispatch": "0x0003e938",
            "config_runtime_address": "0x200067c4",
            "state_runtime_address": "0x20016a60",
        },
        "initial_configuration": {
            "bytes_sha256": hashlib.sha256(initial_config).hexdigest(),
            "long_press_threshold_raw": 1000,
            "coordinate_min": 10,
            "coordinate_max": 180,
            "pressure_reference": 240.0,
            "pressure_initial_peak": 400.0,
            "calibration_span_units": 213.3333282470703,
            "normalized_coordinate_span": 200.0,
        },
        "events": {
            "0x01": "press",
            "0x02": "release",
            "0x04": "tap/click",
            "0x08": "multi-click completion",
            "0x10": "long press",
            "0x20": "negative-direction slide",
            "0x40": "positive-direction slide",
            "0x80": "press timeout/error",
        },
        "ownership": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "vendor_algorithm_included": False,
            "controller_register_semantics_included": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_gpio_or_i2c_access": False,
            "raw_controller_sender_emitted": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
