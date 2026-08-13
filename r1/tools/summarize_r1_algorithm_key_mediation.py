#!/usr/bin/env python3
"""Pin the production R1 algorithm-key request and first-party phone mediation.

This is a read-only audit of the supplied firmware image and decompiled Android AOT text. It does
not contact Even's API, retrieve or retain key material, connect to BLE, execute firmware, or
construct/transmit a provisioning command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


DEFAULT_AOT_ROOT = (
    Path(__file__).resolve().parents[3]
    / "SybilSight-v2"
    / "firmware"
    / "blutter_output_2.2.0"
    / "asm"
)

HANDLER_START = 0x00083E50
HANDLER_END = 0x00083EEC
HANDLER_SHA256 = "ee55c78f47da403c60f713f4a308e525e13c7306907cabbf3341c02454ea881e"
RESPONSE_HELPER_START = 0x000838BA
RESPONSE_HELPER_END = 0x000838DE
RESPONSE_HELPER_SHA256 = "6b7e341052267787e0aeed00bc0cf8e267a736accc0e83e8a607f9788ceb3574"
REQUEST_LATCH_GETTER_START = 0x0006ABD8
REQUEST_LATCH_GETTER_END = 0x0006ABE4
REQUEST_LATCH_GETTER_SHA256 = "de9454ad0a58248ad7d3ee005f0857a866ed6cf02265eb01c8299e5f15a1c505"
REQUEST_LATCH_CLEAR_START = 0x0006AADC
REQUEST_LATCH_CLEAR_END = 0x0006AAE4
REQUEST_LATCH_CLEAR_SHA256 = "eacaae3bbc56723e39a2d1c9704b34bf9e222097274224f9ae1bfc5145716f9c"
IDENTIFIER_GETTER_START = 0x0006AB88
IDENTIFIER_GETTER_END = 0x0006ABC2
IDENTIFIER_GETTER_SHA256 = "2ff97992dc73d02a97d5eb91e726c742915db7b3d57a8216009a5f751a0151e6"
REGISTRATION_ADDRESS = 0x0009A514
REGISTRATION_BYTES = bytes.fromhex("0b000000513e0800")


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset : offset + end - start]


def checked_range(
    image: bytes,
    base: int,
    start: int,
    end: int,
    expected: str,
) -> dict[str, str]:
    actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
    if actual != expected:
        raise ValueError(f"unexpected range 0x{start:08x}...0x{end:08x}: {actual}")
    return {
        "start": f"0x{start:08x}",
        "end_exclusive": f"0x{end:08x}",
        "sha256": actual,
    }


def require(text: str, marker: str, label: str) -> dict[str, object]:
    if marker not in text:
        raise ValueError(f"missing {label}: {marker!r}")
    return {
        "label": label,
        "marker": marker,
        "line": text[: text.index(marker)].count("\n") + 1,
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branch_addresses(image: bytes, base: int, target: int) -> list[int]:
    return [address for address, _ in direct_thumb_branches_to(image, base, target)]


def summarize(image_path: Path, base: int, aot_root: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    home_path = (
        aot_root / "even/pages/main_screen/tab_page/home/home_controller.dart"
    )
    proto_path = aot_root / "even_connect/ring1/ble_ring1_cmd_proto.dart"
    model_path = (
        aot_root
        / "even_connect/ring1/models/system/ble_ring1_system_algo_key.dart"
    )
    api_path = aot_root / "even/common/api/api_service.dart"
    aot_paths = [home_path, proto_path, model_path, api_path]
    missing = [str(path) for path in aot_paths if not path.is_file()]
    if missing:
        raise ValueError("missing AOT source files:\n" + "\n".join(missing))

    home = home_path.read_text(errors="replace")
    proto = proto_path.read_text(errors="replace")
    model = model_path.read_text(errors="replace")
    api = api_path.read_text(errors="replace")

    registration = flash_bytes(
        image,
        base,
        REGISTRATION_ADDRESS,
        REGISTRATION_ADDRESS + len(REGISTRATION_BYTES),
    )
    if registration != REGISTRATION_BYTES:
        raise ValueError(f"unexpected algorithm-key registration: {registration.hex()}")

    expected_branches = {
        REQUEST_LATCH_GETTER_START: [0x00083E60],
        REQUEST_LATCH_CLEAR_START: [0x00083E98],
        IDENTIFIER_GETTER_START: [0x0006B29E, 0x00083E78, 0x0008EA72],
        RESPONSE_HELPER_START: [0x00083EE4],
    }
    verified_branches: dict[str, list[str]] = {}
    for target, expected in expected_branches.items():
        actual = branch_addresses(image, base, target)
        if actual != expected:
            raise ValueError(
                f"unexpected direct branches to 0x{target:08x}: "
                f"{[hex(value) for value in actual]}"
            )
        verified_branches[f"0x{target:08x}"] = [
            f"0x{address:08x}" for address in actual
        ]
    if direct_thumb_branches_to(image, base, HANDLER_START):
        raise ValueError("table-dispatched algorithm-key handler acquired a direct branch")

    home_markers = [
        require(home, "0x1489fa4: EnterFrame", "ring startup information routine"),
        require(home, "0x148a440: r0 = BleRing1CmdGoMoreExt.getAlgoKeyStatus()",
                "algorithm-key status query"),
        require(home, "0x148a454: cmp             w0, NULL", "nil status gate"),
        require(home, "0x148a460: cmp             x1, #1", "status-one provisioning gate"),
        require(home, "0x148a484: LoadField: r2 = r0->field_f",
                "ring-provided identifier read"),
        require(home, "0x148a48c: r0 = ApiServiceHealthExt.getGoMorePKey()",
                "vendor key fetch"),
        require(home, "0x148a49c: LoadField: r2 = r0->field_13",
                "nullable server string read"),
        require(home, "0x148a4a4: cmp             w2, NULL", "nil server-key gate"),
        require(home, "0x148a4b0: cbz             w0, #0x148a4d0",
                "empty server-key gate"),
        require(home, "0x148a4c0: r0 = BleRing1CmdGoMoreExt.setAlgoKey()",
                "ring provisioning call"),
        require(home, "0x148a4cc: r0 = Await()", "provisioning await"),
        require(home, "0x148a4e8: r0 = HealthCtlPublicFetchExt.fetchAllLatestDataFromCacheAndCloud()",
                "unconditional continuation after key flow"),
    ]
    proto_markers = [
        require(proto, "0x148a5e8: EnterFrame", "setAlgoKey routine"),
        require(proto, "0x148a628: LoadField: r2 = r0->field_7",
                "Dart string-length prefix source"),
        require(proto, "0x148a64c: r0 = toBytes()", "set payload serialization"),
        require(proto, "0x148a650: r16 = Instance_BleRing1StatusMethod",
                "status method send"),
        require(proto, "0x148a680: r0 = BleRing1CmdPublicExt.sendCmd()",
                "normal provisioning sender"),
        require(proto, "0x148a8dc: EnterFrame", "getAlgoKeyStatus routine"),
        require(proto, "0x148a930: r0 = BleRing1CmdPublicExt.sendCmd()",
                "normal status sender"),
        require(proto, "0x148a980: cmp             x0, #1",
                "requires response payload longer than one byte"),
        require(proto, "0x148a990: r0 = fromBytes()", "typed status decode"),
    ]
    model_markers = [
        require(model, "0x148a6b4: r3 = 2",
                "one-element Dart list represented as Smi two"),
        require(model, "0x148a700: StoreField: r2->field_f = r0",
                "length byte stored first"),
        require(model, "0x148a730: r0 = StringExt.toUint8List()",
                "UTF-8-like string conversion"),
        require(model, "0x148a73c: r0 = addAll()", "key bytes appended"),
        require(model, "0x148a9e4: ldrb            w3, [x0]",
                "status byte zero decode"),
        require(model, "0x148a9f8: r2 = 2",
                "sublist index one represented as Smi two"),
        require(model, "0x148aa18: r0 = Uint8listExt.decodeToString()",
                "identifier decode from byte one"),
    ]
    api_markers = [
        require(api, "0x148a844: EnterFrame", "getGoMorePKey routine"),
        require(api, '0x148a880: r16 = "uuid"', "query parameter name"),
        require(api, '0x148a8ac: r16 = "/v2/g/health/get_pkey"',
                "vendor key endpoint"),
        require(api, "0x148a8c0: r0 = evenGet()", "authenticated vendor GET"),
    ]

    return {
        "analysis": "R1 production algorithm-key request and phone mediation",
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": [
            checked_range(
                image, base, HANDLER_START, HANDLER_END, HANDLER_SHA256
            ),
            checked_range(
                image,
                base,
                RESPONSE_HELPER_START,
                RESPONSE_HELPER_END,
                RESPONSE_HELPER_SHA256,
            ),
            checked_range(
                image,
                base,
                REQUEST_LATCH_GETTER_START,
                REQUEST_LATCH_GETTER_END,
                REQUEST_LATCH_GETTER_SHA256,
            ),
            checked_range(
                image,
                base,
                REQUEST_LATCH_CLEAR_START,
                REQUEST_LATCH_CLEAR_END,
                REQUEST_LATCH_CLEAR_SHA256,
            ),
            checked_range(
                image,
                base,
                IDENTIFIER_GETTER_START,
                IDENTIFIER_GETTER_END,
                IDENTIFIER_GETTER_SHA256,
            ),
        ],
        "registration": {
            "address": f"0x{REGISTRATION_ADDRESS:08x}",
            "system_subcommand": "0x0b",
            "handler_thumb": "0x00083e51",
            "raw_hex": registration.hex(),
        },
        "verified_direct_branches": verified_branches,
        "firmware_response": {
            "payload_bytes": 25,
            "status_offset": 0,
            "identifier_offset": 1,
            "identifier_bytes": 24,
            "status_zero": "no phone provisioning request",
            "status_one": "one-shot phone provisioning request",
            "status_one_clears_latch_before_response": True,
            "response_subcommand": "0x0b",
            "response_type_raw": 1,
            "request_serial_preserved": True,
        },
        "aot": {
            "source": "Even Android 2.2.0 AOT disassembly",
            "files": [
                {"path": str(path), "sha256": sha256(path)}
                for path in aot_paths
            ],
            "home_markers": home_markers,
            "proto_markers": proto_markers,
            "model_markers": model_markers,
            "api_markers": api_markers,
            "flow": {
                "query_after_ring_startup": True,
                "fetch_only_when_status_is_one": True,
                "endpoint": "/v2/g/health/get_pkey",
                "query_parameter": "uuid",
                "set_only_for_nonnull_nonempty_server_string": True,
                "first_party_exact_64_byte_validation": False,
                "set_payload": "Dart string length byte followed by encoded string bytes",
                "post_write_status_or_flash_verification": False,
                "provisioning_result_controls_following_health_fetch": False,
            },
        },
        "safety": {
            "network_contact_performed": False,
            "key_material_read_or_retained": False,
            "live_command_constructed": False,
            "ble_access": False,
            "firmware_executed": False,
            "storage_mutated": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    parser.add_argument("--aot-root", type=Path, default=DEFAULT_AOT_ROOT)
    args = parser.parse_args()
    print(json.dumps(
        summarize(args.image, args.base, args.aot_root),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
